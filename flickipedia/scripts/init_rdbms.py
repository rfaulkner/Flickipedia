#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Creates RDBMS Tables via sqlalchemy interface

Ryan Faulkner 2014

"""

from flickipedia.mysqlio import DataIOMySQL
import argparse


def parseargs():
    """Parse command line arguments.

    Returns *args*, the list of arguments left over after processing.

    """
    parser = argparse.ArgumentParser(
        description="This script handle database initialization for the project.",
        epilog="",
        conflict_handler="resolve",
        usage="run.py [OPTS]"
              "\n\t[-q --quiet] \n\t[-s --silent] \n\t[-v --verbose]"
              "\n\t[-d --debug] \n\t[-r --reloader]"
    )

    parser.allow_interspersed_args = False


    # Global options.
    parser.add_argument("-d", "--drop",
                        action="store_true",
                        help="Run in flask debug mode.")

    args = parser.parse_args()
    return args

def main():

    # Parse cli args
    args = parseargs()

    io = DataIOMySQL()
    io.connect()

    if args.drop:
        io.drop_table('User')
        io.drop_table('Photo')
        io.drop_table('Article')
        io.drop_table('ArticleContent')
        io.drop_table('Like')
        io.drop_table('Exclude')
        io.drop_table('Upload')

    io.create_table('User')
    io.create_table('Photo')
    io.create_table('Article')
    io.create_table('ArticleContent')
    io.create_table('Like')
    io.create_table('Exclude')
    io.create_table('Upload')

def cli():
    exit(main())


if __name__ == '__main__':
    cli()

