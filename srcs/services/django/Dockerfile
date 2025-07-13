FROM alpine:3.20

RUN	apk update ; apk upgrade ; apk add --no-cache \
                python3 \
                python3-dev \
                py3-pip \
                gcc \
                musl-dev \
                postgresql-libs \
                postgresql-dev \
                postgresql \
                bash \
                gettext

RUN python -m venv env

ENV PATH="/env/bin:$PATH"

COPY conf/requirements.txt /tmp/requirements.txt

RUN pip install -r/tmp/requirements.txt

COPY transcendence /transcendence

COPY tools/check_db.py      /tmp/check_db.py
COPY tools/db_populate.py   /tmp/db_populate.py
COPY tools/start_server.sh  /tmp/start_server.sh
COPY tools/seed_news.json   /tmp/seed_news.json

RUN chmod 775 /tmp/start_server.sh /tmp/check_db.py

EXPOSE 8000


WORKDIR /transcendence/

ENTRYPOINT ["sh", "/tmp/start_server.sh"]