import sys
sys.path.insert(0, "..")
import random
from data_swd import *
from inference.meta_electre_tri_global2 import meta_electre_tri_global
from mcda.types import criterion_value, criteria_values
from mcda.electre_tri import electre_tri_bm
from tools.generate_random import generate_random_categories_profiles
from tools.generate_random import generate_random_profiles
from tools.generate_random import generate_random_criteria_weights
from tools.sorted import sorted_performance_table
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances
from tools.utils import compute_ac

cat_profiles = generate_random_categories_profiles(cats)
worst = get_worst_alternative_performances(pt, c)
best = get_best_alternative_performances(pt, c)
b = ["b%d" % i for i in range(1, len(cats))]

bpt = generate_random_profiles(b, c, worst = worst, best = best, seed = 3)
cvs = generate_random_criteria_weights(c)
lbda = random.uniform(0.5, 1)

model = electre_tri_bm(c, cvs, bpt, lbda, cat_profiles)
aa2 = model.pessimist(pt)

print "CA original:", compute_ac(aa, aa2)

pt_sorted = sorted_performance_table(pt)

meta = meta_electre_tri_global(model, pt_sorted, aa)

for i in range(20):
    print meta.optimize(20)
