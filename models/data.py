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
