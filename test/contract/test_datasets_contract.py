from datetime import datetime

import pytest
from requests import get

service_url = "http://localhost:8000"
dataset_report_url = f"{service_url}/report/datasets"
dataset_time_series_url = f"{service_url}/timeseries/datasets"


class TestDatasetsReport:

    @pytest.mark.contract
    def test_report_has_correct_format(self, wait_for_ready):
        result = get(url=dataset_report_url)
        assert result.status_code == 200
        content = result.json()
        keys = result.json().keys()
        assert "totalObjects" in keys
        assert "newLastWeek" in keys
        assert "nationalComponent" in keys
        assert "opendata" in keys
        assert "catalogs" in keys
        assert "withSubject" in keys
        assert "accessRights" in keys
        assert "themesAndTopicsCount" in keys
        assert "orgPaths" in keys
        assert len(content.get("orgPaths")) > len(content.get("catalogs"))
        assert content.get("totalObjects") == 1251
        assert content.get("nationalComponent") > 0
        assert content.get("opendata") > 0
        assert len(content.get("catalogs")) > 0
        assert content.get("withSubject") > 0
        assert len(content.get("accessRights")) == 4
        assert len(content.get("themesAndTopicsCount")) > 0

    @pytest.mark.contract
    def test_report_filter_on_orgPath(self, wait_for_ready):
        result = get(url=f"{dataset_report_url}?orgPath=/STAT/972417858/971040238")
        assert result.status_code == 200
        content = result.json()
        assert content["totalObjects"] == 110
        for org in content["catalogs"]:
            exp_orgpath_parts = "/STAT/972417858/971040238".split("/")
            for orgpath_part in org.get("key").split("/"):
                assert orgpath_part in exp_orgpath_parts

    @pytest.mark.contract
    def test_organization_id_filter(self, wait_for_ready):
        test_org_id = "950037687"
        exp_org_path = ["/PRIVAT/950037687", "/PRIVAT"]
        result = get(url=f"{dataset_report_url}?organizationId={test_org_id}")
        assert result.status_code == 200
        content = result.json()
        assert len(content) > 0
        for orgpath in content.get("orgPaths"):
            assert orgpath["key"] in exp_org_path

    @pytest.mark.contract
    def test_theme_profile_los_path_filter(self, wait_for_ready):
        accepted_paths = ["trafikk-og-transport", "trafikk-og-transport/mobilitetstilbud",
                          "trafikk-og-transport/trafikkinformasjon",
                          "trafikk-og-transport/veg-og-vegregulering", "trafikk-og-transport/yrkestransport"]
        result = get(url=f"{dataset_report_url}?themeprofile=transport")
        result_paths = result.json().get("themesAndTopicsCount")
        assert len(result_paths) > 0
        for path in result_paths:
            assert path["key"] in accepted_paths

    @pytest.mark.contract
    def test_time_series_has_correct_format(self, wait_for_ready):
        result = get(url=dataset_time_series_url)
        assert result.status_code == 200
        time_series = result.json()
        assert time_series[0]["xAxis"] == "01.08.2020"
        assert time_series[0]["yAxis"] == 1251
        last_date = time_series[len(time_series) - 1]["xAxis"]
        dt = datetime.strptime(last_date, '%d.%m.%Y')
        now = datetime.now()
        assert dt.month == now.month
        assert dt.year == now.year
