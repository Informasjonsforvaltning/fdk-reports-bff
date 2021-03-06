from src.elasticsearch.queries import EsMappings
from src.elasticsearch.utils import elasticsearch_get_time_series
from src.rdf_namespaces import JsonRDF
from src.responses import TimeSeriesResponse
from src.utils import QueryParameter, ServiceKey


def get_time_series(content_type: ServiceKey, args) -> TimeSeriesResponse:
    orgpath = args.get(QueryParameter.ORG_PATH)
    theme = args.get(QueryParameter.THEME)
    theme_profile = args.get(QueryParameter.THEME_PROFILE)
    organization_id = args.get(QueryParameter.ORGANIZATION_ID)
    if content_type == ServiceKey.DATA_SETS:
        return get_time_series_response(
            report_type=content_type,
            org_path=orgpath,
            theme=theme,
            theme_profile=theme_profile,
            organization_id=organization_id,
            series_field=f"{EsMappings.RECORD}.{JsonRDF.dct.issued}.value",
        )
    elif content_type == ServiceKey.DATA_SERVICES:
        return get_time_series_response(
            report_type=content_type,
            org_path=orgpath,
            organization_id=organization_id,
            series_field=f"{EsMappings.ISSUED}.value",
        )
    elif content_type in [ServiceKey.CONCEPTS, ServiceKey.INFO_MODELS]:
        return get_time_series_response(
            report_type=content_type,
            org_path=orgpath,
            organization_id=organization_id,
            series_field=EsMappings.FIRST_HARVESTED,
        )
    else:
        raise KeyError()


def get_time_series_response(
    report_type=None,
    org_path=None,
    theme=None,
    theme_profile=None,
    organization_id=None,
    series_field=None,
) -> TimeSeriesResponse:
    es_time_series = elasticsearch_get_time_series(
        report_type=report_type,
        org_path=org_path,
        theme=theme,
        theme_profile=theme_profile,
        organization_id=organization_id,
        series_field=series_field,
    )
    return TimeSeriesResponse(es_time_series)
