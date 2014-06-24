#!/bin/bash

#   Ryan Faulkner, 2014
#   bobs.ur.uncle@gmail.com
#
#   Installer for mysql

apt-get install -y mysql-server
apt-get install -y mysql-client

# Setup admin
mysqladmin -u root -h localhost password '$MYSQL_ROOT_PASS'
# mysqladmin -u root -h {%hostname%} password '{%mysql_password%}'