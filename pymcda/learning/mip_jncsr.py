from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import PairwiseRelations, PairwiseRelation
import pulp

verbose = True

class MipJNCSR():

    def __init__(self, model, pt, aa, pwcs, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa if aa is not None else set()
        self.pwcs = pwcs
        self.model = model
        self.criteria = model.criteria.get_active()
        self.cps = model.categories_profiles

        self.epsilon = epsilon

        self.__alternatives = set()
        if aa:
            self.__alternatives |= set(self.aa.keys())
        if pwcs:
            self.__alternatives |= set(self.pwcs.get_alternatives())
        self.__profiles = self.cps.get_ordered_profiles()
        self.__categories = self.cps.get_ordered_categories()

        self.pt.update_direction(model.criteria)

        if self.model.bpt is not None:
            self.model.bpt.update_direction(model.criteria)

            tmp_pt = self.pt.copy()
            for bp in self.model.bpt:
                tmp_pt.append(bp)

            self.ap_min = tmp_pt.get_min()
            self.ap_max = tmp_pt.get_max()
            self.ap_range = tmp_pt.get_range()
        else:
            self.ap_min = self.pt.get_min()
            self.ap_max = self.pt.get_max()
            self.ap_range = self.pt.get_range()

        for c in self.criteria:
            self.ap_min.performances[c.id] -= self.epsilon
            self.ap_max.performances[c.id] += self.epsilon
            self.ap_range.performances[c.id] += 2 * self.epsilon * 100

        self.pt.update_direction(model.criteria)
        if self.model.bpt is not None:
            self.model.bpt.update_direction(model.criteria)

        self.lp = pulp.LpProblem("JNCSR", pulp.LpMaximize)
        self.variables = self.add_variables()
        self.add_objective()
        self.add_constraints()

    def add_variables(self):
        variables = {}

        # w_i
        for c in self.criteria:
            name = f"w_{c.id}"
            variables[name] = pulp.LpVariable(name, lowBound=0, upBound=1)

        # lambda
        variables["lambda"] = pulp.LpVariable("lambda", lowBound=0.5, upBound=1)

        # b_i^h
        for c, h in product(self.criteria, self.__profiles):
            name = f"b_{c.id},{h}"
            variables[name] = pulp.LpVariable(name,
                                              lowBound=self.ap_min.performances[c.id],
                                              upBound=self.ap_max.performances[c.id] + self.epsilon)
        # delta_i(x,b^h)
        for c, a, bh in product(self.criteria, self.__alternatives, self.__profiles):
            name = f"delta_{c.id}({a},{bh})"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # w_i(x,b^h)
        for c, a, bh in product(self.criteria, self.__alternatives, self.__profiles):
            name = f"w_{c.id}({a},{bh})"
            variables[name] = pulp.LpVariable(name, lowBound=0, upBound=1)

        # y_{x,h}
        for a, h in product(self.__alternatives, self.__categories):
            name = f"y_{a},{h}"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # sigma^{cat}(x,x')
        for pwc in self.pwcs:
            name = f"sigmac({pwc.a},{pwc.b})"
            variables[name] = pulp.LpVariable(name, lowBound=0,
                                              upBound=len(self.__profiles))

        # epsilon_{x,x',h}
        for pwc, h in product(self.pwcs, self.__categories):
            name = f"epsilon_{pwc.a},{pwc.b},{h}"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # sigma1(x,x',h)
        for pwc, h in product(self.pwcs, self.__categories[1:]):
            name = f"sigma1({pwc.a},{pwc.b},{h})"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # sigma2(x,x',h)
        for pwc, h in product(self.pwcs, self.__categories[:-1]):
            name = f"sigma2({pwc.a},{pwc.b},{h})"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # eta(x,x',h)
        for pwc, h in product(self.pwcs, self.__categories[1:-1]):
            name = f"eta({pwc.a},{pwc.b},{h})"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        # compm(x,x')
        for pwc in self.pwcs:
            name = f"compm({pwc.a},{pwc.b})"
            variables[name] = pulp.LpVariable(name, cat='Binary')

        return variables

    def add_dominance_constraint(self):
        lp = self.lp
        v = self.variables

        profiles = self.cps.get_ordered_profiles()
        for h, c in product(range(len(profiles) - 1), self.criteria):
            # g_j(b_h) <= g_j(b_{h+1})
            lp += v[f"b_{c.id},{profiles[h]}"] - v[f"b_{c.id},{profiles[h + 1]}"] <= 0

        if self.model.bpt is not None:
            for bp, c in product(self.model.bpt, self.model.criteria):
                lp += v[f"b_{c.id},{bp.id}"] == bp.performances[c.id]

    def add_weights_constraint(self):
        lp = self.lp
        v = self.variables

        if self.model.cv is None:
            # sum w_j = 1
            lp += pulp.lpSum(v[f"w_{c.id}"] for c in self.criteria) == 1
        else:
            for c in self.criteria:
                lp += v[f"w_{c.id}"] == self.model.cv[c.id].value

        if self.model.lbda is not None:
            lp += v["lambda"] == self.model.lbda

    def add_assignment_constraints(self):
        lp = self.lp
        v = self.variables

        for a, c, h in product(self.__alternatives, self.criteria, self.__profiles):
            bigm = self.ap_range.performances[c.id]

            # M \delta_i(x,b^h) + b_i^h >= x_i + \epsilon
            lp += bigm * v[f"delta_{c.id}({a},{h})"] + v[f"b_{c.id},{h}"] >= self.pt[a].performances[c.id] + self.epsilon

            # M \delta_i(x,b^h) + b_i^h <= x_i + M
            lp += bigm * v[f"delta_{c.id}({a},{h})"] + v[f"b_{c.id},{h}"] <= self.pt[a].performances[c.id] + bigm

            # \delta_i(x, b^h) - w_i(x, b^h) >= 0
            lp += v[f"delta_{c.id}({a},{h})"] - v[f"w_{c.id}({a},{h})"] >= 0

            # w_i - w_i(x, b^h) >= 0
            lp += v[f"w_{c.id}"] - v[f"w_{c.id}({a},{h})"] >= 0

            # w_i(x, b^h) - \delta_i(x, b^h) - w_i >= - 1
            lp += v[f"w_{c.id}({a},{h})"] - v[f"delta_{c.id}({a},{h})"] - v[f"w_{c.id}"] >= -1

        for a, h in product(self.__alternatives, self.__profiles):
            bigm = 2
            i = self.__profiles.index(h)
            lcat = self.__categories[i]
            ucat = self.__categories[i + 1]

            # \sum_{i \in [n]} w_i(x,b^h) - \lambda + M y_{x,h} <= M - \epsilon
            lp += pulp.lpSum(v[f"w_{c.id}({a},{h})"] for c in self.criteria) \
                        - v["lambda"] + bigm * v[f"y_{a},{lcat}"] <= bigm - self.epsilon

            # \sum_{i \in [n]} w_j(x, b^{h-1}) - \lambda - M y_{x,h} >= -M
            lp += pulp.lpSum(v[f"w_{c.id}({a},{h})"] for c in self.criteria) \
                        - v["lambda"] - bigm * v[f"y_{a},{ucat}"] >= -bigm


        # \sum_{h \in {1, ..., p} y_{x,h} = 1
        for a in self.__alternatives:
            lp += pulp.lpSum(v[f"y_{a},{h}"] for h in self.__categories) == 1

    def add_pairwise_constraints(self):
        lp = self.lp
        v = self.variables

        for pwc in self.pwcs:
            # \sum_{h=1}^p h * (y_{x,h} - y_{x',h}) + \sigmac(x,x') >= 0
            lp += pulp.lpSum((i + 1) * v[f"y_{pwc.a},{h}"] for i, h in enumerate(self.__categories)) \
                    - pulp.lpSum((i + 1) * v[f"y_{pwc.b},{h}"] for i, h in enumerate(self.__categories)) \
                    + v[f"sigmac({pwc.a},{pwc.b})"] >= 0

        for pwc, h in product(self.pwcs, self.__categories):
            # \epsilon_{x,x',h} - y_{x,h} <= 0
            lp += v[f"epsilon_{pwc.a},{pwc.b},{h}"] - v[f"y_{pwc.a},{h}"] <= 0

            # \epsilon_{x,x',h} - y_{x',h} <= 0
            lp += v[f"epsilon_{pwc.a},{pwc.b},{h}"] - v[f"y_{pwc.b},{h}"] <= 0

            # \epsilon_{x,x',h} - y_{x,h} - y_{x',h} >= -1
            lp += v[f"epsilon_{pwc.a},{pwc.b},{h}"] - v[f"y_{pwc.a},{h}"] \
                    - v[f"y_{pwc.b},{h}"] >= -1

        # Alternatives in best category
        for pwc in self.pwcs:
            bigm = 3
            h = self.__profiles[-1]
            cat = self.__categories[-1]

            # M \epsilon_{x,x',h} - \sigma1(x,x',h) - \Delta_{h-1}(x,x') <= M - \epsilon
            lp += bigm * v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - v[f"sigma1({pwc.a},{pwc.b},{cat})"] \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.a},{h})"] for c in self.criteria) \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.b},{h})"] for c in self.criteria) \
                    <= bigm - self.epsilon

        # Alternatives in worst category
        for pwc in self.pwcs:
            bigm = 3
            h = self.__profiles[0]
            cat = self.__categories[0]

            # M \epsilon_{x,x',h} - \sigma2(x,x',h) - \Delta_{h}(x,x') <= M - \epsilon
            lp += bigm * v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - v[f"sigma2({pwc.a},{pwc.b},{cat})"] \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.a},{h})"] for c in self.criteria) \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.b},{h})"] for c in self.criteria) \
                    <= bigm - self.epsilon

        # Alternatives in middle category (comparison to h-1)
        for pwc, h in product(self.pwcs, self.__profiles[:-1]):
            bigm = 3
            i = self.__profiles.index(h)
            cat = self.__categories[i + 1]

            # M \epsilon_{x,x',h} - \sigma1(x,x',h) - \Delta_{h-1}(x,x') <= M
            lp += bigm * v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - v[f"sigma1({pwc.a},{pwc.b},{cat})"] \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.a},{h})"] for c in self.criteria) \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.b},{h})"] for c in self.criteria) \
                    <= bigm

        # Alternatives in middle category (comparison to h)
        for pwc, h in product(self.pwcs, self.__profiles[1:]):
            bigm = 3
            i = self.__profiles.index(h)
            hm1 = self.__profiles[i - 1]
            cat = self.__categories[i]

            # \eta_h(x,x') - \Delta_{h-1}(x,x') + epsilon(x,x',h) <= 2 - \varepsilon
            lp += v[f"eta({pwc.a},{pwc.b},{cat})"] \
                    + v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.a},{hm1})"] for c in self.criteria) \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.b},{hm1})"] for c in self.criteria) \
                    <= 2 - self.epsilon

            # - \eta_h(x,x') + \Delta_{h-1} (x,x') + \epsilon_{xx'h} <= 1
            lp += v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - v[f"eta({pwc.a},{pwc.b},{cat})"] \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.a},{hm1})"] for c in self.criteria) \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.b},{hm1})"] for c in self.criteria) \
                    <= 1

            # M \epsilon_{x,x',h} - M \eta_h(x,x') - \sigma2(x,x',h) - \Delta_h(x,x') <= M - \epsilon
            lp += bigm * v[f"epsilon_{pwc.a},{pwc.b},{cat}"] \
                    - bigm * v[f"eta({pwc.a},{pwc.b},{cat})"] \
                    - v[f"sigma2({pwc.a},{pwc.b},{cat})"] \
                    - pulp.lpSum(v[f"w_{c.id}({pwc.a},{h})"] for c in self.criteria) \
                    + pulp.lpSum(v[f"w_{c.id}({pwc.b},{h})"] for c in self.criteria) \
                    <= bigm - self.epsilon

        for pwc in self.pwcs:
            bigm = 3 * len(self.__categories) + 1
            # M compm(x,x') + \sigmac(x,x') + \sum_{h=1,...,p} \sigma1(x,x',h) + \sigma2(x,x',h) <= M
            lp += bigm * v[f"compm({pwc.a},{pwc.b})"] \
                    + v[f"sigmac({pwc.a},{pwc.b})"] \
                    + pulp.lpSum(v[f"sigma1({pwc.a},{pwc.b},{cat})"] for cat in self.__categories[1:]) \
                    + pulp.lpSum(v[f"sigma2({pwc.a},{pwc.b},{cat})"] for cat in self.__categories[:-1]) \
                    <= bigm

    def add_constraints(self):
        self.add_dominance_constraint()
        self.add_weights_constraint()
        self.add_assignment_constraints()
        self.add_pairwise_constraints()

    def add_objective(self):
        v = self.variables
        self.lp += pulp.lpSum(v[f"y_{aa.id},{aa.category_id}"] for aa in self.aa) \
                    + pulp.lpSum(v[f"compm({pwc.a},{pwc.b})"] for pwc in self.pwcs)

    def status_string(self):
        return pulp.LpStatus[self.lp.status]

    def solve(self, time_limit=None):
        solver = pulp.GUROBI(manageEnv=True, timeLimit=time_limit)
        #solver = pulp.GUROBI_CMD()
        #solver = pulp.CPLEX_CMD()
        #solver = pulp.GLPK_CMD()
        #solver = pulp.HiGHS_CMD()
        self.lp.solve(solver)

        status = self.lp.status
        if status < 0:
            raise RuntimeError(f"Solver status: {status} ({status_string()})")

        obj = pulp.value(self.lp.objective)

        cvs = CriteriaValues()
        for c in self.criteria:
            cv = CriterionValue()
            cv.id = c.id
            cv.value = self.variables[f"w_{c.id}"].varValue
            cvs.append(cv)

        self.model.cv = cvs

        self.model.lbda = self.variables["lambda"].varValue

        pt = PerformanceTable()
        for p in self.__profiles:
            ap = AlternativePerformances(p)
            for c in self.criteria:
                perf = self.variables[f"b_{c.id},{p}"].varValue
                ap.performances[c.id] = round(perf, 5)
            pt.append(ap)

        self.model.bpt = pt
        self.model.bpt.update_direction(self.model.criteria)

        return status, obj

    def dump_variables(self, filename=None):
        with open(filename, "w+") as f:
            for v in self.lp.variables():
                print(f"{v.name} = {v.varValue}", file=f)

    def dump_constraints(self, filename=None):
        self.lp.writeLP(filename)

