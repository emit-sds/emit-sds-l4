"""
Delivers L4 model runs to the DAAC

Author: Winston Olson-Duvall, winston.olson-duvall@jpl.nasa.gov
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess

import numpy as np

from emit_main.workflow.workflow_manager import WorkflowManager


def initialize_ummg(granule_name: str, creation_time: datetime, collection_name: str, collection_version: str,
                    start_time: datetime, stop_time: datetime, pge_name: str, pge_version: str,
                    l4_software_delivery_version: str = None, doi: str = None,
                    esm: str = None, resolution: str = None, in_mineralogy: str = None,
                    ext_meteorology: str = None, time_period: str = None, scenario: str = None):
    """ Initialize a UMMG metadata output file
    Args:
        granule_name: granule UR tag
        creation_time: creation timestamp
        collection_name: short name of collection reference
        collection_version: collection version
        l4_software_delivery_version: version of software build
        pge_name: PGE name  from build configuration
        pge_version: PGE version from build configuration

    Returns:
        dictionary representation of ummg
    """

    ummg = {"ProviderDates": []}
    ummg['MetadataSpecification'] = {'URL': 'https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5', 'Name': 'UMM-G',
                                     'Version': '1.6.5'}

    ummg['Platforms'] = [{'ShortName': 'ISS', 'Instruments': [{'ShortName': 'EMIT Imaging Spectrometer'}]}]
    ummg['GranuleUR'] = granule_name

    ummg['TemporalExtent'] = {
        'RangeDateTime': {
            'BeginningDateTime': start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'EndingDateTime': stop_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

    # Use ProviderDate type "Update" per DAAC. Use this for data granule ProductionDateTime field too.
    ummg['ProviderDates'].append({'Date': creation_time.strftime("%Y-%m-%dT%H:%M:%SZ"), 'Type': "Update"})
    ummg['CollectionReference'] = {
        "ShortName": collection_name,
        "Version": str(collection_version)
    }

    # First attribute is required and others may be optional
    ummg['AdditionalAttributes'] = []
    if l4_software_delivery_version is not None:
        ummg['AdditionalAttributes'].append(
            {'Name': 'SOFTWARE_DELIVERY_VERSION', 'Values': [str(l4_software_delivery_version)]})
    if doi is not None:
        ummg['AdditionalAttributes'].append({'Name': 'Identifier_product_doi_authority', 'Values': ["https://doi.org"]})
        ummg['AdditionalAttributes'].append({'Name': 'Identifier_product_doi', 'Values': [str(doi)]})
    if esm is not None:
        ummg['AdditionalAttributes'].append({'Name': 'EARTH_SYSTEM_MODEL', 'Values': [str(esm)]})
    if resolution is not None:
        r = resolution.split("-")
        ummg['AdditionalAttributes'].append({'Name': 'RESOLUTION_LATITUDE', 'Values': [f"{r[0]:.1f}"]})
        ummg['AdditionalAttributes'].append({'Name': 'RESOLUTION_LONGITUDE', 'Values': [f"{r[1]:.1f}"]})
        ummg['AdditionalAttributes'].append({'Name': 'RESOLUTION_LEVEL', 'Values': [f"{r[2]:.1f}"]})
    if in_mineralogy is not None:
        ummg['AdditionalAttributes'].append({'Name': 'INPUT_MINERALOGY', 'Values': [str(in_mineralogy)]})
    if ext_meteorology is not None:
        ummg['AdditionalAttributes'].append({'Name': 'EXTERNAL_METEOROLOGY', 'Values': [str(ext_meteorology)]})
    if time_period is not None:
        t = time_period.split("-")
        ummg['AdditionalAttributes'].append({'Name': 'START_YEAR', 'Values': [str(t[0])]})
        ummg['AdditionalAttributes'].append({'Name': 'END_YEAR', 'Values': [str(t[1])]})
    if scenario is not None:
        ummg['AdditionalAttributes'].append({'Name': 'EMISSION_CONCENTRATION_SCENARIO', 'Values': [str(scenario)]})

    # TODO: Keep?
    ummg['PGEVersionClass'] = {'PGEName': pge_name, 'PGEVersion': pge_version}

    return ummg


def calc_checksum(path, hash_alg="sha512"):
    checksum = {}
    if hash_alg.lower() == "sha512":
        h = hashlib.sha512()
    with open(path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            h.update(byte_block)
    return h.hexdigest()


def add_data_files_ummg(ummg: dict, paths: list, daynight: str):
    """
    Add boundary points list to UMMG in correct format
    Args:
        ummg: existing UMMG to augment
        paths: list of paths to existing data files to add

    Returns:
        dictionary representation of ummg with new data granule
    """

    prod_datetime_str = None
    for subdict in ummg['ProviderDates']:
        if subdict['Type'] == 'Update':
            prod_datetime_str = subdict['Date']
            break

    archive_info = []
    for path in paths:
        fileformat = "PNG" if path.endswith(".png") else "NETCDF-4"
        archive_info.append({
                             "Name": os.path.basename(path),
                             "SizeInBytes": os.path.getsize(path),
                             "Format": fileformat,
                             "Checksum": {
                                 'Value': calc_checksum(path),
                                 'Algorithm': 'SHA-512'
                                 }
                            })

    ummg['DataGranule'] = {
        'DayNightFlag': daynight,
        'ArchiveAndDistributionInformation': archive_info
    }

    if prod_datetime_str is not None:
        ummg['DataGranule']['ProductionDateTime'] = prod_datetime_str

    return ummg


class SerialEncoder(json.JSONEncoder):
    """Encoder for json to help ensure json objects can be passed to the workflow manager.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return super(SerialEncoder, self).default(obj)


