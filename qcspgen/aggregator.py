#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

from qcspgen_exception import QCSPGenException
import functools


def _verify_type(func):
    """
    decorator to verify item type supplied for the wrapped function

    :param func: decorated function
    :return: wrapper
    """
    @functools.wraps(func)
    def wrapper(self, *item):
        if not isinstance(item[-1], self.item_type):
            raise QCSPGenException("- typeError: item is not type {}".format(self.item_type))
        return func(self, *item)
    return wrapper


class Aggregator(object):
    """
    python list like base class, example:
    ::

        a = Aggregator(str)
        a.append("hello")
        a.append("world")
        print a.aggregator, a.item_type

    :param item_kind: the item type for aggregator's elements
    """
    def __init__(self, item_kind):
        super(Aggregator, self).__init__()
        self._aggregation = []
        self._type = item_kind

    @_verify_type
    def append(self, item):
        """
        to add an item for an aggregator

        :param item: the item to be appended
        :return: None
        """
        self._aggregation.append(item)

    @_verify_type
    def remove(self, item):
        """
        to remove an item from an aggregator

        :param item: the item to be removed
        :return: None
        """
        try:
            self._aggregation.remove(item)
        except ValueError:
            raise QCSPGenException("- item is not in {}, cannot remove".format(self.__class__.__name__))

    def empty(self):
        """
        to empty an aggregator

        :return: None
        """
        self._aggregation = []

    @property
    def aggregation(self):
        """
        getter for _aggregation

        :return: the list of added items
        """
        return self._aggregation

    @property
    def item_type(self):
        """
        getter for _type

        :return: acceptable type for items of an aggregator
        """
        return self._type

    @property
    def size(self):
        """
        getter for item size

        :return: the size of items
        """
        return len(self._aggregation)

    def __getitem__(self, item):
        return self.aggregation[item]

    @_verify_type
    def __setitem__(self, key, value):
        self.aggregation[key] = value

    def __str__(self):
        return str([str(item) for item in self._aggregation])

    __repr__ = __str__


if __name__ == "__main__":
    # try:
    #     a = Aggregator(str)
    #     a.append("hello")
    #     a.append("123")
    #     a[2] = 123
    #     print a[0]
    #     print a.aggregation, a.item_type
    # except QCSPGenException, e:
    #     e.display()
    # except Exception, e:
    #     print e.message
    pass

