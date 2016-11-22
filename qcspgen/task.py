#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

import checker


class Task(object):
    """
    task class with attributes of

    * location
    * index
    * processing time

    example:
    ::

        t = Task()
        t.index = 1
        t.location = 2
        t.processing_time = 2.0

    """
    def __init__(self):
        super(Task, self).__init__()
        self.__location = -1
        self.__index = -1
        self.__processing_time = 0

    @property
    def index(self):
        """
        getter for index

        :return: task index
        """
        return self.__index

    @property
    def location(self):
        """
        getter for location

        :return: task location
        """
        return self.__location

    @property
    def processing_time(self):
        """
        getter for processing time

        :return: task processing time
        """
        return self.__processing_time

    @index.setter
    @checker.func_arg_check
    def index(self, value):
        """
        setter for index

        :param value: prefix:``task index`` with type:``int`` in range:``(0,inf)``
        """
        self.__index = value

    @location.setter
    @checker.func_arg_check
    def location(self, value):
        """
        setter for location

        :param value: prefix:``task location`` with type:``int`` in range:``(0,inf)``
        """
        self.__location = value

    @processing_time.setter
    @checker.func_arg_check
    def processing_time(self, p):
        """
        setter for processing time

        :param p: prefix:``task processing time`` with type:``float`` in range:``[0, inf)``
        """
        self.__processing_time = p

    def __str__(self):
        return "Task {s.index} (p={s.processing_time:.1f}, l={s.location:d})".format(s=self)

    __repr__ = __str__


if __name__ == "__main__":
    pass