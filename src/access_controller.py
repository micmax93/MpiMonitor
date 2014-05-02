from access_manager import *
from access_algo import *


class AccessController:
    """
    Klasa odpowiedzialna za spójną kontrolę dostępu i operacji na zasobie
    Itegruje ze sobą kolejkę dostępu z managerem zasobu
    kolejka - odpowiada za to żeby dostęp do krytycznej częsci zasobu był sekwencyjny i sprawiedliwy
    manager - odpowiada za to aby zasób był użytkowany zgodnie z określonymi regułami
    """
    def __init__(self, name, type, monitor):
        #utworzenie kolejki i managera
        self.queue = AccessAlgo(name)
        self.manager = AccessManager(name, type, monitor)

        #powiązanie sekcji krytycznej kolejki z żądaniem uzyskania zasobu
        self.queue.get_access_func = self.manager.get_in

        #zwolnienie sekcji krytycznej po uzyskaniu zasobu
        self.manager.free_critical_func = self.queue.exit_critical


    def set_access_func(self, delay, func):
        #ustawia funkcję wywoływaną po uzyskaniu zasobu
        self.manager.access_func = func
        self.manager.get_in_delay = delay

    def set_exit_func(self, delay, func):
        #ustawia funkcję wywoływaną po zwolnieniu zasobu
        self.manager.exit_func = func
        self.manager.get_out_delay = delay

    def enter(self):
        #zgłoszenie zamiaru uzyskania zasobu
        self.queue.send_request()

    def exit(self):
        #zwolnienie zasobu
        self.manager.get_out()

    def on_confirmation(self, sender, data):  #zdarzenie otrzymania potwierdzenia
        self.queue.on_confirmation(sender)

    def on_request(self, sender, data):  #zdarzenie otrzymania żądania
        self.queue.on_request(sender, data)

    def on_update(self, sender, data):  #zdarzenie otrzymania żądania
        self.manager.on_update(sender, data)