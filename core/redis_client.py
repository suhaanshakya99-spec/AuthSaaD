from redis.asyncio import Redis
import asyncio

'''
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:latest
'''

redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)


