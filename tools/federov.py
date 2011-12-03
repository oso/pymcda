import sys
sys.path.insert(0, "..")
import random
import logging
from numpy import matrix, multiply, transpose, linalg
from mcda.types import alternatives, performance_table

FORMAT = '%(asctime)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

def generate_init_plan(a, pt, n):
    a_in = alternatives()
    pt_in = performance_table()
    while len(a_in) < n:
        j = random.randint(0, len(a)-1)
        alt = a[j]
        if alt not in a_in:
            a_in.append(alt)
            pt_in.append(pt(alt.id))

    return (a_in, pt_in)

def get_vector_of_evaluations(ap, c):
    perfs = []
    for crit in c:
        if crit.disabled:
            continue
        perfs.append(ap.performances[crit.id])
    return perfs

def get_matrix_of_evaluation(pt, c):
    perfs_m = []
    for ap in pt:
        perfs = get_vector_of_evaluations(ap, c)
        perfs_m.append(perfs)
    return matrix(perfs_m)

def compute_xtx(pt, c):
    x = get_matrix_of_evaluation(pt, c)
    xt = transpose(x)
    return xt*x

def update_xtx(xtx, ap_i, ap_j, c):
    perfs_i = matrix(get_vector_of_evaluations(ap_i, c))
    perfs_j = matrix(get_vector_of_evaluations(ap_j, c))
    perfs_it = transpose(perfs_i)
    perfs_jt = transpose(perfs_j)
    return xtx - (perfs_it*perfs_i) + (perfs_jt*perfs_j)

def compute_d_criterion(xtx, n):
    d = linalg.det(xtx)
    return d/n

def federov(a, c, pt, n, p0_a=None, p0_pt=None):
    # a = alternatives
    # c = criteria
    # pt = performance table
    # n = number of candidates

    # Generate initial plan
    if p0_a and p0_pt:
        p_a = p0_a
        p_pt = p0_pt
    else:
        p_a, p_pt = generate_init_plan(a, pt, n)

    # Compute D criterion
    xtx = compute_xtx(p_pt, c)
    d = compute_d_criterion(xtx, n) 
    logging.debug("D = %g" % d)

    # Optimisation cycle
    z=0
    d1 = d
    while True:
        z += 1
        alt_i_to_del = None
        alt_j_to_add = None
        for i, alt_i in enumerate(p_a):
            for j, alt_j in enumerate(a):
                if alt_i == alt_j or alt_j in p_a:
                    continue

                xtx_temp = update_xtx(xtx, pt(alt_i.id), pt(alt_j.id), c)
                d_temp = compute_d_criterion(xtx_temp, n)

                if d_temp > d1:
                    alt_i_to_del = alt_i
                    alt_j_to_add = alt_j
                    xtx1 = xtx_temp
                    d1 = d_temp

        if not alt_i_to_del and not alt_j_to_add:
            break

        i = p_a.index(alt_i_to_del)
        p_a[i] = alt_j_to_add

        alt_i_p = pt(alt_i_to_del.id)
        alt_j_p = pt(alt_j_to_add.id)
        i = p_pt.index(alt_i_p)
        p_pt[i] = alt_j_p

        logging.debug("D = %g" % d1)

        xtx = xtx1

    return (p_a, p_pt)

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_performance_table

    a = generate_random_alternatives(1000)
    c = generate_random_criteria(2)
    pt = generate_random_performance_table(a, c)

    p_a, p_pt = federov(a, c, pt, 4)

    import pprint
    pprint.pprint(p_a)
    pprint.pprint(p_pt)
