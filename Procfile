release: ./manage.py migrate
web: gunicorn --bind 0.0.0.0:$PORT dandiapi.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery --app dandiapi.celery worker --loglevel INFO
celery-beat: REMAP_SIGTERM=SIGQUIT celery --app dandiapi.celery beat --loglevel INFO
