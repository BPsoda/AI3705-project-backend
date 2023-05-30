import asyncio
import queue

from asyncua import Client

url = "opc.tcp://localhost:4840/freeopcua/server/"
namespace = "drink.production.example"
msg_queue = queue.Queue()

async def start_client():

    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        # Find the namespace index
        nsidx = await client.get_namespace_index(namespace)
        print(f"Namespace Index for '{namespace}': {nsidx}")
        
        while True:
            # print("Queue size: {}".format(msg_queue.qsize()))
            if msg_queue.empty():
                await asyncio.sleep(1)
                continue
            msg = msg_queue.get()   # blocks when the queue is empty
            # Get the variable node for read / write
            var = await client.nodes.root.get_child(
                ["0:Objects", f"{nsidx}:{msg['node_id']}", f"{nsidx}:process_stage"]
            )
            # value = await var.read_value()
            # print(f"Value of MyVariable ({var}): {value}")

            # new_value = value - 50
            # print(f"Setting value of MyVariable to {new_value} ...")
            await var.write_value(msg['product'])


if __name__ == "__main__":
    asyncio.run(start_client())