#!/usr/bin/python
# -*- coding: utf-8 -*-

from qc import QC
from qcspgen_exception import QCSPGenException
from aggregator import Aggregator
import checker


class Quay(Aggregator):
    """
    quay object is an aggregation of quay cranes. Different from other aggregators, for its initialization, you need to
    supply the number of quay cranes, n (n>0) and quay cranes' properties that you would like to set. For example:
    ::
        qu = Quay(4, t=1, ready_time=[1, 2, 3, 4], due_date=[3, 4, 5, 6])
        print qu

    Note that if a property of a quay crane is identical for all quay cranes in the quay, you can squeeze the argument
    list into one value.

    :param n: the number of quay cranes of the quay
    :param kwargs: properties of quay cranes

    """

    @checker.func_arg_check
    def __init__(self, n, **kwargs):
        """
        initialization function of a quay

        :param n: prefix:``number of QCs``, type:``int``, range:``(0, inf)``
        :param kwargs: properties of quay cranes
        :return: None
        """
        super(Quay, self).__init__(QC)

        for i in range(n):
            super(Quay, self).append(QC())

        for p in QC.PROPERTY:
            if p in kwargs.keys():
                if isinstance(kwargs[p], (float, int)):
                    for q in self.qcs:
                        setattr(q, p, kwargs[p])
                elif len(kwargs[p]) == self.size:
                    for i, q in enumerate(self.qcs):
                        setattr(q, p, kwargs[p][i])
                else:
                    raise QCSPGenException("- {0}=n or =[{0}_1,...{0}_n] where n is the number of QCs!".format(p))

    @property
    def qcs(self):
        """
        getter for quay crane list

        :return: quay crane added in the quay
        """
        return self.aggregation

    def __str__(self):
        return "Quay:\n{}".format([str(q) for q in self.qcs])

    __repr__ = __str__


if __name__ == "__main__":
    # try:
    #     qu = Quay(4, t=1, ready_time=[1, 2, 3, 4])
    #     print qu
    #     print qu.size
    # except QCSPGenException, e:
    #     e.display()
    pass
