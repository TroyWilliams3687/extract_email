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
from urllib.parse import urlparse, parse_qs

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
    "--launch-pdf", is_flag=True, help="Launch the URLs in the browser."
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

    $ extract "/home/troy/tmp/extract tbird email" --verbose --launch-pdf

    Reference:

    - https://docs.python.org/3/library/email.message.html
    - https://docs.python.org/3/library/email.parser.html
    - https://docs.python.org/3/library/email.html

    """

    # Store the links mapped to the link description
    links = {}
    total_urls = 0

    search = Path(kwargs['search'])

    for f in search.rglob("*.eml"):
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

                        total_urls += 1

                        if l['href'] not in links:
                            links[l['href']] = l.string

                        else:
                            # if kwargs['verbose']:
                            #     click.echo('Duplicate URL...')

                            if links[l['href']] != l.string:
                                click.echo(f"WARNING - {l['href']} exists, but has different string!")

            elif msg.get_content_type() == 'text/plain':

                raise NotImplementedError("Handling `text/plain` messages is not implemented!")

            else:

                raise ValueError(f'{msg.get_content_type()} type messages not supported.')

    if links:

        click.echo()
        click.echo('--------')
        click.echo(f'Unique URLS: {len(links)}...')
        click.echo(f'Total URLS:  {total_urls}...')


        filtered_links = {}

        for url, v in links.items():
            parsed = urlparse(url)

            if parsed.netloc in ['scholar.google.com', 'scholar.google.ca']:

                # At this point for google scholar, we are only
                # interested in the links

                if parsed.path not in ['/scholar_url' ]:

                    # if kwargs['verbose']:
                    #     click.echo('Skipping non-url links...')
                    continue

                # Process the query and attemp to extract the link url
                pq = parse_qs(parsed.query)

                # There should only be 1, otherwise raise an error and
                # make a modification
                if len(pq['url']) != 1:
                    raise ValueError(f'INVALID URL in QUERY - {parsed}...')

                for query_url in pq['url']:
                    query_url_parsed = urlparse(query_url)
                    filtered_links.setdefault(query_url_parsed.netloc, {})[query_url] = v

            else:
                # Not Google Scholars
                filtered_links.setdefault('NOT HANDLED', {})[url] = v


        # We shouldn't have any 'NOT HANDLED' links, they should be
        # filtered
        if 'NOT HANDLED' in filtered_links:

            for url, v in filtered_links["NOT HANDLED"].items():
                click.echo(f'NOT HANDLED - `{v}` - {url}')

            raise KeyError('Other links were detected in the list - these were not handled!')

        for k, v in filtered_links.items():
            click.echo(f'{k:<28} {len(v):>3}')

            if kwargs['verbose']:
                for url, title in v.items():
                    click.echo(f'\t {title} -> {url}')

        if kwargs['verbose']:
            click.echo()
            for k, v in filtered_links.items():
                click.echo(f'{k:<28}')

                for url, title in v.items():
                    click.echo(f'- `{title}` -> {url}')

                click.echo()

        # At this point we have a list of URLS filtered by domain, let's
        # see if we have any pdf links

        pdf_list = {url:title for k,v in filtered_links.items() for url, title in v.items() if url.lower().endswith(".pdf")}

        click.echo(f'Direct PDF Links: {len(pdf_list)}')
        for url, title in pdf_list.items():
            click.echo(f'- `{title}` -> {url}')

        # Also have a list of domains that typically provide pdfs but not in the links


        # Launch PDF

        if kwargs['launch_pdf']:
            for url, title in pdf_list.items():
                click.echo(f'Launching {url}')
                click.launch(url)


        # ---------
        # Sort the links by ones that point directly to pdf files


        # session = requests.Session()
        # session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

        # for url,v in links.items():

        #     r = session.get(url)

        #     for r in r.history:
        #         click.echo(r.url)

        #     click.echo(r.url)
        #     return

        # for url,v in links.items():
        #     click.echo(f'{v}; {url}')


        # if kwargs['launch']:
        #     click.echo('Launching...')
        #     for k,v in links.items():
        #         click.echo(f'Launching {v}...')
        #         click.launch(k)
