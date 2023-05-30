from .state_machine import State, StateMachine, ShortTransition, LongTransition, PassTrainsition
from opc_ua import msg_queue
from .product import BaseProduct
import queue
import time

class BaseNode:
    def __init__(self, id, batchmng) -> None:
        self.id = id
        self.batchmng = batchmng
        self.batchmng.add_node(self)
        self.state_machine = None

    def get_product(self, product: BaseProduct):
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

    def get_product(self, product: BaseProduct):
        print("Node {} get product {}".format(self.id, product))
        product.src_node_id = self.id
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
        node_state['number'] = len(self.sink)
        if len(self.sink) > 0:
            node_state['product'] = self.sink[0].prod_type
        return node_state


class TankModel(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return LongTransition(self)
    
    def process_product(self, product: BaseProduct):
        global msg_queue
        product = super().process_product(product)
        if product.prod_type == 'raw tea':   # mixing
            product.prod_type = 'mixed tea'
        elif product.prod_type == 'mixed tea':  # filtering
            product.prod_type = 'filtered tea'
        elif product.prod_type == 'concentrated juice':   # diluting
            product.prod_type = 'diluted juice'
        elif product.prod_type == 'diluted juice':    # mixing
            product.prod_type = 'mixed juice'
        elif product.prod_type == 'soda base':    # mixing
            product.prod_type = 'mixed soda'
        elif product.prod_type == 'iced mixed soda':   # carbonating
            product.prod_type = 'carbonated soda'
        else:
            raise ValueError('Unknown product type {}'.format(product.prod_type))
        msg_queue.put(make_msg(self.id, product))
        print(msg_queue.qsize())
        return product
        
    
class Pasteurizer(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
    def process_product(self, product):
        global msg_queue
        product = super().process_product(product)
        product.prod_type = 'pasteurized ' + product.prod_type
        msg_queue.put(make_msg(self.id, product))
        return product
    
class FillingMachine(SinkNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
    def get_product(self, product):
        global msg_queue
        if 'milk' in product.prod_type:
            product.prod_type = 'bottled milk'
        elif 'juice' in product.prod_type:
            product.prod_type = 'bottled juice'
        elif 'tea' in product.prod_type:
            product.prod_type = 'bottled tea'
        elif 'water' in product.prod_type:
            product.prod_type = 'bottled water'
        elif 'soda' in product.prod_type:
            product.prod_type = 'bottled soda'
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
        global msg_queue
        product = super().process_product(product)
        product.prod_type = 'iced ' + product.prod_type
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
        self.state_machine = StateMachine(self.create_transition())
    def create_transition(self):
        return PassTrainsition(self)

class End(VirtualNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())
    def create_transition(self):
        return PassTrainsition(self)

class Restart(VirtualNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())
    def create_transition(self):
        return PassTrainsition(self)

def make_msg(node_id, product):
    return {'node_id': node_id, 'product': product.prod_type}