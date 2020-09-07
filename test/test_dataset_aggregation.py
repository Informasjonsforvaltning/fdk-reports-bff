import pytest

from src.dataset_aggregation import create_dataset_report
from src.responses import DataSetResponse
from test.unit_mock_data import mock_access_rights_catalog_response


@pytest.mark.unit
def test_get_datasets(mock_es_report, get_access_rights_mock):
    result: DataSetResponse = create_dataset_report(None, None, None, None)
    assert 6 == len(result.formats)
    assert 35 == int(result.withSubject)
    assert 0 == int(result.newLastWeek)
    assert 331 == int(result.opendata)
    assert 1251 == int(result.totalObjects)
    assert 8 == int(result.nationalComponent)
    assert 4 == len(result.accessRights)
    assert 5 == len(result.catalogs)


mock_es_result = {
    "took": 14,
    "timed_out": "false",
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1251,
            "relation": "eq"
        },
        "max_score": 1.0,
        "hits": [
            {
                "_index": "datasets",
                "_type": "_doc",
                "_id": "MUNjL3QBKXToLKwBxo0_",
                "_score": 1.0,
                "_source": {
                    "http://purl.org/dc/terms/accessRights": [
                        {
                            "type": "uri",
                            "value": "http://publications.europa.eu/resource/authority/access-right/PUBLIC"
                        }
                    ],
                    "http://www.w3.org/ns/dcat#theme": [
                        {
                            "type": "uri",
                            "value": "http://publications.europa.eu/resource/authority/data-theme/GOVE"
                        },
                        {
                            "type": "uri",
                            "value": "http://publications.europa.eu/resource/authority/data-theme/REGI"
                        },
                        {
                            "type": "uri",
                            "value": "https://register.geonorge.no/subregister/metadata-kodelister/kartverket/nasjonal-temainndeling/kartverket/basis-geodata"
                        }
                    ],
                    "http://www.w3.org/ns/dcat#distribution": [
                        {
                            "http://www.w3.org/ns/dcat#accessURL": [
                                {
                                    "type": "uri",
                                    "value": "https://kartkatalog.geonorge.no/metadata/uuid/554d9e3f-18d1-40f2-bf23-5d104a8cb1ff"
                                }
                            ],
                            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": [
                                {
                                    "type": "uri",
                                    "value": "http://www.w3.org/ns/dcat#Distribution"
                                }
                            ],
                            "http://purl.org/dc/terms/format": [
                                {
                                    "type": "literal",
                                    "value": "GML"
                                }
                            ],
                            "http://www.w3.org/ns/adms#status": [
                                {
                                    "type": "literal",
                                    "value": ""
                                }
                            ],
                            "http://purl.org/dc/terms/description": [
                                {
                                    "type": "literal",
                                    "value": "Datasettet er ikke tilgjengelig for direkte nedlastning"
                                }
                            ],
                            "http://purl.org/dc/terms/license": [
                                {
                                    "type": "uri",
                                    "value": "https://creativecommons.org/licenses/by/4.0/"
                                }
                            ],
                            "http://purl.org/dc/terms/title": [
                                {
                                    "type": "literal",
                                    "value": "Ingen online tilgang",
                                    "lang": "no"
                                }
                            ],
                            "nodeUri": "https://kartkatalog.geonorge.no/Metadata/uuid/554d9e3f-18d1-40f2-bf23-5d104a8cb1ff/GML"
                        }
                    ],
                    "nodeUri": "https://kartkatalog.geonorge.no/Metadata/uuid/554d9e3f-18d1-40f2-bf23-5d104a8cb1ff",
                    "orgPath": "/STAT/972417858/971040238",
                    "dcatRecord": {
                        "http://purl.org/dc/terms/issued": [
                            {
                                "type": "literal",
                                "value": "2020-08-19T09:39:10.1Z",
                                "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"
                            }
                        ]
                    },
                    "OpenLicense": "true",
                    "formatCodes": [
                        "GML"
                    ]
                }
            }
        ]
    },
    "aggregations": {
        "losPath": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "MISSING",
                    "doc_count": 1251
                }
            ]
        },
        "code": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
                    "doc_count": 1231
                },
                {
                    "key": "http://publications.europa.eu/resource/authority/access-right/RESTRICTED",
                    "doc_count": 11
                },
                {
                    "key": "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC",
                    "doc_count": 8
                },
                {
                    "key": "MISSING",
                    "doc_count": 1
                }
            ]
        },
        "nationalComponent": {
            "doc_count": 8
        },
        "orgPath": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "/ANNET/910298062",
                    "doc_count": 642
                },
                {
                    "key": "MISSING",
                    "doc_count": 370
                },
                {
                    "key": "/STAT/972417858/971040238",
                    "doc_count": 110
                },
                {
                    "key": "/ANNET/910244132",
                    "doc_count": 60
                },
                {
                    "key": "/STAT/972417904/971032081",
                    "doc_count": 54
                },
                {
                    "key": "/ANNET/910258028",
                    "doc_count": 12
                },
                {
                    "key": "/ANNET/HIDRASUND OG BJONEROA",
                    "doc_count": 2
                },
                {
                    "key": "/ANNET/911527170",
                    "doc_count": 1
                }
            ]
        },
        "catalogs": {
            "buckets": [
                {
                    "key": "/ANNET/910298062",
                    "doc_count": 642
                },
                {
                    "key": "/STAT/972417858/971040238",
                    "doc_count": 110
                },
                {
                    "key": "/ANNET/910244132",
                    "doc_count": 60
                },
                {
                    "key": "/STAT/972417904/971032081",
                    "doc_count": 54
                },
                {
                    "key": "/ANNET/910258028",
                    "doc_count": 12
                }
            ]
        }
        ,
        "opendata": {
            "doc_count": 331
        },
        "format": {
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
            "buckets": [
                {
                    "key": "GML",
                    "doc_count": 478
                },
                {
                    "key": "SOSI",
                    "doc_count": 282
                },
                {
                    "key": "CSV",
                    "doc_count": 231
                },
                {
                    "key": "MISSING",
                    "doc_count": 158
                },
                {
                    "key": "JSON",
                    "doc_count": 111
                },
                {
                    "key": "geoJSON",
                    "doc_count": 99
                }
            ]
        },
        "withSubject": {
            "doc_count": 35
        },
        "new_last_week": {
            "meta": {},
            "doc_count": 0
        }
    }
}


@pytest.fixture
def mock_es_report(mocker):
    return mocker.patch("src.dataset_aggregation.elasticsearch_get_report_aggregations", return_value=mock_es_result)


@pytest.fixture
def get_access_rights_mock(mocker):
    mocker.patch('src.referenced_data_store.fetch_access_rights_from_reference_data',
                 side_effect=mock_access_rights_catalog_response)
