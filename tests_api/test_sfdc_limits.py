from api.contracts.jsonschema_helpers import assert_matches_schema
from api.contracts.schemas import LIMITS_SCHEMA


def test_limits_contract(sfdc_api_client, sfdc_api_version):
    resp = sfdc_api_client.get(f"/services/data/v{sfdc_api_version}/limits")
    assert resp.status_code == 200
    assert resp.json is not None
    assert_matches_schema(resp.json, LIMITS_SCHEMA)

    print(resp)
