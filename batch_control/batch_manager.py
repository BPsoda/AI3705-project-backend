import queue
import time
from concurrent.futures import ThreadPoolExecutor

from .state_machine import State, StateMachine, PassTrainsition

class BatchManager:
    def __init__(self, queue_size=-1) -> None:
        self.nodes = {} # store all facility nodes, {node_id: node}
        self.connections = {} # store all connections between nodes. {node1: node2}
        self.queue = queue.Queue(queue_size) # store all batch requests (products)
        self.state_machine = StateMachine(PassTrainsition(self))
        self.transfer_pool = ThreadPoolExecutor(max_workers=15) # thread pool for transfering products between nodes

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_connection(self, node1, node2):
        self.connections[node1] = node2

    def add_product(self, product):
        self.queue.put(product)

    def run(self):
        self.state_machine.start()
        while self.state_machine.currentState == State.RUNNING:
            if not self.queue.empty():
                product = self.queue.get()  # get blocks when the queue is empty
                print("Manager get product {}".format(product))
                target_node = self.connections[product['src_node_id']]
                print("Manager transferring product {} to node {}".format(product, target_node))
                self.transfer_pool.submit(self.nodes[target_node].get_product, product) # submit transfer task to thread pool
            else:
                time.sleep(0.5)

    def get_state(self):
        state = []
        for node in self.nodes.values():
            state.append(node.get_state())
        state.append(str(self.queue.qsize()))
        return state
            
    def get_nodes(self):
        '''Return list of node ids.'''
        node_ids = []
        for node in self.nodes.values():
            node_ids.append(node.id)
        return node_ids