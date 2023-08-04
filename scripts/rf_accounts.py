#! /usr/bin/python
# Copyright Notice:
# Copyright 2019-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Tacklebox/blob/main/LICENSE.md

"""
Redfish Accounts

File : rf_accounts.py

Brief : This script uses the redfish_utilities module to manage user accounts
"""

import argparse
import datetime
import logging
import redfish
import redfish_utilities
import traceback
import sys
from redfish.messages import RedfishPasswordChangeRequiredError

def print_password_change_required_and_logout(redfish_obj, args):
    print("Password change required\n run rf_accounts.py -r {} -u {} -p <old password> --setpassword {} <new password> \nto set your password\n".format(args.rhost ,args.user, args.user))
    try:
        redfish_obj.logout()
    except Exception as e:
        pass
    sys.exit(1)

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool to manage user accounts on a Redfish service" )
argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The address of the Redfish service (with scheme)" )
argget.add_argument( "--add", "-add", type = str, nargs = 3, metavar = ( "name", "password", "role" ), help = "Adds a new user account" )
argget.add_argument( "--delete", "-delete", type = str, help = "Deletes a user account with the given name" )
argget.add_argument( "--setname", "-setname", type = str, nargs = 2, metavar = ( "old_name", "new_name" ) , help = "Sets a user account to a new name" )
argget.add_argument( "--setpassword", "-setpassword", type = str, nargs = 2, metavar = ( "name", "new_password" ), help = "Sets a user account to a new password" )
argget.add_argument( "--setrole", "-setrole", type = str, nargs = 2, metavar = ( "name", "new_role" ), help = "Sets a user account to a new role" )
argget.add_argument( "--enable", "-enable", type = str, help = "Enables a user account with the given name" )
argget.add_argument( "--disable", "-disable", type = str, help = "Disabled a user account with the given name" )
argget.add_argument( "--unlock", "-unlock", type = str, help = "Unlocks a user account with the given name" )
argget.add_argument( "--debug", action = "store_true", help = "Creates debug file showing HTTP traces and exceptions" )
args = argget.parse_args()

if args.debug:
    log_file = "rf_accounts-{}.log".format( datetime.datetime.now().strftime( "%Y-%m-%d-%H%M%S" ) )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = redfish.redfish_logger( log_file, log_format, logging.DEBUG )
    logger.info( "rf_accounts Trace" )

# Set up the Redfish object
try:
    redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password , timeout=5, max_retry=3)
    redfish_obj.login( auth = "session" )
except RedfishPasswordChangeRequiredError as e:
    if args.setpassword is None:
        print_password_change_required_and_logout(redfish_obj, args)
        sys.exit(1)
    else:
        if args.setpassword[0] == args.user:
            pass
        else:
            print_password_change_required_and_logout(redfish_obj, args)
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

try:
    redfish_obj
except Exception as e:
    print("Login Failed\n")
    sys.exit(1)

exit_code = 0
try:
    print_accounts = True
    if args.add is not None:
        print( "Adding new user '{}'".format( args.add[0] ) )
        redfish_utilities.add_user( redfish_obj, args.add[0], args.add[1], args.add[2] )
        print_accounts = False
    if args.delete is not None:
        print( "Deleting user '{}'".format( args.delete ) )
        redfish_utilities.delete_user( redfish_obj, args.delete )
        print_accounts = False
    if args.setname is not None:
        print( "Changing name of user '{}' to '{}'".format( args.setname[0], args.setname[1] ) )
        redfish_utilities.modify_user( redfish_obj, args.setname[0], new_name = args.setname[1] )
        print_accounts = False
    if args.setpassword is not None:
        print( "Changing password of user '{}'".format( args.setpassword[0] ) )
        redfish_utilities.modify_user( redfish_obj, args.setpassword[0], new_password = args.setpassword[1] )
        print_accounts = False
    if args.setrole is not None:
        print( "Changing role of user '{}' to '{}'".format( args.setrole[0], args.setrole[1] ) )
        redfish_utilities.modify_user( redfish_obj, args.setrole[0], new_role = args.setrole[1] )
        print_accounts = False
    if args.enable is not None:
        print( "Enabling user '{}'".format( args.enable ) )
        redfish_utilities.modify_user( redfish_obj, args.enable, new_enabled = True )
        print_accounts = False
    if args.disable is not None:
        print( "Disabling user '{}'".format( args.disable ) )
        redfish_utilities.modify_user( redfish_obj, args.disable, new_enabled = False )
        print_accounts = False
    if args.unlock is not None:
        print( "Unlocking user '{}'".format( args.unlock ) )
        redfish_utilities.modify_user( redfish_obj, args.unlock, new_locked = False )
        print_accounts = False
    if print_accounts:
        user_list = redfish_utilities.get_users( redfish_obj )
        redfish_utilities.print_users( user_list )
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
