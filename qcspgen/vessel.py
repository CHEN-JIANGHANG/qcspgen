#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Chen Jiang Hang'

from task import Task
from bay import Bay
from aggregator import Aggregator
import random
import checker


class _Parameter(object):
    """
    parameter class to hold all vessel related parameters
    """

    @checker.func_arg_check
    def __init__(self, **kwargs):
        """
        :param n: prefix:``number of tasks``, type:``int``, range:``(0, inf)``
        :param b: prefix:``number of bays``, type:``int``, range:``(0, inf)``
        :param c: prefix:``capacity per bay``, type:``int``, range:``(0, inf)``
        :param f: prefix:``handling rate``, type:``float``, range:``[0, 1]``
        :param loc: prefix:``task bay distribution pattern``, type:``str``, range:``(uni, cl1, cl2)``
        :param d: prefix:``precedent density``, type:``int, float``, range:``[0, 1]``
        :param g: prefix:``non-simultaneity density``, type:``int, float``, range:``[0, 1]``
        :param std: prefix:``standard deviation for task distribution``, type:``int, float``, range:``[0, int)``
        :param means: means for task distribution
        """

        self.task_size = kwargs["n"]
        self.bay_size = kwargs["b"]
        self.capacity = kwargs["c"]
        self.handling_rate = kwargs["f"]
        self.pattern = kwargs["loc"].lower()
        self.p_density = kwargs["d"]
        self.ns_density = kwargs["g"]
        self.std = kwargs["std"] * self.bay_size
        self.mean1, self.mean2 = Vessel.set_mean(self.bay_size, self.pattern) if kwargs["means"] is None else \
            kwargs["means"]


