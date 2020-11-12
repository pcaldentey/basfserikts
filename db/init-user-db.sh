#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SEQUENCE serial_patent;
    CREATE TABLE patent (
        id        integer PRIMARY KEY DEFAULT nextval('serial_patent'),
        title   varchar(1024) NOT NULL,
        doc_number   varchar(32) NOT NULL,
        application_year  integer,
        abstract text NOT NULL,
        description text NOT NULL,
        named_entities text[]
    );
EOSQL
