import os
import re
from dotenv import load_dotenv
import pytest
from pathlib import Path
from typing import Generator, Optional
from urllib.parse import quote
from playwright.sync_api import Page

from auth.salesforce import get_salesforce_auth

ARTIFACTS_DIR = Path("artifacts")

# Load environment variables from .env for local runs.
# In CI, these are expected to be provided by the environment.
load_dotenv()



# -------------------------------------------------------------------------------------------------
# Funcitions
# -------------------------------------------------------------------------------------------------


def _safe_name(name: str) -> str:
    # Make a filename-safe test id by replacing problematic characters with underscores
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", f"{name}")


def _env_flag(name: str, default: str = "0") -> bool:
    # Interpret environment variable as a boolean flag (for PAUSE_ON_FAIL = 1/true/yes)
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _delete_dir_if_empty(path):
    # Attempt to delete the directory if it exists and is empty, ignoring errors if it's not empty or in use 
    # (we just want to clean up empty dirs from successful tests, but don't want to risk losing data from failed tests)
    try:
        if path.exists() and path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    except OSError:
        # Directory not empty or in use – ignore
        pass


# -------------------------------------------------------------------------------------------------
# Pytest hook
# -------------------------------------------------------------------------------------------------


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to capture test outcomes and handle failures.
    This runs after each test phase (setup, call, teardown) and allows us to inspect the result and perform actions on failure 
    (capture screenshots, traces, html, and pause if env variable PAUSE_ON_FAIL = 1/true/yes).
    """
    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)

    if rep.when != "call" or not rep.failed:
        return
    # If we get here, the test has failed during the "call" phase (the test body itself), so we want to capture artifacts and optionally pause.
    print("\n==== PYTEST FAILURE (longrepr) ====\n")
    print(rep.longrepr)

    crash = getattr(rep.longrepr, "reprcrash", None)
    if crash and getattr(crash, "message", None):
        # If available, print the crash message for easier debugging (e.g. Playwright error details)
        print("\n==== PYTEST FAILURE (message) ====\n")
        print(crash.message)

    page = getattr(item, "pw_page", None)
    if not page:
        # If we don't have a page attached, we can't capture artifacts or pause, but at least print a warning so it's clear why no artifacts are being saved.
        print("[warn] Test failed but no pw_page attached (did the test use sfdc_page?)")
        return
    
    # Generate file name and directory for artifacts based on the test id
    test_id = _safe_name(item.nodeid)
    test_dir = ARTIFACTS_DIR / test_id
    test_dir.mkdir(parents=True, exist_ok=True)

    # Capture artifacts (screenshot, HTML) on failure for easier debugging, and optionally pause the browser if PAUSE_ON_FAIL is set.
    try:
        screenshot_path = test_dir / "screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"[artifact] Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"[warn] Could not take screenshot: {e}")

    try:
        html_path = test_dir / "page.html"
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"[artifact] HTML saved: {html_path}")
    except Exception as e:
        print(f"[warn] Could not save page HTML: {e}")

    if _env_flag("PAUSE_ON_FAIL"):
        page.pause()


# -------------------------------------------------------------------------------------------------
# Salesforce frontdoor helpers
# -------------------------------------------------------------------------------------------------

def build_frontdoor_url(auth: dict, target: str) -> str:
    """
    Build a Salesforce frontdoor URL for direct, session-based login.

    This allows bypassing the UI login flow by reusing a valid access token
    and redirecting straight to a Lightning page.
    """
    return (
        f"{auth['instance_url'].rstrip('/')}/secur/frontdoor.jsp"
        f"?sid={quote(auth['access_token'])}"
        f"&retURL={quote(target)}"
    )


def sfdc_login_with_frontdoor(page: Page, auth: dict, target: str) -> None:
    """
    Navigate to Salesforce using the frontdoor URL and wait until
    the Lightning UI has fully loaded.
    """
    url = build_frontdoor_url(auth, target)
    page.goto(url, wait_until="domcontentloaded")

    # Ensure we have landed in Lightning before continuing
    page.wait_for_url("**/lightning/**", timeout=60000)


# -------------------------------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sfdc_auth():
    """
    Obtain Salesforce OAuth credentials once per test session.

    Fails fast if authentication is misconfigured to avoid
    confusing downstream test failures.
    """
    auth = get_salesforce_auth()

    # Make failures explicit and easy to diagnose
    assert "instance_url" in auth and auth["instance_url"]
    assert "access_token" in auth and auth["access_token"]

    return auth


@pytest.fixture(scope="session")
def sfdc_storage_state(browser, sfdc_auth):
    """
    Create an authenticated browser storage state using frontdoor login.

    This runs once per session and allows tests to reuse an already
    authenticated context without logging in again.
    """
    context = browser.new_context()
    page = context.new_page()

    # Use a stable landing page to establish the session
    target = "/lightning/o/Lead/home"
    sfdc_login_with_frontdoor(page, sfdc_auth, target)

    # Persist cookies and local storage for reuse
    state = context.storage_state()

    context.close()
    return state


@pytest.fixture()
def sfdc_context(browser, sfdc_storage_state):
    """
    Provide a fresh browser context per test, pre-authenticated
    using the session-level storage state.
    """
    context = browser.new_context(storage_state=sfdc_storage_state)
    yield context
    context.close()


@pytest.fixture()
def sfdc_page(sfdc_context, request) -> Page:
    """
    Provide a fresh Playwright Page per test using the authenticated
    Salesforce browser context.

    The page and its parent context are attached to the pytest node
    to enable hook-based failure handling (e.g. pause, tracing, or
    artifact capture) before teardown closes browser resources.

    Teardown only closes the page; additional failure logic is handled
    separately in pytest hooks.
    """
    page = sfdc_context.new_page()

    # Attach for hook-time capture (before teardown closes anything)
    request.node.pw_page = page
    request.node.pw_context = sfdc_context

    yield page

    # Keep teardown simple; hook handles pause/artifacts
    page.close()


@pytest.fixture(scope="session")
def sfdc_base_url():
    """
    Resolve the base Salesforce URL based on the target environment.

    Example:
      SF_ENV=DEV  -> reads SF_ENV_URL_DEV
      SF_ENV=UAT  -> reads SF_ENV_URL_UAT
    """
    env = os.getenv("SF_ENV", "DEV").upper()
    key = f"SF_ENV_URL_{env}"
    url = os.getenv(key)

    assert url, f"{key} not set"
    return url.rstrip("/")


@pytest.fixture(autouse=True)
def trace_per_test(sfdc_context, request):
    test_id = _safe_name(request.node.nodeid)
    test_dir = ARTIFACTS_DIR / test_id
    test_dir.mkdir(parents=True, exist_ok=True)

    sfdc_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield

    rep = getattr(request.node, "rep_call", None)
    failed = bool(rep and rep.failed)

    if failed:
        trace_path = test_dir / "trace.zip"
        sfdc_context.tracing.stop(path=str(trace_path))
        print(f"[artifact] Trace saved: {trace_path}")
    else:
        sfdc_context.tracing.stop()

    _delete_dir_if_empty(test_dir)
