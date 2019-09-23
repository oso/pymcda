from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import AlternativePerformances
from pymcda.types import Criterion, Criteria, CriteriaValues, PerformanceTable
from pymcda.types import CategoryProfile, CategoriesProfiles, Limits
from pymcda.types import PairwiseRelations, PairwiseRelation
from pymcda.electre_tri import MRSort

class SortAndRank(MRSort):


    def __init__(self, criteria = None, cv = None, bpt = None,
                 lbda = None, categories_profiles = None,
                 categories_cvs = None):
        super(SortAndRank, self).__init__(criteria, cv, bpt, lbda,
                                          categories_profiles)
        self.categories_cvs = categories_cvs

    def compare_category(self, ap1, ap2, category):
        cid = self.categories.index(category)
        bps = []
        if cid > 0:
            bps.append(self.bpt[self.profiles[cid - 1]])
        if cid < len(self.categories) - 1:
            bps.append(self.bpt[self.profiles[cid]])

        relation = PairwiseRelation.INDIFFERENT
        cvs = self.categories_cvs[category]
        for bp in bps:
            coa1 = self.criteria_coalition(ap1, bp)
            coa2 = self.criteria_coalition(ap2, bp)
            coa1w = self.coalition_weight(coa1, cvs)
            coa2w = self.coalition_weight(coa2, cvs)
            if coa1w > coa2w:
                relation = PairwiseRelation.PREFERRED
                break
            elif coa1w < coa2w:
                relation = PairwiseRelation.WEAKER
                break

        return PairwiseRelation(ap1.id, ap2.id, relation)

    def compare(self, ap1, ap2):
        a1 = self.get_assignment(ap1)
        a2 = self.get_assignment(ap2)

        cid1 = self.categories.index(a1.category_id)
        cid2 = self.categories.index(a2.category_id)

        if cid1 > cid2:
            return PairwiseRelation(ap1.id, ap2.id, PairwiseRelation.PREFERRED)
        elif cid1 < cid2:
            return PairwiseRelation(ap1.id, ap2.id, PairwiseRelation.WEAKER)
        else:
            return self.compare_category(ap1, ap2, a1.category_id)

if __name__ == "__main__":
    from pymcda.types import CriteriaValues, CriterionValue
    from pymcda.types import AlternativePerformances

    ap1 = AlternativePerformances("a", {"c1": 7, "c2": 7, "c3": 7})
    ap2 = AlternativePerformances("b", {"c1": 8, "c2": 4, "c3": 8})
    ap3 = AlternativePerformances("c", {"c1": 8, "c2": 5, "c3": 4})
    ap4 = AlternativePerformances("d", {"c1": 4, "c2": 4, "c3": 9})
    ap5 = AlternativePerformances("e", {"c1": 5, "c2": 2, "c3": 1})
    ap6 = AlternativePerformances("f", {"c1": 1, "c2": 2, "c3": 6})
    pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6])

    c1 = Criterion("c1")
    c2 = Criterion("c2")
    c3 = Criterion("c3")
    criteria = Criteria([c1, c2, c3])

    bp1 = AlternativePerformances("b1", {"c1": 3, "c2": 3, "c3": 3})
    bp2 = AlternativePerformances("b2", {"c1": 6, "c2": 6, "c3": 6})
    bpt = PerformanceTable([bp1, bp2])

    cv1 = CriterionValue("c1", 1)
    cv2 = CriterionValue("c2", 1)
    cv3 = CriterionValue("c3", 1)
    cvs = CriteriaValues([cv1, cv2, cv3])

    lbda = 2

    cpb1 = CategoryProfile("b1", Limits("cat1", "cat2"))
    cpb2 = CategoryProfile("b2", Limits("cat2", "cat3"))
    cpbs = CategoriesProfiles([cpb1, cpb2])

    cvs1 = CriteriaValues([CriterionValue("c1", 40),
                           CriterionValue("c2", 25),
                           CriterionValue("c3", 35)])
    cvs2 = CriteriaValues([CriterionValue("c1", 35),
                           CriterionValue("c2", 40),
                           CriterionValue("c3", 25)])
    cvs3 = CriteriaValues([CriterionValue("c1", 25),
                           CriterionValue("c2", 35),
                           CriterionValue("c3", 40)])
    categories_cvs = {"cat1": cvs1, "cat2": cvs2, "cat3": cvs3}

    snr = SortAndRank(criteria, cvs, bpt, lbda, cpbs, categories_cvs)

    print(snr.compare(ap1, ap2))
    print(snr.compare(ap2, ap3))
    print(snr.compare(ap3, ap4))
    print(snr.compare(ap4, ap5))
    print(snr.compare(ap5, ap6))
