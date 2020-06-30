import os
import httpx

from src.utils import ServiceKey

service_urls = {
    ServiceKey.ORGANIZATIONS: os.getenv('ORGANIZATION_CATALOG_URL', 'http://localhost:8080/organizations'),
    ServiceKey.INFO_MODELS: os.getenv('INFORMATIONMODELS_HARVESTER_URL', 'http://localhost:8080/informationmodels'),
    ServiceKey.DATA_SERVICES: os.getenv('DATASERVICE_HARVESTER_URL', 'http://localhost:8080/apis'),
    ServiceKey.DATA_SETS: os.getenv('DATASET_HARVESTER_URL', 'http://localhost:8080/datasets'),
    ServiceKey.CONCEPTS: os.getenv('CONCEPT_HARVESTER_URL', 'http://localhost:8080/concepts'),
}

default_headers = {
    'accept': 'application/json'
}


# from organization catalog !important
def get_organizations() -> list:
    pass


async def get_organization(session: httpx.AsyncClient, organization_id: str) -> dict:
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/{organization_id}'

    response = await session.get(url=url, headers=default_headers, timeout=5)
    return response.json()


async def get_organization_same(organization_id: str) -> dict:
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/{organization_id}'
    async with httpx.AsyncClient() as session:
        response = await session.get(url=url, headers=default_headers, timeout=5)
        return response.json()


# from reference data (called seldom, not a crisis if they're slow) !important
async def get_themes_and_topics():
    pass


async def get_access_rights():
    pass


# informationmodels
async def get_informationmodels_statistic():
    # see informationmodels in unit_mock_data.py for expected result
    pass


# concepts
async def get_concepts_in_use():
    # see concepts_in_user in unit_mock_data.py for expected result
    pass


async def get_concepts_statistics():
    # see concepts_aggregation in unit_mock_data.py for expected result
    pass


# datasets !important
async def get_datasets_statistics():
    # see datasets_simple_aggs_response in unit_mock_data.py for expected result
    pass


async def get_datasets_access_rights():
    # see datasets_access_rights in unit_mock_data.py for expected result
    pass


async def get_datasets_themes_and_topics():
    # see datasets_themes_and_topics in unit_mock_data.py for expected result
    pass


async def get_dataset_time_series():
    # see timeseries in unit_mock_data.py for expected result
    pass
