import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import time
import datetime
from pymcda.electre_tri import MRSort
from pymcda.generate import generate_categories_profiles
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.utils import compute_ca
from pymcda.learning.meta_mrsort3 import MetaMRSortPop3
from pymcda.learning.heur_mrsort_init_profiles import HeurMRSortInitProfiles
from pymcda.learning.lp_mrsort_weights import LpMRSortWeights
from pymcda.learning.heur_mrsort_profiles4 import MetaMRSortProfiles4
from pymcda.learning.lp_mrsort_mobius import LpMRSortMobius
from pymcda.learning.heur_mrsort_profiles_choquet import MetaMRSortProfilesChoquet
from pymcda.learning.mip_mrsort import MipMRSort
from pymcda.learning.lp_avfsort import LpAVFSort
from pymcda.ui.graphic import display_electre_tri_models
from pymcda.ui.graphic_uta import display_utadis_model
from pymcda.uta import AVFSort
from pymcda.utils import compute_confusion_matrix
from pymcda.utils import print_confusion_matrix
from pymcda.utils import print_pt_and_assignments
from test_utils import load_mcda_input_data
from test_utils import save_to_xmcda

def usage():
    print("%s file.csv meta_mrsort|meta_mrsortc|mip_mrsort|lp_utadis" % sys.argv[0])
    sys.exit(1)

if len(sys.argv) != 3:
    usage()

algo = sys.argv[2]

nseg = 4
nmodels = 10
nloop = 10
nmeta = 20

data = load_mcda_input_data(sys.argv[1])

print(data.c)
worst = data.pt.get_worst(data.c)
best = data.pt.get_best(data.c)

t1 = time.time()

if algo == 'meta_mrsort':
    heur_init_profiles = HeurMRSortInitProfiles
    lp_weights = LpMRSortWeights
    heur_profiles = MetaMRSortProfiles4
elif algo == 'meta_mrsortc':
    heur_init_profiles = HeurMRSortInitProfiles
    lp_weights = LpMRSortMobius
    heur_profiles = MetaMRSortProfilesChoquet

if algo == 'meta_mrsort' or algo == 'meta_mrsortc':
    model_type = 'mrsort'
    cat_profiles = generate_categories_profiles(data.cats)
    model = MRSort(data.c, None, None, None, cat_profiles)
    pt_sorted = SortedPerformanceTable(data.pt)

    meta = MetaMRSortPop3(nmodels, model.criteria,
                          model.categories_profiles.to_categories(),
                          pt_sorted, data.aa,
                          heur_init_profiles,
                          lp_weights,
                          heur_profiles)

    for i in range(0, nloop):
        model, ca_learning = meta.optimize(nmeta)
        if ca_learning == 1:
            break
elif algo == 'mip_mrsort':
    model_type = 'mrsort'
    cat_profiles = generate_categories_profiles(data.cats)
    model = MRSort(data.c, None, None, None, cat_profiles)
    mip = MipMRSort(model, data.pt, data.aa)
    mip.solve()
elif algo == 'lp_utadis':
    model_type = 'utadis'
    css = CriteriaValues(CriterionValue(c.id, nseg) for c in data.c)
    lp = LpAVFSort(data.c, css, data.cats, worst, best)
    obj, cvs, cfs, catv = lp.solve(data.aa, data.pt)
    model = AVFSort(data.c, cvs, cfs, catv)
else:
    print("Invalid algorithm!")
    sys.exit(1)

t_total = time.time() - t1

model.id = 'learned'
data.pt.id = 'learning_set'
data.aa.id = 'learning_set'

dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
save_to_xmcda("data/%s-all-%s-%s.bz2" % (algo, data.name, dt),
              data.aa, data.pt, model)

aa2 = model.get_assignments(data.pt)

ca = compute_ca(data.aa, aa2)
auc = model.auc(data.aa, data.pt)

anok = []
for a in data.a:
    if data.aa[a.id].category_id != aa2[a.id].category_id:
        anok.append(a)

if len(anok) > 0:
    print("Alternatives wrongly assigned:")
    print_pt_and_assignments(anok, data.c, [data.aa, aa2], data.pt)

print("Model parameters:")
cids = model.criteria.keys()
if model_type == 'mrsort':
    print(model.bpt)
    print(model.cv)
    print("lambda: %.7s" % model.lbda)
#    display_electre_tri_models([model], [worst], [best])
elif model_type == 'utadis':
    model.cfs.display(criterion_ids = cids)
    model.cat_values.display()
#    display_utadis_model(model.cfs)

print("t:   %g" % t_total)
print("CA:  %g" % ca)
print("AUC: %g" % auc)

print("Confusion matrix:")
print_confusion_matrix(compute_confusion_matrix(data.aa, aa2,
                                                data.cats.get_ordered_categories()))
