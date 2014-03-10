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
from pymcda.learning.mip_mrsort_veto import MipMRSortVC
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.utils import add_errors_in_assignments_proba
from test_utils import test_result, test_results

def test_mip_mrsort_vc(seed, na, nc, ncat, na_gen, veto_interval, pcerrors):

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model_with_coalition_veto(nc, ncat, seed,
                                        veto_interval = veto_interval / 100)

    # Generate a set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    # Add errors in assignment examples
    aa_err = aa.copy()
    aa_erroned = add_errors_in_assignments_proba(aa_err,
                                                 model.categories,
                                                 pcerrors / 100)
    na_err = len(aa_erroned)

    # Run the MIP
    t1 = time.time()

    model2 = model.copy()
    model2.cv = None
    model2.bpt = None
    model2.lbda = None

    mip = MipMRSortVC(model2, pt, aa)
    mip.solve()

    t_total = time.time() - t1

    # Determine the number of erroned alternatives badly assigned
    aa2 = model2.pessimist(pt)

    ok_errors = ok2_errors = ok = 0
    for alt in a:
        if aa(alt.id) == aa2(alt.id):
            if alt.id in aa_erroned:
                ok_errors += 1
            ok += 1

        if aa_err(alt.id) == aa2(alt.id) and alt.id in aa_erroned:
            ok2_errors += 1

    total = len(a)
    ca2_errors = ok2_errors / total
    ca_best = ok / total
    ca_errors = ok_errors / total

    # Generate alternatives for the generalization
    a_gen = generate_alternatives(na_gen)
    pt_gen = generate_random_performance_table(a_gen, model.criteria)
    aa_gen = model.pessimist(pt_gen)
    aa_gen2 = model2.pessimist(pt_gen)
    ca_gen = compute_ca(aa_gen, aa_gen2)

    aa_gen_err = aa_gen.copy()
    aa_gen_erroned = add_errors_in_assignments_proba(aa_gen_err,
                                                     model.categories,
                                                     pcerrors / 100)
    aa_gen2 = model2.pessimist(pt_gen)
    ca_gen_err = compute_ca(aa_gen_err, aa_gen2)

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%d-%d" % (seed, na, nc, ncat,
                    na_gen, veto_interval, pcerrors))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['na_gen'] = na_gen
    t['veto_interval'] = veto_interval
    t['pcerrors'] = pcerrors

    # Ouput params
    t['na_err'] = na_err
    t['ca_best'] = ca_best
    t['ca_errors'] = ca_errors
    t['ca_gen'] = ca_gen
    t['ca_gen_err'] = ca_gen_err
    t['t_total'] = t_total

    return t

def run_tests(na, nc, ncat, na_gen, pcerrors, veto_intervals, nseeds,
              filename):
    # Create the CSV writer
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['algorithm', algo.__name__])
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
    writer.writerow(['na_gen', na_gen])
    writer.writerow(['veto_intervals', veto_intervals])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test_results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _ncat, _na_gen, _veto_interval, _pcerrors, seed \
        in product(na, nc, ncat, na_gen, veto_intervals, pcerrors, seeds):

        t1 = time.time()
        t = test_mip_mrsort_vc(seed, _na, _nc, _ncat, _na_gen,
                               _veto_interval, _pcerrors)
        t2 = time.time()

        if initialized is False:
            fields = ['seed', 'na', 'nc', 'ncat', 'na_gen', 'veto_interval',
                      'pcerrors', 'na_err', 'ca_best', 'ca_errors', 'ca_gen',
                      'ca_gen_err', 't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()

        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'ncat', 'na_gen', 'veto_interval',
                         'pcerrors'],
                        ['na_err', 'ca_best', 'ca_errors',
                         'ca_gen', 'ca_gen_err', 't_total'])
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
    parser.add_option("-v", "--veto_intervals", action = "store", type="string",
                      dest = "vetointervals",
                      help = "veto intervals (in percents)")
    parser.add_option("-s", "--nseeds", action = "store", type="string",
                      dest = "nseeds",
                      help = "number of seeds")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")

    (options, args) = parser.parse_args()

    algo = MipMRSortVC

    options.na = read_multiple_integer(options.na,
                                       "Number of assignment examples")
    options.nc = read_multiple_integer(options.nc, "Number of criteria")
    options.ncat = read_multiple_integer(options.ncat, "Number of categories")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization alternatives")
    options.vetointervals = read_multiple_integer(options.vetointervals,
                                                  "Veto interval (in percents)")
    options.pcerrors = read_multiple_integer(options.pcerrors, "Ratio of " \
                                             "errors")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "data/test_%s-%s.csv" % (algo.__name__, dt)
    options.filename = read_csv_filename(options.filename, default_filename)

    run_tests(options.na, options.nc, options.ncat, options.na_gen,
              options.pcerrors, options.vetointervals, options.nseeds,
              options.filename)

    print("Results saved in '%s'" % options.filename)
