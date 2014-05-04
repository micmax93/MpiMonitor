import time
import datetime
from my_mpi import *
from shared_monitor import SharedMonitor

monitor = SharedMonitor()
monitor.start()

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


# buffer = monitor.get_variables('buffer')
# full = monitor.get_conditional('full')
# empty = monitor.get_conditional('empty')
#
#
# buffer.lock()
# if buffer.version == 0:
#     print('Setting initial values @by ', monitor.id)
#     buffer.set('curr', 0)
#     buffer.set('max', 5)
#     buffer.set('data', [])
# buffer.unlock()
#
#
# def add(val):
#     buffer.lock()
#     while buffer.get('curr') == buffer.get('max'):
#         full.wait(buffer)
#
#     data = buffer.get('data')
#     data.append(val)
#     print(monitor.id, ' @add ', val)
#     curr = buffer.get('curr')
#     curr += 1
#     buffer.set('data', data)
#     buffer.set('curr', curr)
#
#     empty.signal()  # if one
#     buffer.unlock()
#
#
# def get():
#     buffer.lock()
#     while buffer.get('curr') == 0:
#         empty.wait(buffer)
#
#     data = buffer.get('data')
#     value = data.pop(0)
#     print(monitor.id, ' @get ', value)
#     curr = buffer.get('curr')
#     curr -= 1
#     buffer.set('data', data)
#     buffer.set('curr', curr)
#
#     full.signal()  # if full-1
#     buffer.unlock()
#     return value
#
# n = 0
# while n < 20:
#     time.sleep(0.1)
#     n += 1
#     if monitor.id == 0:
#         add(n)
#     else:
#         val = get()
#         if val >= 20:
#             exit()


cv = monitor.get_conditional('alert')
mx = monitor.get_mutex('mutex')

if mpi_rank() == 0:
    time.sleep(2)
    cv.signal_all()
    # n = 1
    # while n < mpi_count():
    #     time.sleep(0.5)
    #     cv.signal()
    #     n += 1
else:
    mx.lock()
    cv.wait(mx)
    print(mpi_rank(), ' @ Done')
    mx.unlock()

monitor.stop()
