from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import time
import random
from itertools import product

from pymcda.types import AlternativesAssignments, PerformanceTable
from pymcda.electre_tri import ElectreTri
from pymcda.learning.lp_mrsort_weights import LpMRSortWeights
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_random_performance_table
from pymcda.utils import compute_ca
from pymcda.utils import add_errors_in_assignments
from test_utils import test_result, test_results

def test_lp_learning_weights(seed, na, nc, ncat, na_gen, pcerrors):
    # Generate an ELECTRE TRI model and assignment examples
    model = generate_random_mrsort_model(nc, ncat, seed)
    model2 = model.copy()

    # Generate a first set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)

    aa = model.pessimist(pt)

    # Add errors in assignment examples
    aa_err = aa.copy()
    aa_erroned = add_errors_in_assignments(aa_err, model.categories,
                                           pcerrors / 100)

    # Run linear program
    t1 = time.time()
    lp_weights = LpMRSortWeights(model2, pt, aa_err, 0.0001)
    t2 = time.time()
    obj = lp_weights.solve()
    t3 = time.time()

    # Compute new assignment and classification accuracy
    aa2 = model2.pessimist(pt)
    ok = ok_errors = ok2 = ok2_errors = 0
    for alt in a:
        if aa_err(alt.id) == aa2(alt.id):
            ok2 += 1
            if alt.id in aa_erroned:
                ok2_errors += 1

        if aa(alt.id) == aa2(alt.id):
            ok += 1
            if alt.id in aa_erroned:
                ok_errors += 1

    total = len(a)

    ca2 = ok2 / total
    ca2_errors = ok2_errors / total

    ca = ok / total
    ca_errors = ok_errors / total

    # Perform the generalization
    a_gen = generate_alternatives(na_gen)
    pt_gen = generate_random_performance_table(a_gen, model.criteria)
    aa = model.pessimist(pt_gen)
    aa2 = model2.pessimist(pt_gen)
    ca_gen = compute_ca(aa, aa2)

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%g" % (seed, na, nc, ncat, na_gen,
                    pcerrors))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['na_gen'] = na_gen
    t['pcerrors'] = pcerrors

    # Output params
    t['obj'] = obj
    t['ca'] = ca
    t['ca_errors'] = ca_errors
    t['ca2'] = ca2
    t['ca2_errors'] = ca2_errors
    t['ca_gen'] = ca_gen
    t['t_total'] = t3 - t1
    t['t_const'] = t2 - t1
    t['t_solve'] = t3 - t2

    return t

def run_tests(na, nc, ncat, na_gen, pcerrors, nseeds, filename):
    # Create the CSV writer
    writer = csv.writer(open(filename, 'wb'))

    # Write the test options
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
    writer.writerow(['na_gen', na_gen])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _ncat, _na_gen, _pcerrors, seed \
        in product(na, nc, ncat, na_gen, pcerrors, seeds):

        t1 = time.time()
        t = test_lp_learning_weights(seed, _na, _nc, _ncat, _na_gen,
                                     _pcerrors)
        t2 = time.time()

        if initialized is False:
            writer.writerow(t.get_attributes())
            initialized = True

        t.tocsv(writer)
        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])
    t = results.summary(['na', 'nc', 'ncat', 'na_gen', 'pcerrors'],
                        ['obj', 'ca', 'ca_errors', 'ca2', 'ca2_errors',
                         'ca_gen', 't_total', 't_const', 't_solve'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    from test_utils import read_single_integer, read_multiple_integer
    from test_utils import read_csv_filename

    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])
    parser.add_option("-n", "--na", action = "store", type="string",
                      dest = "na",
                      help = "number of assignment examples")
    parser.add_option("-c", "--nc", action = "store", type="string",
                      dest = "nc",
                      help = "number of criteria")
    parser.add_option("-t", "--ncat", action = "store", type="string",
                      dest = "ncat",
                      help = "number of categories")
    parser.add_option("-g", "--na_gen", action = "store", type="string",
                      dest = "na_gen",
                      help = "number of generalization alternatives")
    parser.add_option("-e", "--errors", action = "store", type="string",
                      dest = "pcerrors",
                      help = "ratio of errors in the learning set")
    parser.add_option("-s", "--nseeds", action = "store", type="string",
                      dest = "nseeds",
                      help = "number of seeds")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")

    (options, args) = parser.parse_args()

    options.na = read_multiple_integer(options.na, "Number of " \
                                       "assignment examples")
    options.nc = read_multiple_integer(options.nc, "Number of criteria")
    options.ncat = read_multiple_integer(options.ncat, "Number of " \
                                         "categories")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization alternatives")
    options.pcerrors = read_multiple_integer(options.pcerrors,
                                             "Ratio of errors")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "data/test_lp_learning_weights-%s.csv" % dt
    options.filename = read_csv_filename(options.filename, default_filename)

    run_tests(options.na, options.nc, options.ncat, options.na_gen,
              options.pcerrors, options.nseeds, options.filename)

    print("Results saved in '%s'" % options.filename)
