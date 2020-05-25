import pytest
import requests
from jsonpath_ng import parse

from tests.contract.utils import read_expected_values, ContentTypeKey

report_url = "http://localhost:8000"
datasets_report_url = f"{report_url}/datasets"
expected_values = read_expected_values(ContentTypeKey.DATA_SETS)
expected_stats = expected_values["aggregations"]


class TestDataSets:

    @pytest.mark.contract
    def test_has_correct_overall_stats(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        assert result.status_code == 200
        result_body = result.json()
        result_keys = result_body.keys()
        assert "totalElements" in result_keys
        assert result_body["totalElements"] == expected_values["hits"]["total"]
        assert "newElementsLastWeek" in result_keys
        assert result_body["newElementsLastWeek"] == expected_stats["firstHarvested"]["last7days"]["count"]
        assert "withSubject" in result_keys
        assert result_body["withSubject"] == expected_stats["withSubject"]["47"]

    @pytest.mark.contract
    def test_has_correct_organizations_count(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        if result.status_code != 200:
            pytest.xfail(f"Server returned status {result.status_code}")

        result_body = result.json()
        result_keys = result_body.keys()
        assert "organizations" in result_keys
        expected_org_path_list = [match.value for match in parse('orgPath.buckets.*key').find(expected_stats)]
        for org in result_body['organizations']:
            assert org['key'] in expected_org_path_list
            expected_content_count = parse(f"orgPath.buckets.[?key=={org['key']}]").find(expected_stats)
            assert org['count'] == expected_content_count

    @pytest.mark.contract
    def test_has_correct_catalog_count(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        if result.status_code != 200:
            pytest.xfail(f"Server returned status {result.status_code}")

        result_body = result.json()
        result_keys = result_body.keys()
        assert "catalogs" in result_keys
        expected_org_path_list = [match.value for match in parse('catalog.buckets.*key').find(expected_stats)]
        for catalog in result_body['catalogs']:
            assert catalog['key'] in expected_org_path_list
            expected_content_count = parse(f"orgPath.buckets.[?key=={catalog['key']}]").find(expected_stats)
            assert catalog['count'] == expected_content_count

    @pytest.mark.contract
    def test_has_correct_availability_count(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        if result.status_code != 200:
            pytest.xfail(f"Server returned status {result.status_code}")

        result_body = result.json()
        result_keys = result_body.keys()
        assert "withDistribution" in result_keys
        assert "publicWithoutDistribution" in result_keys
        assert "nonPublicWithDistribution" in result_keys
        assert "nonPublicWithoutDistribution" in result_keys

        assert result_body["withDistribution"] == expected_stats["withDistribution"]['doc_count']
        assert result_body["publicWithoutDistribution"] == expected_stats["publicWithoutDistribution"]["doc_count"]
        assert result_body["nonPublicWithDistribution"] == expected_stats["nonPublicWithDistribution"]["doc_count"]
        assert result_body["nonPublicWithoutDistribution"] == expected_stats["nonPublicWithoutDistribution"]

    @pytest.mark.contract
    def test_has_correct_distribution_type_for_count(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        if result.status_code != 200:
            pytest.xfail(f"Server returned status {result.status_code}")

        result_body = result.json()
        result_keys = result_body.keys()
        assert "distributionCountForType" in result_keys()
        dist_count_type = result_body["distributionCountForType"]
        assert dist_count_type["api"] == expected_stats["distributionCountForTypeApi"]
        assert dist_count_type["file"] == expected_stats["distributionCountForTypeFile"]
        assert dist_count_type["stream"] == expected_stats["distributionCountForTypeStream"]

    @pytest.mark.contract
    def test_has_correct_access_rights(self, wait_for_ready):
        result = requests.get(url=datasets_report_url, timeout=10)
        if result.status_code != 200:
            pytest.xfail(f"Server returned status {result.status_code}")

        result_body = result.json()
        result_keys = result_body.keys()
        expected_access_rights = [match.value for match in parse('accessRights.buckets.*').find(expected_stats)]
        for accessRight in result_body["accesRights"]:
            assert accessRight in expected_access_rights
        assert "opendata" in result_keys
        assert result_body["opendata"] == expected_stats["opendata"]["doc_count"]
