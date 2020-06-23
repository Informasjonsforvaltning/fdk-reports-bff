import pytest
from requests import get

service_url = "http://localhost:8000"
informationmodels_report_url = f"{service_url}/report/informationmodels"


class TestInformationModelsReport:

    @pytest.mark.contract
    def test_has_correct_format(self, wait_for_ready):
        pytest.xfail("under development")
        result = get(url=informationmodels_report_url)
        assert result.status_code == 200
        keys = result.json().keys()
        assert "totalObjects" in keys
        assert "newLastWeek" in keys
        assert "organizations" in keys
        assert "catalogs" in keys



