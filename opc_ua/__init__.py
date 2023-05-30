from .ua_client import *
from .ua_server import *
import asyncio

async def start_opc_ua(recipe):
    await create_server(recipe)
    # wait til server is ready, then start client
    server_task = asyncio.create_task(start_server())
    client_task = asyncio.create_task(start_client())

    await server_task
    await client_task