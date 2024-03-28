#!/bin/bash
set -e

psql -d $DB_NAME -U $DB_USER -f /etc/postgresql/partition_manually.sql