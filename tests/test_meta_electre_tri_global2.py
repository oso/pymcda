from __future__ import division
import csv
import datetime
import sys
sys.path.insert(0, "..")
import time
import random
from itertools import product

from mcda.types import alternatives_affectations, performance_table
from mcda.electre_tri import electre_tri
from inference.meta_electre_tri_global2 import meta_electre_tri_global
from tools.utils import compute_ac
from tools.sorted import sorted_performance_table
from tools.generate_random import generate_random_electre_tri_bm_model
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_performance_table
from tools.utils import normalize_criteria_weights
from tools.utils import add_errors_in_affectations
from test_utils import test_result, test_results

def test_meta_electre_tri_global(seed, na, nc, ncat, na_gen, pcerrors,
                                 max_oloops, nmodels, max_loops):

    # Generate a random ELECTRE TRI BM model
    model = generate_random_electre_tri_bm_model(nc, ncat, seed)

    # Generate a set of alternatives
    a = generate_random_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    # Add errors in assignment examples
    aa_err = aa.copy()
    aa_erroned = add_errors_in_affectations(aa_err, model.categories,
                                            pcerrors)

    # Sort the performance table
    pt_sorted = sorted_performance_table(pt)

    # Initialize nmodels meta instances
    ncriteria = len(model.criteria)
    ncategories = len(model.categories)
    pt_sorted = sorted_performance_table(pt)
    metas = []
    models_ca = {}
    for i in range(nmodels):
        model_meta = generate_random_electre_tri_bm_model(ncriteria,
                                                          ncategories)
        meta = meta_electre_tri_global(model_meta, pt_sorted, aa)
        metas.append(meta)
        models_ca[meta.model] = meta.meta.good / meta.meta.na

    models_ca = sorted(models_ca.iteritems(),
                       key = lambda (k,v): (v,k),
                       reverse = True)

    t1 = time.time()

    # Perform at max oloops on the set of metas
    ca2_iter = [models_ca[0][1]] + [1] * (max_oloops)
    nloops = 0
    for i in range(0, max_oloops):
        models_ca = {}
        for meta in metas:
            m = meta.model
            print m
            ca2 = meta.optimize(max_loops)
            models_ca[m] = ca2

            if ca2 == 1:
                break

        models_ca = sorted(models_ca.iteritems(),
                           key = lambda (k,v): (v,k),
                           reverse = True)

        nloops += 1
        ca2_best = models_ca[0][1]

        ca2_iter[i + 1] = ca2_best

        if ca2_best == 1:
            break

        for j in range(int((nmodels + 1) / 2), nmodels):
            model_meta = generate_random_electre_tri_bm_model(ncriteria,
                                                              ncategories)
            metas[j] = meta_electre_tri_global(model_meta, pt_sorted, aa)

    t_total = time.time() - t1

    model2 = models_ca[0][0]

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
    a_gen = generate_random_alternatives(na_gen)
    pt_gen = generate_random_performance_table(a_gen, model.criteria)
    aa_gen = model.pessimist(pt_gen)
    aa_gen2 = model2.pessimist(pt_gen)
    ca_gen = compute_ac(aa_gen, aa_gen2)

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%g-%d" % (seed, na, nc, ncat, na_gen,
                    pcerrors, max_loops))

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['na_gen'] = na_gen
    t['pcerrors'] = pcerrors
    t['max_loops'] = max_loops
    t['nmodels'] = nmodels
    t['max_oloops'] = max_oloops

    # Ouput params
    t['ca_best'] = ca_best
    t['ca_errors'] = ca_errors
    t['ca2_best'] = ca2_best
    t['ca2_errors'] = ca2_errors
    t['ca_gen'] = ca_gen
    t['nloops'] = nloops
    t['t_total'] = t_total

    t['ca2_iter'] = ca2_iter

    return t

