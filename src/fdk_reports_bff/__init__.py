import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from fdk_reports_bff.elasticsearch.scheduler import schedule_updates
from fdk_reports_bff.endpoints import Ping, Ready, Report, TimeSeries, Updates
from fdk_reports_bff.utils import StartSchedulerError


def create_app(test_config: any = None) -> Flask:
    # Create and configure the app
    load_dotenv(override=True)
    app = Flask(__name__, instance_relative_config=True)

    CORS(app)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
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
    api.add_resource(Ping, "/ping")
    api.add_resource(Report, "/report/<string:content_type>")
    api.add_resource(TimeSeries, "/timeseries/<string:content_type>")
    api.add_resource(Updates, "/updates")
    try:
        schedule_updates()
    except StartSchedulerError as err:
        logging.warning(str(err))
    return app
