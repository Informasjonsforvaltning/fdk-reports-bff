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
        keys = result.json().keys()
        assert "totalObjects" in keys
        assert "newLastWeek" in keys
        assert "nationalComponent" in keys
        assert "opendata" in keys
        assert "catalogs" in keys
        assert "withSubject" in keys
        assert "accessRights" in keys
        assert "themesAndTopicsCount" in keys

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
