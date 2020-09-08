import pytest

from src.elasticsearch.queries import EsMappings
from src.rdf_namespaces import ContentKeys
from src.responses import InformationModelResponse, ConceptResponse, TimeSeriesResponse, DataSetResponse
from src.utils import ThemeProfile
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
        "key_as_string": "01.11.2019",
        "doc_count": 8
    }
    es_bucket_january = {
        "key_as_string": "01.01.2020",
        "doc_count": 2
    }
    es_bucket_april = {
        "key_as_string": "01.04.2020",
        "doc_count": 1
    }
    es_bucket_may = {
        "key_as_string": "01.05.2020",
        "doc_count": 1
    }
    es_bucket_june = {
        "key_as_string": "01.06.2020",
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
    assert result[0][ContentKeys.TIME_SERIES_X_AXIS] == "01.11.2019"
    assert result[1][ContentKeys.TIME_SERIES_X_AXIS] == "01.12.2019"
    assert result[2][ContentKeys.TIME_SERIES_X_AXIS] == "01.01.2020"
    assert result[3][ContentKeys.TIME_SERIES_X_AXIS] == "01.02.2020"
    assert result[4][ContentKeys.TIME_SERIES_X_AXIS] == "01.03.2020"
    assert result[5][ContentKeys.TIME_SERIES_X_AXIS] == "01.04.2020"
    assert result[6][ContentKeys.TIME_SERIES_X_AXIS] == "01.05.2020"
    assert result[7][ContentKeys.TIME_SERIES_X_AXIS] == "01.06.2020"
    assert result[0][ContentKeys.TIME_SERIES_Y_AXIS] == 8
    assert result[1][ContentKeys.TIME_SERIES_Y_AXIS] == 8
    assert result[2][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[3][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[4][ContentKeys.TIME_SERIES_Y_AXIS] == 10
    assert result[5][ContentKeys.TIME_SERIES_Y_AXIS] == 11
    assert result[6][ContentKeys.TIME_SERIES_Y_AXIS] == 12
    assert result[7][ContentKeys.TIME_SERIES_Y_AXIS] == 15


@pytest.mark.unit
def test_dataset_with_theme_profile():
    result = DataSetResponse(
        total=21,
        catalogs=[
            {
                "key": "/STAT/912660680/970188290",
                "count": 17
            },
            {
                "key": "/STAT/972417904/874783242",
                "count": 15
            },
            {
                "key": "/KOMMUNE/958935420",
                "count": 13
            }
        ],
        org_paths=[
            {
            "key": "/STAT/912660680/970188290",
            "count": 17
        },
            {
                "key": "/STAT/972417904/874783242",
                "count": 15
            },
            {
                "key": "/KOMMUNE/958935420",
                "count": 13
            }
        ],
        access_rights=[],
        themes=[
            {
                "key": "trafikk-og-transport",
                "count": 112
            },
            {
                "key": "familie-og-barn",
                "count": 108
            },
            {
                "key": "naring",
                "count": 105
            },
            {
                "key": "naring/landbruk",
                "count": 98
            },
            {
                "key": "bygg-og-eiendom",
                "count": 97
            },
            {
                "key": "bygg-og-eiendom",
                "count": 97
            },
            {
                "key": "trafikk-og-transport/mobilitetstilbud",
                "count": 97
            },
            {
                "key": "trafikk-og-transport/trafikkinformasjon",
                "count": 97
            },
            {
                "key": "trafikk-og-transport/veg-og-vegregulering",
                "count": 97
            },
            {
                "key": "trafikk-og-transport/yrkestransport",
                "count": 97
            }

        ],
        with_subject=19,
        opendata=3,
        new_last_week=1,
        national_component=2,
        dist_formats=[],
        theme_profile=ThemeProfile.TRANSPORT
    )

    assert len(result.themesAndTopicsCount) == 4
    assert len(result.catalogs) == 3
    assert result.totalObjects == 21
    assert result.withSubject == 19
