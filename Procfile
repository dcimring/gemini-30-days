web: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
worker: celery -A app.celery worker --loglevel=info
