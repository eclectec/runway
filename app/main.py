from fastapi import Depends, FastAPI, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pyArango.connection import Connection
from bs4 import BeautifulSoup
from app.util import to_geo_json
from os import getenv
import aioredis
import asyncio
import json
import requests

message_broker = getenv("BROKER", "kafka")
broker_port = getenv("PORT", "9093")
topic = getenv("TOPIC", "rumble")

app = FastAPI()

conn = Connection(
    arangoURL="http://hangar:8529",
    username="root", 
    password="arango"
)

db = conn["summaries"]

origins = [
        "http://localhost",
        "http://localhost:3000"
        "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/files", StaticFiles(directory="/code/files"), name="files")

async def get_redis():
    redis = await aioredis.from_url("redis://redis", encoding="utf-8", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

@app.get("/")
def status():
    return {"Im": "Up"}

@app.get("/airports")
def get_airports():
    aql = "FOR airport IN airports RETURN airport"
    results = db.AQLQuery(aql, rawResults=True)
    airports = [airport for airport in results]

    return JSONResponse(content=jsonable_encoder(airports))

@app.get("/images/{description}")
def get_images(description: str):
    image_list = []
    image_req = f"""https://www.airteamimages.com/search?q={description}&sort=id%2Cdesc"""
    response = requests.get(image_req)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        div_block = soup.find("main", id="photo-search-pane")
        if div_block:
            images = div_block.find_all("img")
            for image in images[:5]:
                image_list.append(image['src'])
    
    return JSONResponse(content=jsonable_encoder(image_list))                   

@app.websocket("/redis/rumble")
async def rumble_socket(websocket: WebSocket, redis: aioredis.Redis = Depends(get_redis)):
    await websocket.accept()
    consumer = redis.pubsub()

    await consumer.subscribe("rumble")

    while True:
        message = await consumer.get_message(ignore_subscribe_messages=True)

        if message is not None and 'data' in message:
            await websocket.send_json(to_geo_json(json.loads(message['data'])))
        else:
            await asyncio.sleep(1)

    await websocket.close()

