web: gunicorn base.wsgi tika-server/target/tika-server-1.13-SNAPSHOT.jar 
worker: celery -A base worker -l info

