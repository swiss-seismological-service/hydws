#!/bin/bash
set -e

set -a
. .env
set +a

psql -d $DB_NAME -U $DB_USER --host $POSTGRES_HOST  -f $(pwd)/db/partition.sql
psql -d $DB_NAME -U $DB_USER --host $POSTGRES_HOST  -c "CREATE OR REPLACE TRIGGER partition_daily_function
                                                        BEFORE INSERT
                                                        ON hydraulicsample
                                                        FOR EACH ROW
                                                        WHEN (pg_trigger_depth() < 1)
                                                        EXECUTE FUNCTION partition_daily_function($DB_USER);"