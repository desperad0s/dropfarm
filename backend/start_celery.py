from backend import celery

if __name__ == '__main__':
    celery.worker_main(['worker', '--pool=solo', '--loglevel=info'])
