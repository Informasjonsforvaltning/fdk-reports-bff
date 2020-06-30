import os

from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from src.endpoints import Ping, Ready, Report

import asyncio
import httpx
import time

from .service_requests import get_organization, get_organization_same

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
    api.add_resource(Report, '/report/<string:content_type>')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    coroutines = [
        '910244132', '910244132', '910244132', '910244132', '910244132',
        '910244132', '910244132', '910244132', '910244132', '910244132'
    ]

    session = httpx.AsyncClient()

    start = time.time()
    res = loop.run_until_complete(asyncio.gather(*[get_organization(session, '910244132') for _ in coroutines]))
    finish = time.time()

    print(f'Elapsed: {finish - start} s')

    start = time.time()
    res = loop.run_until_complete(asyncio.gather(*[get_organization_same('910244132') for _ in coroutines]))
    finish = time.time()

    print(f'Elapsed: {finish - start} s')
    return app
