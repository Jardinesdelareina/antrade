from fastapi import FastAPI
from trading.api import trading_router
from db import database, metadata, engine

app = FastAPI(
    title='Antrade',
    description='Platform for algorithmic trading by FastAPI',
    version='0.1.0',
)

app.state.database = database
metadata.create_all(engine)

@app.on_event('startup')
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()

@app.on_event('shutdown')
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()

app.include_router(trading_router, prefix='/orders')