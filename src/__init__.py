import os

from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from src.endpoints import Ping, Ready, InformationModelsReport, ConceptsReport, DataSetsReport, DataServicesReport


def create_app(test_config=None):
    # Create and configure the app
    load_dotenv(override=True)
    app = Flask(__name__, instance_relative_config=True)

    CORS(app)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # add endpoints
    api = Api(app)
    api.add_resource(Ready, "/ready")
    api.add_resource(Ping, '/ping')
    api.add_resource(InformationModelsReport, '/report/informationmodels')
    api.add_resource(ConceptsReport, '/report/concepts')
    api.add_resource(DataSetsReport, '/report/datasets')
    api.add_resource(DataServicesReport, '/report/dataservices')
    return app