def stage_files(wm, paths):
    # Copy files to staging server
    daac_partial_dir = os.path.join(wm.config["daac_base_dir"], wm.config['environment'], "partial_transfers")
    partial_dir_arg = f"--partial-dir={daac_partial_dir}"
    daac_staging_dir = os.path.join(wm.config["daac_base_dir"], wm.config['environment'], "products", "l4")
    target = f"{wm.config['daac_server_internal']}:{daac_staging_dir}/"
    group = f"emit-{wm.config['environment']}" if wm.config["environment"] in ("test", "ops") else "emit-dev"
    # This command only makes the directory and changes ownership if the directory doesn't exist
    cmd_make_target = ["ssh", wm.config["daac_server_internal"], "\"if", "[", "!", "-d",
                       f"'{daac_staging_dir}'", "];", "then", "mkdir", f"{daac_staging_dir};", "chgrp",
                       group, f"{daac_staging_dir};", "fi\""]
    # print(f"cmd_make_target: {' '.join(cmd_make_target)}")
    output = subprocess.run(" ".join(cmd_make_target), shell=True, capture_output=True)
    if output.returncode != 0:
        raise RuntimeError(output.stderr.decode("utf-8"))

    # files is a list of local paths
    for p in paths:
        cmd_rsync = ["rsync", "-av", partial_dir_arg, p, target + os.path.basename(p)]
        # print(f"rsync cmd: {' '.join(cmd_rsync)}")
        output = subprocess.run(" ".join(cmd_rsync), shell=True, capture_output=True)
        if output.returncode != 0:
            raise RuntimeError(output.stderr.decode("utf-8"))


def submit_cnm_notification(wm, granule_ur, paths, collection, collection_version):
    # Build notification dictionary
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    cnm_submission_id = f"{granule_ur}_{utc_now.strftime('%Y%m%dt%H%M%S')}"
    cnm_submission_path = cnm_submission_id + "_cnm.json"
    # TODO: Use S3 provider?
    provider = wm.config["daac_provider_forward"]
    queue_url = wm.config["daac_submission_url_forward"]

    notification = {
        "collection": collection,
        "provider": provider,
        "identifier": cnm_submission_id,
        "version": wm.config["cnm_version"],
        "product": {
            "name": granule_ur,
            "dataVersion": collection_version,
            "files": []
        }
    }

    daac_uri_base = f"https://{wm.config['daac_server_external']}/emit/lpdaac/{wm.config['environment']}/products/l4/"
    for i, p in enumerate(paths):
        # ["data", "browse", "metadata"]
        format = "data"
        if p.endswith(".png"):
            format = "browse"
        if p.endswith(".cmr.json"):
            format = "metadata"
        notification["product"]["files"].append(
            {
                "name": os.path.basename(p),
                "uri": daac_uri_base + os.path.basename(p),
                "type": format,
                "size": os.path.getsize(p),
                "checksumType": "sha512",
                "checksum": calc_checksum(p, "sha512")
            }
        )

    # Write notification submission to file
    print(f"Writing CNM notification file to {cnm_submission_path}")
    with open(cnm_submission_path, "w") as p:
        p.write(json.dumps(notification, indent=4))
    wm.change_group_ownership(cnm_submission_path)

    # Submit notification via AWS SQS
    print(f"Submitting CNM notification via AWS SQS")
    cnm_submission_output = cnm_submission_path.replace(".json", ".out")
    cmd_aws = [wm.config["aws_cli_exe"], "sqs", "send-message", "--queue-url", queue_url, "--message-body",
               f"file://{cnm_submission_path}", "--profile", wm.config["aws_profile"], ">", cnm_submission_output]
    # print(f"cmd_aws: {' '.join(cmd_aws)}")
    output = subprocess.run(" ".join(cmd_aws), shell=True, capture_output=True)
    if output.returncode != 0:
        raise RuntimeError(output.stderr.decode("utf-8"))


