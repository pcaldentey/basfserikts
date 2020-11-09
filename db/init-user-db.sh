#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SEQUENCE serial_patent;
    CREATE TABLE patent (
        id        integer PRIMARY KEY DEFAULT nextval('serial_patent'),
        title       varchar(80) NOT NULL,
        application_year   date,
        abstract text NOT NULL,
        description text NOT NULL
    );

    CREATE SEQUENCE serial_ne;
    CREATE TABLE named_entity (
        id    integer PRIMARY KEY DEFAULT nextval('serial_ne'),
         name  varchar(80) NOT NULL CHECK (name <> '')
    );
EOSQL
