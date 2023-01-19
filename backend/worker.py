from celery import Celery
import environs

env = environs.Env()
env.read_env('.env')

CELERY_BROKER_URL = env('REDIS')
CELERY_RESULT_BACKEND = env('REDIS')

celery = Celery('celery', backend=CELERY_BROKER_URL, broker=CELERY_RESULT_BACKEND)
