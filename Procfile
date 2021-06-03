web: newrelic-admin run-program gunicorn base.wsgi --preload --timeout 120
worker: celery -A repro worker --detach --hostname repro --logfile celery.log --loglevel DEBUG --pool solo
