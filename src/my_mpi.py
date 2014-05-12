import inspect
from mpi4py import MPI


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


# rank: [type] [name] [operation] msg
# def say(*args):
#     print(mpi_rank(), ' : ', *args, sep='')


def log(name, *args):
    caller = inspect.stack()[1][3]
    print(mpi_rank(), ' : %-10s ' % name, '@ %-18s: ' % caller, *args, sep='')