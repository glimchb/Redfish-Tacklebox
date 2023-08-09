#! /usr/bin/python
# Copyright Notice:
# Copyright 2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Virtual Media

File : rf_virtual_media.py

Brief : This script uses the redfish_utilities module to manage virtual media
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
argget = argparse.ArgumentParser( description = "A tool to manage virtual media of a system" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--system", "-s", type = str, help = "The ID of the system containing the virtual media" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
subparsers = argget.add_subparsers( dest = "command" )
info_argget = subparsers.add_parser( "info", help = "Displays information about the virtual media for a system" )
insert_argget = subparsers.add_parser( "insert", help = "Inserts virtual media for a system" )
insert_argget.add_argument( "--image", "-image", type = str, required = True, help = "The URI of the image to insert" )
insert_argget.add_argument( "--id", "-i", type = str, help = "The identifier of the virtual media instance to insert" )
insert_argget.add_argument( "--notinserted", "-notinserted", action = "store_false", help = "Indicates if the media is to be marked as not inserted for the system", default = None )
insert_argget.add_argument( "--writable", "-writable", action = "store_false", help = "Indicates if the media is to be marked as writable for the system", default = None )
insert_argget.add_argument( "--mediatypes", "-mt", type = str, nargs = '+', help = "A list of acceptable media types for the virtual media" )
eject_argget = subparsers.add_parser( "eject", help = "Ejects virtual media from a system" )
eject_argget.add_argument( "--id", "-i", type = str, required = True, help = "The identifier of the virtual media instance to eject" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_virtual_media-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_virtual_media Trace" )

# Set up the Redfish object
redfish_obj = None
try:
    redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password , timeout=5, max_retry=3)
    redfish_obj.login( auth = "session" )
except RedfishPasswordChangeRequiredError as e:
    redfish_utilities.print_password_change_required_and_logout(redfish_obj, args)
    sys.exit(1)
except Exception as e:
    # other error
    error_string = str(e)
    if len(error_string) > 0:
        print("{}\nLogin Failed\n".format(error_string))
    else:
        print("Login Failed\n")
    redfish_utilities.logout(redfish_obj, print_error = False)
    sys.exit(1)

exit_code = 0
try:
    if args.command == "insert":
        print( "Inserting '{}'".format( args.image ) )
        redfish_utilities.insert_virtual_media( redfish_obj, args.image, args.system, args.id, args.mediatypes, args.notinserted, args.writable )
    elif args.command == "eject":
        print( "Ejecting '{}'".format( args.id ) )
        redfish_utilities.eject_virtual_media (redfish_obj, args.id, args.system )
    else:
        virtual_media = redfish_utilities.get_virtual_media( redfish_obj, args.system )
        redfish_utilities.print_virtual_media( virtual_media )
except Exception as e:
    if args.debug:
        logger.error( "Caught exception:\n\n{}\n".format( traceback.format_exc() ) )
    exit_code = 1
    print( e )
finally:
    # Log out
    redfish_utilities.logout(redfish_obj, print_error = True)

sys.exit( exit_code )
