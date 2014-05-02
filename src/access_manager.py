from my_mpi import *
from access_monitor import *
from utils import *


class AccessManager():  #klasa odpowiedzialna za rozgłaszanie informacji o zasobach i zbieranie potwierdzeń
    my_state = 'idle'
    my_type = None
    req_id = None
    req_state = 'outside'
    monitor = Monitor()  #monitor definiujący reguły dostępu do zasobów
    free_critical_func = empty_func  #procedura wywoływana po uzyskaniu dostępu do sekcji krytycznej
    access_func = empty_func  #procedura wywoływana po uzyskaniu zasobu
    get_in_delay = 0  #opóźnienie wywołania funkcji access_func
    exit_func = empty_func #procedura wywoływana po zwolnieniu zasobu
    get_out_delay = 0  #opóźnienie wywołania funkcji exit_func

    def __init__(self, name, type, monitor):
        self.name = name
        self.confirmations_num = 0
        self.my_type = type
        self.monitor = monitor

    def mk_msg(self, cmd):  #generowanie treści komunikatu
        rank = mpi_rank()
        data = {'cmd': cmd, 'rank': rank, 'name': self.name}
        if cmd == 'update':
            data['id'] = self.req_id
            data['type'] = self.my_type
            data['state'] = self.req_state
        return data

    def send_update(self):  #wysłanie informacji o aktualnie wykonanej operacji
        data = self.mk_msg('update')
        mpi_bcast(data)
        self.my_state = 'active'
        #say("update sent ", data)

    def get_in(self):  #próba uzyskania zasobu
        if self.my_state != 'requesting':
            say("Requesting ", self.name)
        (entry, id) = self.monitor.get_access(self.my_type)
        self.req_state = 'entering'
        if entry:
            self.req_id = id
            self.send_update()
            say(">>Entering ", self.name, " ", self.req_id)
            self.monitor.get_in(self.req_id, self.my_type)
            self.req_state = 'inside'
            self.free_critical_func()
            self.my_state = 'idle'
            exec_later(self.get_in_delay, self.access_func)
        elif self.my_state != 'requesting':
            say("Waiting for ", self.name, " free")
            self.my_state = 'requesting'

    def get_out(self):  #zwolnienie zasobu
        self.req_state = 'exiting'
        self.send_update()
        say(">>Exiting ", self.name, " ", self.req_id)
        self.monitor.get_out(self.req_id)
        self.req_state = 'outside'
        exec_later(self.get_out_delay, self.exit_func)
        self.my_state = 'idle'

    def on_update(self, sender, data):  #zdarzenie otrzymania informacji o zmianie w zasobie
        op = data['state']
        if op == 'entering':
            self.monitor.get_in(data['id'], data['type'])
        elif op == 'exiting':
            self.monitor.get_out(data['id'])
            if self.my_state == 'requesting':
                self.get_in()
