import abc
import json

from src.rdf_namespaces import JSON_RDF
from src.utils import ServiceKey, ThemeProfile, ContentKeys


class EsMappings:
    PART_OF_CATALOG = "partOfCatalog"
    BUCKETS = "buckets"
    AGGREGATIONS = "aggregations"
    DOC_COUNT = "doc_count"
    ORGANIZATION_ID = "orgId"
    TIME_SERIES = "timeseries"
    FORMAT = "formatCodes"
    LOS = "los"
    RECORD = "dcatRecord"
    VALUE_KEYWORD = ".value.keyword"
    NODE_URI = "nodeUri"
    ORG_PATH = "orgPath"
    LOS_PATH = "losPaths"
    MISSING = "MISSING"
    OPEN_LICENSE = "OpenLicense"
    PUBLISHER = "publisher"
    URI = "uri"


DATASET_AGGREGATION_FIELDS = [EsMappings.ORG_PATH, EsMappings.ORGANIZATION_ID, EsMappings.LOS, JSON_RDF.dct.accessRights,
                              JSON_RDF.dct.provenance, JSON_RDF.dct.subject, JSON_RDF.dcat.distribution,
                              JSON_RDF.dcat.theme, EsMappings.NODE_URI, EsMappings.RECORD, EsMappings.OPEN_LICENSE,
                              EsMappings.FORMAT, EsMappings.PART_OF_CATALOG]

CATALOG_RECORD_AGGREGATION_FIELDS = [
    JSON_RDF.dct.issued, JSON_RDF.dct.isPartOf, JSON_RDF.foaf.primaryTopic
]


class Query(metaclass=abc.ABCMeta):
    def __init__(self):
        self.aggregations = None
        self.query = None

    def add_filters(self, orgpath, themes, theme_profile, organization_id):
        if orgpath or themes or theme_profile or organization_id:
            self.query = {
                "bool": {
                    "filter": []
                }
            }
            if themes:
                self.query["bool"]["filter"].extend(get_los_path_filter(themes_str=themes))
            if orgpath:
                self.query["bool"]["filter"].append(get_org_path_filter(orgpath))
            if theme_profile:
                self.query["bool"]["filter"].append(get_theme_profile_filter(ThemeProfile.TRANSPORT))
            if organization_id:
                self.query["bool"]["filter"].append(get_term_query(EsMappings.ORGANIZATION_ID, organization_id))

    def build(self):
        body = {
            "size": 0,
            "aggregations": self.aggregations
        }
        if self.query:
            body["query"] = self.query
        return body


