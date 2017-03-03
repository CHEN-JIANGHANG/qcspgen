#!/usr/bin/python
# -*- coding: utf-8 -*-

from vessel import Vessel
from quay import Quay
from qcspgen_exception import QCSPGenException
import checker
import random
import itertools
import template


class Instance(object):
    """
    Instance class is used to generate QCSP instances, for example:
    ::

        Instance.seed(12345)
        v = Vessel(b=10, c=200, f=0.5, d=1.0, g=0.0, n=n, loc="uni")
        qu = Quay(2, t=1, ready_time=0)
        instance = Instance(safety_margin=1, vessel=v, quay=qu)
        instance.generate(style="json", name="QCSP.json", path="./output")

    :param safety_margin: prefix:``safety margin between two consecutive QCs``,type:``int``,range:``[0, inf)``
    :param vessel: prefix:``vessel for an instance``, type:``Vessel``
    :param quay: prefix:``quay for an instance``, type:``Quay``
    :param kwargs: other options, e.g., 'fixed', which means that the initial location of QCs are given by kwargs['fixed']
    :return: None
    """

    @staticmethod
    def seed(sd):
        """
        function to change the seed of random functions used in this module

        :param sd: a random number seed
        """
        random.seed(sd)

    @checker.func_arg_check
    def __init__(self, safety_margin, vessel, quay, **kwargs):
        """
        initialization function for Instance class

        :param safety_margin: prefix:``safety margin between two consecutive QCs``,type:``int``,range:``[0, inf)``
        :param vessel: prefix:``vessel for an instance``, type:``Vessel``
        :param quay: prefix:``quay for an instance``, type:``Quay``
        :param kwargs: other options, e.g., 'fixed', which means that the initial location of QCs are given by kwargs['fixed']
        :return: None
        """
        super(Instance, self).__init__()
        self.__safety_margin = safety_margin
        self.__vessel = vessel
        self.__quay = quay

        if "fixed" in kwargs:
            if isinstance(kwargs["fixed"], (list, tuple)) and len(kwargs["fixed"]) == len(self.quay.size):
                previous_position = -1 * float("inf")
                for i, q in enumerate(self.quay.size):
                    if kwargs["fixed"][i] - previous_position > self.__safety_margin:
                        q.initial_location = kwargs["fixed"][i]
                        previous_position = q.initial_location
                    else:
                        raise QCSPGenException("- initial location data error: safety margin=%d" % self.__safety_margin)
            else:
                raise QCSPGenException("- kwargs['fixed'] should be list/tuple with length=%d" % self.quay.size)
        else:
            self._set_qcs_l0_randomly()

    @property
    def vessel(self):
        return self.__vessel

    @property
    def quay(self):
        return self.__quay

    @property
    def safety_margin(self):
        return self.__safety_margin

    def _set_qcs_l0_randomly(self):
        factor = 2
        delta = int(0.25 * self.vessel.bay_size)
        shift = random.randint(-1*delta, delta)
        l0 = [1 + shift] * self.quay.size
        for i in range(1, self.quay.size):
            l0[i] = l0[i-1] + random.randint(self.safety_margin + 1, factor * (self.safety_margin + 1))

        for i, q in enumerate(self.quay.qcs):
            q.initial_location = l0[i]

    def generate(self, path="./", name="QCSP.txt", style="opl"):
        """
        to generate output file by given file style

        :param path: to specify the path of the generated file
        :param name: the name of the generated file
        :param style: the style of the generated file, currelty supported file stypes are 'opl' and 'json'
        """
        import os
        filename = path + os.path.sep + name
        n = self.vessel.task_size
        b = self.vessel.bay_size
        t_index = [i+1 for i in range(self.vessel.task_size)]
        p = [t.processing_time for t in self.vessel.tasks]
        l = [t.location for t in self.vessel.tasks]
        Phi = self.vessel.precedence
        Psi = self.vessel.non_simultaneity
        q = self.quay.size
        q_index = [i+1 for i in range(self.quay.size)]
        r = [qc.ready_time for qc in self.quay.qcs]
        l0 = [qc.initial_location for qc in self.quay.qcs]
        t = [qc.t for qc in self.quay.qcs]
        s = self.safety_margin

        with open(filename, "w") as f:
            f.write(getattr(self, "_%s_format" % style)(locals()))
        print "Instance file %s (style: %s) has been generated!" % (name, style)

    @staticmethod
    def _opl_format(data):
        def opl_array(array, bracket="[]"):
            out = ", ".join([str(i) for i in array])
            if isinstance(bracket, str) and len(bracket) == 2:
                out = bracket[0] + out + bracket[1]
            return out

        def opl_array_2d(array, bracket="{}"):
            out = ", ".join(opl_array(a, "<>") for a in array)
            if isinstance(bracket, str) and len(bracket) == 2:
                out = bracket[0] + out + bracket[1]
            return out

        data["t_index"] = opl_array(data["t_index"], bracket=None)
        data["p"] = opl_array(data["p"])
        data["l"] = opl_array(data["l"])
        data["Phi"] = opl_array_2d(data["Phi"])
        data["Psi"] = opl_array_2d(data["Psi"])
        data["q_index"] = opl_array(data["q_index"], bracket=None)
        data["r"] = opl_array(data["r"])
        data["l0"] = opl_array(data["l0"])
        data["t"] = opl_array(data["t"])

        return template.OPL_TEMPLATE.format(**data)

    @staticmethod
    def _json_format(data):
        def json_array(array, bracket="[]"):
            out = ", ".join([str(i) for i in array])
            if isinstance(bracket, str) and len(bracket) == 2:
                out = bracket[0] + out + bracket[1]
            return out

        def json_array_2d(array, bracket="[]"):
            out = ", ".join(json_array(a,) for a in array)
            if isinstance(bracket, str) and len(bracket) == 2:
                out = bracket[0] + out + bracket[1]
            return out

        data["p"] = json_array(data["p"])
        data["l"] = json_array(data["l"])
        data["Phi"] = json_array_2d(data["Phi"])
        data["Psi"] = json_array_2d(data["Psi"])
        data["r"] = json_array(data["r"])
        data["l0"] = json_array(data["l0"])
        data["t"] = json_array(data["t"])

        return template.JSON_TEMPLATE.format(**data)


