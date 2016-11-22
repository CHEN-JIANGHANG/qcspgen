# qcspgen: A Python Version of QCSPgen

## Introduction

**[QCSPgen][1]** is a Java toolkit developed by [Prof. Dr. Frank Meisel][2] to generate benchmark instances for the Quay Crane Scheduling Problem (QCSP). QCSPgen was first introduced in paper ["A unified approach for the evaluation of quay crane scheduling models and algorithms"][3] publised in the journal *Computer & Operations Research*, 38, p. 683-693, 2001. The pros and cons of QCSPgen can be summarized below:

### Advantages

* The toolkit can be run in any operating system (Windows, Unix, Mac OS, Linux, etc.) as long as a Java Runtime Environment is installed;
* QCSPgen provides a GUI to facilitate the usage of the software. Besides, since all parameter input fields in the GUI only use *Spinners* and *Combo boxes*, data validation is guaranteed.

### Shortcomings

* QCSPgen is not open source and thus not modifiable;
* All parameters are limited to certain ranges, e.g., the range for `number of tasks` is [10, 100] and the range for `handling rate` is [0.10, 0.90] with step 0.05;
* The output file format is in OPL style. The instances in OPL (Optimization Programming Language)  format can be conveniently solved by IBM ILOG optimizer. But sometimes, users would like to adopt more generic data transfer formats like JSON or XML;
* The crane data parameters in QCSPgen only allow `number of cranes`, `crane travel time`, and `safety margin`. However, with the popularity of the study of the **rich QCSP**, more and more researchers would like to consider `time windows`, `heterogeneous cranes` (i.e., different cranes can have different moving speed and task handling efficiency) and `initial positions` as well for the QCSP;
* It is cumbersome for users to generate instances in a batch mode.

The aforementioned reasons motivate the development of **qcspgen**. **qcspgen** is written in python (version 2.7.10) and can be run in any operating system with python 2.x installed. No third party python modules is required and the instance generator is carefully designed for user usage, data validation, and future extention. 


## Usage

A typical use of **qcspgen** is as followed:

```
# in qcspgen.py
try:
	# specify the seed for python built-in random module
	# any hashable object can be used as argument
	# without any argument, the system cpu time will be used implicitly
	Instance.seed()
	# construct a vessel instance
	# n: number of container groups
	# b: number of bays
	# c: capacity per bay
	# f: handling rate
	# loc: location parameter ["uni", "cl1", "cl2"]
	# d: precedence density
	# g: non-simultaneity density
	# for advanced user, you can also specify the parameters std and means for task distribution
	v = Vessel(b=20, c=600, f=0.5, d=1.0, g=0.0, n=200, loc="uni")
	# create a quay configuration
	# t: crane travel time
	# ready_time: crane ready times
	q = Quay(6, t=1, ready_time=[0, 2, 4, 6, 8, 0])
	# generate an instance object
	# safety_margin: safety margin between any two quay cranes
	# vessel: a vessel object
	# quay: a quay configuration
	instance = Instance(safety_margin=1, vessel=v, quay=q)
	# for output
	# style: specify the output file format
	# name: the output file name
	instance.generate(style="json", name="QCSP.json")
except QCSPGenException, e:
	print e.traceback()
    print e.message
```

[1]: http://prodlog.wiwi.uni-halle.de/forschung/research_data/qcspgen/
[2]: https://www.scm.bwl.uni-kiel.de/de/team/prof.-dr.-frank-meisel
[3]: http://www.sciencedirect.com/science/article/pii/S0305054810001632