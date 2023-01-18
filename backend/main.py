from fastapi import FastAPI
from info.api import info_router

app = FastAPI(
    title='Antrade',
    description='Platform for algorithmic trading',
    version='0.1.0',
)

app.include_router(info_router, prefix='/info', tags=['about'])
