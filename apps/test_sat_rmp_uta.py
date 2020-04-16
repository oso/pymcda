from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import math
import time
import random
from itertools import product

from pymcda.uta import Uta
from pymcda.types import Alternative
from pymcda.types import PairwiseRelations
from pymcda.types import PerformanceTable
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_random_criteria_values
from pymcda.generate import generate_random_alternative_performances
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_random_criteria_functions
from pymcda.rmp import RMP
from pymcda.learning.sat_rmp import SatRMP
from test_utils import test_result, test_results
from test_utils import save_to_xmcda

DATADIR = os.getenv('DATADIR', '%s/pymcda-data' % os.path.expanduser('~'))

def test_sat_rmp(seed, na, nc, nsegments, nprofiles2, na_gen, pcerrors):

    random.seed(2 ** seed + 3 ** na + 5 ** nc + 7 ** nsegments)

    # Generate random UTA model
    c = generate_criteria(nc)
    cv = generate_random_criteria_values(c)
    cfs = generate_random_criteria_functions(c, nseg_min = nsegments,
                                             nseg_max = nsegments)
    model = Uta(c, cv, cfs)

    ninversions = math.ceil(pcerrors * na / 100)

    i = 0
    pwcs = PairwiseRelations()
    pt = PerformanceTable()
    while i != na:
        x = Alternative("x%d" % (i + 1))
        y = Alternative("y%d" % (i + 1))
        apx = generate_random_alternative_performances(x, c)
        apy = generate_random_alternative_performances(y, c)
        pwc = model.compare(apx, apy)
        if pwc.relation == pwc.INDIFFERENT:
            continue

        if apx.dominates(apy, c) or apy.dominates(apx, c):
            continue

        if i < ninversions:
            if pwc.relation == pwc.PREFERRED:
                pwc.relation = pwc.WEAKER
            else:
                pwc.relation = pwc.PREFERRED

        pt.append(apx)
        pt.append(apy)
        pwcs.append(pwc)
        i += 1

    pwcs.weaker_to_preferred()

    # Run the SAT
    t1 = time.time()

    b2 = [ "b%d" % i for i in range(1, nprofiles2 + 1)]
    model2 = RMP(c, None, b2, None)

    satrmp = SatRMP(model2, pt, pwcs)
    solution = satrmp.solve(True)
    if solution is False:
        print("Warning: solution is UNSAT")

    t_total = time.time() - t1

    # Compare with the new model
    ok = 0
    pwcs2 = PairwiseRelations()
    for pwc in pwcs:
        pwc2 = model2.compare(pt[pwc.a], pt[pwc.b])
        pwcs2.append(pwc2)
        if pwc.relation == pwc2.relation:
            ok += 1

    ra_learning = float(ok) / len(pwcs)

    # Generate alternatives for the generalization
    i = ok = 0
    while i != na_gen:
        x = Alternative("x%d" % (i + 1))
        y = Alternative("y%d" % (i + 1))
        apx = generate_random_alternative_performances(x, c)
        apy = generate_random_alternative_performances(y, c)
        pwc = model.compare(apx, apy)
        if pwc.relation != pwc.INDIFFERENT:
            pwc2 = model2.compare(apx, apy)
            i += 1
            if pwc == pwc2:
                ok += 1
    pwcs.weaker_to_preferred()

    ra_test = float(ok) / na_gen

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%d" % (seed, na, nc, nsegments,
                    na_gen, pcerrors))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['nsegments'] = nsegments
    t['nprofiles2'] = nprofiles2
    t['na_gen'] = na_gen
    t['pcerrors'] = pcerrors

    # Output params
    t['ra_learning'] = ra_learning
    t['ra_test'] = ra_test
    t['t_total'] = t_total

    return t

def run_tests(options):
    na = options.na
    nc = options.nc
    nsegments = options.nsegments
    nprofiles2 = options.nprofiles2
    na_gen = options.na_gen
    pcerrors = options.pcerrors
    nseeds = options.nseeds
    filename = options.filename

    # Create the CSV writer
    f = open(filename, 'w')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['algorithm', algo.__name__])
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['nsegments', nsegments])
    writer.writerow(['nprofiles2', nprofiles2])
    writer.writerow(['na_gen', na_gen])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test_results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _nsegments, _nprofiles2,  _na_gen, _pcerrors, seed \
        in product(na, nc, nsegments, nprofiles2, na_gen, pcerrors, seeds):

        t1 = time.time()
        t = test_sat_rmp(seed, _na, _nc, _nsegments, _nprofiles2, _na_gen,
                         _pcerrors)
        t2 = time.time()

        if initialized is False:
            fields = ['seed', 'na', 'nc', 'nsegments', 'nprofiles2', 'na_gen',
                      'pcerrors', 'ra_learning', 'ra_test', 't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()

        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'nsegments', 'nprofiles2', 'na_gen',
                         'pcerrors'],
                        ['ra_learning', 'ra_test', 't_total'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    from test_utils import read_single_integer, read_multiple_integer
    from test_utils import read_csv_filename

    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])
    parser.add_option("-n", "--na", action = "store", type="string",
                      dest = "na",
                      help = "number of pairwise comparisons")
    parser.add_option("-c", "--nc", action = "store", type="string",
                      dest = "nc",
                      help = "number of criteria")
    parser.add_option("-p", "--nsegments", action = "store", type="string",
                      dest = "nsegments",
                      help = "number of profiles")
    parser.add_option("-q", "--nprofiles2", action = "store", type="string",
                      dest = "nprofiles2",
                      help = "number of profiles of learned model")
    parser.add_option("-e", "--errors", action = "store", type="string",
                      dest = "pcerrors",
                      help = "ratio of errors in the learning set")
    parser.add_option("-g", "--na_gen", action = "store", type="string",
                      dest = "na_gen",
                      help = "number of generalization pairwise comparisons")
    parser.add_option("-s", "--nseeds", action = "store", type="string",
                      dest = "nseeds",
                      help = "number of seeds")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")

    (options, args) = parser.parse_args()

    algo = SatRMP

    options.na = read_multiple_integer(options.na,
                                       "Number of pairwise comparisons")
    options.nc = read_multiple_integer(options.nc, "Number of criteria")
    options.nsegments = read_multiple_integer(options.nsegments,
                                              "Number of segments")
    options.nprofiles2 = read_multiple_integer(options.nprofiles2,
                                               "Number of profiles of learned model")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization pairwise comparisons")
    options.pcerrors = read_multiple_integer(options.pcerrors,
                                             "Ratio of errors")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "%s/test_%s-%s.csv" % (DATADIR, algo.__name__, dt)
    options.filename = read_csv_filename(options.filename, default_filename)

#    directory = options.filename + "-data"
#    if not os.path.exists(directory):
#        os.makedirs(directory)

    run_tests(options)

    print("Results saved in '%s'" % options.filename)
