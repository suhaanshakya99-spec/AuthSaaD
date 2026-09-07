from redis.asyncio import Redis
from core.config import settings
from fastapi import HTTPException

'''
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:latest
'''

redis_client = Redis(host="redis", port=6379, db=0, decode_responses=True)

async def ratelimiting(email:str):

  key = f"email:{email}"
  count = await redis_client.incr(key)

  if count == 1:
    await redis_client.expire(key, settings.TIMEFRAME)

  if count > settings.LIMIT:
    print(f"{email}'s number of request = {count}")
    raise HTTPException(status_code=429, detail="too many requests")