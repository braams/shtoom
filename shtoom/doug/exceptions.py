# Copyright (C) 2004 Anthony Baxter

class StateMachineError(Exception):
    pass
class EventNotSpecifiedError(StateMachineError):
    pass
class NonEventError(StateMachineError):
    pass
