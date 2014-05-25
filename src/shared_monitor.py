from threading import Semaphore, Thread, Lock
from shared_conditional import SharedConditional
from shared_mutex import SharedMutex
from shared_variables import SharedVariables
from my_mpi import *


class SharedContext:
    def __init__(self):
        self.shared_objects = {}
        self.access_lock = Lock()

    def get_mutex(self, name):
        return self.get_raw('mx:' + name)

    def get_conditional(self, name):
        return self.get_raw('cv:' + name)

    def get_variables(self, name):
        return self.get_raw('sv:' + name)

    def get_raw(self, name):
        self.access_lock.acquire()

        if name in self.shared_objects:
            pass
        elif name.find('mx:') == 0:
            self.shared_objects[name] = SharedMutex(name)
            log('context', 'Created ' + name)
        elif name.find('cv:') == 0:
            self.shared_objects[name] = SharedConditional(name)
            log('context', 'Created ' + name)
        elif name.find('sv:') == 0:
            self.shared_objects[name] = SharedVariables(name)
            log('context', 'Created ' + name)
        else:
            raise Exception('Invalid naming format for variable ' + name)

        self.access_lock.release()
        return self.shared_objects[name]


class SharedMonitor(SharedContext):
    def __init__(self):
        super().__init__()
        self.finished = [False] * mpi_count()
        self.exit_lock = Semaphore(value=0)
        self.dispatcher = None
        self.id = mpi_rank()

    def message_dispatcher(self):
        log('monitor', 'Started dispatcher.')
        while True:
            data = mpi_recv()
            if data is not None:
                name = data['name']
                #say("Received com ", data)
                if data['cmd'] == 'request':
                    self.get_raw(name).on_request(data['rank'], data)
                elif data['cmd'] == 'confirm':
                    self.get_raw(name).on_confirmation(data['rank'], data)
                elif data['cmd'] == 'signal':
                    self.get_raw(name).on_signal(data['rank'], data)
                elif data['cmd'] == 'finished':
                    self.finished[data['rank']] = True
                    if False not in self.finished:
                        break
        self.exit_lock.release()
        log('monitor', 'Exiting.')

    def start(self):
        mpi_barrier()
        self.dispatcher = Thread(target=self.message_dispatcher)
        self.dispatcher.start()

    def stop(self):
        data = {'cmd': 'finished', 'rank': self.id, 'name': self.id}
        mpi_bcast(data)
        mpi_send(self.id, data)
        log('monitor', 'Finished.')
        self.exit_lock.acquire()