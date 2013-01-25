from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import time
import csv
from itertools import product

from mcda.generate import generate_random_electre_tri_bm_model
from mcda.generate import generate_alternatives
from mcda.generate import generate_random_performance_table
from mcda.generate import generate_random_profiles
from mcda.pt_sorted import sorted_performance_table
from mcda.utils import add_errors_in_assignments
from mcda.utils import compute_ca
from algo.heur_etri_profiles import heur_etri_profiles
from algo.heur_etri_coalitions import heur_etri_coalitions
from algo.lp_electre_tri_weights import lp_electre_tri_weights
from test_utils import test_result, test_results

def test_heur_etri_profiles(seed, na, nc, ncat, pcerrors):
    # Generate an ELECTRE TRI model and assignment examples
    model = generate_random_electre_tri_bm_model(nc, ncat, seed)
    model2 = model.copy()
    model3 = model.copy()

    # Generate a first set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)

    # Compute assignments
    aa = model.pessimist(pt)

    # Initialize the second model with random generated profiles
    b = model.categories_profiles.get_ordered_profiles()
    model2.bpt = generate_random_profiles(b, model2.criteria)

    # Run the heuristic
    cats = model.categories_profiles.to_categories()
    pt_sorted = sorted_performance_table(pt)
    heur = heur_etri_profiles(model3.criteria, pt_sorted, aa, cats)
    model3.bpt = heur.solve()

    # Learn the weights and cut threshold
    cps = model.categories_profiles

    lp_weights = lp_electre_tri_weights(model2, pt, aa, cps)
    lp_weights.solve()

    lp_weights = lp_electre_tri_weights(model3, pt, aa, cps)
    lp_weights.solve()

    # Compute the classification accuracy
    aa2 = model2.pessimist(pt)
    aa3 = model3.pessimist(pt)

    ca2 = compute_ca(aa, aa2)
    ca3 = compute_ca(aa, aa3)

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%g" % (seed, na, nc, ncat, pcerrors))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['pcerrors'] = pcerrors

    # Output params
    t['ca_rdom'] = ca2
    t['ca_heur'] = ca3

    return t

def run_tests(na, nc, ncat, pcerrors, nseeds, filename):
    # Create the CSV writer
    writer = csv.writer(open(filename, 'wb'))

    # Write the test options
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _ncat, _pcerrors, seed \
        in product(na, nc, ncat, pcerrors, seeds):

        t1 = time.time()
        t = test_heur_etri_profiles(seed, _na, _nc, _ncat, _pcerrors)
        t2 = time.time()

        if initialized is False:
            writer.writerow(t.get_attributes())
            initialized = True

        t.tocsv(writer)
        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])
    t = results.summary(['na', 'nc', 'ncat', 'pcerrors'],
                        ['ca_rdom', 'ca_heur'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    import datetime

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
    parser.add_option("-p", "--pcexamples", action = "store", type="string",
                      dest = "pcexamples",
                      help = "ratio of examples to use")
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

    while not options.na:
        options.na = raw_input("Number of assignment examples ? ")
    options.na = options.na.split(",")
    options.na = [ int(x) for x in options.na ]

    while not options.nc:
        options.nc = raw_input("Number of criteria ? ")
    options.nc = options.nc.split(",")
    options.nc = [ int(x) for x in options.nc ]

    while not options.ncat:
        options.ncat = raw_input("Number of categories ? ")
    options.ncat = options.ncat.split(",")
    options.ncat = [ int(x) for x in options.ncat ]

    while not options.pcerrors:
        options.pcerrors = raw_input("Ratio of errors ? ")
    options.pcerrors = options.pcerrors.split(",")
    options.pcerrors = [ float(x) for x in options.pcerrors ]

    while not options.nseeds:
        options.nseeds = raw_input("Number of seeds ? ")
    options.nseeds = int(options.nseeds)

    while not options.filename:
        dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_filename = "data/test_heur_etri_profiles-%s.csv" % dt
        options.filename = raw_input("File to save CSV data [%s] ? " \
                                     % default_filename)
        if not options.filename:
            options.filename = default_filename

    if options.filename[-4:] != ".csv":
        options.filename += ".csv"

    run_tests(options.na, options.nc, options.ncat, options.pcerrors,
              options.nseeds, options.filename)

    print("Results saved in '%s'" % options.filename)
