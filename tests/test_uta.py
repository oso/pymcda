import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.uta import uta, utadis
from pymcda.types import *
import unittest

class tests_uta(unittest.TestCase):

    def generate_model(self):
        c1 = Criterion("c1")
        c2 = Criterion("c2")
        c3 = Criterion("c3")
        c = Criteria([c1, c2, c3])

        cv1 = CriterionValue("c1", 0.5)
        cv2 = CriterionValue("c2", 0.25)
        cv3 = CriterionValue("c3", 0.25)
        cvs = CriteriaValues([cv1, cv2, cv3])

        f1 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.2)),
                               Segment(Point(2.5, 0.2), Point(5, 1), True,
                                                              True)])
        f2 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.8)),
                               Segment(Point(2.5, 0.8), Point(5, 1), True,
                                                              True)])
        f3 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.5)),
                               Segment(Point(2.5, 0.5), Point(5, 1), True,
                                                              True)])
        cf1 = CriterionFunction("c1", f1)
        cf2 = CriterionFunction("c2", f2)
        cf3 = CriterionFunction("c3", f3)
        cfs = CriteriaFunctions([cf1, cf2, cf3])

        return uta(c, cvs, cfs)

    def test001(self):
        model = self.generate_model()

        a1 = Alternative("a1")
        ap1 = AlternativePerformances("a1",
                                       {"c1": 2.5, "c2": 2.5, "c3": 2.5})
        a2 = Alternative("a2")
        ap2 = AlternativePerformances("a1",
                                       {"c1": 5, "c2": 5, "c3": 5})
        a3 = Alternative("a3")
        ap3 = AlternativePerformances("a3",
                                       {"c1": 0, "c2": 0, "c3": 0})

        self.assertAlmostEqual(model.global_utility(ap1).value, 0.425)
        self.assertAlmostEqual(model.global_utility(ap2).value, 1)
        self.assertAlmostEqual(model.global_utility(ap3).value, 0)

class tests_utadis(unittest.TestCase):

    def generate_model(self):
        c1 = Criterion("c1")
        c2 = Criterion("c2")
        c3 = Criterion("c3")
        c = Criteria([c1, c2, c3])

        cv1 = CriterionValue("c1", 0.5)
        cv2 = CriterionValue("c2", 0.25)
        cv3 = CriterionValue("c3", 0.25)
        cvs = CriteriaValues([cv1, cv2, cv3])

        f1 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.2)),
                               Segment(Point(2.5, 0.2), Point(5, 1), True,
                                                              True)])
        f2 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.8)),
                               Segment(Point(2.5, 0.8), Point(5, 1), True,
                                                              True)])
        f3 = PiecewiseLinear([Segment(Point(0, 0), Point(2.5, 0.5)),
                               Segment(Point(2.5, 0.5), Point(5, 1), True,
                                                              True)])
        cf1 = CriterionFunction("c1", f1)
        cf2 = CriterionFunction("c2", f2)
        cf3 = CriterionFunction("c3", f3)
        cfs = CriteriaFunctions([cf1, cf2, cf3])

        cat1 = Category("cat1")
        cat2 = Category("cat2")
        cat3 = Category("cat3")
        cats = Categories([cat1, cat2, cat3])

        catv1 = CategoryValue("cat1", Interval(0, 0.25))
        catv2 = CategoryValue("cat2", Interval(0.25, 0.65))
        catv3 = CategoryValue("cat3", Interval(0.65, 1))

        catv = CategoriesValues([catv1, catv2, catv3])

        return utadis(c, cvs, cfs, catv)

    def test001(self):
        model = self.generate_model()

        a1 = Alternative("a1")
        ap1 = AlternativePerformances("a1",
                                       {"c1": 2.5, "c2": 2.5, "c3": 2.5})
        aa1 = model.get_assignment(ap1)
        self.assertEquals(aa1.category_id, "cat2")

    def test002(self):
        model = self.generate_model()

        a2 = Alternative("a2")
        ap2 = AlternativePerformances("a2",
                                       {"c1": 0, "c2": 0, "c3": 0})
        aa2 = model.get_assignment(ap2)
        self.assertEquals(aa2.category_id, "cat1")

    def test003(self):
        model = self.generate_model()

        a3 = Alternative("a3")
        ap3 = AlternativePerformances("a3",
                {"c1": 5, "c2": 5, "c3": 5})
        aa3 = model.get_assignment(ap3)
        self.assertEquals(aa3.category_id, "cat3")

    def test004(self):
        model = self.generate_model()

        a1 = Alternative("a1")
        ap1 = AlternativePerformances("a1",
                                       {"c1": 2.5, "c2": 2.5, "c3": 2.5})
        aa1 = model.get_assignment(ap1)

        a2 = Alternative("a2")
        ap2 = AlternativePerformances("a2",
                                       {"c1": 0, "c2": 0, "c3": 0})
        aa2 = model.get_assignment(ap2)

        a3 = Alternative("a3")
        ap3 = AlternativePerformances("a3",
                {"c1": 5, "c2": 5, "c3": 5})
        aa3 = model.get_assignment(ap3)

        pt = PerformanceTable([ap1, ap2, ap3])

        assignments = model.get_assignments(pt)

        self.assertEquals(assignments["a1"].category_id, "cat2")
        self.assertEquals(assignments["a2"].category_id, "cat1")
        self.assertEquals(assignments["a3"].category_id, "cat3")

test_classes = [tests_uta, tests_utadis]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
