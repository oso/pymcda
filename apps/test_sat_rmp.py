from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import time
import random
from itertools import product

from pymcda.types import Alternative
from pymcda.types import PairwiseRelations
from pymcda.types import PerformanceTable
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_random_criteria_values
from pymcda.generate import generate_random_alternative_performances
from pymcda.generate import generate_random_performance_table
from pymcda.rmp import RMP
from pymcda.learning.sat_rmp import SatRMP
from test_utils import test_result, test_results
from test_utils import save_to_xmcda

DATADIR = os.getenv('DATADIR', '%s/pymcda-data' % os.path.expanduser('~'))

def test_sat_rmp(seed, na, nc, nprofiles, na_gen):

    random.seed(seed)

    # Generate random RMP model
    c = generate_criteria(nc)
    cv = generate_random_criteria_values(c)
    b = [ "b%d" % i for i in range(1, nprofiles + 1)]
    random.shuffle(b)
    bpt = generate_random_profiles(b, c)
    model = RMP(c, cv, b, bpt)

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

        pt.append(apx)
        pt.append(apy)
        pwcs.append(pwc)
        i += 1

    pwcs.weaker_to_preferred()

    # Run the SAT
    t1 = time.time()

    model2 = RMP(c, None, b, None)

    satrmp = SatRMP(model2, pt, pwcs)
    solution = satrmp.solve()
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
    t = test_result("%s-%d-%d-%d-%d" % (seed, na, nc, nprofiles,
                    na_gen))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['nprofiles'] = nprofiles
    t['na_gen'] = na_gen

    # Output params
    t['ra_learning'] = ra_learning
    t['ra_test'] = ra_test
    t['t_total'] = t_total

    return t

def run_tests(na, nc, nprofiles, na_gen, nseeds, filename):
    # Create the CSV writer
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['algorithm', algo.__name__])
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['nprofiles', nprofiles])
    writer.writerow(['na_gen', na_gen])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test_results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _nprofiles, _na_gen, seed \
        in product(na, nc, nprofiles, na_gen, seeds):

        t1 = time.time()
        t = test_sat_rmp(seed, _na, _nc, _nprofiles, _na_gen)
        t2 = time.time()

        if initialized is False:
            fields = ['seed', 'na', 'nc', 'nprofiles', 'na_gen',
                      'ra_learning', 'ra_test', 't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()

        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'nprofiles', 'na_gen'],
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
    parser.add_option("-p", "--nprofiles", action = "store", type="string",
                      dest = "nprofiles",
                      help = "number of profiles")
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
    options.nprofiles = read_multiple_integer(options.nprofiles, "Number of profiles")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization pairwise comparisons")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "%s/test_%s-%s.csv" % (DATADIR, algo.__name__, dt)
    options.filename = read_csv_filename(options.filename, default_filename)

#    directory = options.filename + "-data"
#    if not os.path.exists(directory):
#        os.makedirs(directory)

    run_tests(options.na, options.nc, options.nprofiles, options.na_gen,
              options.nseeds, options.filename)

    print("Results saved in '%s'" % options.filename)
