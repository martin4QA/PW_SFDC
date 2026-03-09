from sfdc.lead_api import create_lead, delete_lead


def test_delete_lead_via_api(sfdc_api_client, sfdc_api_version):
    # first create a lead to delete
    payload = {
        "LastName": "API Lead",
        "Company": "Martin4QA Inc",
        "Email": "api.lead@example.com",
        "Phone": "+49123456789",
        "Title": "QA Test Lead",
    }

    result = create_lead(sfdc_api_client, sfdc_api_version, payload)

    assert result.success is True
    assert result.id, f"Expected lead id, got: {result}"

    # now delete the lead we just created
    delete_lead(sfdc_api_client, sfdc_api_version, result.id)
