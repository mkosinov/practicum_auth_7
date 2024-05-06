#!/bin/bash
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f create_schema.ddl