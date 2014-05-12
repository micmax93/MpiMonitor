import time
import datetime
from my_mpi import *
from shared_monitor import SharedMonitor

monitor = SharedMonitor()
monitor.start()

id = monitor.id
buffer = monitor.get_variables('buffer')
full = monitor.get_conditional('full')
empty = monitor.get_conditional('empty')


def init():
    buffer.lock()
    if buffer.version == 0:
        log('USER','Setting initial buffer values')
        buffer.set('curr', 0)
        buffer.set('max', mpi_count()*2)
        buffer.set('data', [])
    buffer.unlock()
init()


def producer(limit):
    buffer.lock()
    val = 0
    start = 0
    while val < limit:
        while buffer.get('curr') == buffer.get('max'):
            log('$user', 'Added ', val-start, ' values')
            full.wait(buffer)
            start = val
        data = buffer.get('data')
        data.append(val)
        log('$user', 'Adding "', val, '" to buffer')
        curr = buffer.get('curr')
        curr += 1
        buffer.set('data', data)
        buffer.set('curr', curr)
        val += 1
        empty.signal()  # if one
    buffer.unlock()


def consumer(limit):
    n = 1
    while n < limit:
        buffer.lock()
        while buffer.get('curr') == 0:
            empty.wait(buffer)
        data = buffer.get('data')
        value = data.pop(0)
        curr = buffer.get('curr')
        curr -= 1
        buffer.set('data', data)
        buffer.set('curr', curr)
        n += 1
        full.signal()  # if full-1
        buffer.unlock()
        log('$user', 'Taking "', value, '" from buffer')

cons = 15
prod = cons * (mpi_count()-1)

if id == 0:
    producer(prod)
else:
    consumer(cons)

monitor.stop()




# mx = monitor.get_mutex('mutex')
# mx.lock()
# print('Yea!')
# mx.unlock()


# var_ns = monitor.get_variables('my_namespace')
# var_ns.lock()
#
# if var_ns.version == 0:
#    var_ns.set('counter', 1)
#
# while var_ns.get('counter') < 50:
#     counter = var_ns.get('counter')
#     print('@', counter)
#     var_ns.set('counter', counter+1)
#     var_ns.commit()
#
# var_ns.unlock()


# cv = monitor.get_conditional('alert')
# mx = monitor.get_mutex('mutex')
#
# if mpi_rank() == 0:
#     time.sleep(2)
#     cv.signal_all()
#     # n = 1
#     # while n < mpi_count():
#     #     time.sleep(0.5)
#     #     cv.signal()
#     #     n += 1
# else:
#     mx.lock()
#     cv.wait(mx)
#     print(mpi_rank(), ' @ Done')
#     mx.unlock()

