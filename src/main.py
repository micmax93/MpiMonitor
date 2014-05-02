from my_mpi import *
from access_controller import *
from lockers_monitor import *
from shower_monitor import *


def job_done():
    """
    Informs process about finished task loop
    """
    data = {'cmd': 'job_done', 'rank': mpi_rank(), 'name': mpi_rank()}
    mpi_send(mpi_rank(), data)


def job_finished():
    """
    Informs all processes in "world" about finishing all loops
    """
    data = {'cmd': 'job_done', 'rank': mpi_rank(), 'name': mpi_rank()}
    mpi_bcast(data)


if __name__ == '__main__':

    mpi_barrier()
    q = {}

    gender = get_rand_gender()  # Przypisanie płci do procesu
    q['lockers'] = AccessController('lockers', gender, LockersMonitor())  # Kolejka odpowiedzialna za szatnie
    q['showers'] = AccessController('showers', gender, ShowerMonitor())  # Kolejka odpowiedzialna za natrysk

    LOCKER_DELAY = get_rand_timeout(LOCKER_TIMEOUT)  # Czas spędzony w szatni
    SHOWER_DELAY = get_rand_timeout(SHOWER_TIMEOUT)  # Czas spędzony pod natryskiem
    POOL_DELAY = get_rand_timeout(POOL_TIMEOUT)  # Czas spędzony w basenie

    # Po uzyskaniu dostępu do szatni, proces dokona próby wejścia pod natrysk
    q['lockers'].set_access_func(LOCKER_DELAY, q['showers'].enter)

    # Po wejściu pod natrysk i odczekaniu, proces wyjdzie z pod natrysku
    q['showers'].set_access_func(SHOWER_DELAY, q['showers'].exit)

    # Po wyjściu z pod natrysku proces wykonuje timeout, który odzwierciedla czas spędzony na basenie
    # Po wyjściu z basenu następuje wywołanie wyjścia z szatni
    q['showers'].set_exit_func(POOL_DELAY, q['lockers'].exit)

    # Po wyjściu z szatni proces informuje o wykonaniu zadania
    q['lockers'].set_exit_func(0, job_done)

    # Ilość pętli jakie wykonuje każdy proces (-1) dla nieskonczoności
    loops = 1

    finished = 0
    q['lockers'].enter()  #Powiadomienie o chęci wejścia do szatni

    while True:
        data = mpi_recv()
        name = data['name']
        #say("Received com ", data)
        if data['cmd'] == 'request':
            q[name].on_request(data['rank'], data)

        elif data['cmd'] == 'allowed':
            q[name].on_confirmation(data['rank'], data)

        elif data['cmd'] == 'update':
            q[name].on_update(data['rank'], data)

        elif data['cmd'] == 'job_done':
            if loops == -1:
                q['lockers'].enter()
            elif data['rank'] == mpi_rank():
                loops -= 1
                if loops > 0:
                    q['lockers'].enter()
                else:
                    finished += 1
                    job_finished()
            else:
                finished += 1
            if finished == mpi_count():
                break
