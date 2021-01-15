#!/usr/bin/env python3
"""license_manager handlers module."""
import json
import os
import socket
import sys

from license_manager.logging import log
from license_manager.slurm_tools import (
    required_licenses_for_job as slurm_job_requirement,
)


def _client(license_manager_server_endpoint, message):
    ip_port = license_manager_server_endpoint.split(":")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip_port[0], int(ip_port[1])))
        sock.sendall(bytes(message, "ascii"))
        response = str(sock.recv(1024), "ascii")
        response = bool(response)

        if response:
            log.info("License booking completed!")

        else:
            log.info("License booking failed! " f"Received: {response}.")

        return response


def _job_context():
    """Assign variables from SLURM environ variables."""
    ctxt = set()
    try:
        ctxt = {
            # Get cluster name
            "cluster_name": os.environ["SLURM_CLUSTER_NAME"],
            # Get job id of job
            "job_id": os.environ["SLURM_JOB_ID"],
            #  Get first node which execute application
            "compute_host": os.environ["SLURM_JOB_NODELIST"].split(",")[0],
            # Get user name
            "user": os.environ["SLURM_JOB_USER"],
        }
    except KeyError as e:
        # If not all keys could be assigned, then return non 0 exit status
        log.error(
            f"All required environment variables were not set, missing: {e}. "
            "Expecting: SLURM_CLUSTER_NAME, SLURM_JOB_ID, SLURM_JOB_NODELIST, "
            "SLURM_JOB_USER"
        )
        sys.exit(1)

    return ctxt


def _epilog_controller(license_manager_server_endpoint):
    """Epilog to be executed by controller."""
    ctxt = _job_context()
    compute_host = ctxt["compute_host"]
    job_id = ctxt["job_id"]
    user_name = ctxt["user"]

    job_req = slurm_job_requirement(job_id, debug=True)
    if not job_req:
        log.info("No licenses requested")
        sys.exit(0)
    else:
        # Generate requests for all required tokens
        requests = []
        for license_feature, license_server, tokens in job_req:
            # Generate request to license manager
            request = dict()
            request["feature"] = license_feature
            request["required_tokens"] = tokens
            request["job_id"] = job_id
            request["user_name"] = user_name
            request["compute_host_name"] = compute_host

            # Set action at license manager
            request["action"] = "return_license"

            requests.append(request)

        # Convert request into a string
        json_request = json.dumps(requests)

    # Debug log request
    log.debug(json_request)

    # Send request to license manager
    request_response = _client(
        license_manager_server_endpoint,
        json_request,
    )

    if request_response:
        log.info("License was returned")
        sys.exit(0)
    else:
        log.info("License was not booked")
        sys.exit(0)


def _prolog_controller(license_manager_server_endpoint):
    """Prolog to be executed by ctld."""
    ctxt = _job_context()
    compute_host = ctxt["compute_host"]
    job_id = ctxt["job_id"]
    user_name = ctxt["user"]

    job_req = slurm_job_requirement(job_id, debug=True)
    if not job_req:
        log.info("No licenses requested")
        sys.exit(0)
    else:
        # Generate requests for all required tokens
        requests = []
        for license_feature, license_server, tokens in job_req:
            # Generate request to license manager
            request = dict()
            request["feature"] = license_feature
            request["required_tokens"] = tokens
            request["job_id"] = job_id
            request["user_name"] = user_name
            request["compute_host_name"] = compute_host

            # Set action at license manager
            request["action"] = "book_license"

            requests.append(request)

        # Convert request into a string
        json_request = json.dumps(requests)

    # Debug log request
    log.debug(json_request)

    # Send request to license manager
    request_response = _client(
        license_manager_server_endpoint,
        json_request,
    )

    if request_response:
        log.info("Sufficient tokens")
        sys.exit(0)
    else:
        log.info("Unsufficient tokens")
        sys.exit(1)


def run_controller_prolog_or_epilog(license_manager_server_endpoint, script_type):
    """Determine the script type and run the appropriate prolog/epilog ctrl."""
    if script_type == "epilog":
        _epilog_controller(license_manager_server_endpoint)
    else:
        _prolog_controller(license_manager_server_endpoint)
