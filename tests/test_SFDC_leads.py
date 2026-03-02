import pytest
from playwright.sync_api import expect
from ui_pages.leads import LeadsPage
from test_data.lead_data import generate_test_data


@pytest.fixture()
def test_data_generator():
    return generate_test_data()

@pytest.fixture()
def sfdc_leads_home(sfdc_page, sfdc_base_url):
    sfdc_page.goto(sfdc_base_url + "/lightning/o/Lead/home", wait_until="domcontentloaded")
    # Ensure we have landed in the correct app before continuing
    # sfdc_page.pause()

    # sfdc_page.wait_for_timeout(300)
    sfdc_page.wait_for_load_state("domcontentloaded")
    sfdc_page.get_by_role("button", name="App Launcher").click()
    expect(sfdc_page.get_by_role("option", name="Developer Edition")).to_be_visible()
    sfdc_page.locator("//span/p[text()='Developer Edition']").click()
    # sfdc_page.get_by_role("option", name="Developer Edition").click()
    return sfdc_page




# def test_SFDC_login(sfdc_page, sfdc_base_url):
#     sfdc_page.goto(sfdc_base_url + "/lightning/o/Lead/home", wait_until="domcontentloaded")
#     assert sfdc_page.wait_for_selector("text=Leads", timeout=60000)

# def test_SFDC_add_lead(sfdc_leads_home):
#     sfdc_leads_home.get_by_role("button", name="Global Actions").click()
#     sfdc_leads_home.get_by_text("New Lead").click()
#     sfdc_leads_home.get_by_role("dialog", name="New Lead").wait_for()

#     sfdc_leads_home.get_by_label("Salutation").click()
#     sfdc_leads_home.locator("a[title='Mr.']").click()

#     sfdc_leads_home.get_by_text("First Name").fill("TestFirstName")
#     sfdc_leads_home.get_by_text("Last Name").fill("TestLastName")
#     sfdc_leads_home.get_by_text("Company").last.fill("TestCompany")
#     sfdc_leads_home.get_by_role("button", name="Save").click()

# def test_SFDC_search_leads_home(sfdc_leads_home):
#     sfdc_leads_home.pause()
#     expect(sfdc_leads_home.get_by_role("button", name="Search", exact=True)).to_be_visible()
#     sfdc_leads_home.get_by_role("button", name="Search", exact=True).click()
#     # sfdc_leads_home.pause()
#     sfdc_leads_home.get_by_role("button", name="Search").click()
#     sfdc_leads_home.get_by_role("searchbox", name="Search...").fill("TestLead")
#     sfdc_leads_home.get_by_role("searchbox", name="Search...").press("Enter")
#     sfdc_leads_home.get_by_role("link", name="TestLead").first.click()
#     sfdc_leads_home.wait_for_url("**/lightning/r/Lead/**", timeout=60000)
#     sfdc_leads_home.on(inputFileHandler =lambda file: file.set_files("path/to/local/file.txt"))

def test_SFDC_add_full_lead(sfdc_leads_home, test_data_generator):

    leads_page = LeadsPage(sfdc_leads_home) 
    leads_page.click_global_actions()
    leads_page.click_new_lead()
    leads_page.fill_lead_form_full(test_data_generator["salutation"], test_data_generator["first_name"], test_data_generator["last_name"], test_data_generator["company"], test_data_generator["title"], test_data_generator["email"], test_data_generator["phone"])
    expect(leads_page.page.locator("lightning-formatted-name")).to_be_visible()
    expect(leads_page.page.get_by_role("link", name=test_data_generator["email"])).to_be_visible()
    expect(leads_page.page.get_by_role("link", name=str(test_data_generator["phone"]))).to_be_visible()
    expect(leads_page.page.locator("lightning-formatted-text").filter(has_text=test_data_generator["company"])).to_be_visible()
    expect(leads_page.page.locator("lightning-formatted-text").filter(has_text=test_data_generator["title"])).to_be_visible()