def run_tests(na, nc, ncat, na_gen, pcerrors, nseeds, max_loops, nmodels,
              max_oloops, filename):
    # Create the CSV writer
    writer = csv.writer(open(filename, 'wb'))

    # Write the test options
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
    writer.writerow(['na_gen', na_gen])
    writer.writerow(['pcerrors', pcerrors])
    writer.writerow(['nseeds', nseeds])
    writer.writerow(['max_loops', max_loops])
    writer.writerow(['nmodels', nmodels])
    writer.writerow(['max_oloops', max_oloops])
    writer.writerow(['', ''])

    # Create a test_results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _na, _nc, _ncat, _na_gen, _pcerrors, _max_oloops, _nmodels, \
        _max_loops, seed \
        in product(na, nc, ncat, na_gen, pcerrors, max_oloops, nmodels,
                   max_loops, seeds):

        t1 = time.time()
        t = test_meta_electre_tri_global(seed, _na, _nc, _ncat, _na_gen,
                                         _pcerrors, _max_oloops, _nmodels,
                                         _max_loops)
        t2 = time.time()

        if initialized is False:
            fields = ['seed', 'na', 'nc', 'ncat', 'na_gen', 'pcerrors',
                      'max_oloops', 'nmodels', 'max_loops', 'ca_best',
                      'ca_errors', 'ca2_best', 'ca2_errors', 'nloops',
                      't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'ncat', 'na_gen', 'pcerrors',
                         'max_oloops', 'nmodels', 'max_loops'],
                         ['ca_best', 'ca_errors', 'ca2_best',
                          'ca2_errors', 'nloops', 't_total'])
    t.tocsv(writer)

    # Summary by columns
    writer.writerow(['', ''])

    t = results.summary_columns(['na', 'nc', 'ncat', 'na_gen', 'pcerrors',
                                 'max_oloops', 'nmodels', 'max_loops'],
                                ['ca2_iter'], 'seed')
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser

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
    parser.add_option("-l", "--max-loops", action = "store", type="string",
                      dest = "max_loops",
                      help = "max number of loops for the metaheuristic " \
                             "used to find the profiles")
    parser.add_option("-m", "--nmodels", action = "store", type="string",
                      dest = "nmodels",
                      help = "Size of the population (of models)")
    parser.add_option("-o", "--max_oloops", action = "store", type="string",
                      dest = "max_oloops",
                      help = "Max number of loops of the whole "
                             "metaheuristic")
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

    while not options.na_gen:
        options.na_gen = raw_input("Number of generalization " \
                                   "alternatives ? ")
    options.na_gen = options.na_gen.split(",")
    options.na_gen = [ int(x) for x in options.na_gen ]

    while not options.pcerrors:
        options.pcerrors = raw_input("Ratio of errors ? ")
    options.pcerrors = options.pcerrors.split(",")
    options.pcerrors = [ float(x) for x in options.pcerrors ]

    while not options.max_loops:
        options.max_loops = raw_input("Max number of loops for profiles' " \
                                      "metaheuristic ? ")
    options.max_loops = options.max_loops.split(",")
    options.max_loops = [ int(x) for x in options.max_loops ]

    while not options.nmodels:
        options.nmodels = raw_input("Population size (models) ? ")
    options.nmodels = options.nmodels.split(",")
    options.nmodels = [ int(x) for x in options.nmodels ]

    while not options.max_oloops:
        options.max_oloops = raw_input("Max number of loops for the " \
                                       "whole metaheuristic ? ")
    options.max_oloops = options.max_oloops.split(",")
    options.max_oloops = [ int(x) for x in options.max_oloops ]

    while not options.nseeds:
        options.nseeds = raw_input("Number of seeds ? ")
    options.nseeds = int(options.nseeds)

    while not options.filename:
        dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        default_filename = "data/test_meta_electre_tri_global-%s.csv" % dt
        options.filename = raw_input("File to save CSV data [%s] ? " \
                                     % default_filename)
        if not options.filename:
            options.filename = default_filename

    if options.filename[-4:] != ".csv":
        options.filename += ".csv"

    run_tests(options.na, options.nc, options.ncat, options.na_gen,
              options.pcerrors, options.nseeds, options.max_loops,
              options.nmodels, options.max_oloops, options.filename)

    print("Results saved in '%s'" % options.filename)
