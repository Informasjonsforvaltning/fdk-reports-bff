import asyncio
import logging
from typing import List

from src.elasticsearch.queries import DATASERVICE_AGGREGATION_FIELDS
from src.elasticsearch.utils import (
    add_org_paths_to_document,
    elasticsearch_ingest,
    get_all_organizations_with_publisher,
    get_unique_records,
)
from src.service_requests import fetch_dataservices, fetch_publishers_from_dataservice
from src.utils import FetchFromServiceException, ServiceKey


def insert_dataservices(success_status, failed_status):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        collection_tasks = asyncio.gather(
            fetch_dataservices(), fetch_publishers_from_dataservice()
        )
        dataservices, publishers = loop.run_until_complete(collection_tasks)
        prepared_docs = loop.run_until_complete(
            prepare_documents(documents=dataservices, publishers=publishers)
        )
        elasticsearch_ingest(
            index_key=ServiceKey.DATA_SERVICES, documents=prepared_docs
        )
        return success_status
    except FetchFromServiceException as err:
        logging.error(err.reason)
        return failed_status


async def prepare_documents(documents: dict, publishers) -> List[dict]:
    await get_all_organizations_with_publisher(publishers)
    dataservices_with_fdk_portal_paths = await asyncio.gather(
        *[add_org_paths_to_document(rdf_values=entry) for entry in documents]
    )

    unique_record_items = get_unique_records(dataservices_with_fdk_portal_paths)

    for document in documents:
        if "mediaType" in document:
            item = next(
                (
                    item
                    for item in unique_record_items
                    if item["record"]["value"] == document["record"]["value"]
                ),
                None,
            )

            document_value = document["mediaType"]["value"]

            if item.get("mediaType", {}).get("value"):
                if not isinstance(item["mediaType"]["value"], list):
                    item["mediaType"]["value"] = [item["mediaType"]["value"]]
                if document_value not in item["mediaType"]["value"]:
                    item["mediaType"]["value"].append(document_value)
            else:
                item["mediaType"]["value"] = document_value
                print(item)

    return [
        reduce_dataservice(dataservice=dataservice)
        for dataservice in unique_record_items
    ]


def reduce_dataservice(dataservice: dict):
    reduced_dict = dataservice.copy()
    for items in dataservice.items():
        key = items[0]
        if key not in DATASERVICE_AGGREGATION_FIELDS:
            reduced_dict.pop(key)
    return reduced_dict
