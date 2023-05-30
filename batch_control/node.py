from .state_machine import State, StateMachine, ShortTransition, LongTransition, PassTrainsition
from opc_ua import msg_queue
import queue
import time

class BaseNode:
    def __init__(self, id, batchmng) -> None:
        self.id = id
        self.batchmng = batchmng
        self.batchmng.add_node(self)
        self.state_machine = None

    def get_product(self, product):
        raise NotImplementedError
    
    def create_transition(self):
        raise NotImplementedError
    
    def get_state(self):
        return {'id': self.id, 'state': self.state_machine.currentState.name}
    
    def action(self, action):
        self.state_machine.__getattribute__(action)()

    def run(self):
        raise NotImplementedError


class SourceNode(BaseNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)

    def run(self):
        self.state_machine.start()
        time.sleep(1)
        self.state_machine.stop()

    def get_product(self, product):
        '''Imediately add product to batch manager'''
        self.batchmng.add_product(product)

class VirtualNode(BaseNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.transition = StateMachine(PassTrainsition(self))

    def run(self):
        pass

class StorageNode(BaseNode):
    def __init__(self, id, batchmng, capacity=-1) -> None:
        super().__init__(id, batchmng)
        self.storage = queue.Queue(maxsize=capacity)

    def get_product(self, product):
        print("Node {} get product {}".format(self.id, product))
        product['src_node_id'] = self.id
        self.storage.put(product)

    def run(self):
        while self.state_machine.currentState != State.STOPPING and self.state_machine.currentState != State.STOPPED:
            if self.storage.empty():
                # waiting for products
                if self.state_machine.currentState == State.RUNNING:
                    self.state_machine.pause()
                time.sleep(0.1)
            else:
                # get product, start running
                product = self.storage.get()
                if self.state_machine.currentState == State.IDLE:
                    self.state_machine.start()
                elif self.state_machine.currentState == State.PAUSED:
                    self.state_machine.resume()
                print("Node {} start processing product {}".format(self.id, product))
                product = self.process_product(product)
                self.batchmng.add_product(product)

    def process_product(self, product):
        time.sleep(1)
        return product


class SinkNode(BaseNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.sink = []

    def get_product(self, product):
        '''To record product in the sink'''
        self.sink.append(product)

    def run(self):
        pass

    def get_state(self):
        node_state = super().get_state()
        # count the product in sink
        node_state['products'] = {}
        node_state['products']['number'] = len(self.sink)
        if len(self.sink) > 0:
            node_state['products']['types'] = self.sink[0]['type']
        return node_state


class TankModel(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return LongTransition(self)
    
    def process_product(self, product):
        product = super().process_product(product)
        if product['type'] == 'water':
            product['type'] = 'filtered water'
        elif product['type'] == 'filtered water':
            product['type'] = 'finely filtered water'
        msg_queue.put(make_msg(self.id, product))
        return product
        
    
class Pasteurizer(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
    def process_product(self, product):
        product = super().process_product(product)
        product['type'] = 'pasteurized ' + product['type']
        msg_queue.put(make_msg(self.id, product))
        return product
    
class FillingMachine(SinkNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
    def get_product(self, product):
        if 'milk' in product['type']:
            product['type'] = 'bottled milk'
        elif 'juice' in product['type']:
            product['type'] = 'bottled juice'
        elif 'tea' in product['type']:
            product['type'] = 'bottled tea'
        elif 'water' in product['type']:
            product['type'] = 'bottled water'
        elif 'soda' in product['type']:
            product['type'] = 'bottled soda'
        self.sink.append(product)
        msg_queue.put(make_msg(self.id, product))
        return product
    
class SourceTank(SourceNode):
    def __init__(self, id, batchmng, capacity=-1) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)

class IcingMachine(StorageNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())
        self.storage = queue.Queue()

    def create_transition(self):
        return LongTransition(self)
    
    def process_product(self, product):
        product = super().process_product(product)
        product['type'] = 'iced ' + product['type']
        msg_queue.put(make_msg(self.id, product))
        return product

class SinkTank(SinkNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    

class Start(VirtualNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)

class End(VirtualNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)

class Restart(VirtualNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)


def make_msg(node_id, product):
    return {'node_id': node_id, 'product': product['type']}