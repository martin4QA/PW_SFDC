from playwright.sync_api import Page, expect


class LeadsPage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to_leads_home(self):
        self.page.goto("/lightning/o/Lead/home", wait_until="domcontentloaded")

    def click_global_actions(self):
        self.page.get_by_role("button", name="Global Actions").click()

    def click_new_lead(self):
        expect(self.page.get_by_text("New Lead")).to_be_visible()
        self.page.get_by_text("New Lead").click()
        self.page.get_by_role("dialog", name="New Lead").wait_for()

    def fill_lead_form_mandatory(self, salutation: str, first_name: str, last_name: str, company: str):
        self.page.get_by_label("Salutation").click()
        self.page.locator(f"a[title='{salutation}']").click()
        self.page.get_by_text("First Name").fill(first_name)
        self.page.get_by_text("Last Name").fill(last_name)
        self.page.get_by_text("Company").last.fill(company)
        
    def fill_lead_form_full(self, salutation: str, first_name: str, last_name: str, company: str, title: str, email: str, phone: int):
        # self.page.get_by_role("button", name="Lead View Settings").click()
        # self.page.get_by_role("menuitem", name="Select Fields to Display").press("Escape")
        # self.page.get_by_role("button", name="App Launcher").click()
        # self.page.get_by_role("option", name="Developer Edition").click()
        # self.page.get_by_role("button", name="Global Actions").click()
        # self.page.get_by_role("menuitem", name="New Lead").click()
        self.page.get_by_role("button", name="Salutation").click()
        self.page.get_by_role("option", name="Prof.").click()
        self.page.get_by_role("textbox", name="First Name").fill(first_name)
        self.page.get_by_role("textbox", name="Last Name *").fill(last_name)
        self.page.get_by_role("textbox", name="Email").fill(email)
        self.page.get_by_role("textbox", name="Phone").fill(str(phone))
        self.page.get_by_role("textbox", name="Company *").fill(company)
        self.page.get_by_role("textbox", name="Title").fill(title)
        self.page.get_by_role("button", name="Save").click()
        self.page.get_by_role("link", name=f"Lead \"{first_name} {last_name}\" was").click()



    def save_lead(self):
        self.page.get_by_role("button", name="Save").click()

    def search_lead(self, lead_name: str):
        self.page.get_by_role("button", name="Search", exact=True).click()
        self.page.get_by_role("button", name="Search").click()
        self.page.get_by_role("searchbox", name="Search...").fill(lead_name)
        self.page.get_by_role("searchbox", name="Search...").press("Enter")
        self.page.get_by_role("link", name=lead_name).first.click()
        self.page.wait_for_url("**/lightning/r/Lead/**", timeout=60000)