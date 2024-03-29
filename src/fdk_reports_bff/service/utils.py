from datetime import datetime
from typing import Any, List, Optional

from dateutil import parser


class ContentKeys:
    SPARQL_RESULTS = "results"
    SPARQL_BINDINGS = "bindings"
    SAME_AS = "sameAs"
    PUBLISHER = "publisher"
    SRC_ORGANIZATION = "publisher"
    SERVICE = "service"
    FORMAT = "format"
    WITH_SUBJECT = "withSubject"
    OPEN_DATA = "opendata"
    TOTAL = "total"
    NEW_LAST_WEEK = "new_last_week"
    NATIONAL_COMPONENT = "nationalComponent"
    ORGANIZATION = "organization"
    COUNT = "count"
    KEY = "key"
    VALUE = "value"
    ACCESS_RIGHTS_CODE = "code"
    TIME_SERIES_MONTH = "month"
    TIME_SERIES_YEAR = "year"
    TIME_SERIES_Y_AXIS = "yAxis"
    TIME_SERIES_X_AXIS = "xAxis"
    THEME = "theme"
    ORG_NAME = "name"
    ORGANIZATION_URI = "organization"
    LOS_PATH = "losPath"
    CATALOGS = "catalogs"
    ORGANIZATION_COUNT = "organizationCount"
    EMBEDDED = "_embedded"
    CONCEPTS = "concepts"
    PAGE_OBJECT = "page"
    TOTAL_PAGES = "totalPages"
    MOST_IN_USE = "most_in_use"
    INFO_MODELS = "informationmodels"
    TITLE = "title"
    FIRST_HARVESTED = "firstHarvested"
    HITS = "hits"


class OrgCatalogKeys:
    NAME = "name"
    URI = "norwegianRegistry"
    ORG_PATH = "orgPath"


class ServiceKey:
    ORGANIZATIONS = "organizations"
    INFO_MODELS = "informationmodels"
    DATA_SERVICES = "dataservices"
    DATA_SETS = "datasets"
    DATASET_TIME_SERIES = "dataset_time_series"
    DATASERVICE_TIME_SERIES = "data_service_time_series"
    CONCEPT_TIME_SERIES = "concept_time_series"
    CONCEPTS = "concepts"
    REFERENCE_DATA = "reference_data"
    FDK_BASE = "fdk_base"
    SPARQL_BASE = "sparql_base"
    DATASET_QUERY_CACHE = "dataset_query_cache"
    DATASERVICE_QUERY_CACHE = "data_service_query_cache"
    CONCEPT_QUERY_CACHE = "concept_query_cache"
    API_KEY = "api_key"

    @staticmethod
    def get_key(string_key: str) -> str:
        if string_key == ServiceKey.ORGANIZATIONS:
            return ServiceKey.ORGANIZATIONS
        if string_key == ServiceKey.INFO_MODELS:
            return ServiceKey.INFO_MODELS
        if string_key == ServiceKey.DATA_SERVICES:
            return ServiceKey.DATA_SERVICES
        if string_key == ServiceKey.DATA_SETS:
            return ServiceKey.DATA_SETS
        if string_key == ServiceKey.DATASET_TIME_SERIES:
            return ServiceKey.DATASET_TIME_SERIES
        if string_key == ServiceKey.DATASERVICE_TIME_SERIES:
            return ServiceKey.DATASERVICE_TIME_SERIES
        if string_key == ServiceKey.CONCEPT_TIME_SERIES:
            return ServiceKey.CONCEPT_TIME_SERIES
        if string_key == ServiceKey.CONCEPTS:
            return ServiceKey.CONCEPTS
        if string_key == ServiceKey.REFERENCE_DATA:
            return ServiceKey.REFERENCE_DATA
        if string_key == ServiceKey.FDK_BASE:
            return ServiceKey.FDK_BASE
        if string_key == ServiceKey.SPARQL_BASE:
            return ServiceKey.SPARQL_BASE
        if string_key == ServiceKey.DATASET_QUERY_CACHE:
            return ServiceKey.DATASET_QUERY_CACHE
        if string_key == ServiceKey.DATASERVICE_QUERY_CACHE:
            return ServiceKey.DATASERVICE_QUERY_CACHE
        if string_key == ServiceKey.CONCEPT_QUERY_CACHE:
            return ServiceKey.CONCEPT_QUERY_CACHE
        else:
            raise NotAServiceKeyException(string_key)