def main():
    # Set up args
    parser = argparse.ArgumentParser(description="Deliver L4 products to LP DAAC")
    parser.add_argument("path", help="The path to the directory of the granule to be delivered.")
    parser.add_argument("--env", default="ops", help="The operating environment - dev, test, ops")
    parser.add_argument("--collection_version", default="001", help="The DAAC collection version")
    args = parser.parse_args()

    # Get workflow manager and ghg config options
    sds_config_path = f"/store/emit/{args.env}/repos/emit-main/emit_main/config/{args.env}_sds_config.json"

    # Get the current emit-sds-l4 version
    cmd = ["git", "symbolic-ref", "-q", "--short", "HEAD", "||", "git", "describe", "--tags", "--exact-match"]
    output = subprocess.run(" ".join(cmd), shell=True, capture_output=True)
    if output.returncode != 0:
        raise RuntimeError(output.stderr.decode("utf-8"))
    repo_version = output.stdout.decode("utf-8").replace("\n", "")

    # TODO: If collection version and DOI don't go hand in hand then adjust dois below
    l4_config = {
        "collection_version": args.collection_version,
        "repo_name": "emit-sds-l4",
        "repo_version": repo_version,
        "doi": "EMITL4ESM"
    }

    print(f"Using sds_config_path: {sds_config_path}")
    print(f"Using l4_config: {l4_config}")
    print(f"Publishing granule at path: {args.path}")

    # Example granule_ur: EMIT_L4_ESM_001_CESM_1.0-1.0-05_EMIT001-B_MER_2007-2011_SSP2-4.5
    # See https://github.com/emit-sds/emit-sds-l4/blob/main/README.md for description of fields
    collection = "EMITL4ESM"
    granule_ur = os.path.basename(args.path)
    tokens = granule_ur.split("_")
    esm = tokens[4]
    resolution = tokens[5]
    in_mineralogy = tokens[6]
    ext_meteorology = tokens[7]
    time_period = tokens[8]
    scenario = tokens[9]

    nc_paths = glob.glob(os.path.join(args.path, f"{granule_ur}*nc"))
    browse_path = os.path.join(args.path, f"{granule_ur}.png")
    ummg_path = os.path.join(args.path, f"{granule_ur}.cmr.json")
    # paths = nc_paths + [browse_path] + [ummg_path]
    paths = nc_paths + [ummg_path]

    print(f"paths: {paths}")

    # Create the UMM-G file
    print(f"Creating ummg file at {ummg_path}")
    creation_times = []
    for p in nc_paths:
        creation_times.append(datetime.datetime.fromtimestamp(os.path.getmtime(p), tz=datetime.timezone.utc))
    daynight = "Day"
    # Start/stop times are in UTC - formatting is handled during UMM-G creation
    start_time = datetime.datetime(2022, 8, 10, 0, 0, 0)
    stop_time = datetime.datetime(2023, 11, 30, 0, 0, 0)
    ummg = initialize_ummg(granule_ur, min(creation_times), collection, l4_config["collection_version"],
                           start_time, stop_time, l4_config["repo_name"], l4_config["repo_version"],
                           l4_software_delivery_version=l4_config["repo_version"],
                           doi=l4_config["doi"], esm=esm, resolution=resolution,
                           in_mineralogy=in_mineralogy, ext_meteorology=ext_meteorology,
                           time_period=time_period, scenario=scenario)
    ummg = add_data_files_ummg(ummg, paths[:-1], daynight)

    # ummg = add_boundary_ummg(ummg, acq.gring)
    # TODO: Update?
    ummg["SpatialExtent"] = {
        "HorizontalSpatialDomain": {
            "Geometry": {
                "BoundingRectangles": [
                    {
                        "WestBoundingCoordinate": -180,
                        "NorthBoundingCoordinate": 55,
                        "EastBoundingCoordinate": 180,
                        "SouthBoundingCoordinate": -55
                    }
                ]
            }
        }
    }

    with open(ummg_path, 'w', errors='ignore') as fout:
        fout.write(json.dumps(ummg, indent=2, sort_keys=False, cls=SerialEncoder))

    # Copy files to staging server
    wm = WorkflowManager(config_path=sds_config_path)
    # print(f"Staging files to web server")
    # stage_files(wm, paths)

    # Build and submit CNM notification
    # submit_cnm_notification(wm, granule_ur, paths, collection, l4_config["collection_version"])


if __name__ == '__main__':
    main()
