from globals import *
from random import randint
from access_monitor import *


class LockersMonitor(Monitor):
    """
    Locker monitor keeps locker room's states and enabled to retrieve them.
    """
    lockers = []

    def __init__(self):
        self.lockers = [[GENDER_FEMALE, 0], [GENDER_FEMALE, 0], [GENDER_FEMALE, 0]]  # ladies first ;)

    # Enter the locker room #num by person of given #gender
    def locker_in(self, num, gender):
        if self.is_locker_empty(num):
            self.lockers[num][0] = gender
        self.lockers[num][1] += 1

    # Leave the locker room #num
    def locker_out(self, num):
        self.lockers[num][1] -= 1

    # Test if locker #num is full
    def is_locker_full(self, num):
        if self.lockers[num][1] == GLOBAL_LOCKER_CAPACITY:
            return True
        return False

    # Test if locker #num is empty
    def is_locker_empty(self, num):
        if self.lockers[num][1] == 0:
            return True
        return False

    # Check if locker room #num is empty or has same gender
    def check_locker_gender(self, num, gender):
        if self.lockers[num][0] == gender or self.is_locker_empty(num):
            return True
        return False

    # Test if person of #gender can enter locker room #num
    def check_enter(self, num, gender):
        if self.lockers[num][1] < GLOBAL_LOCKER_CAPACITY and self.check_locker_gender(num, gender):
            return True
        return False

    # Find optimal locker room according to #gender
    def propose_best(self, gender):
        best = []
        best_val = -1
        for l in range(3):
            lck = self.lockers[l]
            if self.check_locker_gender(l, gender) and (not self.is_locker_full(l)):
                if lck[1] > best_val:
                    best_val = lck[1]
                    best = [l]
                elif lck[1] == best_val:
                    best.append(l)
        if len(best) == 1:
            return True, best[0]
        elif len(best) > 1:
            return True, best[randint(0, len(best) - 1)]
        else:
            return False, -1

    def get_in(self, id, type):
        self.locker_in(id, type)

    def get_out(self, id):
        self.locker_out(id)

    def get_access(self, type):
        return self.propose_best(type)