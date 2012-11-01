import random


def exponential(l):
    '''An exponential random variate with lambda=l.'''
    return lambda: random.expovariate(l)


def triangular(low=0.0, high=1.0, mode=None):
    '''A triangular random variate with parameters a, b, mode.'''
    return lambda: random.triangular(low, high, mode=None)


def uniform(a=0.0, b=1.0):
    '''A uniform random variate from a to b.'''
    return lambda: random.uniform(a, b)
