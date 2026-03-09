

import time

from playwright.sync_api import Locator, expect


def sfdc_click(
    locator: Locator,
    *,
    retries: int = 3,
    timeout: int = 15000,
) -> None:
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            expect(locator).to_be_visible(timeout=timeout)
            expect(locator).to_be_enabled(timeout=timeout)

            if attempt == 0:
                locator.click(timeout=timeout)
            elif attempt == 1:
                locator.scroll_into_view_if_needed(timeout=timeout)
                locator.click(timeout=timeout)
            else:
                locator.scroll_into_view_if_needed(timeout=timeout)
                locator.click(timeout=timeout, force=True)

            return


        except TimeoutError as exc:
            last_error = exc
        # It's not pretty, but sometimes just waiting works
        # each retry will wait longer (2s, 4s, 6s) to give the page more time to stabilize
        time.sleep(retries * 2)
        
    if last_error:
        raise last_error