if __name__ == "__main__":
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.utils import print_pt_and_assignments
    from pymcda.ui.graphic import display_electre_tri_models
    from pymcda.utils import add_errors_in_assignments
    from itertools import combinations
    import time

    seed = 9
    ncrit = 5
    ncat = 3

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(ncrit, ncat, seed)

    # Display model parameters
    print('Original model')
    print('==============')
    cids = sorted(model.criteria.keys())
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model.lbda)

    # Generate a set of alternatives
    a = generate_alternatives(25)
    pt = generate_random_performance_table(a, model.criteria)

    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)

    # Assign the alternatives
    aa = model.pessimist(pt)

    # Add pairwise comparisons
    errors = 5
    pwcs = PairwiseRelations()
    for pwa in combinations(a.keys(), 2):
        pwc = model.compare(pt[pwa[0]], pt[pwa[1]])
        if pwc.relation == PairwiseRelation.INDIFFERENT:
            continue

        if errors > 0:
            pwc.a, pwc.b = pwc.b, pwc.a
            errors -= 1

        pwcs.append(pwc)

    pwcs.weaker_to_preferred();

    print(f"# pairwise comparisons: {len(pwcs)}")

    # Run the MIP
    model2 = model.copy()
    model2.cv = None
    model2.lbda = None
    model2.bpt = None

