from concurrent.futures import ThreadPoolExecutor

from .product import BaseProduct
from .batch_manager import BatchManager
from . import node

manager = BatchManager()
node_list = []
thread_pool = ThreadPoolExecutor(max_workers=15)
recipe_store = None

def create_from_recipe(recipe):
    '''Create batch from recipe. Returns batch manager.'''
    global node_list, manager, recipe_store, thread_pool
    # shutdown thread pool if it is running
    if not thread_pool._shutdown:
        thread_pool.shutdown(wait=False)
        thread_pool = ThreadPoolExecutor(max_workers=15)
    recipe_store = recipe
    manager = BatchManager()
    node_list = []
    # Add nodes
    for node_config in recipe['nodes']:
        if node_config['dtype'] == 'Start':
            manager.start_node_id = node_config['id']
        node_list.append(node.__dict__[node_config['dtype']](node_config['id'], manager))
    # Add connections
    for connection in recipe['edges']:
        manager.add_connection(connection['source'], connection['target'])
    print("Batch created")
    return manager


def run_batch(product_config):
    print("Start running batch")
    manager.load_products(product_config['type'], int(product_config['number']))
    thread_pool.submit(manager.run)
    for node in node_list:
        thread_pool.submit(node.run)
    return manager.get_state()


def get_batch_state():
    state = manager.get_state()
    print(state)
    for i in range(len(node_list)):
        recipe_store['nodes'][i].update(state[i])
    return recipe_store

def stop_batch():
    '''Force stop batch'''
    print("Stopping batches")
    manager.state_machine.stop()
    for v_node in node_list:
        v_node.state_machine.stop()
    thread_pool.shutdown(wait=False)
    print("Batches stopped")
    return manager.get_state()

def restart_batch():
    print("Restarting batches")
    # create a new batch
    create_from_recipe(recipe_store)
    return manager.get_state()