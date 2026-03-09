from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from sfdc.helpers import sfdc_click


class CommonPage:
    # -------------------------
    # Constructor
    # -------------------------
    def __init__(self, page: Page):
        self.page = page

    # -------------------------
    # Locators
    # -------------------------
    @property
    def global_actions_button(self) -> Locator:
        return self.page.get_by_role("button", name="Global Actions")

    @property
    def global_actions_menu(self) -> Locator:
        return self.page.get_by_label("Global Actions")

    def global_action_item(self, action_name: str) -> Locator:
        # fall back to exact text within the menu container if not found.
        menu = self.global_actions_menu
        item = menu.get_by_role("menuitem", name=action_name)
        return item if item.count() > 0 else menu.get_by_text(action_name, exact=True)

    def heading(self, heading_name: str) -> Locator:
        return self.page.get_by_role("heading", name=heading_name)

    @property
    def app_launcher_button(self) -> Locator:
        return self.page.get_by_role("button", name="App Launcher")

    @property
    def app_launcher_panel(self) -> Locator:
        # In many Lightning orgs this is a dialog; if yours differs,
        # update it here and the rest of the code stays untouched.
        return self.page.get_by_role("heading", name="App Launcher")

    @property
    def launcher_searchbox(self) -> Locator:
        return self.page.get_by_role("searchbox")

    def launcher_target(self, app_name: str) -> Locator:
        # App launcher entries vary by org and view.
        return (
            self.page.get_by_role("option", name=app_name)
            .or_(self.page.get_by_role("link", name=app_name))
            .or_(self.page.get_by_text(app_name, exact=True))
        ).first
    
    @property
    def success_message(self) -> Locator:
        return self.page.locator("div").filter(has_text="Success notification.Lead \"")


    # -------------------------
    # Actions (behaviour)
    # -------------------------
    def open_global_actions_menu(self) -> None:

        expect(self.global_actions_button).to_be_visible(timeout=30000)
        # if not self.global_actions_menu.is_visible():
        sfdc_click(self.global_actions_button)
        # print("[info] Clicked Global Actions button to open menu")
        expect(self.global_actions_menu).to_be_visible(timeout=30000)


    def select_global_action(self, action_name: str) -> None:

        self.open_global_actions_menu()
 
        item = self.global_action_item(action_name)
        expect(item).to_be_visible()
        item.click()

        expect(self.heading(action_name)).to_be_visible()

    def open_app_from_launcher(self, app_name: str, attempts: int = 3) -> None:
        btn = self.app_launcher_button
        panel = self.app_launcher_panel

        for i in range(attempts):
            try:
                sfdc_click(btn)
        #     expect(btn).to_be_visible()
        #     btn.click()

                # Wait for launcher UI (not network)
                #expect(panel).to_be_visible(timeout=30000)
                sfdc_click(self.launcher_target(app_name))

        # # Search if available (more reliable than scrolling)
        # search = self.launcher_searchbox
        # if search.count() > 0:
        #     search.first.fill(app_name)

        # target = self.launcher_target(app_name)
        # expect(target).to_be_visible()

        # try:
        #     target.click()
                return
            except Exception:
                # Lightning re-render / panel collapsed mid-click; retry
                if i == attempts - 1:
                    raise

