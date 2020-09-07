import pytest

from src.utils import ServiceKey, NotAServiceKeyException, ParsedDataPoint


@pytest.mark.unit
def test_get_key():
    assert ServiceKey.get_key("informationmodels") == ServiceKey.INFO_MODELS
    assert ServiceKey.get_key("datasets") == ServiceKey.DATA_SETS
    assert ServiceKey.get_key("concepts") == ServiceKey.CONCEPTS
    assert ServiceKey.get_key("organizations") == ServiceKey.ORGANIZATIONS
    assert ServiceKey.get_key("dataservices") == ServiceKey.DATA_SERVICES
    with pytest.raises(NotAServiceKeyException):
        ServiceKey.get_key("notakey")


@pytest.mark.unit
def test_get_next_month():
    es_bucket_november = {
        "key_as_string": "01.11.2019",
        "doc_count": 8
    }

    november = ParsedDataPoint(es_bucket=es_bucket_november)
    december = november.get_next_month()
    assert december.y_axis == 8


@pytest.mark.unit
def test_add_last_count_to_es_data_point():
    es_bucket_november = {
        "key_as_string": "01.11.2019",
        "doc_count": 8
    }

    november = ParsedDataPoint(es_bucket=es_bucket_november, last_month_count=112)
    assert november.y_axis == 120
