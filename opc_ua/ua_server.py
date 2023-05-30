import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod

server = None
idx = None

async def init_server():
    global server, idx
    # setup our server
    print("Initializing OPC server...")
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # set up our own namespace, not really necessary but should as spec
    uri = "drink.production.example"
    idx = await server.register_namespace(uri)

asyncio.run(init_server())  # it takes really long to init server, so we do it in advance


async def start_server():
    global server
    _logger = logging.getLogger(__name__)
    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)

async def create_server(recipe):
    global server, idx
    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    for node in recipe['nodes']:
        node_obj = await setup_node(server, idx, node)
    print("OPC server setup done!")
    return server

async def setup_node(server: Server, idx, node):
    node_type = node['dtype']
    node_obj = await server.nodes.objects.add_object(idx, node['id'])
    state = await node_obj.add_variable(idx, 'state', 'IDLE')
    await state.set_writable()
    process_stage = await node_obj.add_variable(idx, 'process_stage', '')
    await process_stage.set_writable()
    node_type = await server.nodes.objects.add_variable(idx, 'node_type', node_type)
    # if node_type == 'TankModel':
    #     loading = await node_obj.add_variable(idx, 'loading', 0)
    #     await loading.set_writable()
    # elif node_type == 'IcingMachine':
    #     loading = await node_obj.add_variable(idx, 'loading', 0)
    #     await loading.set_writable()
    #     temperature = await node_obj.add_variable(idx, 'temperature', 0.)
    #     await temperature.set_writable()
    return node_obj

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    recipe = {
        "nodes": [
            {
                "dtype": "SourceTank",
                "id": "source"
            },
            {
                "dtype": "TankModel",
                "id": "storage"
            },
            {
                "dtype": "SinkTank",
                "id": "sink"
            }
        ]
    }
    server = asyncio.run(create_server(recipe), debug=True)
    asyncio.run(start_server(server), debug=True)