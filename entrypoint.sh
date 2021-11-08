#!/bin/sh


#python manage.py migrate --run-syncdb
#python manage.py loaddata db.json
#python manage.py collectstatic --no-input

gunicorn spirits.wsgi:application --bind 0.0.0.0:8000 --reload  -w 4
