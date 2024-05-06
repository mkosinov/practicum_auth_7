FROM postgres:16.0-alpine3.18

WORKDIR /docker-entrypoint-initdb.d
COPY create_schema.ddl .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh