from my_mpi import *
from shared_mutex import SharedMutex


class SharedVariables(SharedMutex):
    variables = {}
    version = 0
    changed = False

    def __init__(self, name):
        SharedMutex.__init__(self, name)
        self.type = 'SharedVariables'

    def mk_msg(self, cmd):  # generowanie treści komunikatu
        rank = mpi_rank()
        data = {'cmd': cmd, 'rank': rank, 'name': self.name, 'type': self.type, 'clock': self.req_clock}
        if cmd == 'request':
            data['version'] = self.version
        elif cmd == 'allowed':
            data['version'] = self.version
            data['variables'] = self.variables
        return data

    def on_confirmation(self, sender, data):
        if data['version'] > self.version:
            self.version = data['version']
            self.variables = data['variables']
        SharedMutex.on_confirmation(self, sender, data)

    def on_request(self, sender, data):
        SharedMutex.on_request(self, sender, data)

    def get(self, var):
        if self.my_state == 'active':
            return self.variables[var]
        else:
            raise Exception('Trying access variable without permission!!!')

    def set(self, var, value):
        if self.my_state == 'active':
            self.variables[var] = value
            self.changed = True
        else:
            raise Exception('Trying access variable without permission!!!')

    def unlock(self):
        if self.changed:
            self.version += 1
            self.changed = False
        SharedMutex.unlock(self)