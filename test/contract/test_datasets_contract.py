import pytest
from requests import get

service_url = "http://localhost:8080"
dataset_report_url = f"{service_url}/report/datasets"
dataset_time_series_url = f"{service_url}/timeseries/datasets"


class TestDatasetsReport:
    @pytest.mark.contract
    def test_report_has_correct_format(self, docker_service, api):
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
        assert "organizationCount" in keys
        assert "formats" in keys
        assert len(content.get("orgPaths")) > len(content.get("catalogs"))
        assert content.get("organizationCount") < len(content.get("orgPaths"))
        assert content.get("organizationCount") > len(content.get("catalogs"))
        assert len(content.get("catalogs")) > 1
        assert content.get("totalObjects") == 1548
        assert content.get("nationalComponent") > 0
        assert content.get("opendata") > 0
        assert len(content.get("catalogs")) > 0
        assert content.get("withSubject") > 0
        assert len(content.get("accessRights")) == 5
        assert len(content.get("themesAndTopicsCount")) > 0
        assert len(content.get("formats")) > 0
