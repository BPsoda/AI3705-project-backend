from .state_machine import StateMachine

class BaseNode:
    def __init__(self, id, batchmng) -> None:
        self.id = id
        self.batchmng = batchmng
        self.batchmng.add_node(self)
        self.state_machine = StateMachine(self.create_transition())

    def get_product(self, product):
        raise NotImplementedError
    
    def create_transition(self):
        raise NotImplementedError
    
    def get_state(self):
        return {'id': self.id, 'state': self.state_machine.currentState.name}
    
    def action(self, action):
        self.state_machine.__getattribute__(action)()