class AggregationQuery(Query):
    def __init__(self, report_type: ServiceKey, orgpath=None, theme=None, theme_profile=None,
                 organization_id=None):
        super().__init__()
        self.aggregations = {
            EsMappings.ORG_PATH: {
                "terms": {
                    "field": EsMappings.ORG_PATH,
                    "missing": "MISSING",
                    "size": 100000
                }
            },
            ContentKeys.NEW_LAST_WEEK: get_last_x_days_filter(key=f"{EsMappings.RECORD}.{JSON_RDF.dct.issued}.value",
                                                              days=7),
            ContentKeys.CATALOGS: {
                "terms": {
                    "field": f"{EsMappings.PART_OF_CATALOG}.keyword",
                    "missing": "MISSING",
                    "size": 100000
                }
            },
            ContentKeys.ORGANIZATION_COUNT: {
                "cardinality": {
                    "field": f"{EsMappings.ORGANIZATION_ID}.keyword"
                }
            }
        }
        if report_type == ServiceKey.DATA_SETS:
            self.__add_datasets_aggregation()
        self.query = None
        self.add_filters(orgpath, theme, theme_profile, organization_id)

    def __add_datasets_aggregation(self):
        self.aggregations[ContentKeys.ACCESS_RIGHTS_CODE] = AggregationQuery.json_rdf_terms_aggregation(
            JSON_RDF.dct.accessRights)
        self.aggregations[ContentKeys.NATIONAL_COMPONENT] = {
            "filter": {
                "term": {
                    AggregationQuery.es_keyword_key(
                        JSON_RDF.dct.provenance): "http://data.brreg.no/datakatalog/provinens/nasjonal"
                }
            }
        }
        self.aggregations[ContentKeys.WITH_SUBJECT] = {
            "filter": {
                "exists": {
                    "field": JSON_RDF.dct.subject
                }
            }
        }
        self.aggregations[ContentKeys.LOS_PATH] = {
            "terms": {
                "field": EsMappings.LOS,
                "missing": "MISSING",
                "size": 100000
            }
        }
        self.aggregations[ContentKeys.OPEN_DATA] = open_data_aggregation()
        self.aggregations[ContentKeys.FORMAT] = {
            "terms": {
                "field": f"{EsMappings.FORMAT}.keyword",
                "missing": "MISSING",
                "size": 100000
            }
        }

    @staticmethod
    def es_keyword_key(json_ld_key: str):
        return f"{json_ld_key}{EsMappings.VALUE_KEYWORD}"

    @staticmethod
    def json_rdf_terms_aggregation(json_ld_field: str, size: int = None):
        return {
            "terms": {
                "field": AggregationQuery.es_keyword_key(json_ld_field),
                "missing": EsMappings.MISSING,
                "size": size or 10
            }
        }


class TimeSeriesQuery(Query):
    def __init__(self, series_field, orgpath, theme, theme_profile, organization_id):
        super().__init__()
        self.aggregations = {
            f"{EsMappings.TIME_SERIES}": {
                "date_histogram": {
                    "field": series_field,
                    "calendar_interval": "month"
                }
            }
        }
        self.add_filters(orgpath, theme, theme_profile, organization_id)


def org_path_aggregation() -> dict:
    return {
        "terms": {
            "field": "orgPath",
            "missing": EsMappings.MISSING,
            "size": 1000000000
        }
    }


def open_data_aggregation() -> dict:
    return {"filter": {
        "bool": {
            "must": [
                {
                    "term": {
                        AggregationQuery.es_keyword_key(
                            JSON_RDF.dct.accessRights): "http://publications.europa.eu/resource/authority/access"
                                                       "-right/PUBLIC"
                    }
                },
                {
                    "term": {
                        EsMappings.OPEN_LICENSE: "true"
                    }
                }
            ]
        }
    }
    }


def get_last_x_days_filter(key: str, days: int):
    range_str = f"now-{days}d/d"
    return {"filter": {
        "range": {
            key: {
                "gte": range_str,
                "lt": "now/d"
            }
        }
    }}


def get_los_path_filter(themes_str: str = None, profile_themes_list=None):
    if themes_str is not None:
        themes_list = themes_str.split(",")
    elif profile_themes_list is not None:
        themes_list = profile_themes_list
    else:
        return
    terms = []
    for theme in themes_list:
        terms.append({
            "term": {
                EsMappings.LOS: theme
            }
        })
    return terms


def get_org_path_filter(org_path: str):
    return {
        "term": {
            EsMappings.ORG_PATH: org_path
        }
    }


def get_theme_profile_filter(profile: ThemeProfile):
    if profile == ThemeProfile.TRANSPORT:
        should_list = get_los_path_filter(profile_themes_list=ThemeProfile.TRANSPORT_THEMES)
        return {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": should_list
                        }
                    },
                    {
                        "term": {
                            AggregationQuery.es_keyword_key(
                                JSON_RDF.dct.accessRights): "http://publications.europa.eu/resource/authority/access"
                                                           "-right/PUBLIC"
                        }

                    }
                ]
            }
        }


def get_term_query(field, value) -> dict:
    return {
        "term": {
            f"{field}.keyword": {
                "value": value
            }
        }
    }
