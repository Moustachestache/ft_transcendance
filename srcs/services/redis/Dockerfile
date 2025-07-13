FROM redis:alpine

EXPOSE 6380

COPY conf/redis.conf /tmp/redis.conf

CMD ["redis-server", "/tmp/redis.conf"]