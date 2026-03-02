from sfdc.lead_api import create_lead
from test_data.lead_data import generate_test_data, lead_payload_from_test_data

def test_create_lead_via_api(sfdc_api_client, sfdc_api_version):
    test_data = generate_test_data()

    payload = lead_payload_from_test_data(test_data)

    result = create_lead(sfdc_api_client, sfdc_api_version, payload)

    assert result.success is True
    assert result.id, f"Expected lead id, got: {result}"

    # verify created record via API
    resp = sfdc_api_client.get(
        f"/services/data/v{sfdc_api_version}/sobjects/Lead/{result.id}"
    )

    assert resp.status_code == 200
    assert resp.json["LastName"] == test_data["last_name"]
    assert resp.json["Company"] == test_data["company"]

