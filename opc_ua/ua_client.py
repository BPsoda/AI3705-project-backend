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
            msg = msg_queue.get()   # blocks when the queue is empty
            # Get the variable node for read / write
            var = await client.nodes.root.get_child(
                ["0:Objects", f"{nsidx}:MyObject", f"{nsidx}:MyVariable"]
            )
            value = await var.read_value()
            print(f"Value of MyVariable ({var}): {value}")

            new_value = value - 50
            print(f"Setting value of MyVariable to {new_value} ...")
            await var.write_value(new_value)

            # Calling a method
            res = await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
            print(f"Calling ServerMethod returned {res}")


if __name__ == "__main__":
    asyncio.run(start_client())