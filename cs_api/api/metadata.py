import flask
from flask_cors import cross_origin

from cs_api import constants as const
from cs_api import server, utils
from cs_api.db import db


@server.app.route(const.GET_DATASET_TYPES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_dataset_types():
    """
    Gets the possible dataset types from the db
    """
    server.app.logger.info(f"Received request at {const.GET_DATASET_TYPES}")
    return flask.jsonify(db.get_dataset_types())


@server.app.route(const.GET_UNIQUE_EVENTS, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_all_unique_events():
    """
    Gets all the unique events from every run on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_UNIQUE_EVENTS}")
    unique_faults = db.get_all_unique_events()
    return flask.jsonify(unique_faults)


@server.app.route(const.GET_UNIQUE_SITES, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_all_unique_sites():
    """
    Gets all the unique sites from every run on dropbox
    """
    server.app.logger.info(f"Received request at {const.GET_UNIQUE_SITES}")
    unique_sites = db.get_all_unique_sites()
    return flask.jsonify(unique_sites)
