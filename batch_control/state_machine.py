'''State machine definition follows ISA 88 standard.'''
from enum import IntEnum
import time

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
        if self.currentState != State.ABORTED and self.currentState != State.COMPLETE and self.currentState != State.STOPPED:
            raise RuntimeError('Can not reset from state {}'.format(self.currentState))
        self.transition.reset()
        self.currentState = State.IDLE

    def hold(self):
        if self.currentState != State.RUNNING:
            raise RuntimeError('Can not hold from state {}'.format(self.currentState))
        self.currentState = State.HOLDING
        self.transition.hold()
        self.currentState = State.HELD

    def restart(self):
        if self.currentState != State.HELD:
            raise RuntimeError('Can not restart from state {}'.format(self.currentState))
        self.currentState = State.RESTARTING
        self.transition.restart()
        self.currentState = State.RUNNING


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
    
    def restart(self):
        raise NotImplementedError
    
class ShortTransition(BaseTransition):
    '''Short transition class. The transition puts sleep 1s in each method.'''
    def __init__(self, node) -> None:
        super().__init__(node)

    def start(self):
        time.sleep(1)

    def pause(self):
        time.sleep(1)
    
    def resume(self):
        time.sleep(1)

    def stop(self):
        time.sleep(1)
    
    def abort(self):
        time.sleep(1)

    def reset(self):
        time.sleep(1)

    def hold(self):
        time.sleep(1)

    def restart(self):
        time.sleep(1)


class LongTransition(BaseTransition):
    '''Long transition. The transition puts sleep 5s in each method.'''
    def __init__(self, node) -> None:
        super().__init__(node)

    def start(self):
        time.sleep(5)

    def pause(self):
        time.sleep(5)
    
    def resume(self):
        time.sleep(5)

    def stop(self):
        time.sleep(5)

    def abort(self):
        time.sleep(5)

    def reset(self):
        time.sleep(5)

    def hold(self):
        time.sleep(5)

    def restart(self):
        time.sleep(5)


class PassTrainsition(BaseTransition):
    '''Pass transition. The transition does nothing.'''
    def __init__(self, node) -> None:
        super().__init__(node)
    def start(self):
        pass
    def pause(self):
        pass
    def resume(self):
        pass
    def stop(self):
        pass
    def abort(self):
        pass
    def reset(self):
        pass
    def hold(self):
        pass
    def restart(self):
        pass