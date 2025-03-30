#!/bin/bash

source "./src/server/.env"

docker run -d --name database \
  -e POSTGRES_PASSWORD=$DBPASSWORD \
  -e POSTGRES_USER='server' \
  -e POSTGRES_DB='calculator' \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v "$(pwd)/dbdata":/var/lib/postgresql/data \
  -v "$(pwd)/src/server/scripts/sql":/docker-entrypoint-initdb.d \
  -p 8888:5432 postgres
