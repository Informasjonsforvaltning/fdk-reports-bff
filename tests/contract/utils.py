import json
import os


class ContentTypeKey:
    ORGANIZATIONS = "organization"
    INFO_MODELS = "informationmodels"
    DATA_SERVICES = "dataservices"
    DATA_SETS = "datasets"
    CONCEPTS = "concepts"


mapping_files = {
    ContentTypeKey.DATA_SETS: f"{os.getcwd().split('/test')[0]}/mock/mappings/datasets-a3f473d5-f141-4dde-939c"
                              f"-f999b5b6355f.json"
}


def read_expected_values(key: ContentTypeKey):
    with open(mapping_files[key]) as mock_mappings:
        response_body = json.load(mock_mappings)["response"]["body"]
        return json.loads(response_body)