class Vessel(Aggregator):
    """
    vessel class which is an aggregator of bays (BTW, bay is an aggregator of tasks). For detailed construction of a
    vessel object, please refer to *A unified approach for the evaluation of quay crane scheduling models and algorithms*,
    published in **Computer & Operations Research**

    :param std: to determine the standard deviation for task distribution. The applied standard deviation is std\*the \
    of number of bays. The default std is set to 0.25.

    :param means: the means for task distribution. The default means is None. In this case, `set_mean` function will be\
    called to generate suitable means depending on the selected task distribution pattern, i.e., *cl1*, or *cl2*. If you\
    would like to use *uni*, just use the default means; For customized *cl1* or *cl2* type task distribution, the\
    input means should be a tuple with two elements. For *cl1* case, means can be (10, -1). The second element can be\
    arbitrary. However, for *cl2* case, both elements of means tuple should be meaningful.

    :param existing_task: if the parameter is not None but a list of task elements, then the constructed vessel will\
    use the supplied tasks instead of generating a set of new tasks.

    :param n: number of container groups (tasks).
    :param b: number of bays.
    :param c: capacity per bay.
    :param f: handling rate
    :param loc: task bay distribution pattern
    :param d: precedent density
    :param g: non-simultaneity density
    """

    BAY_DISTRIBUTION_PATTERN = ("uni", "cl1", "cl2")

    @staticmethod
    @checker.func_arg_check
    def calculate_pij(i, j, density):
        """
        calculation of probability pij
        :param i: index i
        :param j: index j
        :param density: prefix:``density``, type:``int, float``, range:``[0, inf)``
        :return: pij
        """
        import math
        if density >= 1.0:
            return 1.0
        part = (1-density)**(math.fabs(j-i)-1)
        return density*part/(1-density*(1-part))

    @staticmethod
    def set_mean(size, pattern):
        """
        to set the means for task distribution

        :param size: the size of a vessel
        :param pattern: task distribution pattern (uni, cl1, cl2)
        :return: means tuple
        """
        if pattern == "uni":
            return -1, -1
        elif pattern == "cl1":
            return random.randint(1, size), -1
        elif pattern == "cl2":
            mean1 = random.randint(1, size)
            if mean1 > self.bay_size/2:
                mean2 = mean1 - size/2
            else:
                mean2 = mean1 + size/2
            return mean1, mean2
        else:
            return -1, -1

    @staticmethod
    def sample_gauss(size, mean, std):
        """
        sampling from a gaussian distribution

        :param size: the size of a vessel
        :param mean: mean of the gaussian distribution
        :param std: std of the gaussian distribution
        :return: a sample
        """
        while True:
            sample = int(random.gauss(mean, std))
            if 1 <= sample <= size:
                return sample

    def __init__(self, std=0.25, means=None, existing_tasks=None, **kwargs):
        super(Vessel, self).__init__(Bay)
        
        # initialize/process parameters
        self.parameter = _Parameter(std=std, means=means, **kwargs)
        
        # generate bays
        self.generate_bays()

        # generate tasks, distribute them, & index them
        self.tasks = []
        self.generate_tasks(existing_tasks)

        # generate precedence/non simultaneity pairs
        self.precedence = []
        self.non_simultaneity = []
        self.generate_precedence(self.parameter.p_density)
        self.generate_non_simultaneity(self.parameter.ns_density)
    
    @property
    def bays(self):
        return self.aggregation
    
    @property
    def bay_size(self):
        return self.size
    
    @property
    def task_size(self):
        return len(self.tasks)

    def generate_bays(self):
        """
        generate bays
        :return: None
        """
        for i in range(self.parameter.bay_size):
            self.append(Bay(self.parameter.capacity, i + 1))

    def generate_tasks(self, existing_tasks):
        """
        generate tasks

        :param existing_tasks: if it is None then a set of new tasks will be generated, otherwise, existing_tasks will\
        be used instead
        :return: None
        """
        if existing_tasks is None:
            self._create_tasks(self.parameter.task_size)
        else:
            self.tasks.extend(existing_tasks)

        self._distribute_tasks(self.parameter.pattern)
        self._index_tasks()

    def generate_precedence(self, density):
        """
        A convenient technique for generating precedence constraints, which we call GGEN, is
        described by Potts (1985) and van de Velde (1995). First, a parameter D, where 0<D<1,
        is specified. For each pair of nodes i and j in the graph, where 1<=i<j<=n, a random number
        r_ij is generated from the uniform distribution over the interval [0, 1]. If r_ij < D, then arc
        (i ,j) is included in the graph. The requirement that i < j ensures that the graph is acyclic.
        If needed, any transitive arcs can then be added.

        :param density: precedence density
        """
        for b in self.bays:
            for ti in b.tasks:
                for tj in b.tasks:
                    j = tj.index
                    i = ti.index
                    if j > i:
                        p_ij = Vessel.calculate_pij(i, j, density)
                        if random.random() < p_ij:
                            self.precedence.append((i, j))

    def generate_non_simultaneity(self, density):
        """
        Use the same technique as ``generate_precedence()`` to generate non-simultaneity pairs

        :param density: non-simultaneity density
        """
        for ti in self.tasks:
            for tj in self.tasks:
                if ti.location < tj.location:
                    i = ti.index
                    j = tj.index
                    p_ij = Vessel.calculate_pij(i, j, density)
                    if random.random() < p_ij:
                        self.non_simultaneity.append((i, j))

    def clone(self):
        """
        deep copy of the vessel
        :return: a copy of the vessel
        """
        import copy
        return copy.deepcopy(self)

    @checker.func_arg_check
    def aggregate(self, ns_density=None):
        """
        to aggregate cluster-level tasks into bay-level tasks

        :param ns_density: prefix:`noon-simultaneity density``, type:``float``, range:``[0, 1]``
        :return: None
        """
        if ns_density is None:
            ns_density = self.parameter.ns_density

        v = self.clone()
        v.parameter.p_density = 0.0
        v.parameter.ns_density = ns_density
        v.precedence = []
        v.non_simultaneity = []

        # create aggregated bay-level tasks
        # remove all the cluster-level tasks
        # insert bay-level tasks into bays
        v.tasks = []
        for b in v.bays:
            t = Task()
            t.processing_time = b.aggregate_task_processing_time
            t.index = b.index
            b.empty()
            b.append(t)
            v.tasks.append(t)

        # generate non-simultaneity set
        v.generate_non_simultaneity(ns_density)

        return v

    def _create_tasks(self, n):
        # w = fbc
        handling_volume = int(self.parameter.handling_rate * self.bay_size * self.parameter.capacity)
        cut_points = [(i+1)*self.parameter.capacity for i in range(handling_volume/self.parameter.capacity)]
        cut_points.append(handling_volume)
        while len(cut_points) < n:
            cut = random.randint(1, handling_volume - 1)
            if cut not in cut_points:
                cut_points.append(cut)
        cut_points.insert(0, 0)
        cut_points.sort()

        # generate tasks
        for i in range(n):
            t = Task()
            t.processing_time = cut_points[i+1] - cut_points[i]
            self.tasks.append(t)

    def _distribute_tasks(self, pattern):
        self.tasks.sort(key=lambda x: x.processing_time, reverse=True)

        for t in self.tasks:
            bay_selected = getattr(self, "_%s_distribution" % pattern)()
            bay = self.bays[bay_selected - 1]
            if bay.remaining_capacity >= t.processing_time:
                bay.append(t)
            else:
                # search the neighboring bays
                left = right = True
                step = 1
                while step <= self.bay_size:
                    if left and bay_selected + step <= self.bay_size:
                        bay_left = self.bays[bay_selected - 1 + step]
                        if bay_left.remaining_capacity >= t.processing_time:
                            bay_left.append(t)
                            break
                    else:
                        left = False

                    if right and bay_selected - step > 0:
                        bay_right = self.bays[bay_selected - 1 - step]
                        if bay_right.remaining_capacity >= t.processing_time:
                            bay_right.append(t)
                            break
                    else:
                        right = False

                    step += 1

    def _index_tasks(self):
        # tasks are lexicographically indexed by increasing bay locations
        index = 0
        for b in self.bays:
            tasks = b.tasks
            order = range(len(tasks))
            random.shuffle(order)
            for i, t in enumerate(tasks):
                t.index = order[i] + index + 1
            index += len(tasks)

        self.tasks.sort(key=lambda x: x.index)

    def _uni_distribution(self):
        return random.randint(1, self.bay_size)

    def _cl1_distribution(self):
        mean = self.parameter.mean1
        std = self.parameter.std
        return Vessel.sample_gauss(self.bay_size, mean, std)

    def _cl2_distribution(self):
        mean = random.choice([self.parameter.mean1, self.parameter.mean2])
        std = self.parameter.std
        return Vessel.sample_gauss(self.bay_size, mean, std)

    def __str__(self):
        return "A vessel: %s" % ([str(b) for b in self.bays])

    __repr__ = __str__

if __name__ == "__main__":
    pass