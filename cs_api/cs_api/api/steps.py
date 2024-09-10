from datetime import datetime

import flask
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from cs_api.db import db
from cs_api.db.models import StepMetadata, JobMetadata


@server.app.route(const.ADD_JOB, methods=["POST"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def add_job():
    """
    Adds a Job to the database, adds in a Step if needed and links the Step to a Run, Fault or Realisation
    """
    server.app.logger.info(f"Received request at {const.ADD_JOB}")
    (
        run,
        fault,
        realisation,
        workflow_step,
        step_id,
        job_id,
        time_submitted,
        time_started,
        time_ended,
        ncpus,
        type,
    ) = utils.get_check_keys(
        flask.request.args,
        (
            "run_name",
            "fault_name",
            "realisation_name",
            "workflow_step",
            ("step_id", int),
            ("job_id", int),
            ("time_submitted", datetime),
            ("time_started", datetime),
            ("time_ended", datetime),
            ("ncpus", int),
            "type",
        ),
    )

    # Get the runtime
    runtime = time_ended - time_started

    # Get the order of the step
    step = db.get_step(step_id)

    # Check if there is a step
    new_step = False
    if step is None:
        # Get the Run
        run = db.get_run(run)
        if fault is not None:
            fault = db.get_fault(fault, run)
        if realisation is not None:
            if fault is None:
                # Return Error
                return flask.jsonify({"error": "Fault must be specified if realisation is specified"}), 400
            realisation = db.get_realisation(realisation, fault)

        # Create the step
        step = StepMetadata(
            id=step_id,
            workflow_step=workflow_step,
            run=run,
            fault=fault,
            realisation=realisation,
        )
        new_step = True

    # Get length of current jobs for the step to determine this jobs order
    order = len(step.jobs) + 1
    # TODO Do updating of order for all jobs in the step if the time_ended is before another jobs time_ended

    # Create the Job
    job = JobMetadata(
        job_id=job_id,
        time_submitted=time_submitted,
        time_started=time_started,
        time_ended=time_ended,
        ncpus=ncpus,
        runtime=runtime,
        type=type,
        order=order,
        step_metadata=step,
    )
    db.session.add(job)

    # Add the Job to the step
    step.jobs.append(job)

    # Add the Step to the database if it is new
    if new_step:
        db.session.add(step)

    # Commit the changes
    db.session.commit()

    # Return the success message
    return flask.jsonify({"success": "Added job to database"}), 200
