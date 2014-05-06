#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Creates RDBMS Tables via sqlalchemy interface

Ryan Faulkner 2014

"""

from flickipedia.mysqlio import DataIOMySQL


def main():
    io = DataIOMySQL()
    io.connect()

    io.create_table('User')
    io.create_table('Photo')
    io.create_table('Article')
    io.create_table('Like')


def cli():
    exit(main())


if __name__ == '__main__':
    cli()

