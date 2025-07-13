
#!bin/bash

python /tmp/check_db.py

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser --noinput \
        --username  $DJANGO_SUPERUSER_USERNAME \
        --email     $DJANGO_SUPERUSER_EMAIL

# a Haiku: 
#       here lies for;
#               the sake;
#                       of posterity;
# ancient db seed method:
# python /tmp/db_populate.py --verbose

# new, correct, best practice way of doing it
# plus execute only if database is empty

# python manage.py shell --command="import django; print(django.__version__)"
python /transcendence/manage.py loaddata /tmp/seed_news.json

python manage.py collectstatic --noinput

python manage.py compilemessages --locale=en --locale=fr --locale=ka --locale=uk --locale=egy
# python /transcendence/manage.py compilemessages -l en -l fr -l ka -l uk -l egy
python /transcendence/manage.py compilemessages --locale=en --locale=fr --locale=ka --locale=uk --locale=egy

#exec makes the process listening to the docker stop signal : D
exec daphne -b 0.0.0.0 -p 8000 transcendence.asgi:application
