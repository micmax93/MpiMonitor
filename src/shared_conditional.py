from threading import Semaphore
from utils import *
from my_mpi import *


class SignalController:
    type = 'signal'
    my_state = 'idle'
    callback = empty_func
    waiting_list = []

    def __init__(self, name):
        self.name = name

    def wait_for_signal(self, callback=empty_func):
        self.my_state = 'waiting'
        self.callback = callback
        data = self.mk_msg('request', forward=False)
        mpi_bcast(data)

    def mk_msg(self, command, forward, sender=None):  # generowanie treści komunikatu
        if sender is None:
            sender = mpi_rank()
        data = {'cmd': command, 'rank': sender, 'name': self.name, 'forward': forward, 'type': self.type}
        return data

    def send_signal_all(self):
        data = self.mk_msg('signal', forward=False)
        mpi_bcast(data)

    def send_signal_once(self, sender=None):
        data = self.mk_msg('signal', forward=True, sender=sender)
        if len(self.waiting_list)>0:
            mpi_send(self.waiting_list.pop(0), data)

    def on_request(self, sender, data):
        self.waiting_list.append(sender)

    def on_confirmation(self, sender, data):
        self.waiting_list.remove(sender)

    def on_signal_received(self, sender, forward):
        if sender == mpi_rank():
            return False
        if self.my_state == 'waiting':
            self.my_state = 'idle'
            data = self.mk_msg('confirm', forward=False)
            mpi_bcast(data)
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
        self.on_request = self.controller.on_request
        self.on_confirmation = self.controller.on_request

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