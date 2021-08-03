import asyncio
import time
from test.unit_mock_data import (
    mock_access_rights_catalog_response,
    mock_los_path_reference_response,
    parsed_org_catalog_mock,
    single_parsed_org_mock,
)

import pytest
import requests
from urllib3.exceptions import MaxRetryError, NewConnectionError


@pytest.fixture(scope="session")
def wait_for_ready():
    timeout = time.time() + 60
    attempts = 0
    while True:
        try:
            response = requests.get("http://localhost:8000/ready")
            if response.status_code == 200:
                time.sleep(2)
                break
            if time.time() > timeout:
                pytest.fail(
                    "Test function setup: timed out while waiting for reports-bff ready response, last response "
                    "was {0}".format(response.status_code)
                )
            time.sleep(1)
        except (
            requests.exceptions.ConnectionError,
            ConnectionRefusedError,
            MaxRetryError,
            NewConnectionError,
        ):
            if attempts > 3:
                pytest.fail(
                    "Test function setup: could not contact fdk-organization-bff"
                )
            else:
                time.sleep(10)
                attempts += 1
                continue


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture
def get_organization_from_service_mock(mocker):
    mocker.patch(
        "fdk_reports_bff.referenced_data_store.get_organization_from_organization_catalog",
        side_effect=single_parsed_org_mock,
    )


@pytest.fixture
def get_organizations_mock(mocker):
    mocker.patch(
        "fdk_reports_bff.referenced_data_store.get_organizations",
        side_effect=parsed_org_catalog_mock,
    )


@pytest.fixture
def get_access_rights_mock(mocker):
    mocker.patch(
        "fdk_reports_bff.referenced_data_store.fetch_access_rights_from_reference_data",
        side_effect=mock_access_rights_catalog_response,
    )


@pytest.fixture
def get_los_paths_mock(mocker):
    mocker.patch(
        "fdk_reports_bff.referenced_data_store.fetch_themes_and_topics_from_reference_data",
        side_effect=mock_los_path_reference_response,
    )
