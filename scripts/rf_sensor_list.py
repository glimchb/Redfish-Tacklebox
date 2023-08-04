#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Sensor List

File : rf_sensor_list.py

Brief : This script uses the redfish_utilities module to dump sensor info
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback
import sys
from redfish.messages import RedfishPasswordChangeRequiredError

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to walk a Redfish service and list sensor info" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_sensor_list-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_sensor_list Trace" )

# Set up the Redfish object
try:
    redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password , timeout=5, max_retry=3)
    redfish_obj.login( auth = "session" )
except RedfishPasswordChangeRequiredError as e:
    print("Password change required\n run rf_accounts.py -r {} -u {} -p <old password> --setpassword {} <new password> \nto set your password\n".format(args.rhost ,args.user, args.user))
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
    sys.exit(1)
except Exception as e:
    # other error
    error_string = str(e)
    if len(error_string) > 0:
        print("{}\nLogin Failed\n".format(error_string))
    else:
        print("Login Failed\n")
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
    sys.exit(1)

exit_code = 0
try:
    # Get and print the sensor info
    sensors = redfish_utilities.get_sensors( redfish_obj )
    redfish_utilities.print_sensors( sensors )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    try:
        redfish_obj.logout()
    except Exception as e:
        pass

sys.exit( exit_code )
