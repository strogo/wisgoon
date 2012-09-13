#!/bin/sh
#
# ADDTOANY UPDATER
#
# This shell script caches the static content for the
# AddToAny Share/Save & Subscribe drop-down menus
# so that you can serve the menus 100% locally while still
# receiving important updates to the script, URI schemes, images, etc.
# www.addtoany.com
#
#
# HOW TO RUN:
# Once configured, set a cron job to run this once a day
# Example: 0 0 * * * addtoany_updater.sh
#
#
# CONFIGURATION:
# Set the path for the public AddToAny files
# The directory will be created if it doesn't exist




#
# SCRIPT BEGINS, NO NEED TO EDIT BELOW
#

THIS_SCRIPT_DIR=`pwd`

ADDTOANY_DIR=${THIS_SCRIPT_DIR}/feedreader/media/sharing

USER_AGENT=addtoany_updater

FILES_LIST_REMOTE=http://www.addtoany.com/ext/updater/files_list/

FILES_LIST_LOCAL=addtoany_files_list.txt

LOGFILE=addtoany_updater.log

# Remove temp directory if exists
rm -rf ${ADDTOANY_DIR}/temp

# Create and/or change to temp directory
mkdir -p ${ADDTOANY_DIR}/temp
cd ${ADDTOANY_DIR}/temp

# Get list of files to download from addtoany.com
wget $FILES_LIST_REMOTE --output-document=$FILES_LIST_LOCAL -U $USER_AGENT -q

# Download files in the list from addtoany.com, and log
wget --input-file=$FILES_LIST_LOCAL --output-file=${THIS_SCRIPT_DIR}/$LOGFILE -U $USER_AGENT

# Remove list
rm -f $FILES_LIST_LOCAL

# Copy all files from temp to ADDTOANY_DIR
cp -f -R ${ADDTOANY_DIR}/temp/* $ADDTOANY_DIR

# Remove temp directory
rm -rf ${ADDTOANY_DIR}/temp
