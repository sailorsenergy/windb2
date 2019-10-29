FROM postgres:11.5

RUN apt update && apt install -y wget python3 python3-psycopg2 python3-tz python3-numpy postgresql-11-postgis-2.5
WORKDIR /windb2
COPY / /windb2/

# Create a database called 'windb2' upon startup
COPY docker/create-windb2-in-docker.sh /docker-entrypoint-initdb.d

# Allow connections from outside using an MD5 password
RUN echo 'listen_addresses = "*"' >> /etc/postgresql/postgresql.conf
