#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Troy Williams

# uuid:   5c7210ae-c605-11eb-8fdc-6b520513f9ef
# author: Troy Williams
# email:  troy.williams@bluebill.net
# date:   2021-06-05
# -----------

"""
This is a template python script for use in creating other classes and applying
a standard to them
"""

# ------------
# System Modules - Included with Python

import sys
import logging

from pathlib import Path

# ------------
# 3rd Party - From pip

import click

# ------------
# Custom Modules


# -------------
# Logging

# get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO) # change logging level here...

# make a console logger
console = logging.StreamHandler()

# add the console logger to the root logger
logger.addHandler(console)

# Assign the variable
log = logging.getLogger(__name__)
# -------------

@click.command()
@click.version_option()
@click.argument('search', type=click.Path(exists=True))
@click.option(
    "--launch", is_flag=True, help="Launch the URLs in the browser."
)
@click.pass_context
def main(*args, **kwargs):
    """

    Extract url links from .eml messages and present the results deduplicated

    Optionally, it should be able to launch them in the browser

    """


