web: gunicorn base.wsgi tika-server/target/tika-server-1.13-SNAPSHOT.jar --host=0.0.0.0 --port=$PORT
worker: celery -A base worker -l info
