from fastapi import APIRouter

info_router = APIRouter(tags=['info'])

@info_router.get('/start')
async def home():
    return {
        'key': 'value'
    }
