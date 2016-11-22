#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

from qcspgen_exception import QCSPGenException
from task import Task
from aggregator import Aggregator
import checker


class Bay(Aggregator):
    """
    bay object which is an aggregator for task objects, example:
    ::

        b = Bay(capacity=200, index=20)
        t1 = Task()
        t2 = Task()
        t3 = Task()
        b.append(t1, t2, t3)
        b.remove(t3, t2)

    :param capacity: the maximal number of containers that a bay can hold
    :param index: the index of a bay
    """

    @checker.func_arg_check
    def __init__(self, capacity, index):
        """
        init function of bay
        :param capacity: prefix:``bay capacity`` with type:``int`` in range:``(0,inf)``
        :param index: prefix:``index of a bay``with type:``int``in range:``[1,inf)``
        :return: None
        """
        super(Bay, self).__init__(Task)
        self.__index = index
        self.__remaining_capacity = capacity
        self.__aggregate_task_processing_time = 0

    def append(self, *args):
        """
        overridden method for Aggregator ``append``, to append a list of tasks into a bay

        :param args: a list of tasks
        :return: None
        """
        for t in args:
            super(Bay, self).append(t)
            t.location = self.__index
            self.__remaining_capacity -= t.processing_time
            self.__aggregate_task_processing_time += t.processing_time
            if self.__remaining_capacity < 0:
                raise QCSPGenException("- the remaining capacity of a bay must be non-negative!")

    def remove(self, *args):
        """
        overridden method for Aggregator ``remove``, to remove a list of tasks from a bay

        :param args: a list of tasks
        :return: None
        """
        for t in args:
            super(Bay, self).remove(t)
            self.__remaining_capacity += t.processing_time
            self.__aggregate_task_processing_time -= t.processing_time

    def empty(self):
        """
        overridden method for Aggregator ``empty``, to empty all the added tasks

        :return: None
        """
        super(Bay, self).empty()
        self.__remaining_capacity += self.__aggregate_task_processing_time
        self.__aggregate_task_processing_time = 0

    @property
    def index(self):
        """
        getter for bay index

        :return: index of the bay
        """
        return self.__index

    @property
    def tasks(self):
        """
        getter for all the added tasks

        :return: all the added tasks
        """
        return self.aggregation

    @property
    def remaining_capacity(self):
        """
        getter for bay remaining capacity

        :return: the remaining capacity of the bay
        """
        return self.__remaining_capacity

    @property
    def aggregate_task_processing_time(self):
        """
        getter for bay aggregated task processing time

        :return: the aggregated task processing time of the bay
        """
        return self.__aggregate_task_processing_time

    def __str__(self):
        return """Bay {self.index:d} rc={self.remaining_capacity:d}: {self.aggregation}""".format(self=self)

    __repr__ = __str__

if __name__ == "__main__":
    # try:
    #     b = Bay(capacity=200, index=20)
    #     # t1 = Task()
    #     # t2 = Task()
    #     # t3 = Task()
    #     # b.append(t1, t2)
    # except QCSPGenException, e:
    #     e.display()
    pass