import os
from typing import List
import urllib.parse

from httpcore import ConnectError
from httpx import AsyncClient, ConnectTimeout, HTTPError

from fdk_reports_bff.service.utils import (
    ContentKeys,
    FetchFromServiceException,
    ServiceKey,
)
from fdk_reports_bff.sparql import (
    dataset_timeseries_datapoint_query,
    get_concepts_query,
    get_dataservice_query,
    get_datasets_query,
    get_info_models_query,
)

service_urls = {
    ServiceKey.REFERENCE_DATA: os.getenv("FDK_REFERENCE_DATA_URL")
    or "http://localhost:8000",
    ServiceKey.SPARQL_BASE: os.getenv("SPARQL_BASE") or "http://localhost:8000",
    ServiceKey.DATASET_QUERY_CACHE: os.getenv("DATASET_QUERY_CACHE_URL")
    or "http://localhost:8000",
}

default_headers = {"accept": "application/json"}


# from reference data (called seldom, not a crisis if they're slow) !important
async def fetch_themes_and_topics_from_reference_data() -> List[dict]:
    url = f"{service_urls.get(ServiceKey.REFERENCE_DATA)}/reference-data/los/themes-and-words"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json().get("losNodes")
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data themes and topics", url=url
            )


async def fetch_access_rights_from_reference_data() -> list:
    url = (
        f"{service_urls.get(ServiceKey.REFERENCE_DATA)}/reference-data/eu/access-rights"
    )
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json().get("accessRights")
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data get access rights", url=url
            )


async def fetch_media_types_from_reference_data() -> list:
    url = (
        f"{service_urls.get(ServiceKey.REFERENCE_DATA)}/reference-data/iana/media-types"
    )
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json().get("mediaTypes")
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data get media-types", url=url
            )


async def fetch_file_types_from_reference_data() -> list:
    url = f"{service_urls.get(ServiceKey.REFERENCE_DATA)}/reference-data/eu/file-types"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, timeout=5)
            response.raise_for_status()
            return response.json().get("fileTypes")
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="reference-data get file-types", url=url
            )


async def fetch_datasets() -> List[dict]:
    datasets_query = urllib.parse.quote_plus(get_datasets_query())
    url = f"{service_urls.get(ServiceKey.SPARQL_BASE)}?query={datasets_query}"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            sparql_bindings = res_json[ContentKeys.SPARQL_RESULTS][
                ContentKeys.SPARQL_BINDINGS
            ]
            return sparql_bindings
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="fetching datasets catalog", url=url
            )


# informationmodels
async def get_informationmodels_statistic() -> List[dict]:
    models_query = urllib.parse.quote_plus(get_info_models_query())
    url = f"{service_urls.get(ServiceKey.SPARQL_BASE)}?query={models_query}"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            sparql_bindings = res_json[ContentKeys.SPARQL_RESULTS][
                ContentKeys.SPARQL_BINDINGS
            ]
            return sparql_bindings
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="fetching information models catalog", url=url
            )


# concepts
async def fetch_all_concepts() -> List[dict]:
    concepts_query = urllib.parse.quote_plus(get_concepts_query())
    url = f"{service_urls.get(ServiceKey.SPARQL_BASE)}?query={concepts_query}"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            sparql_bindings = res_json[ContentKeys.SPARQL_RESULTS][
                ContentKeys.SPARQL_BINDINGS
            ]
            return sparql_bindings
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="fetching dataservices catalog", url=url
            )


# dataservices
async def fetch_dataservices() -> List[dict]:
    dataservice_query = urllib.parse.quote_plus(get_dataservice_query())
    url = f"{service_urls.get(ServiceKey.SPARQL_BASE)}?query={dataservice_query}"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            sparql_bindings = res_json[ContentKeys.SPARQL_RESULTS][
                ContentKeys.SPARQL_BINDINGS
            ]
            return sparql_bindings
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="fetching dataservices catalog", url=url
            )


async def fetch_diff_store_metadata() -> dict:
    url = f"{service_urls.get(ServiceKey.DATASET_QUERY_CACHE)}/api/metadata"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="diff store metadata", url=url
            )


async def fetch_dataset_time_series_datapoint(timestamp: str) -> dict:
    sparql_query = urllib.parse.quote_plus(dataset_timeseries_datapoint_query())
    url = f"{service_urls.get(ServiceKey.DATASET_QUERY_CACHE)}/api/sparql/{timestamp}?query={sparql_query}"
    async with AsyncClient() as session:
        try:
            response = await session.get(url=url, headers=default_headers, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            return {
                "timestamp": timestamp,
                "results": res_json[ContentKeys.SPARQL_RESULTS][
                    ContentKeys.SPARQL_BINDINGS
                ],
            }
        except (ConnectError, HTTPError, ConnectTimeout):
            raise FetchFromServiceException(
                execution_point="dataset time series query", url=url
            )
