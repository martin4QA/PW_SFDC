import os
from dotenv import load_dotenv
import pytest
from urllib.parse import quote
from playwright.sync_api import Page

from auth import get_salesforce_auth


# Load environment variables from .env for local runs.
# In CI, these are expected to be provided by the environment.
load_dotenv()

# -------------------------------------------------------------------------------------------------
# Pytest hook
# -------------------------------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Attach the test result to the test item so fixtures can
    react to failures (e.g. pause the browser for debugging).
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.rep_call = rep


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
def sfdc_page(sfdc_context, request):
    """
    Provide a new page per test and optionally pause execution
    on failure to support local debugging.
    """
    page = sfdc_context.new_page()
    yield page

    # If the test failed, optionally pause the browser for inspection.
    # Enabled only when PWDEBUG=1 is set locally.
    rep = getattr(request.node, "rep_call", None)
    failed = bool(rep and rep.failed)
    if failed and os.getenv("PWDEBUG") == "1":
        print("Test failed – pausing Playwright")
        page.pause()

    # Explicit close for clarity (context.close will also close pages)
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
