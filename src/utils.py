from threading import Thread
import time
from globals import *
from random import randint, random


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


def get_rand_gender():
    rd = randint(0, 1)
    if rd == 0:
        return GENDER_FEMALE
    else:
        return GENDER_MALE


def get_rand_timeout(timeout=(0, 1)):
    return timeout[0] + (random() * timeout[1])