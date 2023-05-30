from concurrent.futures import ThreadPoolExecutor

from .batch_manager import BatchManager
from . import node

manager = BatchManager()
node_list = []
thread_pool = ThreadPoolExecutor(max_workers=15)

def create_from_recipe(recipe):
    '''Create batch from recipe. Returns batch manager.'''
    global node_list, manager
    manager = BatchManager()
    node_list = []
    for node_config in recipe['nodes']:
        node_list.append(node.__dict__[node_config['type']](node_config['id'], manager))
    for connection in recipe['connections']:
        manager.add_connection(connection['from'], connection['to'])
    for product in recipe['products']:
        manager.add_product(product)
    return manager


def run_batch():
    print("Start running batch")
    thread_pool.submit(manager.run)
    for node in node_list:
        thread_pool.submit(node.run)
    return manager.get_state()


def get_batch_state():
    return manager.get_state()

def stop_batch():
    '''Force stop batch'''
    print("Stopping batches")
    manager.state_machine.stop()
    for node in node_list:
        node.state_machine.stop()
    thread_pool.shutdown(wait=False)
    print("Batches stopped")
    return manager.get_state()