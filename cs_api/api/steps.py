from datetime import datetime

import flask
import pandas as pd
from flask_cors import cross_origin

from cs_api import server, utils
from cs_api import constants as const
from cs_api.server import db
from cs_api.db import db as cs_db
from cs_api.db.models import StepMetadata, JobMetadata


@server.app.route(const.ADD_JOB, methods=["POST"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def add_job():
    """
    Adds a Job to the database, adds in a Step if needed and links the Step to a Run, Event or Realisation
    """
    breakpoint()
    server.app.logger.info(f"Received request at {const.ADD_JOB}")
    (
        run,
        event,
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
            "event_name",
            "realisation_name",
            "workflow_step",
            ("step_id", int),
            ("job_id", int),
            ("time_submitted", datetime.fromisoformat),
            ("time_started", datetime.fromisoformat),
            ("time_ended", datetime.fromisoformat),
            ("n_cpus", int),
            "type",
        ),
    )

    # Get the runtime
    runtime = time_ended - time_started

    # Get the realisation number
    realisation_num = None if realisation is None else int(realisation.split("_")[-1][3:])

    # Get the order of the step
    step = cs_db.get_step(step_id)

    # Check if there is a step
    new_step = False
    if step is None:
        # Get the Run
        run = cs_db.get_run(run)
        if event is not None:
            event = cs_db.get_event(event, run)
        if realisation is not None:
            if event is None:
                # Return Error
                return flask.jsonify({"error": "Event must be specified if realisation is specified"}), 400
            realisation = cs_db.get_realisation(realisation_num, event)

        # Create the step
        step = StepMetadata(
            id=step_id,
            workflow_step=workflow_step,
            run=run,
            event=event,
            realisation=realisation,
        )
        new_step = True

    # Create the Job
    job = JobMetadata(
        job_id=job_id,
        time_submitted=time_submitted,
        time_started=time_started,
        time_ended=time_ended,
        ncpus=ncpus,
        runtime=runtime,
        type=type,
        order=1, # Updated below, just filler for now
        step_metadata=step,
    )
    db.session.add(job)

    # Add the Job to the step
    step.jobs.append(job)

    # Update all jobs by ensuring correct order from time_ended
    jobs = sorted(step.jobs, key=lambda job: job.time_ended)
    for index, job in enumerate(jobs):
        job.order = index + 1

    # Add the Step to the database if it is new
    if new_step:
        db.session.add(step)

    # Commit the changes
    db.session.commit()

    # Return the success message
    return flask.jsonify({"success": "Added job to database"}), 200


@server.app.route(const.GET_JOBS_CSV, methods=["GET"])
@cross_origin(expose_headers=["Content-Type", "Authorization"])
@utils.endpoint_exception_handling(server.app)
def get_jobs_csv():
    """
    Fetches all job information for a run and returns it as a CSV file
    """
    server.app.logger.info(f"Received request at {const.GET_JOBS_CSV}")
    run_name = flask.request.args.get("run_name")

    if not run_name:
        return flask.jsonify({"error": "run_name parameter is required"}), 400

    # Fetch the run object
    run = cs_db.get_run(run_name)
    if not run:
        return flask.jsonify({"error": "Run not found"}), 404

    # Get all the steps for the run
    steps = cs_db.get_all_steps(run)

    # Convert job information to a DataFrame
    job_data = [
        {
            "job_id": job.job_id,
            "time_submitted": job.time_submitted,
            "time_started": job.time_started,
            "time_ended": job.time_ended,
            "ncpus": job.ncpus,
            "runtime": job.runtime,
            "type": job.type.value,
            "order": job.order,
            "step_id": job.step_metadata_id,
        }
        for step in steps for job in step.jobs
    ]
    df = pd.DataFrame(job_data)

    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)

    # Send CSV to user
    return flask.Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={run_name}_jobs.csv"}
    )