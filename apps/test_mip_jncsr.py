from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import csv
import datetime
import time
import random
from itertools import product
from itertools import combinations
from collections import OrderedDict

from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.learning.mip_jncsr import MipJNCSR
from pymcda.types import PairwiseRelations, PairwiseRelation
from pymcda.types import AlternativePerformances
from pymcda.types import PerformanceTable
from pymcda.utils import add_errors_in_assignments
from pymcda.utils import compute_ca

from test_utils import save_to_xmcda

DATADIR = os.getenv('DATADIR', '%s/pymcda-data' % os.path.expanduser('~')) + '/'

def generate_random_strict_preferences(n, model):
    i = 0
    pwcs = PairwiseRelations()
    pt = PerformanceTable()
    while i < n:
        perf1 = {c.id: round(random.uniform(0, 1), 3) for c in model.criteria}
        perf2 = {c.id: round(random.uniform(0, 1), 3) for c in model.criteria}
        ap1 = AlternativePerformances(f"x{i+1}" , perf1)
        ap2 = AlternativePerformances(f"y{i+1}" , perf2)
        pwc = model.compare(ap1, ap2)
        if pwc.relation == PairwiseRelation.INDIFFERENT:
            continue

        pwc.weaker_to_preferred()

        pt.append(ap1.copy())
        pt.append(ap2.copy())
        pwcs.append(pwc.copy())
        i += 1

    return pwcs, pt

def test_mip_jncsr(params):
    random.seed(int(params["seed"]))

    m1 = generate_random_mrsort_model(params["ncrit"], params["ncat"])
    a_aa = generate_alternatives(params["naa"])
    pt_aa = generate_random_performance_table(a_aa, m1.criteria)

    aa = m1.pessimist(pt_aa)
    pwcs, pt_pwcs = generate_random_strict_preferences(params["npwcs"], m1)

    a_aa_test = generate_alternatives(params["naa_test"])
    pt_aa_test = generate_random_performance_table(a_aa_test, m1.criteria)
    pwcs_test, pt_pwcs_test = generate_random_strict_preferences(params["npwcs_test"], m1)

    pt = PerformanceTable()
    pt.update(pt_aa)
    pt.update(pt_pwcs)
    pt_test = PerformanceTable()
    pt_test.update(pt_test)
    pt_test.update(pt_pwcs_test)

    m2 = m1.copy()
    m2.cv = m2.lbda = m2.bpt = None
    mip = MipJNCSR(m2, pt, aa, pwcs)

    t1 = time.time()
    obj = mip.solve()
    t2 = time.time()

    aa_m2 = m2.pessimist(pt_aa)
    ca = compute_ca(aa, aa_m2)

    pwa = 0
    for pwc in pwcs:
        ap1 = pt_pwcs[pwc.a]
        ap2 = pt_pwcs[pwc.b]
        pwc_m2 = m2.compare(ap1, ap2)
        pwc_m2.weaker_to_preferred()
        if pwc == pwc_m2:
            pwa += 1
    pwa /= len(pwcs)

    aa_test = m1.pessimist(pt_aa_test)
    aa_test_m2 = m2.pessimist(pt_aa_test)
    ca_test = compute_ca(aa_test, aa_test_m2)

    pwa_test = 0
    for pwc in pwcs_test:
        ap1 = pt_pwcs_test[pwc.a]
        ap2 = pt_pwcs_test[pwc.b]
        pwc_m2 = m2.compare(ap1, ap2)
        pwc_m2.weaker_to_preferred()
        if pwc == pwc_m2:
            pwa_test += 1
    pwa_test /= len(pwcs_test)

    m1.id = 'initial'
    m2.id = 'learned'
    pt.id = 'learning_set'
    pt_test.id = 'test_set'
    aa.id = 'learning_set'
    aa_test.id = 'test_set'
    pwcs.id = 'learning_set'
    pwcs_test.id = 'test_set'

    data = OrderedDict()
    data["m1"] = m1
    data["m2"] = m2
    data["pt"] = pt
    data["pt_test"] = pt_test
    data["aa"] = aa
    data["aa_test"] = aa_test
    data["pwcs"] = pwcs
    data["pwcs_test"] = pwcs_test

    results = OrderedDict()
    results["objective"] = obj
    results["time"] = f"{t2-t1:.2f}"
    results["ca"] = ca
    results["pwa"] = pwa
    results["ca_test"] = ca_test
    results["pwa_test"] = pwa_test

    return data, results

def save_data(params, data, directory):
    pass

def run_test(params):
    nseed = params.pop("nseed")
    fname = params.pop("filename")

    default_name = '-'.join(map(str, params.values()))
    fname = DATADIR + default_name + '.csv' if fname is None else fname

    if os.path.exists(fname):
        f = open(fname, 'a')
    else:
        f = open(fname, 'w')

    writer = csv.writer(f)

    directory = fname + "-data"
    os.makedirs(directory, exist_ok = True)

    for i in range(nseed):
        print(f"Seed #{i}");
        dataf = f"{directory}/{default_name}-{i}.xml"
        if os.path.exists(dataf):
            continue

        params["seed"] = i
        data, results = test_mip_jncsr(params)
        save_to_xmcda(dataf, data['m1'], data['m2'],
                      data['pt'], data['pt_test'])

        if i == 0:
            row = list(params.keys()) + list(results.keys())
            writer.writerow(row)

        row = list(params.values()) + list(results.values())
        writer.writerow(row)

def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Parameters for testing MipJNCSR")
    parser.add_argument("--nseed", type=int, required=True, help="Number of seeds")
    parser.add_argument("--ncrit", type=int, required=True, help="Number of criteria")
    parser.add_argument("--ncat", type=int, required=True, help="Number of caterogies")
    parser.add_argument("--naa", type=int, required=True, help="Number of assignments in learning set")
    parser.add_argument("--npwcs", type=int, required=True, help="Number of pairwise comparisons in learning set")
    parser.add_argument("--eratio", type=float, required=True, help="Ratio of errors in learning set")
    parser.add_argument("--naa-test", type=int, required=True, help="Number of assignments in test set")
    parser.add_argument("--npwcs-test", type=int, required=True, help="Number of pairwise comparisons in test set")
    parser.add_argument("--filename", type=str, help="File in which to save results")

    args = parser.parse_args()

    return vars(args)

if __name__ == "__main__":
    params = parse_args()
    run_test(params)
#    print(args)
#
#    params = {}
#    params["seed"] = 0
#    params["ncrit"] = 3
#    params["ncat"] = 2
#    params["naa"] = 100
#    params["npwcs"] = 100
#    params["eratio"] = 0
#    params["naa_test"] = 1000
#    params["npwcs_test"] = 50000

