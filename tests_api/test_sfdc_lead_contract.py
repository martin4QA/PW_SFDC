from urllib.parse import quote

from api.contracts.jsonschema_helpers import assert_matches_schema
from api.contracts.schemas import LEAD_SCHEMA
from sfdc.soql import LEAD_EXTENDED_FIELDS, latest_lead


def test_lead_query_contract(sfdc_api_client, sfdc_api_version):

    # build the test query from the library
    soql = latest_lead(LEAD_EXTENDED_FIELDS)

    # api call to run soql query against salesforce
    resp = sfdc_api_client.get(f"/services/data/v{sfdc_api_version}/query?q={quote(soql)}")

    # First check the http status code shows success
    assert resp.status_code == 200

    data = resp.json or {}
    records = data.get("records", [])

    # next check we got records returned
    assert records, "No Lead records returned"

    # finally make sure the record matches the schema
    lead = records[0]
    assert_matches_schema(lead, LEAD_SCHEMA)

    print(resp)
    print(records)
