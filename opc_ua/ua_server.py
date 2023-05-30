import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


async def start_server(recipe):
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # set up our own namespace, not really necessary but should as spec
    uri = "drink.production.example"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    objects = {}    # store all facility nodes, {node_id: node}
    variables = {}  # store all variables, {node_id: {key: variable}}
    for node in recipe['nodes']:
        node_obj = await setup_node(server, idx, node)
    # await server.nodes.objects.add_method(
    #     ua.NodeId("ServerMethod", idx),
    #     ua.QualifiedName("ServerMethod", idx),
    #     func,
    #     [ua.VariantType.Int64],
    #     [ua.VariantType.Int64],
    # )
    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)


async def setup_node(server: Server, idx, node):
    node_type = node['dtype']
    node_obj = server.nodes.objects.add_object(idx, node['id'])
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
    asyncio.run(start_server(), debug=True)