from threading import Semaphore
from utils import *
from my_mpi import *


class SignalController:
    def __init__(self, name):
        self.name = name
        self.type = 'signal'
        self.my_state = 'idle'
        self.callback = empty_func
        self.waiting_list = []

    def wait_for_signal(self, callback=empty_func):
        self.my_state = 'waiting'
        self.callback = callback
        data = self.mk_msg('request', forward=False)
        # log(self.name, 'Broadcasting wait request')
        mpi_bcast(data)

    def mk_msg(self, command, forward, sender=None):  # generowanie treści komunikatu
        if sender is None:
            sender = mpi_rank()
        data = {'cmd': command, 'rank': sender, 'name': self.name, 'forward': forward, 'type': self.type}
        return data

    def send_signal_all(self):
        data = self.mk_msg('signal', forward=False)
        # log(self.name, 'Broadcasting signal_all')
        mpi_bcast(data)

    def send_signal_once(self, sender=None):
        data = self.mk_msg('signal', forward=True, sender=sender)
        if len(self.waiting_list) > 0:
            recp = self.waiting_list.pop(0)
            # log(self.name, 'Sending signal to ', recp)
            mpi_send(recp, data)

    def on_request(self, sender, data):
        # log(self.name, 'Adding ', sender, ' to waiting list')
        self.waiting_list.append(sender)

    def on_confirmation(self, sender, data):
        # log(self.name, 'Removing ', sender, ' from waiting list')
        self.waiting_list.remove(sender)

    def on_signal_received(self, sender, forward):
        if sender == mpi_rank():
            return False
        if self.my_state == 'waiting':
            self.my_state = 'idle'
            # log(self.name, 'Received signal from ', sender)
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