
FROM postgres:alpine3.20

RUN mkdir -p /var/lib/postgresql/data && \
	chown -R postgres:postgres /var/lib/postgresql/data

ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_DB=${POSTGRES_DB}

COPY tools/news_backup.csv /tmp/news_backup.csv

EXPOSE 5432

CMD ["postgres"]