#    aa2 = aa.get_subset([f"a{i+1}" for i in range(10)])
    aa2 = add_errors_in_assignments(aa, model.categories, 0.2)
    print(f"Added errors: {aa2}")
    mip = MipJNCSR(model2, pt, aa, pwcs)

    t1 = time.time()
    status, obj = mip.solve()
    t2 = time.time()

    print(f"Solving time: {t2-t1:.2f} s.")
    print(f"Status: {mip.status_string()}")
    print(f"Objective: {obj}")
    mip.dump_variables("mip_jncsr-variables.lp")
    mip.dump_constraints("mip_jncsr-constraints.lp")

    # Display learned model parameters
    print('Learned model')
    print('=============')
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model2.lbda)

    # Compute assignment with the learned model
    aa2 = model2.pessimist(pt)

    # Compute CA
    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt.id)
            nok += 1

    print("Good assignments: %3g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, model.criteria.keys(),
                                 [aa, aa2], pt)

    errors = 0
    for pwc in pwcs:
        pwc2 = model2.compare(pt[pwc.a], pt[pwc.b])
        if pwc2.relation != pwc.relation:
            errors += 1
            print("Pairwise error: (%s != %s)" %(pwc, pwc2))
            print_pt_and_assignments([pwc.a, pwc.b], model.criteria.keys(),
                                     [aa, aa2], pt)

    print("Pairwise errors: %d" % errors)

    # Display models
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
