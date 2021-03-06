from threading import Semaphore, Lock
from utils import *
from my_mpi import *


class AccessController:  # Kolejka oparta o algorytm Ricarta-Agrawali

    def __init__(self, name):
        self.name = name
        self.type = 'raw'
        self.my_state = 'idle'
        self.confirmations_tab = [False] * mpi_count()
        self.waiting_set = []
        self.callback = empty_func  # procedura wywoływana po uzyskaniu dostępu do sekcji krytycznej
        self.local_lock = Lock()
        self.my_clock = 0
        self.req_clock = None

    def mk_msg(self, cmd):  # generowanie treści komunikatu
        rank = mpi_rank()
        data = {'cmd': cmd, 'rank': rank, 'name': self.name, 'type': self.type, 'clock': self.req_clock}
        return data

    def send_request(self, callback=empty_func):  # wysłanie żądania dostępu do sekcji krytycznej
        self.local_lock.acquire()
        self.my_clock += 1
        self.req_clock = self.my_clock
        data = self.mk_msg('request')
        self.my_state = 'waiting'
        self.callback = callback
        self.confirmations_tab = [False] * mpi_count()
        self.confirmations_tab[mpi_rank()] = True
        mpi_bcast(data)
        log(self.name, 'Requesting critical section')
        self.local_lock.release()

    def send_confirmation(self, target):  # wysłanie zezwolenia na wejście do sekcji krytycznej
        data = self.mk_msg('confirm')
        mpi_send(target, data)
        log(self.name, "Confirmation sent to ", target)

    def exit_critical(self):  # procedura opuszczenia sekcji krytycznej
        log(self.name, "Exiting critical section")
        self.my_state = 'idle'
        #log(self.name, "Sending confirms to: ", self.waiting_set)
        for e in self.waiting_set:
            self.send_confirmation(e)
        self.waiting_set = []
        self.confirmations_tab = [False] * mpi_count()

    def critical_section(self):  # wywołanie funcji sekcji krytycznej
        #kod sekcji krytycznej
        log(self.name, "Entering critical section")
        if self.callback is not None:
            self.callback()

    def on_confirmation(self, sender, data):  # zdarzenie otrzymania potwierdzenia
        self.local_lock.acquire()
        if self.my_state == 'waiting':
            if not self.confirmations_tab[sender]:
                self.confirmations_tab[sender] = True
            #log(self.name, " Confirmation received from ", sender, " - ",
            #   self.confirmations_tab.count(True)-1, ' out of ', mpi_count() - 1)
            if False not in self.confirmations_tab:
                self.my_state = 'active'
                self.critical_section()
                self.req_clock = None
        self.local_lock.release()

    def on_request(self, sender, data):  # zdarzenie otrzymania żądania dostępu
        self.local_lock.acquire()
        msg_clock = data['clock']
        log(self.name, "Received request from ", sender)
        if self.my_state == 'idle':
            self.send_confirmation(sender)
        elif self.my_state == 'waiting':
            if msg_clock < self.req_clock:
                self.send_confirmation(sender)
            elif msg_clock == self.req_clock and sender < mpi_rank():
                self.send_confirmation(sender)
            else:
                self.waiting_set.append(sender)
                #log(self.name, "Adding ", sender, " to waiting set")
        else:
            self.waiting_set.append(sender)
            #log(self.name, "Adding to waiting set ", sender)
        self.my_clock = max(self.my_clock, msg_clock)
        self.local_lock.release()


class SharedMutex(AccessController):
    def __init__(self, name):
        super().__init__(name)
        self.user_lock = Semaphore(value=0)
        self.type = 'SharedMutex'

    def lock(self):
        if self.my_state != 'idle':
            raise Exception('Multiple locking forbidden.')
        self.send_request(callback=self.user_lock.release)
        self.user_lock.acquire()

    def unlock(self):
        if self.my_state != 'active':
            raise Exception('Only locked mutex can by unlocked.')
        self.exit_critical()