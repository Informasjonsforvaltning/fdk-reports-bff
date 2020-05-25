import time

import pytest
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError


@pytest.fixture(scope="session")
def wait_for_ready():
    timeout = time.time() + 20
    try:
        while True:
            response = requests.get("http://localhost:8000/ready")
            if response.status_code == 200:
                break
            if time.time() > timeout:
                pytest.fail(
                    'Test function setup: timed out while waiting for report-bff, last response '
                    'was {0}'.format(response.status_code))
            time.sleep(1)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, MaxRetryError, NewConnectionError):
        pytest.fail('Test function setup: could not contact fdk-organization-bff')
    yield
