#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

import checker


class QC(object):
    """
    quay crane class

    * `ID`: is a class attribute to count how may quay cranes has been created
    * `PROPERTY`: is a tuple of the available instance attributes for a quay crane object
    """
    ID = 1
    PROPERTY = (
        "ready_time",
        "due_date",
        "initial_location",
        "t",
        "handling_efficiency_factor",
        "index"
    )

    def __init__(self):
        super(QC, self).__init__()
        self.__ready_time = 0.0
        self.__due_date = -1
        self.__initial_location = -1
        self.__t = 1
        self.__handling_efficiency_factor = 1.0
        self.__index = QC.ID
        QC.ID += 1

    @property
    def ready_time(self):
        """
        getter for ready time

        :return: ready time
        """
        return self.__ready_time

    @ready_time.setter
    @checker.func_arg_check
    def ready_time(self, value):
        """
        setter for ready time

        :param value: prefix:``ready time``, type:``int, float``, range:``[0, inf)``
        """
        self.__ready_time = value

    @property
    def due_date(self):
        """
        getter for due date

        :return: due date
        """
        return self.__due_date

    @due_date.setter
    @checker.func_arg_check
    def due_date(self, value):
        """
        setter for due date

        :param value: prefix:``due date``, type:``int, float``, range:``[0, inf)``
        """
        self.__due_date = value

    @property
    def initial_location(self):
        """
        getter for location

        :return: location
        """
        return self.__initial_location

    @initial_location.setter
    @checker.func_arg_check
    def initial_location(self, value):
        """
        setter for location

        :param value: prefix:``initial location``, type:``int``, range:``(-inf, inf)``
        :return: location
        """
        self.__initial_location = value

    @property
    def t(self):
        """
        getter for the time for a quay crane to traverse a distance of one bay, i.e., sort of reciprocal of speed

        :return: reciprocal of speed
        """
        return self.__t

    @t.setter
    @checker.func_arg_check
    def t(self, value):
        """
        setter for reciprocal of speed

        :param value: prefix:``reciprocal of speed``, type:``int, float``, range:``[0, inf)``
        """
        self.__t = value

    @property
    def handling_efficiency_factor(self):
        """
        getter for quay crane handling efficiency

        :return: handling efficiency
        """
        return self.__handling_efficiency_factor

    @handling_efficiency_factor.setter
    @checker.func_arg_check
    def handling_efficiency_factor(self, value):
        """
        setter for quay crane handling efficiency

        :param value: prefix:``handling efficiency``, type:``int, float``, range:``[0, inf)``
        """
        self.__handling_efficiency_factor = value

    @property
    def index(self):
        """
        getter for index

        :return: index
        """
        return self.__index

    def __str__(self):
        return """QC {0} r={s.ready_time:.1f}, d={s.due_date:.1f}, t={s.t:.1f}, l0={s.initial_location}""".format(
            self.__index, s=self)

    __repr__ = __str__

if __name__ == "__main__":
    # print QC()
    pass