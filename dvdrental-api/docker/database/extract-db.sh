#!/bin/bash
set -e

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER postgres;
	GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO postgres;
EOSQL


../usr/lib/postgresql/12/bin/pg_restore -d $POSTGRES_DB -U postgres ../dvdrental.tar