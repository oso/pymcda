from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import time
import random
from itertools import product

from pymcda.types import AlternativesAssignments, PerformanceTable
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.electre_tri import MRSort
from pymcda.learning.mip_mrsort_veto import MipMRSortVC
from pymcda.learning.mip_mrsort import MipMRSort
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
from pymcda.generate import generate_random_mrsort_model_with_binary_veto
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.utils import add_errors_in_assignments_proba
from pymcda.utils import compute_confusion_matrix
from test_utils import test_result, test_results
from test_utils import save_to_xmcda

def test_mip_mrsort_vc(seed, na, nc, ncat, na_gen, veto_param, pcerrors):

    # Generate a random ELECTRE TRI BM model
    if vetot == 'binary':
        model = generate_random_mrsort_model_with_binary_veto(nc, ncat,
                            seed,
                            veto_func = veto_func,
                            veto_param = veto_param)
    elif vetot == 'coalition':
        model = generate_random_mrsort_model_with_coalition_veto(nc, ncat,
                            seed,
                            veto_weights = True,
                            veto_func = veto_func,
                            veto_param = veto_param)

    # Generate a set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)
    nv_m1_learning = sum([model.count_veto_pessimist(ap) for ap in pt])

    # Add errors in assignment examples
    aa_err = aa.copy()
    aa_erroned = add_errors_in_assignments_proba(aa_err,
                                                 model.categories,
                                                 pcerrors / 100)
    na_err = len(aa_erroned)

    # Run the MIP
    t1 = time.time()

    model2 = MRSort(model.criteria, None, None, None,
                    model.categories_profiles, None, None, None)
    if vetot == 'binary':
        w = {c.id: 1 / len(model.criteria) for c in model.criteria}
        w1 = w.keys()[0]
        w[w1] += 1 - sum(w.values())
        model2.veto_weights = CriteriaValues([CriterionValue(c.id,
                                                             w[c.id])
                                              for c in model.criteria])
        model2.veto_lbda = min(w.values())

    mip = algo(model2, pt, aa)
    mip.solve()

    t_total = time.time() - t1

    # Determine the number of erroned alternatives badly assigned
    aa2 = model2.pessimist(pt)
    nv_m2_learning = sum([model2.count_veto_pessimist(ap) for ap in pt])
    cmatrix_learning = compute_confusion_matrix(aa, aa2, model.categories)

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
    nv_m1_gen = sum([model.count_veto_pessimist(ap) for ap in pt_gen])
    nv_m2_gen = sum([model2.count_veto_pessimist(ap) for ap in pt_gen])
    if len(aa_gen) > 0:
        cmatrix_gen = compute_confusion_matrix(aa_gen, aa_gen2,
                                               model.categories)
    ca_gen = compute_ca(aa_gen, aa_gen2)

    aa_gen_err = aa_gen.copy()
    aa_gen_erroned = add_errors_in_assignments_proba(aa_gen_err,
                                                     model.categories,
                                                     pcerrors / 100)
    aa_gen2 = model2.pessimist(pt_gen)
    ca_gen_err = compute_ca(aa_gen_err, aa_gen2)

    # Save all infos in test_result class
    t = test_result("%s-%d-%d-%d-%d-%d-%d" % (seed, na, nc, ncat,
                    na_gen, veto_param, pcerrors))

    model.id = 'initial'
    model2.id = 'learned'
    a.id, pt.id = 'learning_set', 'learning_set'
    aa.id, aa2.id = 'learning_set_m1', 'learning_set_m2'
    a_gen.id, pt_gen.id = 'test_set', 'test_set'
    aa_gen.id, aa_gen2.id = 'test_set_m1', 'test_set_m2'
    save_to_xmcda("%s/%s" % (directory, t.test_name),
                  model, model2, a, a_gen, pt, pt_gen, aa, aa2,
                  aa_gen, aa_gen2)

    # Input params
    t['seed'] = seed
    t['na'] = na
    t['nc'] = nc
    t['ncat'] = ncat
    t['na_gen'] = na_gen
    t['veto_param'] = veto_param
    t['pcerrors'] = pcerrors

    # Ouput params
    t['na_err'] = na_err
    t['nv_m1_learning'] = nv_m1_learning
    t['nv_m2_learning'] = nv_m2_learning
    t['nv_m1_gen'] = nv_m1_gen
    t['nv_m2_gen'] = nv_m2_gen
    t['ca_best'] = ca_best
    t['ca_errors'] = ca_errors
    t['ca_gen'] = ca_gen
    t['ca_gen_err'] = ca_gen_err
    t['t_total'] = t_total

    for k, v in cmatrix_learning.items():
        t['learn_%s_%s' % (k[0], k[1])] = v
    for k, v in cmatrix_gen.items():
        t['test_%s_%s' % (k[0], k[1])] = v

    return t