NATIONAL_REGISTRY_PATTERN = "data.brreg.no/enhetsregisteret"
ORGANIZATION_CATALOG_PATTERN = "fellesdatakatalog.digdir.no/organizations"


class ParsedDataPoint:
    def __init__(
        self: Any,
        es_bucket: Any = None,
        month: Any = None,
        year: Any = None,
        last_month_count: int = 0,
    ) -> None:
        if es_bucket is not None:
            self.y_axis = es_bucket["doc_count"] + last_month_count
            self.x_axis = es_bucket["key_as_string"]
            self.month, self.year = self.parse_date()
        else:
            self.y_axis = last_month_count
            next_date = None
            if month and month < 10:
                next_date = f"01.0{month}.{year}"
            else:
                next_date = f"01.{month}.{year}"

            self.x_axis = datetime.strptime(next_date, "%d.%m.%Y").isoformat() + ".000Z"
            self.year = year
            self.month = month

    def response_dict(self: Any) -> dict:
        return {
            ContentKeys.TIME_SERIES_Y_AXIS: self.y_axis,
            ContentKeys.TIME_SERIES_X_AXIS: self.x_axis,
        }

    def parse_date(self: Any) -> Any:
        date = parser.parse(self.x_axis)
        return date.month, date.year

    def get_next_month(self: Any) -> "ParsedDataPoint":
        next_month = self.month + 1
        next_year = self.year
        if next_month == 13:
            next_month = 1
            next_year += 1
        return ParsedDataPoint(
            month=next_month, year=next_year, last_month_count=self.y_axis
        )

    def __eq__(self: Any, other: Any) -> bool:
        return (
            other is not None and self.month == other.month and self.year == other.year
        )

    @staticmethod
    def from_date_time(
        date: datetime, last_data_point: "ParsedDataPoint"
    ) -> "ParsedDataPoint":
        last_month_count = 0
        if last_data_point is not None:
            last_month_count = last_data_point.y_axis

        return ParsedDataPoint(
            month=date.month, year=date.year, last_month_count=last_month_count
        )


class ThemeProfile:
    TRANSPORT = "transport"
    TRANSPORT_THEMES = [
        "trafikk-og-transport/mobilitetstilbud",
        "trafikk-og-transport/trafikkinformasjon",
        "trafikk-og-transport/veg-og-vegregulering",
        "trafikk-og-transport/yrkestransport",
    ]


class QueryParameter:
    ORGANIZATION_ID = "organizationId"
    THEME_PROFILE = "themeprofile"
    ORG_PATH = "orgPath"
    THEME = "theme"


class NotAServiceKeyException(Exception):
    def __init__(self: Any, string_key: str) -> None:
        self.status = 400
        self.reason = f"service not recognized: {string_key}"


class FetchFromServiceException(Exception):
    def __init__(self: Any, execution_point: str, url: Optional[str] = None) -> None:
        self.status = 500
        self.reason = (
            f"Connection error when attempting to fetch {execution_point} from {url}"
        )


class NotInNationalRegistryException(Exception):
    def __init__(self: Any, uri: str) -> None:
        self.reason = f"{uri} was not found in the nationalRegistry"


class BadOrgPathException(Exception):
    def __init__(self: Any, org_path: str) -> None:
        self.reason = f"could not find any organization with {org_path}"


class NoOrganizationEntriesException(Exception):
    def __init__(self: Any) -> None:
        self.reason = "organization store is empty"


class StartSchedulerError(Exception):
    def __init__(self: Any, hosts: List[dict]) -> None:
        self.message = f"Failed to contact ElasticSearch when attempting to start scheduler.\n hosts: {hosts} "
