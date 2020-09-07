import asyncio

from src.elasticsearch.queries import EsMappings
from src.elasticsearch.utils import elasticsearch_get_report_aggregations
from src.rdf_namespaces import ContentKeys
from src.referenced_data_store import get_access_rights_code
from src.responses import DataSetResponse
from src.utils import ServiceKey


def create_dataset_report(orgpath, theme, theme_profile, organization_id):
    es_report = elasticsearch_get_report_aggregations(report_type=ServiceKey.DATA_SETS,
                                                      orgpath=orgpath,
                                                      theme=theme,
                                                      theme_profile=theme_profile,
                                                      organization_id=organization_id)

    rdf_access_rights_bucket = get_es_aggregation(es_report, ContentKeys.ACCESS_RIGHTS_CODE)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    access_right_code_tasks = asyncio.gather(*[map_access_rights_to_code(access_right) for
                                               access_right in rdf_access_rights_bucket])
    mapped_access_rights = loop.run_until_complete(access_right_code_tasks)

    return DataSetResponse(
        total=es_report["hits"][ContentKeys.TOTAL][ContentKeys.VALUE],
        new_last_week=get_es_aggregation(es_report, ContentKeys.NEW_LAST_WEEK),
        dist_formats=get_es_aggregation(es_report, ContentKeys.FORMAT),
        opendata=get_es_aggregation(es_report, ContentKeys.OPEN_DATA),
        national_component=get_es_aggregation(es_report, ContentKeys.NATIONAL_COMPONENT),
        org_paths=get_es_aggregation(es_report, EsMappings.ORG_PATH),
        themes=get_es_aggregation(es_report, ContentKeys.LOS_PATH),
        with_subject=get_es_aggregation(es_report, ContentKeys.WITH_SUBJECT),
        access_rights=mapped_access_rights,
        catalogs=get_es_aggregation(es_report, ContentKeys.CATALOGS)
    )


def get_es_aggregation(es_hits: dict, content_key):
    single_aggregations = [ContentKeys.NEW_LAST_WEEK,
                           ContentKeys.NATIONAL_COMPONENT,
                           ContentKeys.OPEN_DATA,
                           ContentKeys.WITH_SUBJECT,
                           ]
    if content_key in single_aggregations:
        return es_hits.get("aggregations").get(content_key)["doc_count"]
    else:
        buckets = es_hits.get("aggregations").get(content_key)["buckets"]
        return rename_doc_count_to_count(buckets)


async def map_access_rights_to_code(access_right: dict):
    rdf_key = access_right["key"]
    if rdf_key == EsMappings.MISSING:
        code_key = EsMappings.MISSING
    else:
        code_key = await get_access_rights_code(rdf_key)
    return {
        "key": code_key,
        "count": access_right["count"]
    }


def rename_doc_count_to_count(aggregation_buckets):
    return [{"key": bucket["key"], "count": bucket["doc_count"]} for bucket in aggregation_buckets]
