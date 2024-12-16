import flask
from flask_cors import cross_origin

from cs_api import constants as const
from cs_api import server, utils
from cs_api.db import db as cs_db


@server.app.route(const.GET_DATASETS_INFO, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_full_dataset_info():
    """
    Gets all the dataset information from every dataset on dropbox
    and their metadata from the db
    """
    server.app.logger.info(f"Received request at {const.GET_DATASETS_INFO}")
    available_datasets = cs_db.get_available_datasets()
    dataset_infos = {dataset.name: dataset.to_json() for dataset in available_datasets}
    return flask.jsonify(dataset_infos)
