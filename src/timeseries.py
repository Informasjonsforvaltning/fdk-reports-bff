from src.elasticsearch.queries import EsMappings
from src.elasticsearch.utils import elasticsearch_get_time_series
from src.responses import TimeSeriesResponse
from src.utils import ServiceKey, QueryParameter, ParsedDataPoint


def get_time_series(content_type: ServiceKey, args) -> TimeSeriesResponse:
    orgpath = args.get(QueryParameter.ORG_PATH)
    theme = args.get(QueryParameter.THEME)
    theme_profile = args.get(QueryParameter.THEME_PROFILE)
    organization_id = args.get(QueryParameter.ORGANIZATION_ID)
    return time_series_functions[content_type](org_path=orgpath,
                                               theme=theme,
                                               theme_profile=theme_profile,
                                               organization_id = organization_id)


def get_dataset_time_series(org_path=None, theme=None, theme_profile=None, organization_id=None) -> TimeSeriesResponse:
    es_time_series = elasticsearch_get_time_series(report_type=ServiceKey.DATA_SETS,
                                                   org_path=org_path,
                                                   theme=theme,
                                                   theme_profile=theme_profile,
                                                   organization_id=organization_id)
    return TimeSeriesResponse(es_time_series)


time_series_functions = {
    ServiceKey.DATA_SETS: get_dataset_time_series
}
