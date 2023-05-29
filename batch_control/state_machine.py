'''State machine definition follows ISA 88 standard.'''
from enum import IntEnum

class State(IntEnum):
    '''State machine states.'''
    IDLE = 0
    RUNNING = 1
    PAUSING = 2
    PAUSED = 3
    STOPPING = 4
    STOPPED = 5
    ABORTING = 6
    ABORTED = 7
    HOLDING = 8
    HELD = 9
    RESTARTING = 10
    COMPLETE = 11


class StateMachine:
    '''An state machine under ISA 88 standard.'''
    def __init__(self, transition, initial_state=State.IDLE) -> None:
        self.currentState = initial_state
        self.transition = transition

    def create_transition(self):
        raise NotImplementedError

    def start(self):
        if self.currentState != State.IDLE:
            raise RuntimeError('Can not start from state {}'.format(self.currentState))
        self.transition.start()
        self.currentState = State.RUNNING

    def pause(self):
        if self.currentState != State.RUNNING:
            raise RuntimeError('Can not pause from state {}'.format(self.currentState))
        self.currentState = State.PAUSING
        self.transition.pause()
        self.currentState = State.PAUSED

    def resume(self):
        if self.currentState != State.PAUSED:
            raise RuntimeError('Can not resume from state {}'.format(self.currentState))
        self.trainsition.resume()
        self.currentState = State.RUNNING

    def stop(self):
        if self.currentState != State.RUNNING:
            raise RuntimeError('Can not stop from state {}'.format(self.currentState))
        self.currentState = State.STOPPING
        self.transition.stop()
        self.currentState = State.STOPPED

    def abort(self):
        if self.currentState != State.RUNNING:
            raise RuntimeError('Can not abort from state {}'.format(self.currentState))
        self.currentState = State.ABORTING
        self.transition.abort()
        self.currentState = State.ABORTED

    def reset(self):
        if self.currentState != State.ABORTED and self.currentState != State.COMPLETE:
            raise RuntimeError('Can not reset from state {}'.format(self.currentState))
        self.transition.reset()
        self.currentState = State.IDLE

    def hold(self):
        if self.currentState != State.RUNNING:
            raise RuntimeError('Can not hold from state {}'.format(self.currentState))
        self.currentState = State.HOLDING
        self.transition.hold()
        self.currentState = State.HELD


class BaseTransition:
    '''Base transition class.'''
    def __init__(self, node) -> None:
        self.node = node

    def start(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def resume(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def abort(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def hold(self):
        raise NotImplementedError