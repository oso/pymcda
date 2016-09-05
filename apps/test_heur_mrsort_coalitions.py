from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import random
from itertools import chain, combinations, product

from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_criteria_weights
from test_utils import test_result, test_results

DATADIR = os.getenv('DATADIR', '%s/pymcda-data' % os.path.expanduser('~'))

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def pprint_coalition(coalition):
    string = ""
    for i in coalition:

        if string[:-1] != '':
            string += '+'

        string += str(i)

    if string == '':
        string = "empty"

    return string

def sum_weights(cw, coalition):
    w = 0
    for c in coalition:
        w += cw[c].value
    return w

def one_loop(crits, lbda_min, coalitions):
    cw = generate_random_criteria_weights(crits)
    lbda = random.uniform(lbda_min, 1)

    t = test_result("")
    t["ncoalitions"] = 0
    for i in range(len(crits) + 1):
        t["%d_criteria" % i] = 0

    for coalition in coalitions:
        w = sum_weights(cw, coalition)
        if w >= lbda:
            t[pprint_coalition(coalition)] = 1
            t["ncoalitions"] += 1
            t["%d_criteria" % len(coalition)] += 1
        else:
            t[pprint_coalition(coalition)] = 0

    return t

def run_test(m, n, lbda_min, lbda_max, filename):
    # Create the CSV writer
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Create a test_results instance
    results = test_results()
    initialized = False

    # Run the algorithm
    c = generate_criteria(n)
    coalitions = [ i for i in powerset(c.keys()) ]
    for i in range(m):
        t = one_loop(c, lbda_min, coalitions)
        t.test_name = "%d-%d" % (i, n)
        t['i'] = i
        t['nc'] = n
        t['lbda_min'] = lbda_min
        t['lbda_max'] = lbda_max
        t['n'] = m

        if initialized is False:
            fields = ['i', 'nc', 'lbda_min', 'lbda_max'] \
                      + [pprint_coalition(j) for j in coalitions] \
                      + ["%d_criteria" % i for i in range(len(c) + 1)] \
                      + ["ncoalitions"]
            writer.writerow(fields)
            initialized = True

        results.append(t)
        t.tocsv(writer, fields)
        f.flush()

        print("%s" % t)

    # Perform a summary
    writer.writerow(['', ''])
    t = results.summary(['nc', 'lbda_min', 'lbda_max', 'n'], [pprint_coalition(j)
                         for j in coalitions], [], [])
    t.tocsv(writer)

    writer.writerow(['', ''])
    t = results.summary(['nc', 'lbda_min', 'lbda_max', 'n'],
                        ["%d_criteria" % i for i in range(len(c) + 1)] \
                        + ['ncoalitions'], ['ncoalitions'],
                        ['ncoalitions'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])

    parser.add_option("-n", "--na", action = "store", type="string",
                      dest = "na",
                      help = "number of test instances")
    parser.add_option("-c", "--nc", action = "store", type="string",
                      dest = "nc",
                      help = "number of criteria")
    parser.add_option("-l", "--lmin", action = "store", type="string",
                      dest = "lbda_min",
                      help = "min value of lambda")
    parser.add_option("-m", "--lmax", action = "store", type="string",
                      dest = "lbda_max",
                      help = "max value of lambda")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")

    (options, args) = parser.parse_args()

    while not options.na:
        options.na = raw_input("Number of test instances ? ")
    options.na = int(options.na)

    while not options.nc:
        options.nc = raw_input("Number of criteria ? ")
    options.nc = int(options.nc)

    while not options.lbda_min:
        options.lbda_min = raw_input("Min value of lambda ? ")
    options.lbda_min = float(options.lbda_min)

    while not options.lbda_max:
        options.lbda_max = raw_input("Max value of lambda ? ")
    options.lbda_max = float(options.lbda_max)

    while not options.filename:
        dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_filename = "%s/test_etri_coalitions-%s.csv" % (DATADIR, dt)
        options.filename = raw_input("File to save CSV data [%s] ? " \
                                     % default_filename)
        if not options.filename:
            options.filename = default_filename

    if options.filename[-4:] != ".csv":
        options.filename += ".csv"

    run_test(options.na, options.nc, options.lbda_min, options.lbda_max,
             options.filename)

    print("Results saved in '%s'" % options.filename)
