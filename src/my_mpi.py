from mpi4py import MPI
import time


def mpi_send(target, data, tag=0):
    MPI.COMM_WORLD.send(data, target, tag)


def mpi_recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
    return MPI.COMM_WORLD.recv(None, source, tag)


def mpi_rank():
    return MPI.COMM_WORLD.Get_rank()


def mpi_count():
    return MPI.COMM_WORLD.Get_size()


def mpi_bcast(data, tag=0):
    for r in range(0, mpi_count()):
        if r != mpi_rank():
            mpi_send(r, data, tag)


def mpi_barrier():
    MPI.COMM_WORLD.barrier()


def say(*args):
    print(mpi_rank(), ' : ', *args, sep='')