def run_tests(na, nc, ncat, na_gen, pcerrors, nseeds,
              vetot, vetom, vparam, filename):
    # Create the CSV writer
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['algorithm', algo.__name__])
    writer.writerow(['veto type', vetot])
    writer.writerow(['veto mode', vetom])
    writer.writerow(['veto param', vparam])
    writer.writerow(['na', na])
    writer.writerow(['nc', nc])
    writer.writerow(['ncat', ncat])
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
    for _na, _nc, _ncat, _na_gen, _vparam, _pcerrors, seed \
        in product(na, nc, ncat, na_gen, vparam, pcerrors, seeds):

        t1 = time.time()
        t = test_mip_mrsort_vc(seed, _na, _nc, _ncat, _na_gen,
                               _vparam, _pcerrors)
        t2 = time.time()

        if initialized is False:
            fields = t.get_attributes()
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()

        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'ncat', 'na_gen', 'veto_param',
                         'pcerrors'],
                        ['na_err', 'nv_m1_learning', 'nv_m2_learning',
                         'nv_m1_gen', 'nv_m2_gen', 'ca_best', 'ca_errors',
                         'ca_gen', 'ca_gen_err', 't_total'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    from test_utils import read_single_integer, read_multiple_integer
    from test_utils import read_multiple_float
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
    parser.add_option("-m", "--model", action = "store", type="string",
                      dest = "model",
                      help = "learn a model with (veto) or without veto " \
                             "(noveto)")
    parser.add_option("-y", "--vetotype", action = "store", type="string",
                      dest = "vetot",
                      help = "Type of veto (binary/coalition) ")
    parser.add_option("-v", "--vetomode", action = "store", type="string",
                      dest = "vetom",
                      help = "Mode of veto (absolute/proportional) ")
    parser.add_option("-p", "--vetoparam", action = "store", type="string",
                      dest = "vparam",
                      help = "Mode of veto (absolute/proportional) ")

    (options, args) = parser.parse_args()

    while options.model is None or (options.model != 'veto'
                                    and options.model != 'noveto'):
        print("1. Model with veto")
        print("2. Model without veto")
        i = raw_input("Which type of model to learn? ")
        if i == '1':
            options.model = 'veto'
        elif i == '2':
            options.model = 'noveto'

    if options.model == 'veto':
        algo = MipMRSortVC
    elif options.model == 'noveto':
        algo = MipMRSort

    while options.vetot is None or (options.vetot != 'binary'
                                    and options.vetot != 'coalition'):
        print("1. Model with BINARY veto")
        print("2. Model with COALITION veto")
        i = raw_input("What type of veto? ")
        if i == '1':
            options.vetot = 'binary'
        elif i == '2':
            options.vetot = 'coalition'

    vetot = options.vetot

    if options.vetom is None or (options.vetom != 'absolute'
                                 and options.vetom != 'proportional'):
        print("1. ABSOLUTE veto")
        print("2. PROPORTIONAL veto")
        i = raw_input("What mode of veto? ")
        if i == '1':
            options.vetom = 'absolute'
        elif i == '2':
            options.vetom = 'proportional'

    vetom = options.vetom
    if vetom == 'absolute':
        veto_func = 1
    elif vetom == 'proportional':
        veto_func = 2

    options.vparam = read_multiple_float(options.vparam,
                                         "Value of the veto param")
    options.na = read_multiple_integer(options.na,
                                       "Number of assignment examples")
    options.nc = read_multiple_integer(options.nc, "Number of criteria")
    options.ncat = read_multiple_integer(options.ncat, "Number of categories")
    options.na_gen = read_multiple_integer(options.na_gen, "Number of " \
                                           "generalization alternatives")
    options.pcerrors = read_multiple_integer(options.pcerrors, "Ratio of " \
                                             "errors")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "data/test_%s-%s.csv" % ("mip_mrsort_veto", dt)
    options.filename = read_csv_filename(options.filename, default_filename)

    directory = "data/test_%s-%s" % ("mip_mrsort_veto", dt)
    if not os.path.exists(directory):
        os.makedirs(directory)

    run_tests(options.na, options.nc, options.ncat, options.na_gen,
              options.pcerrors, options.nseeds,
              options.vetot, options.vetom, options.vparam,
              options.filename)

    print("Results saved in '%s'" % options.filename)
