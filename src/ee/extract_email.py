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
from email import message_from_string

# ------------
# 3rd Party - From pip

import click
import requests

from bs4 import BeautifulSoup, SoupStrainer


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
@click.option(
    "--verbose", is_flag=True, help="Launch the URLs in the browser."
)
@click.pass_context
def main(*args, **kwargs):
    """

    Extract URL links from .eml messages and present the results deduplicated

    Optionally, it should be able to launch them in the browser

    # Usage

    $ extract --verbose --launch "/home/troy/tmp/extract tbird email"

    Reference:

    - https://docs.python.org/3/library/email.message.html
    - https://docs.python.org/3/library/email.parser.html
    - https://docs.python.org/3/library/email.html

    """

    # Store the links mapped to the link description
    links = {}

    search = Path(kwargs['search'])

    for f in search.rglob("*.eml"):

        if kwargs['verbose']:
            click.echo(f'Processing {f.name}...')

        msg = message_from_string(f.read_text())

        # >>> click.echo(msg.keys())
        # ['Delivered-To', 'Received', 'X-Received', 'ARC-Seal', 'ARC-Message-Signature', 'ARC-Authentication-Results', 'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results', 'DKIM-Signature', 'X-Google-DKIM-Signature', 'X-Gm-Message-State', 'X-Google-Smtp-Source', 'MIME-Version', 'X-Received', 'Date', 'Message-ID', 'Subject', 'From', 'To', 'Content-Type', 'Content-Transfer-Encoding']

        # click.echo(f'{msg.get_content_type()=}')
        # click.echo(f'{msg.get_content_maintype()=}')
        # click.echo(f'{msg.get_content_subtype()=}')
        # click.echo(f'{msg.get_default_type()=}')
        # click.echo(f'{msg.is_multipart()=}')

        # msg.get_content_type()='text/html'
        # msg.get_content_maintype()='text'
        # msg.get_content_subtype()='html'
        # msg.get_default_type()='text/plain'
        # msg.is_multipart()=False

        # msg.get_content_type() can be one of two types we are interested in:
        # text/plain
        # text/html

        if msg.is_multipart():

            # https://stackoverflow.com/questions/17874360/python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not
            # if b.is_multipart():
            #     for payload in b.get_payload():
            #         # if payload.is_multipart(): ...
            #         print payload.get_payload()
            # else:
            #     print b.get_payload()

            raise NotImplementedError("Handling multipart messages is not implemented!")

        else:

            if msg.get_content_type() == 'text/html':

                body = msg.get_payload(decode=True)

                parser = 'html.parser'  # 'html.parser' or 'lxml' (preferred) or 'html5lib', if installed
                for l in BeautifulSoup(body, parser, parse_only=SoupStrainer('a')):

                    # We only want anchor tags with actual href attributes and text
                    if l.has_attr('href') and l.string is not None and len(l.string) > 0:

                        if l['href'] not in links:
                            links[l['href']] = l.string

                        else:
                            if kwargs['verbose']:
                                click.echo('Duplicate URL...')

                            if links[l['href']] != l.string:

                                if not kwargs['verbose']:
                                    click.echo(f'Processing {f.name}...')

                                click.echo(f"WARNING - {l['href']} exists, but has different string!")

            elif msg.get_content_type() == 'text/plain':

                raise NotImplementedError("Handling `text/plain` messages is not implemented!")

            else:

                raise ValueError(f'{msg.get_content_type()} type messages not supported.')


    if links:

        click.echo()
        click.echo('--------')
        click.echo(f'Found {len(links)}...')
        # for url,v in links.items():
        #     click.echo(f'{v}; {url}')


        if kwargs['launch']:
            click.echo('Launching...')
            for k,v in links.items():
                click.echo(f'Launching {v}...')
                click.launch(k)
