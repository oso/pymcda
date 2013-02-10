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
from pymcda.learning.meta_etri_global2 import MetaEtriGlobal2
from pymcda.learning.meta_etri_global3 import meta_etri_global3
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.utils import add_errors_in_assignments
from test_utils import test_result, test_results

def test_meta_electre_tri_global(seed, na, nc, ncat, na_gen, pcerrors,
                                 max_oloops, nmodels, max_loops):

    # Generate a random ELECTRE TRI BM model
    model = generate_random_electre_tri_bm_model(nc, ncat, seed)

    # Generate a set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    # Add errors in assignment examples
    aa_err = aa.copy()
    aa_erroned = add_errors_in_assignments(aa_err, model.categories,
                                           pcerrors / 100)

    # Sort the performance table
    pt_sorted = SortedPerformanceTable(pt)

    # Initialize nmodels meta instances
    ncriteria = len(model.criteria)
    ncategories = len(model.categories)
    pt_sorted = SortedPerformanceTable(pt)
    model_metas = {}
    model_cas = {}
    for i in range(nmodels):
        m = generate_random_electre_tri_bm_model(ncriteria, ncategories)
        meta = algo(m, pt_sorted, aa_err)
        model_metas[m] = meta
        model_cas[meta.model] = meta.meta.good / meta.meta.na

    model_cas = sorted(model_cas.iteritems(),
                       key = lambda (k,v): (v,k),
                       reverse = True)
    t1 = time.time()

    # Perform at max oloops on the set of metas
    ca2_iter = [model_cas[0][1]] + [1] * (max_loops)
    nloops = 0
    for i in range(0, max_loops):
        model_cas = {}
        for m, meta in model_metas.items():
            model_cas[m] = meta.optimize(max_oloops)
            if model_cas[m] == 1:
                break

        model_cas = sorted(model_cas.iteritems(),
                           key = lambda (k,v): (v,k),
                           reverse = True)

        nloops += 1
        ca2_best = model_cas[0][1]

        ca2_iter[i + 1] = ca2_best

        if ca2_best == 1:
            break

        for model_ca in model_cas[int((nmodels + 1) / 2):]:
            m = model_ca[0]
            del model_metas[m]
            m = generate_random_electre_tri_bm_model(ncriteria, ncategories)
            model_metas[m] = algo(m, pt_sorted, aa_err)

    t_total = time.time() - t1

    model2 = model_cas[0][0]

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

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%g-%d-%d-%d" % (seed, na, nc, ncat,
                    na_gen, pcerrors, max_loops, nmodels, max_oloops))

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
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['algorithm', algo.__name__])
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
                      'ca_errors', 'ca2_best', 'ca2_errors', 'ca_gen',
                      'nloops', 't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()

        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'ncat', 'na_gen', 'pcerrors',
                         'max_oloops', 'nmodels', 'max_loops'],
                         ['ca_best', 'ca_errors', 'ca2_best',
                          'ca2_errors', 'ca_gen', 'nloops', 't_total'])
    t.tocsv(writer)

    # Summary by columns
    writer.writerow(['', ''])

    t = results.summary_columns(['na', 'nc', 'ncat', 'na_gen', 'pcerrors',
                                 'max_oloops', 'nmodels', 'max_loops'],
                                ['ca2_iter'], 'seed')
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    from test_utils import read_single_integer, read_multiple_integer
    from test_utils import read_csv_filename

    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])
    parser.add_option("-2", "--second", action = "store_true",
                      dest = "second", default = False,
                      help = "Second algorithm")
    parser.add_option("-3", "--third", action = "store_true",
                      dest = "third", default = False,
                      help = "Third algorithm")
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
                      help = "Max number of loops of the whole "
                             "metaheuristic")
    parser.add_option("-m", "--nmodels", action = "store", type="string",
                      dest = "nmodels",
                      help = "Size of the population (of models)")
    parser.add_option("-o", "--max_oloops", action = "store", type="string",
                      dest = "max_oloops",
                      help = "max number of loops for the metaheuristic " \
                             "used to find the profiles")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")

    (options, args) = parser.parse_args()

    while options.second is False and options.third is False:
        print("2. Random population and adapted intervals")
        print("3. Heurisitc initialized profiles and adapted intervals")
        i = raw_input("Which algorithm ? ")
        if i == '2':
            options.second = True
        elif i == '3':
            options.third = True

    i = 0
    if options.second is True:
        algo = MetaEtriGlobal2
        i += 1
    if options.third is True:
        algo = meta_etri_global3
        i += 1
    if i > 1:
        print("Cannot select multiple algorithms at the same time")
        sys.exit(1)

    options.na = read_multiple_integer(options.na,
                                       "Number of assignment examples")
    options.nc = read_multiple_integer(options.nc, "Number of criteria")
    options.ncat = read_multiple_integer(options.ncat, "Number of categories")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization alternatives")
    options.pcerrors = read_multiple_integer(options.pcerrors, "Ratio of " \
                                             "errors")
    options.max_oloops = read_multiple_integer(options.max_loops, "Max " \
                                               "number of loops for " \
                                               "profiles' metaheuristic")
    options.nmodels = read_multiple_integer(options.nmodels,
                                            "Population size (models)")
    options.max_loops = read_multiple_integer(options.max_loops, "Max " \
                                              "number of loops for the " \
                                              "whole metaheuristic")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "data/test_%s-%s.csv" % (algo.__name__, dt)
    options.filename = read_csv_filename(options.filename, default_filename)

    run_tests(options.na, options.nc, options.ncat, options.na_gen,
              options.pcerrors, options.nseeds, options.max_loops,
              options.nmodels, options.max_oloops, options.filename)

    print("Results saved in '%s'" % options.filename)
