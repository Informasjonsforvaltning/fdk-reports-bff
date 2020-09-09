import pytest

from src.elasticsearch.queries import EsMappings
from src.rdf_namespaces import ContentKeys
from src.responses import InformationModelResponse, ConceptResponse, TimeSeriesResponse
from src.utils import ParsedDataPoint
from test.unit_mock_data import concepts_aggregation, concepts_in_use


@pytest.mark.unit
def test_information_model_response():
    es_result = {
        "_embedded": {
            "informationmodels": []
        },
        "page": {
            "totalElements": 574,
            "totalPages": 58,
            "number": 0
        },
        "aggregations": {
            "orgPath": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [
                    {
                        "key": "/ANNET",
                        "doc_count": 794
                    },
                    {
                        "key": "/ANNET/910298062",
                        "doc_count": 642
                    },
                    {
                        "key": "/STAT",
                        "doc_count": 466
                    },
                    {
                        "key": "/STAT/972417858",
                        "doc_count": 112
                    },
                    {
                        "key": "/STAT/972417858/971040238",
                        "doc_count": 109
                    },
                    {
                        "key": "/STAT/972417874",
                        "doc_count": 100
                    }
                ]
            },
            "firstHarvested": {
                "buckets": [
                    {
                        "key": "last30days",
                        "count": 96
                    },
                    {
                        "key": "last365days",
                        "count": 4267
                    },
                    {
                        "key": "last7days",
                        "count": 3
                    }
                ]
            }
        },
    }

    result = InformationModelResponse.from_es(es_result)

    assert result.totalObjects == 574
    assert result.newLastWeek == 3
    assert len(result.catalogs) == 6


@pytest.mark.unit
def test_concept_response():
    result = ConceptResponse.from_es(concepts_aggregation, concepts_in_use)
    assert len(result.mostInUse) == 3
    assert result.newLastWeek == 10
    assert len(result.catalogs) == 11


@pytest.mark.unit
def test_time_series_response():
    es_bucket_november = {
        "key_as_string": "2019-11-01T00:00:00.000Z",
        "doc_count": 8
    }
    es_bucket_january = {
        "key_as_string": "2020-01-01T00:00:00.000Z",
        "doc_count": 2
    }
    es_bucket_april = {
        "key_as_string": "2020-04-01T00:00:00.000Z",
        "doc_count": 1
    }
    es_bucket_may = {
        "key_as_string": "2020-05-01T00:00:00.000Z",
        "doc_count": 1
    }
    es_bucket_june = {
        "key_as_string": "2020-06-01T00:00:00.000Z",
        "doc_count": 3
    }
    parsed_series = {
        "aggregations": {
            EsMappings.TIME_SERIES: {
                "buckets": [
                    es_bucket_november, es_bucket_january, es_bucket_april, es_bucket_may,
                    es_bucket_june
                ]
            }
        }
    }
    result = TimeSeriesResponse(parsed_series).json()
    assert len(result) == 11
    assert result[0][ContentKeys.TIME_SERIES_X_AXIS] == "2019-11-01T00:00:00.000Z"
    assert result[1][ContentKeys.TIME_SERIES_X_AXIS] == "2019-12-01T00:00:00.000Z"
    assert result[2][ContentKeys.TIME_SERIES_X_AXIS] == "2020-01-01T00:00:00.000Z"
    assert result[3][ContentKeys.TIME_SERIES_X_AXIS] == "2020-02-01T00:00:00.000Z"
    assert result[4][ContentKeys.TIME_SERIES_X_AXIS] == "2020-03-01T00:00:00.000Z"
    assert result[5][ContentKeys.TIME_SERIES_X_AXIS] == "2020-04-01T00:00:00.000Z"
    assert result[6][ContentKeys.TIME_SERIES_X_AXIS] == "2020-05-01T00:00:00.000Z"
    assert result[7][ContentKeys.TIME_SERIES_X_AXIS] == "2020-06-01T00:00:00.000Z"
    assert result[0][ContentKeys.TIME_SERIES_Y_AXIS] == 8
    assert result[1][ContentKeys.TIME_SERIES_Y_AXIS] == 8
    assert result[2][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[3][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[4][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[5][ContentKeys.TIME_SERIES_Y_AXIS] == 11
    assert result[6][ContentKeys.TIME_SERIES_Y_AXIS] == 12
    assert result[7][ContentKeys.TIME_SERIES_Y_AXIS] == 15
