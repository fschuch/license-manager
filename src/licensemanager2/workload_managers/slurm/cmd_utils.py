"""Utilities that interact with slurm."""
import asyncio
import re
import shlex

from typing import List, Optional

from licensemanager2.agent import log as logger
from licensemanager2.workload_managers.slurm.common import (
    CMD_TIMEOUT,
    SCONTROL_PATH,
    SACCTMGR_PATH,
    ENCODING,
)


async def get_licenses_for_job(slurm_job_id: str) -> List:
    """
    Parse the scontrol output and return licenses needed for job.

    Note: "type: ignore" was used to silence mypy type errors

    See github issue: https://github.com/omnivector-solutions/license-manager/issues/19
    """

    # Command to get license information back from slurm using the
    # slurm_job_id.
    scontrol_show_lic = await asyncio.create_subprocess_shell(
        shlex.join([SCONTROL_PATH, "show", f"job={slurm_job_id}"]),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    scontrol_out, _ = await asyncio.wait_for(
        scontrol_show_lic.communicate(),
        CMD_TIMEOUT
    )
    scontrol_out = str(scontrol_out, ENCODING)  # type: ignore
    logger.info(scontrol_out)

    # Check that the command completed successfully
    if not scontrol_show_lic.returncode == 0:
        msg = f"Could not get SLURM data for job id: {slurm_job_id}"
        logger.error(msg)
        raise Exception(msg)

    # Parse license information from scontrol output
    m = re.search('.* Licenses=([^ ]*).*', scontrol_out)  # type: ignore
    license_list = m.group(1).split(',')  # type: ignore
    return license_list


async def get_used_tokens_for_license(
        product_feature_server: str) -> Optional[int]:
    """
    Return used tokens from scontrol output.
    """

    def match_product_feature_server() -> Optional[str]:
        """
        Return the line after the matched product_feature line.
        """
        matched = False
        for line in scontrol_output.split("\n"):
            if matched:
                return line
            if len(re.findall(rf"({product_feature_server})", line)) > 0:
                matched = True
        return None

    # Get the scontrol output
    scontrol_output = await scontrol_show_lic()

    # Match the product_feature_server
    token_str = match_product_feature_server()
    if token_str is not None:
        for item in token_str.split():
            k, v = item.split("=")
            if k == "Used":
                return int(v)
    return None


async def scontrol_show_lic():
    """
    Get the license usage from scontrol.
    """

    cmd = [
        SCONTROL_PATH,
        "show",
        "lic",
    ]

    proc = await asyncio.create_subprocess_shell(
        shlex.join(cmd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    stdout, _ = await asyncio.wait_for(proc.communicate(), CMD_TIMEOUT)
    output = str(stdout, encoding=ENCODING)
    return output


async def sacctmgr_modify_resource(
        product: str, feature: str, num_tokens) -> bool:
    """
    Update the license resource in slurm.
    """
    cmd = [
        SACCTMGR_PATH,
        "modify",
        "resource",
        f"name={product}.{feature}",
        "set",
        f"count={num_tokens}",
        "-i",
    ]
    logger.info(f"{' '.join(cmd)}")

    sacctmgr_modify_resource = await asyncio.create_subprocess_shell(
        shlex.join(cmd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    modify_resource_stdout, _ = await asyncio.wait_for(
        sacctmgr_modify_resource.communicate(),
        CMD_TIMEOUT,
    )

    rc = sacctmgr_modify_resource.returncode

    if not rc == 0:
        logger.warning(f"rc = {rc}!")
        logger.warning(modify_resource_stdout)
        return False
    return True
