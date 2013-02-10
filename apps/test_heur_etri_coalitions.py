from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import time
import csv
from itertools import product

from pymcda.learning.heur_etri_coalitions import HeurEtriCoalitions
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.utils import compute_winning_coalitions
from pymcda.utils import add_errors_in_assignments
from test_utils import test_result, test_results

def test_heur_etri_coalitions(seed, na, nc, ncat, pcexamples, pcerrors):
    # Generate an ELECTRE TRI model and assignment examples
    model = generate_random_electre_tri_bm_model(nc, ncat, seed)

    # Generate a first set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)

    # Compute assignments
    aa = model.pessimist(pt)

    # Run the heuristic
    heur = HeurEtriCoalitions(model.criteria, model.categories,
                                       pt, aa)
    coal2 = heur.find_coalitions(int(na * pcexamples))

    # Compute the original winning coallitions
    coal = compute_winning_coalitions(model.cv, model.lbda)

    # Compare orignal and computed coalitions
    coal_ni = list((set(coal) ^ set(coal2)) & set(coal))
    coal_add = list((set(coal) ^ set(coal2)) & set(coal2))

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%g-%g" % (seed, na, nc, ncat, pcexamples,
                    pcerrors))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['pcexamples'] = pcexamples
    t['pcerrors'] = pcerrors

    # Output params
    t['ncoal'] = len(coal)
    t['ncoal_ni'] = len(coal_ni)
    t['ncoal_add'] = len(coal_add)

    return t

def run_tests(na, nc, ncat, pcexamples, pcerrors, nseeds, filename):
    # Create the CSV writer
    writer = csv.writer(open(filename, 'wb'))

    # Write the test options
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
    writer.writerow(['pcexamples', pcexamples])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['', ''])

    # Create a test results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _ncat, _pcexamples, _pcerrors, seed \
        in product(na, nc, ncat, pcexamples, pcerrors, seeds):

        t1 = time.time()
        t = test_heur_etri_coalitions(seed, _na, _nc, _ncat, _pcexamples,
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
    t = results.summary(['na', 'nc', 'ncat', 'pcexamples', 'pcerrors'],
                        ['ncoal', 'ncoal_ni', 'ncoal_add'])
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
                      help = "percentage of examples to use")
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

    while not options.pcexamples:
        options.pcexamples = raw_input("Percentage of examples ? ")
    options.pcexamples = options.pcexamples.split(",")
    options.pcexamples = [ float(x) for x in options.pcexamples ]

    while not options.pcerrors:
        options.pcerrors = raw_input("Ratio of errors ? ")
    options.pcerrors = options.pcerrors.split(",")
    options.pcerrors = [ float(x) for x in options.pcerrors ]

    while not options.nseeds:
        options.nseeds = raw_input("Number of seeds ? ")
    options.nseeds = int(options.nseeds)

    while not options.filename:
        dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_filename = "data/test_heur_etri_coalitions-%s.csv" % dt
        options.filename = raw_input("File to save CSV data [%s] ? " \
                                     % default_filename)
        if not options.filename:
            options.filename = default_filename

    if options.filename[-4:] != ".csv":
        options.filename += ".csv"

    run_tests(options.na, options.nc, options.ncat, options.pcexamples,
              options.pcerrors, options.nseeds, options.filename)

    print("Results saved in '%s'" % options.filename)
