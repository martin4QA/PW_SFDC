import os
import time
import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

def get_salesforce_auth():
    """
    Authenticate to Salesforce using the JWT Bearer OAuth flow.

    This uses a connected app configured for JWT-based authentication
    (no browser login) and returns an access token + instance URL.
    All sensitive values are read from environment variables.
    """

    # Default to production login unless explicitly overridden (e.g. sandbox)
    login_url = os.getenv("SF_LOGIN_URL", "https://login.salesforce.com")

    # Load the private key used to sign the JWT assertion
    with open(os.environ["SF_PRIVATE_KEY_PATH"], "rb") as f:
        private_key = f.read()

    # JWT claims required by Salesforce for the JWT Bearer flowcha
    payload = {
        "iss": os.environ["SF_CLIENT_ID"],     # Connected App consumer key
        "sub": os.environ["SF_USERNAME"],      # Salesforce username to impersonate
        "aud": login_url,                      # Login endpoint (prod or sandbox)
        "exp": int(time.time()) + 180,         # Short-lived token (3 minutes)
    }

    # Sign the JWT using the private key registered with the connected app
    assertion = jwt.encode(payload, private_key, algorithm="RS256")

    # Exchange the signed JWT for an access token
    r = requests.post(
        f"{login_url}/services/oauth2/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=30,
    )
    r.raise_for_status()

    # Returns access_token, instance_url, issued_at, etc.
    return r.json()
