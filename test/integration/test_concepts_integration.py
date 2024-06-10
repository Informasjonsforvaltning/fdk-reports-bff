from flask import Flask
import pytest


class TestConceptsReport:
    @pytest.mark.integration
    def test_has_correct_format(self, client: Flask, docker_service, api):
        result = client.get("/report/concepts")
        assert result.status_code == 200
        keys = result.json.keys()
        assert "totalObjects" in keys
        assert "newLastWeek" in keys
        assert "orgPaths" in keys
        assert "organizationCount" in keys
        assert "mostInUse" in keys
