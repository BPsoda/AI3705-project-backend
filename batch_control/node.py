from .state_machine import State, StateMachine, ShortTransition, LongTransition
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

class StorageNode(BaseNode):
    def __init__(self, id, batchmng, capacity=-1) -> None:
        super().__init__(id, batchmng)
        self.storage = queue.Queue(maxsize=capacity)

    def get_product(self, product):
        print("Node {} get product {}".format(self.id, product))
        product['src_node_id'] = self.id
        self.storage.put(product)

    def run(self):
        while self.state_machine.currentState != State.STOPPING:
            if self.storage.empty():
                # waiting for products
                if self.state_machine.currentState == State.RUNNING:
                    self.state_machine.pause()
                time.sleep(1)
            else:
                # get product, start running
                product = self.storage.get()
                if self.state_machine.currentState == State.IDLE:
                    self.state_machine.start()
                elif self.state_machine.currentState == State.PAUSED:
                    self.state_machine.resume()
                print("Node {} start processing product {}".format(self.id, product))
                self.process_product(product)
                self.batchmng.add_product(product)

    def process_product(self, product):
        time.sleep(1)


class SinkNode(BaseNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.sink = []

    def get_product(self, product):
        '''To record product in the sink'''
        self.sink.append(product)

    def run(self):
        pass



class TankModel(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return LongTransition(self)
    
class Pasteurizer(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
class FillingMachine(StorageNode):
    def __init__(self, id, batchmng, capacity=50) -> None:
        super().__init__(id, batchmng, capacity)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)
    
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

class SinkTank(SinkNode):
    def __init__(self, id, batchmng) -> None:
        super().__init__(id, batchmng)
        self.state_machine = StateMachine(self.create_transition())

    def create_transition(self):
        return ShortTransition(self)