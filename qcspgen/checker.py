#!/usr/bin/python
# -*- coding: utf-8 -*-


from qcspgen_exception import QCSPGenException
import re
import inspect
import functools
import itertools


def verify_type(data, t, prefix=""):
    """
    function to check if `data` is type `t`. If no, raise a QCSPGenException.

    :param data: data to be checked
    :param t: expected legitimate data type
    :param prefix: a prefix for the raised QCSPGenException message
    :exception: QCSPGenException
    :return: data
    """
    if not isinstance(data, t):
        raise QCSPGenException("- %s should be %r\n" % (prefix, t))

    return data


def verify_is_in(data, data_range):
    """
    function to check if `data` is in `data_range`. If no, raise a QCSPGenException.

    :param data: a string to be checked
    :param data_range: legitimate data range
    :exception: QCSPGenException
    :return: data
    """
    if data not in data_range:
        raise QCSPGenException("- %s is not in %r\n" % (data, data_range))

    return data


def verify_numerical_type(data, t=(int, float), lb=0.0, ub=float('inf'), prefix="", left_tight=True, right_tight=True):
    """
    function to check the input `data` is numerical and besides, it is in the range of (lb, ub) or [lb, ub] or (lb, ub],
    or [lb, ub).

    :param data: the input to be checked
    :param t: int or float
    :param lb: lower bound
    :param ub: upper bound
    :param prefix: a prefix for the raised QCSPGenException message
    :param left_tight: if True, then lb can be reached
    :param right_tight: if True, then ub can be reached
    :exception: QCSPGenException
    :return: data
    """
    message = ""
    if not isinstance(data, t):
        message += "- data %s should be %r\n" % (prefix, t)
    if left_tight and right_tight and not lb <= data <= ub:
        message += "- %s not in range [%.1f, %.1f]" % (prefix, lb, ub)
    elif left_tight and not right_tight and not lb <= data < ub:
        message += "- %s not in range [%.1f, %.1f)" % (prefix, lb, ub)
    elif not left_tight and right_tight and not lb < data <= ub:
        message += "- %s not in range (%.1f, %.1f]" % (prefix, lb, ub)
    elif not left_tight and not right_tight and not lb < data < ub:
        message += "- %s not in range (%.1f, %.1f)" % (prefix, lb, ub)
    if message is not "":
        raise QCSPGenException(message)

    return data


def compulsory_kwargs(kwargs, compulsory):
    """
    function to check if `kwargs` contains `compulsory` or not. If no, raise a QCSPGenException.

    :param kwargs: key word arguments to be checked
    :param compulsory: compulsory key word dicts
    :exception: QCSPGenException
    """
    for k in compulsory:
        if k not in kwargs:
            raise QCSPGenException("- Compulsory kwargs: %r. %s is missing!" % (compulsory, k))


class Interval(object):
    """
    class for value pair in the format (lb, ub) or [lb, ub] or (lb, ub], or [lb, ub). Constructed by supplying
    a string of aforementioned format.
    """

    left = float('-inf')
    right = float('inf')
    left_tight = False
    right_tight = False
    left_symbol = '('
    right_symbol = ')'

    # left symbol, left interval value, right interval value, right symbol
    DIGIT_PATTERN = re.compile(r'([[(])(.*),(.*)([])])')

    def __init__(self, doc):
        self.left_symbol, a, b, self.right_symbol = Interval.DIGIT_PATTERN.search(doc.strip()).groups()
        if self.left_symbol is '[':
            self.left_tight = True
        if self.right_symbol is ']':
            self.right_tight = True
        try:
            self.left = float(a)
        except ValueError:
            pass

        try:
            self.right = float(b)
        except ValueError:
            pass

        if self.left > self.right:
            self.left, self.right = self.right, self.left

    def check_range(self, data):
        if self.left_tight and self.right_tight and not self.left <= data <= self.right:
            return False
        elif self.left_tight and not self.right_tight and not self.left <= data < self.right:
            return False
        elif not self.left_tight and self.right_tight and not self.left < data <= self.right:
            return False
        elif not self.left_tight and not self.right_tight and not self.left < data < self.right:
            return False
        return True

    def __str__(self):
        return ''.join([self.left_symbol, '%.1f, %.1f' % (self.left, self.right), self.right_symbol])


