import json
import logging
import os
from typing import List

from elasticsearch import helpers
from elasticsearch.helpers import BulkIndexError

from src.elasticsearch import es_client
from src.elasticsearch.queries import EsMappings, AggregationQuery
from src.organization_parser import OrganizationStore, OrganizationReferencesObject, \
    OrganizationStoreNotInitiatedException
from src.rdf_namespaces import JSON_LD, ContentKeys
from src.referenced_data_store import get_org_path, get_organizations, get_los_path
from src.utils import ServiceKey


def add_key_as_node_uri(key, value):
    value[EsMappings.NODE_URI] = key
    return value


async def add_foaf_agent_to_organization_store(foaf_agent_dict: dict):
    store = OrganizationStore.get_instance()
    uri = list(foaf_agent_dict.keys())[0]
    values = foaf_agent_dict[uri]
    same_as = None
    keys = values.keys()
    if JSON_LD.OWL.sameAs in keys:
        same_as = values[JSON_LD.OWL.sameAs][0][ContentKeys.VALUE]
    name = values[JSON_LD.FOAF.name][0][ContentKeys.VALUE]
    if same_as:
        org_path = await get_org_path(uri=same_as, name=name)
    else:
        org_path = await get_org_path(uri=uri, name=name)
    store.add_organization(organization=OrganizationReferencesObject(
        org_uri=uri,
        same_as=same_as,
        org_path=org_path,
        name=name
    ))
    return True


async def add_org_and_los_paths_to_document(json_ld_values: dict, los_themes: List[dict]) -> dict:
    uri = json_ld_values[JSON_LD.DCT.publisher][0][ContentKeys.VALUE]
    store = OrganizationStore.get_instance()
    try:
        org_path = store.get_orgpath(uri)
        json_ld_values[EsMappings.ORG_PATH] = org_path
        return add_los_path_to_document(json_ld_values, los_themes)
    except OrganizationStoreNotInitiatedException:
        await get_organizations()
        return await add_org_and_los_paths_to_document(json_ld_values, los_themes)


def add_los_path_to_document(json_ld_values: dict, los_themes: List[dict]) -> dict:
    if JSON_LD.DCAT.theme in json_ld_values.keys():
        los_uris = [theme.get(ContentKeys.VALUE) for theme in json_ld_values.get(JSON_LD.DCAT.theme)]
        los_paths = get_los_path(uri_list=los_uris, los_themes=los_themes)
        if len(los_paths) > 0:
            json_ld_values[EsMappings.LOS] = los_paths
    return json_ld_values


def elasticsearch_ingest(index_key: ServiceKey, documents: List[dict]):
    recreate_index(index_key=index_key)
    try:
        result = helpers.bulk(client=es_client, index=index_key, actions=yield_documents(documents))
        return result
    except BulkIndexError as err:
        logging.error(f"ingest {ServiceKey.DATA_SETS}", err.errors)


def elasticsearch_get_report_aggregations(report_type: ServiceKey, orgpath=None, theme=None,
                                          theme_profile=None):
    query = AggregationQuery(report_type=report_type,
                             orgpath=orgpath,
                             theme=theme,
                             theme_profile=theme_profile).build()
    aggregations = es_client.search(index=report_type, body=query)
    return aggregations


def yield_documents(documents):
    for doc in documents:
        yield doc


def get_values_from_nested_dict(entry: dict) -> dict:
    root_key = list(entry.keys())[0]
    return entry[root_key]


# noinspection PyBroadException
def recreate_index(index_key):
    """delete and recreate an index with settings and mapping from file"""
    logging.info("reindexing {0}".format(index_key))
    with open(os.getcwd() + "/mapping/{0}_properties.json".format(index_key)) as mapping:
        try:
            es_client.indices.delete(index=index_key, ignore=[400, 404])
            es_client.indices.create(index=index_key, body=json.load(mapping))
        except BaseException as err:
            logging.error("error when attempting to update {0} ".format(index_key))
        return None
