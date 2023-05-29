import queue

class BatchManager:
    def __init__(self, queue_size=-1) -> None:
        self.nodes = {} # store all facility nodes, {node_id: node}
        self.connections = {} # store all connections between nodes. {node1: [node2, node3]}
        self.queue = queue.Queue(queue_size) # store all batch requests (products)

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_connection(self, node1, node2):
        if node1 not in self.connections:
            self.connections[node1] = []
        self.connections[node1].append(node2)

    def add_product(self, product):
        self.queue.put(product)

    def run(self):
        for node in self.nodes.values():
            node.action('start')
        while True:
            if not self.queue.empty():
                product = self.queue.get()
                self.nodes[product.src_node_id].get_product(product)

    def get_state(self):
        state = []
        for node in self.nodes.values():
            state.append(node.get_state())
        return state
            
    def get_nodes(self):
        '''Return list of node ids.'''
        node_ids = []
        for node in self.nodes.values():
            node_ids.append(node.id)
        return node_ids