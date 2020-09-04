import os
from typing import List
from httpcore import ConnectError
from httpx import AsyncClient, ConnectTimeout, HTTPError

from src.sparql import get_dataset_publisher_query
from src.utils import ServiceKey, FetchFromServiceException, NotInNationalRegistryException, ThemeProfile

service_urls = {
    ServiceKey.ORGANIZATIONS: os.getenv('ORGANIZATION_CATALOG_URL') or "http://localhost:8080",
    ServiceKey.INFO_MODELS: os.getenv('INFORMATIONMODELS_HARVESTER_URL') or "http://localhost:8080/informationmodels",
    ServiceKey.DATA_SERVICES: os.getenv('DATASERVICE_HARVESTER_URL') or "http://localhost:8080",
    ServiceKey.DATA_SETS: os.getenv('DATASET_HARVESTER_URL') or "http://localhost:8080",
    ServiceKey.CONCEPTS: os.getenv('CONCEPT_HARVESTER_URL') or "http://localhost:8080/concepts",
    ServiceKey.REFERENCE_DATA: os.getenv('REFERENCE_DATA_URL') or "http://localhost:8080/reference-data"
}

default_headers = {
    'accept': 'application/json'
}


async def fetch_organizations_from_organizations_catalog() -> List[dict]:
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/organizations'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            raise FetchFromServiceException(
                execution_point="organizations",
                url=url
            )


async def fetch_organization_from_catalog(national_reg_id: str, name: str) -> dict:
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/organizations/{national_reg_id}'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=5)
            response.raise_for_status()

            return response.json()
        except (ConnectError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="get organization by id",
                url=url
            )
        except (ConnectTimeout, ConnectError):
            raise FetchFromServiceException(
                execution_point="connection error to organization catalog",
                url=url
            )
        except HTTPError as err:
            if err.response.status_code == 404:
                return await attempt_fetch_organization_by_name_from_catalog(name)
            else:
                raise FetchFromServiceException(
                    execution_point=f"{err.response.status_code}: get organization",
                    url=url
                )


async def attempt_fetch_organization_by_name_from_catalog(name: str) -> dict:
    if name is None:
        raise NotInNationalRegistryException("No name")
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/organizations?name={name.upper()}'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=5)
            response.raise_for_status()
            return response.json()[0]
        except (ConnectError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="get organization by name",
                url=url
            )
        except HTTPError as err:
            if err.response.status_code == 404:
                raise NotInNationalRegistryException(name)
            else:
                raise FetchFromServiceException(
                    execution_point=f"{err.response.status_code}: get organization",
                    url=url
                )
        except IndexError:
            raise NotInNationalRegistryException(name)


async def fetch_generated_org_path_from_organization_catalog(name: str):
    if name is None:
        return None
    url: str = f'{service_urls.get(ServiceKey.ORGANIZATIONS)}/organizations/orgpath/{name.upper()}'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.text
        except (ConnectError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="get organization by name",
                url=url
            )
        except HTTPError as err:
            raise FetchFromServiceException(
                execution_point=f"{err.response.status_code}: get organization",
                url=url
            )


# from reference data (called seldom, not a crisis if they're slow) !important
async def fetch_themes_and_topics_from_reference_data() -> List[dict]:
    url = f'{service_urls.get(ServiceKey.REFERENCE_DATA)}/los'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            raise FetchFromServiceException(
                execution_point="reference-data themes and topics",
                url=url
            )


async def fetch_open_licences_from_reference_data() -> List[dict]:
    url = f'{service_urls.get(ServiceKey.REFERENCE_DATA)}/codes/openlicenses'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            raise FetchFromServiceException(
                execution_point="reference-data themes and topics",
                url=url
            )


async def fetch_access_rights_from_reference_data():
    url = f'{service_urls.get(ServiceKey.REFERENCE_DATA)}/codes/rightsstatement'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data get access rights",
                url=url
            )


async def fetch_media_types_from_reference_data():
    url = f'{service_urls.get(ServiceKey.REFERENCE_DATA)}/codes/mediatypes'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data get mediatypes rights",
                url=url
            )


async def fetch_catalog_from_dataset_harvester() -> dict:
    url = f'{service_urls.get(ServiceKey.DATA_SETS)}/catalogs'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers={"Accept": "application/rdf+json"}, timeout=60)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            raise FetchFromServiceException(
                execution_point="fetching dataset catalog",
                url=url
            )


async def fetch_publishers_from_dataset_harvester() -> dict:
    publisher_query = get_dataset_publisher_query()
    url = f'{service_urls.get(ServiceKey.DATA_SETS)}/sparql/select?query={publisher_query}'
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout) as err:
            raise FetchFromServiceException(
                execution_point="fetching dataset catalog",
                url=url
            )


# TODO
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
