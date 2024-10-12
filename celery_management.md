# Celery Management Guide

This guide provides useful commands and knowledge for managing Celery tasks and workers in the Dropfarm project.

## Starting Celery Worker

Standard worker:
```
celery -A backend.celery_worker worker --loglevel=info --pool=solo
```
