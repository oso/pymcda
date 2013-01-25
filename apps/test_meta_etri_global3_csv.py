import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import random
import time
from itertools import product
from algo.meta_etri_global3 import meta_etri_global3
from mcda.types import criterion_value, criteria_values
from mcda.types import alternatives, criteria, performance_table
from mcda.types import alternatives_assignments, categories
from mcda.electre_tri import electre_tri_bm
from mcda.generate import generate_alternatives
from mcda.generate import generate_categories_profiles
from mcda.generate import generate_random_profiles
from mcda.generate import generate_random_criteria_weights
from mcda.pt_sorted import sorted_performance_table
from mcda.utils import compute_ca
from test_utils import test_result, test_results

class dataset(object):

    def __init__(self, name):
        self.name = name

    def is_complete(self):
        for obj in self.__dict__:
            if obj is None:
                return False
        return True

def load_mcda_data(csvfile, obj, *field):
    csvfile.seek(0)
    csvreader = csv.reader(csvfile, delimiter = ";")
    try:
        obj = obj().from_csv(csvreader, *field)
    except:
        print("Cannot get %s" % obj())
        return None

    return obj

def load_data(filepath):
    try:
        csvfile = open(filepath, 'rb')
        csvreader = csv.reader(csvfile, delimiter = ";")
    except:
        print("Cannot open file '%s'" % filepath)
        return None

    data = dataset(os.path.basename(filepath))
    data.a = load_mcda_data(csvfile, alternatives, "pt")
    data.c = load_mcda_data(csvfile, criteria, "criterion")
    data.pt = load_mcda_data(csvfile, performance_table, "pt",
                             ["c%d" % i
                              for i in range(1, len(data.c) + 1)])
    data.aa = load_mcda_data(csvfile, alternatives_assignments,
                             "pt", "assignment")
    data.cats = load_mcda_data(csvfile, categories, "category",
                               None, "rank")

    if data.is_complete() is False:
        return None

    return data

def run_test(seed, data, pclearning, nloop, nmeta):
    random.seed(seed)

    # Separate learning data and test data
    pt_learning, pt_test = data.pt.split(2, [pclearning, 100 - pclearning])
    aa_learning = data.aa.get_subset(pt_learning.keys())
    aa_test = data.aa.get_subset(pt_test.keys())

    # Initialize a random model
    cat_profiles = generate_categories_profiles(data.cats)
    worst = data.pt.get_worst(data.c)
    best = data.pt.get_best(data.c)
    b = generate_alternatives(len(data.cats) - 1, 'b')
    bpt = generate_random_profiles(b.keys(), data.c, worst = worst,
                                   best = best)
    cvs = generate_random_criteria_weights(data.c)
    lbda = random.uniform(0.5, 1)

    model = electre_tri_bm(data.c, cvs, bpt, lbda, cat_profiles)



    # Assign learning set with the model
    aa_learning2 = model.pessimist(pt_learning)

    # Run the metaheuristic
    t1 = time.time()

    pt_sorted = sorted_performance_table(pt_learning)
    meta = meta_etri_global3(model, pt_sorted, aa_learning)
    for i in range(nloop):
        ca_learning = meta.optimize(nmeta)

        t_total = time.time() - t1

    # Compute CA of test setting
    aa_test2 = model.pessimist(data.pt)
    ca_test = compute_ca(aa_test, aa_test2)

    # Compute CA of whole set
    aa2 = model.pessimist(data.pt)
    ca = compute_ca(data.aa, aa2)

    t = test_result("%s-%d-%d-%d-%d" % (data.name, seed, nloop, nmeta,
                                        pclearning))
    t['seed'] = seed
    t['na'] = len(data.a)
    t['nc'] = len(data.c)
    t['ncat'] = len(data.cats)
    t['nloop'] = nloop
    t['nmeta'] = nmeta
    t['pclearning'] = pclearning
    t['na_learning'] = len(aa_learning)
    t['na_test'] = len(aa_test)
    t['ca_learning'] = ca_learning
    t['ca_test'] = ca_test
    t['ca_all'] = ca
    t['t_total'] = t_total

    return t

def run_tests(nseeds, data, pclearning, nloop, nmeta, filename):
    # Create the CSV writer
    f = open(filename, 'wb')
    writer = csv.writer(f)

    # Write the test options
    writer.writerow(['data', data.name])
    writer.writerow(['nloop', nloop])
    writer.writerow(['nmeta', nmeta])
    writer.writerow(['pclearning', pclearning])

    # Create a test_results instance
    results = test_results()

    # Initialize the seeds
    seeds = range(nseeds)

    # Run the algorithm
    initialized = False
    for _pclearning, _nloop, _nmeta, seed in product(pclearning, nloop,
                                                     nmeta, seeds):
        t1 = time.time()
        t = run_test(seed, data, _pclearning, _nloop, _nmeta)
        t2 = time.time()

        if initialized is False:
            fields = ['seed', 'na', 'nc', 'ncat', 'pclearning',
                      'na_learning', 'na_test', 'nloop', 'nmeta',
                      'ca_learning', 'ca_test', 'ca_all', 't_total']
            writer.writerow(fields)
            initialized = True

        t.tocsv(writer, fields)
        f.flush()
        print("%s (%5f seconds)" % (t, t2 - t1))

        results.append(t)

    # Perform a summary
    writer.writerow(['', ''])

    t = results.summary(['na', 'nc', 'ncat', 'pclearning', 'na_learning',
                         'na_test', 'nloop', 'nmeta'],
                        ['ca_learning', 'ca_test', 'ca_all', 't_total'])
    t.tocsv(writer)

if __name__ == "__main__":
    from optparse import OptionParser
    from test_utils import read_single_integer, read_multiple_integer
    from test_utils import read_csv_filename

    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])
    parser.add_option("-i", "--csvfile", action = "store", type="string",
                      dest = "csvfile",
                      help = "csv file with data")
    parser.add_option("-p", "--pclearning", action = "store", type="string",
                      dest = "pclearning",
                      help = "Percentage of data to use in learning set")
    parser.add_option("-l", "--max-loops", action = "store", type="string",
                      dest = "max_loops",
                      help = "Max number of loops of the whole "
                             "metaheuristic")
    parser.add_option("-o", "--max_oloops", action = "store", type="string",
                      dest = "max_oloops",
                      help = "max number of loops for the metaheuristic " \
                             "used to find the profiles")
    parser.add_option("-s", "--nseeds", action = "store", type="string",
                      dest = "nseeds",
                      help = "number of seeds")
    parser.add_option("-f", "--filename", action = "store", type="string",
                      dest = "filename",
                      help = "filename to save csv output")
    (options, args) = parser.parse_args()

    while not options.csvfile:
        options.csvfile = raw_input("CSV file containing data ? ")
    data = load_data(options.csvfile)
    if data is None:
        exit(1)

    options.pclearning = read_multiple_integer(options.pclearning,
                                               "Percentage of data to " \
                                               "use in the learning set")
    options.max_oloops = read_multiple_integer(options.max_oloops, "Max " \
                                               "number of loops for " \
                                               "profiles' metaheuristic")
    options.max_loops = read_multiple_integer(options.max_loops, "Max " \
                                              "number of loops for the " \
                                              "whole metaheuristic")
    options.nseeds = read_single_integer(options.nseeds, "Number of seeds")

    dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = "data/%s-%s.csv" % (data.name, dt)
    options.filename = read_csv_filename(options.filename, default_filename)

    run_tests(options.nseeds, data, options.pclearning, options.max_loops,
              options.max_oloops, options.filename)

    print("Results saved in '%s'" % options.filename)
