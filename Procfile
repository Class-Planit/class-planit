web: newrelic-admin run-program gunicorn base.wsgi --preload --timeout 120
worker: celery -A base worker -l info