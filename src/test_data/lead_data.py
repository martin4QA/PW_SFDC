# test_data_factory.py
import random
from datetime import datetime, timezone


def generate_test_data(seed: int | None = None) -> dict:
    if seed is None:
        seed = int(datetime.now(timezone.utc).timestamp())

    rng = random.Random(seed)

    return {
        "seed": seed,
        "salutation": "Mr.",
        "first_name": f"TestFirstName_{seed}",
        "last_name": f"TestLastName_{seed}",
        "company": f"TestCompany_{seed}",
        "email": f"testemail{seed}@nowhere.com",
        "phone": rng.randint(1000000000, 9999999999),
        "title": f"TestTitle_{seed}",
    }

def lead_payload_from_test_data(data: dict) -> dict:
    """
    Convert internal test data format to Salesforce Lead REST payload.
    """
    return {
        "Salutation": data["salutation"],
        "FirstName": data["first_name"],
        "LastName": data["last_name"],
        "Company": data["company"],
        "Email": data["email"],
        "Phone": str(data["phone"]),  # SF expects string
        "Title": data["title"],
    }