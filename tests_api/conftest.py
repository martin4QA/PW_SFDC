import os

import pytest
import requests

from api.http_client import ApiClient
from auth.salesforce import get_salesforce_auth


@pytest.fixture(scope="session")
def sfdc_auth():
    auth = get_salesforce_auth()
    assert "instance_url" in auth and auth["instance_url"]
    assert "access_token" in auth and auth["access_token"]
    return auth


@pytest.fixture(scope="session")
def sfdc_api_version():
    # default passt meistens, aber per env overridebar
    return os.getenv("SF_API_VERSION", "60.0")


@pytest.fixture(scope="session")
def http_session():
    s = requests.Session()
    yield s
    s.close()


@pytest.fixture()
def sfdc_api_client(sfdc_auth, http_session):
    return ApiClient(
        base_url=sfdc_auth["instance_url"],
        token=sfdc_auth["access_token"],
        session=http_session,
    )
