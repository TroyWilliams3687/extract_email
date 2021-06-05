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

import logging
import csv

from pathlib import Path
from email import message_from_string
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# ------------
# 3rd Party - From pip

import click

from appdirs import AppDirs
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

__appname__ = "extract_email"
__company__ = "bluebill.net"


def cache_path():
    """
    The paths that the application will commonly use for storing settings
    and caching things.

    """

    dirs = AppDirs()

    cache_path = Path(dirs.user_config_dir).joinpath(__company__).joinpath(__appname__)
    cache_path.mkdir(parents=True, exist_ok=True)

    return cache_path

def process_email(**kwargs):
    """
    """

    search = Path(kwargs['search'])

    links = {}
    total_urls = 0

    for f in search.rglob("*.eml"):
        click.echo(f'Processing {f.name}...')

        msg = message_from_string(f.read_text())

        # msg.get_content_type() can be one of two types we are interested in:
        # text/plain
        # text/html

        contents = [p.get_payload(decode=True) for p in msg.get_payload()] if msg.is_multipart() else [msg.get_payload(decode=True)]

        for body in contents:

            parser = 'html.parser'  # 'html.parser' or 'lxml' (preferred) or 'html5lib', if installed
            for l in BeautifulSoup(body, parser, parse_only=SoupStrainer('a')):

                # We only want anchor tags with actual href attributes and text
                if l.has_attr('href') and l.string is not None and len(l.string) > 0:

                    total_urls += 1

                    if l['href'] not in links:
                        links[l['href']] = l.string

                    else:

                        if links[l['href']] != l.string:
                            click.echo(f"WARNING - {l['href']} exists, but has different string!")

    return links, total_urls

def filter_links(links, **kwargs):
    """
    """

    filtered_links = {}

    for url, v in links.items():
        parsed = urlparse(url)

        if parsed.netloc in ['scholar.google.com', 'scholar.google.ca']:

            # At this point for google scholar, we are only
            # interested in the links

            if parsed.path not in ['/scholar_url' ]:
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

        elif parsed.netloc == 'www.researchgate.net':

            if parsed.path in [
                '/help/whitelist-email',
                '/go.Out.publicationAdded.html',
                '/privacy-policy',
                '/terms-of-service',
                '/go.Out.followedProjectUpdatesNotification.html'
                '/imprint',
                '//',
                '/imprint',
                '/browse.BrowseSuggestResearcher.html',
                '/go.Out.followMe.html',
                '/profile/Troy-Williams/experience',
                '/profile/Troy-Williams/experience',
                '/profile.ProfilePrivacySettings.html',
                '/unsubscribe/mailingRgScoreStatsDigestEnabled',
            ]:
                continue

            filtered_links.setdefault(query_url_parsed.netloc, {})[url] = v

        else:

            # Not Google Scholars
            filtered_links.setdefault('NOT HANDLED', {})[url] = v

    return filtered_links

def display_filtered_links(filtered_links, **kwargs):
    """
    """

    for k, v in filtered_links.items():
        click.echo(f'{k:<28} {len(v):>3}')

    click.echo('---------')

    if kwargs['verbose']:
        click.echo()
        for k, v in filtered_links.items():
            click.echo(f'{k:<28}')

            for url, title in v.items():
                click.echo(f'- `{title}` -> {url}')

            click.echo()

def links_to_csv(links, **kwargs):
    """
    """
    output = cache_path().joinpath(f'{datetime.now().isoformat(timespec="minutes")}.csv')

    with output.open("w", encoding="utf-8") as fo:

        writer = csv.DictWriter(fo, fieldnames=['title', 'url'])
        writer.writeheader()

        for k, v in links.items():
            for url, title in v.items():
                writer.writerow({'title': title, 'url': url})

    return output



@click.command()
@click.version_option()
@click.argument('search', type=click.Path(exists=True))
@click.option(
    "--launch-pdf", is_flag=True, help="Launch the PDF URLs in the browser."
)
@click.option(
    "--verbose", is_flag=True, help="Launch the URLs in the browser."
)
@click.option(
    "--launch-csv", is_flag=True, help="Launch the URLs in your default CSV viewer."
)
@click.pass_context
def main(*args, **kwargs):
    """

    Extract URL links from .eml messages and present the results deduplicated

    Optionally, it should be able to launch them in the browser

    # Usage

    $ extract "/home/troy/tmp/extract tbird email" --verbose --launch-pdf
    $ extract "/home/troy/tmp/extract tbird email" --verbose --launch-csv


    Reference:

    - https://docs.python.org/3/library/email.message.html
    - https://docs.python.org/3/library/email.parser.html
    - https://docs.python.org/3/library/email.html

    """

    links, total_urls = process_email(**kwargs)

    click.echo()
    click.echo('--------')
    click.echo(f'Unique URLS: {len(links)}...')
    click.echo(f'Total URLS:  {total_urls}...')

    if not links:
        return


    filtered_links = filter_links(links, **kwargs)

    # We shouldn't have any 'NOT HANDLED' links, they should be
    # filtered
    if 'NOT HANDLED' in filtered_links:

        for url, v in filtered_links["NOT HANDLED"].items():
            click.echo(f'NOT HANDLED - `{v}` - {url}')

        # raise KeyError('Other links were detected in the list - these were not handled!')

    display_filtered_links(filtered_links, **kwargs)

    # At this point we have a list of URLS filtered by domain, let's
    # see if we have any pdf links

    pdf_list = {url:title for k,v in filtered_links.items() for url, title in v.items() if url.lower().endswith(".pdf")}

    click.echo(f'Direct PDF Links: {len(pdf_list)}')
    for url, title in pdf_list.items():
        click.echo(f'- `{title}` -> {url}')

    # Also have a list of domains that typically provide pdfs but not in the links

    # Launch PDF?
    if kwargs['launch_pdf']:
        for url, title in pdf_list.items():
            click.echo(f'Launching {url}')
            click.launch(url)

    # Launch CSV?
    if kwargs['launch_csv']:
        csv_file = links_to_csv(filtered_links, **kwargs)
        click.echo(f'Launching {csv_file}...')
        click.launch(str(csv_file))


