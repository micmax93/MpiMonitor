from threading import Thread
import time


def __func_execution(delay, function, args=()):
    time.sleep(delay)
    function(*args)


def exec_later(delay, function, args=()):
    """
    Function launches new thread in which given procedure will be executed after given delay.

    :param delay: delay after which function execution will start
    :param function: function to be launched
    :param args: arguments to be passed for function execution
    """
    thread = Thread(target=__func_execution, args=[delay, function, args])
    thread.start()


def empty_func():
    pass

