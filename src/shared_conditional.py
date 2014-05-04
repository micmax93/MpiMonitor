from threading import Semaphore
from utils import *
from my_mpi import *


class SignalController:
    type = 'signal'
    my_state = 'idle'
    callback = empty_func

    def __init__(self, name):
        self.name = name

    def wait_for_signal(self, callback=empty_func):
        self.my_state = 'waiting'
        self.callback = callback

    def mk_msg(self, forward, sender=None):  # generowanie treści komunikatu
        if sender is None:
            sender = mpi_rank()
        data = {'cmd': 'signal', 'rank': sender, 'name': self.name, 'forward': forward, 'type': self.type}
        return data

    def send_signal_all(self):
        data = self.mk_msg(forward=False)
        mpi_bcast(data)

    def send_signal_once(self, sender=None):
        data = self.mk_msg(forward=True, sender=sender)
        nxt = (mpi_rank() + 1) % mpi_count()
        mpi_send(nxt, data)

    def on_signal_received(self, sender, forward):
        if sender == mpi_rank():
            return False
        if self.my_state == 'waiting':
            self.my_state = 'idle'
            self.callback()
            return True
        elif forward:
            self.send_signal_once(sender)
        return False


class SharedConditional:
    def __init__(self, name):
        self.controller = SignalController(name)
        self.user_lock = Semaphore(value=0)
        self.type = 'SharedConditional'

    def wait(self, mutex):
        mutex.unlock()
        self.controller.wait_for_signal(callback=self.user_lock.release)
        self.user_lock.acquire()
        mutex.lock()

    def signal(self):
        self.controller.send_signal_once()

    def signal_all(self):
        self.controller.send_signal_all()

    def on_signal(self, sender, data):
        self.controller.on_signal_received(sender, data['forward'])