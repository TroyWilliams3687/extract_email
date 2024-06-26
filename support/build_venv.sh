#!/usr/bin/env bash

# ----
# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Troy Williams
# ----


# This script needs to be in a sub-directory, one level down from the location
# of the virtual environment folder. In other words, call the script from the
# folder where you want the virtual environment created.


# Exit bash when exception occurs
set -o errexit

# Raise exception if variable is not set
set -o nounset

# Raise exception of any part of a pipe operation fails
set -o pipefail

#----
# Display the current working directory for reference

echo "CWD = ${PWD}"

echo "Script = ${0}"
SCRIPT_PATH="$(dirname -- "${0}")"
echo "Script Path = ${SCRIPT_PATH}"

#----
# The path to the python binary.

# We assume the file containing the information is located in the same folder as
# the script and is called `path.ini`

CFG="${SCRIPT_PATH}/path.ini"

# Extract the line containing `PYTHON` and extract the quoted text

PYTHON="$(grep PYTHON ${CFG} | cut -d'"' -f 2)"
echo "Python Binary = ${PYTHON}"
echo "----"

# ----
# Virtual Environment

echo "Creating Environment..."

"$PYTHON" -m venv --clear --upgrade-deps .venv

# `python -m venv --clear --upgrade-deps .venv`
# - `--clear` switch empties the folder out first - no need to delete in another step
# - `--upgrade-deps` - upgrade pip & setuptools to latest version
# - https://docs.python.org/3/library/venv.html

# ----
# Install Requirements

VPYTHON=".venv/bin/python"

echo "Installing Requirements..."

for requirements in ./*requirements.txt; do
    "$VPYTHON" -m pip install --upgrade -r "${requirements}"
done

# Is the repo representing a package?
PACKAGE=setup.cfg
if [ -f "$PACKAGE" ]; then
    echo "$PACKAGE exists. This repository can be installed."
    $VPYTHON -m pip install -e .
else
    echo "$PACKAGE does not exist. This repository does not contain a package and cannot be installed."
fi


# ----

echo "----"
echo "Installation and Configuration complete."
echo ""