def generate_benchmark():
    """
    function to generate benchmarks ABCDEFG

    :return: None
    """
    # set A
    counter = 1
    for n in range(10, 41, 5):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=10, c=200, f=0.5, d=1.0, g=0.0, n=n, loc="uni")
            qu = Quay(2, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_A_{}.json".format(counter))
            counter += 1

    # set B
    counter = 1
    for n in range(45, 71, 5):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=15, c=400, f=0.5, d=1.0, g=0.0, n=n, loc="uni")
            qu = Quay(4, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_B_{}.json".format(counter))
            counter += 1

    # set C
    counter = 1
    for n in range(75, 101, 5):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=20, c=600, f=0.5, d=1.0, g=0.0, n=n, loc="uni")
            qu = Quay(6, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_C_{}.json".format(counter))
            counter += 1

    # set D
    counter = 1
    for f, loc in itertools.product([0.2, 0.8], ["cl1", "cl2", "uni"]):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=10, c=400, f=f, d=1.0, g=0.0, n=50, loc=loc)
            qu = Quay(4, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_D_{}.json".format(counter))
            counter += 1

    # set E
    counter = 1
    for d in [0.80, 0.85, 0.90, 0.95, 1.0]:
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=15, c=400, f=0.5, d=d, g=0.0, n=50, loc="uni")
            qu = Quay(4, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_E_{}.json".format(counter))
            counter += 1

    # set F
    counter = 1
    for q in range(2, 7):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=15, c=400, f=0.5, d=1, g=0.0, n=50, loc="uni")
            qu = Quay(q, t=1, ready_time=0)
            instance = Instance(safety_margin=1, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_F_{}.json".format(counter))
            counter += 1

    # set G
    counter = 1
    for s in range(0, 5):
        for j in range(1, 11):
            Instance.seed(j)
            v = Vessel(b=15, c=400, f=0.5, d=1, g=0.0, n=50, loc="uni")
            qu = Quay(4, t=1, ready_time=0)
            instance = Instance(safety_margin=s, vessel=v, quay=qu)
            instance.generate(style="json", name="QCSP_Set_G_{}.json".format(counter))
            counter += 1

if __name__ == "__main__":
    try:
        Instance.seed(123)
        v = Vessel(b=10, c=200, f=0.5, d=1.0, g=0.0, n=20, loc="uni")
        qu = Quay(2, t=1, ready_time=0)
        instance = Instance(safety_margin=1, vessel=v, quay=qu)
        instance.generate(style="json", name="test.json")

        # v = Vessel(b=15, c=400, f=0.5, d=1, g=0.0, loc='uni', n=50)
        # import copy
        # bay_size = 20
        # vessel_size = 100
        # Instance.seed("hello")
        # v_0 = Vessel(b=bay_size, c=600, f=0.5, d=1.0, g=0.0, n=200, loc="uni")
        #
        # vessels = []
        # for n in range(vessel_size):
        #     v = Vessel(tasks=copy.deepcopy(v_0.tasks), b=bay_size, c=600, f=0.5, d=1.0, g=0.0, n=100, loc="uni",
        #                means=(10.0, 15.0))
        #     vessels.append(v.bays)
        #
        # number = bay_size * [0]
        # weight = bay_size * [0]
        # for v in vessels:
        #     for b in range(bay_size):
        #         number[b] += len(v[b].tasks)
        #         weight[b] += v[b].aggregate_task_processing_time
        #
        # number = map(lambda x: x*1.0/vessel_size, number)
        # weight = map(lambda x: x*1.0/vessel_size, weight)
        #
        # print ["{:.2f}".format(n) for n in number]
        # print ["{:.2f}".format(w) for w in weight]
        #
        # import matplotlib.pyplot as plt
        #
        # plt.bar(range(bay_size), weight)
        # # plt.plot(number)
        # plt.show()
        pass
    except QCSPGenException, e:
        e.display()
