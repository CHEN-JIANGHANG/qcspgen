#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

import traceback


class QCSPGenException(Exception):
    """
    exception for qcspgen module

    :param message: the message of the exception
    """
    def __init__(self, message):
        super(QCSPGenException, self).__init__()
        self.message = message

    @staticmethod
    def traceback():
        """
        staticmethod in order to trace the errors

        :return: call stack information
        """
        return traceback.format_exc()

    def display(self):
        """
        to display exception traceback info and message

        :return: None
        """
        print QCSPGenException.traceback()
        print self.message
