FROM postgres:12
COPY ./dvdrental.tar .
COPY 1_extract_db.sh /docker-entrypoint-initdb.d/1_extract_db.sh
COPY 2_add_user.sql /docker-entrypoint-initdb.d/2_add_user.sql