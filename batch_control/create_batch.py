from .batch_manager import BatchManager
from . import node

manager = BatchManager()
node_list = []

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
