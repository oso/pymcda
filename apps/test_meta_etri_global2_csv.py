import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import random
from algo.meta_electre_tri_global2 import meta_electre_tri_global
from mcda.types import criterion_value, criteria_values
from mcda.types import alternatives, criteria, performance_table
from mcda.types import alternatives_assignments, categories
from mcda.electre_tri import electre_tri_bm
from mcda.generate import generate_categories_profiles
from mcda.generate import generate_random_profiles
from mcda.generate import generate_random_criteria_weights
from tools.sorted import sorted_performance_table
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances
from tools.utils import compute_ca

def load_data(filepath):
    ok = True

    try:
        csvfile = open(filepath, 'rb')
        csvreader = csv.reader(csvfile, delimiter = ";")
    except:
        print("Cannot open file %s" % filepath)
        return False

    try:
        global a
        a = alternatives().from_csv(csvreader, "pt")
    except:
        print("Cannot get alternatives")
        ok = False

    try:
        global c
        csvfile.seek(0)
        c = criteria().from_csv(csvreader, "criterion")
    except:
        print("Cannot get criteria")
        ok = False

    try:
        global pt
        csvfile.seek(0)
        pt = performance_table().from_csv(csvreader, "pt",
                                          ["c%d" % i for i in range(1, 11)])
    except:
        print("Cannot get performance table")
        ok = False

    try:
        global aa
        csvfile.seek(0)
        aa = alternatives_assignments().from_csv(csvreader, "pt",
                                                 "assignment")
    except:
        print("Cannot get alternatives assignments")
        ok = False

    try:
        global cats
        csvfile.seek(0)
        cats = categories().from_csv(csvreader, "category",
                                     rank_col = "rank")
    except:
        print("Cannot get categories")
        ok = False

    return ok

def usage(pname):
    print("usage: %s csvfile" % pname)

if len(sys.argv) != 2:
    usage(sys.argv[0])
    exit(1)

if load_data(sys.argv[1]) is False:
    exit(1)

cat_profiles = generate_categories_profiles(cats)
worst = get_worst_alternative_performances(pt, c)
best = get_best_alternative_performances(pt, c)
b = ["b%d" % i for i in range(1, len(cats))]

bpt = generate_random_profiles(b, c, worst = worst, best = best, seed = 3)
cvs = generate_random_criteria_weights(c)
lbda = random.uniform(0.5, 1)

model = electre_tri_bm(c, cvs, bpt, lbda, cat_profiles)
aa2 = model.pessimist(pt)

print "CA original:", compute_ca(aa, aa2)

pt_sorted = sorted_performance_table(pt)

meta = meta_electre_tri_global(model, pt_sorted, aa)

for i in range(20):
    print meta.optimize(20)