class ArgElement(object):
    """
    class to analyze docstring of functions/classes in order to make sure variable prefix/range/type are correct.
    For example, ':param index: prefix:``index of a bay``with type:``int``in range:``[1,inf)``' is an element of
    _ArgElement, which needs to be checked in functions
    """
    name = None
    prefix = ""
    type = None
    range = None
    to_consider = True

    PATTERN_TEMPLATE = r':param {0}:.*{1}:``(.*?)``'

    def __init__(self, name, doc):
        prefix_pattern = re.compile(ArgElement.PATTERN_TEMPLATE.format(name, 'prefix'))
        range_pattern = re.compile(ArgElement.PATTERN_TEMPLATE.format(name, 'range'))
        type_pattern = re.compile(ArgElement.PATTERN_TEMPLATE.format(name, 'type'))

        self.name = name

        try:
            self.prefix = prefix_pattern.search(doc).group(1)
        except AttributeError:
            pass

        try:
            self.type = self.split(type_pattern.search(doc).group(1))
        except AttributeError:
            pass

        try:
            if self.is_numeric():
                self.range = Interval(range_pattern.search(doc).group(1))
            else:
                self.range = ArgElement.split(range_pattern.search(doc).group(1).strip()[1:-1])
        except (AttributeError, TypeError):
            pass

        if self.type is None and self.range is None:
            self.to_consider = False

    @staticmethod
    def split(t):
        return [a.strip() for a in t.split(',')]

    def is_numeric(self):
        if 'int' in self.type or 'float' in self.type:
            return True
        return False

    def __str__(self):
        return ' '.join([self.name, ':', self.prefix, str(self.type), str(self.range)])


def func_arg_check(func):
    """
    a decoration function to do argument properties check!
    Note that if docstring of func is empty then no checking will be conducted.

    :param func: function
    :return: a wrapper
    """

    doc_str = func.__doc__

    arg_elements = dict()
    for m in re.compile(r':param (.*?):').findall(doc_str):
        b = ArgElement(m, doc_str)
        if b.to_consider:
            arg_elements.update({m: b})

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        message = ""
        argspect = inspect.getargspec(func)
        for a in arg_elements.iterkeys():
            try:
                data = args[argspect.args.index(a)]
            except (ValueError, IndexError):
                try:
                    data = kwargs[a]
                except KeyError:
                    try:
                        # it's value may appear as default
                        used_defaults = argspect.defaults[len(argspect.defaults)-len(argspect.args)+len(args):]
                        data = list(itertools.chain(args, used_defaults))[argspect.args.index(a)]
                    except:
                        raise QCSPGenException("- Compulsory kwarg %s is missing!" % a)

            if arg_elements[a].type:
                if not('float' in arg_elements[a].type and type(data).__name__ in ('float', 'int') or
                        type(data).__name__ in arg_elements[a].type):
                    message += "- data {} should be {}\n".format(arg_elements[a].prefix, arg_elements[a].type)

            if arg_elements[a].range:
                if (arg_elements[a].is_numeric() and not arg_elements[a].range.check_range(data)) or \
                        (not arg_elements[a].is_numeric() and data not in arg_elements[a].range):
                    message += "- %s not in range %s\n" % (arg_elements[a].prefix, arg_elements[a].range)
        if message is not "":
            raise QCSPGenException(message)
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    pass
    # @func_arg_check
    # def test():
    #     """
    #     :param value: prefix:``task index`` with type:``int`` in range:``(0,inf)``
    #     :param a: prefix:``a tester`` with type:``float`` in range:``(0,1)``
    #     """
    #     print "hello"
    # try:
    #     test(value=2)
    # except QCSPGenException, e:
    #     e.display()
