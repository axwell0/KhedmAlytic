import os
import asyncio
import logging

import motor.motor_asyncio
from dotenv import load_dotenv
from typing import Any


class Mongo:
    """Asynchronous Mongo Client (Wrapper for AsyncIOMotorClient)"""

    _instance = None
    client = None
    database = None

    def __new__(cls, mongo_uri: str, db_name: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name

    def __getitem__(self, coll: str) -> motor.motor_asyncio.AsyncIOMotorCollection:
        """Retrieves MongoDB collection object"""
        return Mongo.database[coll]

    async def insert_job(self, job: Any, collection: str) -> None:
        """Inserts job in collection"""
        if job:
            try:
                await self[collection].insert_one(job)
                print(f"Uploaded document {job['Title']} to collection {collection}")
            except:
                print(f"Skipped {job['Title']}  due to duplicate key error")

    async def wipe(self, collection: str) -> None:
        """Clears all documents from a particular collection"""

        await self[collection].delete_many({})
        print(f'Wiped {collection} of all documents')

    async def __aenter__(self):
        try:

            Mongo.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
            Mongo.client.get_io_loop = asyncio.get_event_loop
            Mongo.database = Mongo.client.get_database(self.db_name)
            return self
        except Exception as e:
            logging.error('Connection Failed', exc_info=True)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if Mongo.client:
            Mongo.client.close()
            Mongo.client = None
            Mongo.database = None
            Mongo._instance = None
