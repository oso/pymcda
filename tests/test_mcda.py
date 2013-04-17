import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
from lxml import etree
from pymcda.types import *
from pymcda.generate import *
import unittest
import csv

XMCDA_HEADER = '{http://www.decision-deck.org/2012/XMCDA-2.2.1}XMCDA'
XMCDA_FILE = os.path.dirname(os.path.abspath(__file__)) + '/XMCDA-2.2.1.xsd'

class tests_xmcda(unittest.TestCase):

    def validate(self, xml):
        root = ElementTree.Element(XMCDA_HEADER)
        root.append(xml)
        xml = ElementTree.tostring(root)

        doc = etree.parse(XMCDA_FILE)
        schema = etree.XMLSchema(doc)
        return schema.validate(etree.fromstring(xml))

    def test001(self):
        c1 = Criterion("c1")
        c2 = Criterion("c2")
        c = Criteria([c1, c2])
        xmcda = c.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        c_from = Criteria().from_xmcda(xmcda)
        self.assertEqual(c, c_from)

    def test002(self):
        a1 = Alternative("a1")
        a2 = Alternative("a2")
        a = Alternatives([a1, a2])
        xmcda = a.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        a_from = Alternatives().from_xmcda(xmcda)
        self.assertEqual(a, a_from)

    def test003(self):
        cv1 = CriterionValue('c1', 10)
        cv2 = CriterionValue('c2', 20)
        cv = CriteriaValues([cv1, cv2])
        xmcda = cv.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        cv_from = CriteriaValues().from_xmcda(xmcda)
        self.assertEqual(cv, cv_from)

    def test004(self):
        p1 = AlternativePerformances('a1', {'c1': 120, 'c2':  284})
        p2 = AlternativePerformances('a2', {'c1': 150, 'c2':  269})
        pt = PerformanceTable([p1, p2])
        xmcda = pt.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        pt_from = PerformanceTable().from_xmcda(xmcda)
        self.assertEqual(pt, pt_from)

    def test005(self):
        cv1 = CategoryValue('cat1', Interval(0, 0.25))
        cv2 = CategoryValue('cat2', Interval(0.25, 0.5))
        cv = CategoriesValues([cv1, cv2])
        xmcda = cv.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        cv_from = CategoriesValues().from_xmcda(xmcda)
        self.assertEqual(cv, cv_from)

    def test006(self):
        av1 = AlternativeValue('a1', 10)
        av2 = AlternativeValue('a2', 20)
        av = AlternativesValues([av1, av2])
        xmcda = av.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        av_from = AlternativesValues().from_xmcda(xmcda)
        self.assertEqual(av, av_from)

    def test007(self):
        af1 = AlternativeAssignment('a1', 'cat1')
        af2 = AlternativeAssignment('a2', 'cat2')
        af = AlternativesAssignments([af1, af2])
        xmcda = af.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        af_from = AlternativesAssignments().from_xmcda(xmcda)
        self.assertEqual(af, af_from)

    def test008(self):
        cp1 = CategoryProfile('b1', Limits('cat1', 'cat2'))
        cp2 = CategoryProfile('b2', Limits('cat2', 'cat3'))
        cp = CategoriesProfiles([cp1, cp2])
        xmcda = cp.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        cp_from = CategoriesProfiles().from_xmcda(xmcda)
        self.assertEqual(cp, cp_from)

    def test009(self):
        cat1 = Category('cat1', rank=1)
        cat2 = Category('cat2', rank=2)
        cat = Categories([cat1, cat2])
        xmcda = cat.to_xmcda()

        self.assertEqual(self.validate(xmcda), True)

        cat_from = Categories().from_xmcda(xmcda)
        self.assertEqual(cat, cat_from)

class tests_Segment(unittest.TestCase):

    def test001(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2)
        self.assertEqual(s.y(2), 2)

    def test002(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2)
        self.assertRaises(ValueError, s.y, -1)

    def test003(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2)
        self.assertRaises(ValueError, s.y, 6)

    def test004(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2)
        self.assertEquals(s.y(0), 0)

    def test005(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2, False)
        self.assertRaises(ValueError, s.y, 0)

    def test006(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2)
        self.assertRaises(ValueError, s.y, 5)

    def test007(self):
        p1 = Point(0, 0)
        p2 = Point(5, 5)
        s = Segment(p1, p2, True, True)
        self.assertEquals(s.y(5), 5)

class tests_PiecewiseLinear(unittest.TestCase):

    def test001(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEquals(plf.y(3), 7)

    def test002(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEquals(plf.y(0.5), 0.5)

    def test003(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEquals(plf.y(0), 0)

    def test004(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEquals(plf.y(1), 5)

    def test005(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEquals(plf.y(0), 0)

    def test006(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(1, 5)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertRaises(ValueError, plf.y, 5)

    def test007(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(3, 7)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertRaises(ValueError, plf.y, 2)

    def test008(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(3, 7)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertRaises(ValueError, plf.y, 1)

    def test009(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        s1 = Segment(p1, p2)

        p3 = Point(3, 7)
        p4 = Point(5, 9)
        s2 = Segment(p3, p4)

        plf = PiecewiseLinear([s1, s2])
        self.assertEqual(plf.xmin, 0)
        self.assertEqual(plf.xmax, 5)
        self.assertEqual(plf.ymin, 0)
        self.assertEqual(plf.ymax, 9)

class tests_CategoriesValues(unittest.TestCase):

    def test001(self):
        cv1 = CategoryValue('cat1', Interval(0, 0.25))
        cv2 = CategoryValue('cat2', Interval(0.25, 0.5))
        cv3 = CategoryValue('cat3', Interval(0.5, 1))
        cvs = CategoriesValues([cv1, cv2, cv3])
        cats = cvs.get_ordered_categories()

        self.assertEqual([cv1.id, cv2.id, cv3.id], cats)

from datasets import swd
class tests_csv(unittest.TestCase):

    def setUp(self):
        filepath = os.path.dirname(os.path.abspath(__file__)) \
                    + "/../datasets/swd.csv"
        csvfile = open(filepath, 'rb')
        self.csvreader = csv.reader(csvfile, delimiter = ";")

    def test001(self):
        a = Alternatives().from_csv(self.csvreader, "pt")
        self.assertEqual(a, swd.a)

    def test002(self):
        c = Criteria().from_csv(self.csvreader, "criterion")
        self.assertEqual(c, swd.c)

    def test003(self):
        pt = PerformanceTable().from_csv(self.csvreader, "pt",
                                          ["c%d" % i for i in range(1, 11)])
        self.assertEqual(pt, swd.pt)

    def test004(self):
        aa = AlternativesAssignments().from_csv(self.csvreader, "pt",
                                                 "assignment")
        self.assertEqual(aa, swd.aa)

    def test005(self):
        cats = Categories().from_csv(self.csvreader, "category",
                                     rank_col = "rank")
        self.assertEqual(cats, swd.cats)

class tests_mcda_methods(unittest.TestCase):

    def test001(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2)
        a1a2 = [ i for i in a1 if i in a2 ]
        self.assertEqual(len(a1), 50)
        self.assertEqual(len(a2), 50)
        self.assertEqual(len(a1a2), 0)

    def test002(self):
        a = generate_alternatives(100)
        a1, a2, a3 = a.split(3)
        a1a2 = [ i for i in a1 if i in a2 ]
        a2a3 = [ i for i in a2 if i in a3 ]
        a1a3 = [ i for i in a1 if i in a3 ]
        self.assertEqual(len(a1), 33)
        self.assertEqual(len(a2), 33)
        self.assertEqual(len(a3), 34)
        self.assertEqual(len(a1a2), 0)
        self.assertEqual(len(a2a3), 0)
        self.assertEqual(len(a1a3), 0)

    def test003(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2, [0.4, 0.6])
        a1a2 = [ i for i in a1 if i in a2 ]
        self.assertEqual(len(a1), 40)
        self.assertEqual(len(a2), 60)
        self.assertEqual(len(a1a2), 0)

    def test004(self):
        a = generate_alternatives(100)
        a1, a2, a3 = a.split(3, [0.33, 0.33, 0.34])
        a1a2 = [ i for i in a1 if i in a2 ]
        a2a3 = [ i for i in a2 if i in a3 ]
        a1a3 = [ i for i in a1 if i in a3 ]
        self.assertEqual(len(a1), 33)
        self.assertEqual(len(a2), 33)
        self.assertEqual(len(a3), 34)
        self.assertEqual(len(a1a2), 0)
        self.assertEqual(len(a2a3), 0)
        self.assertEqual(len(a1a3), 0)

    def test005(self):
        a = generate_alternatives(100)
        a1, a2, a3 = a.split(3, [33, 33, 34])
        a1a2 = [ i for i in a1 if i in a2 ]
        a2a3 = [ i for i in a2 if i in a3 ]
        a1a3 = [ i for i in a1 if i in a3 ]
        self.assertEqual(len(a1), 33)
        self.assertEqual(len(a2), 33)
        self.assertEqual(len(a3), 34)
        self.assertEqual(len(a1a2), 0)
        self.assertEqual(len(a2a3), 0)
        self.assertEqual(len(a1a3), 0)

    def test006(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2, [0.1, 0.1])
        a1a2 = [ i for i in a1 if i in a2 ]
        self.assertEqual(len(a1), 50)
        self.assertEqual(len(a2), 50)
        self.assertEqual(len(a1a2), 0)

    def test007(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2, None, True)
        a1b, a2b = a.split(2, None, True)
        self.assertNotEqual(a1, a1b)
        self.assertNotEqual(a2, a2b)

    def test008(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2, None, False)
        a1b, a2b = a.split(2, None, False)
        self.assertEqual(a1, a1b)
        self.assertEqual(a2, a2b)

    def test009(self):
        a = generate_alternatives(100)
        a1, a2 = a.split(2)
        a3 = a.get_subset(a1.keys())
        self.assertEqual(a1, a3)

    def test010(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        a3 = a1 + a2
        self.assertEqual(a3.performances, {'c1': 5, 'c2': 7, 'c3': 9})

    def test011(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        a3 = a2 - a1
        self.assertEqual(a3.performances, {'c1': 3, 'c2': 3, 'c3': 3})

    def test012(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        a3 = a1 * a2
        self.assertEqual(a3.performances, {'c1': 4, 'c2': 10, 'c3': 18})

    def test013(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        a3 = a2 / a1
        self.assertEqual(a3.performances, {'c1': 4, 'c2': 2.5, 'c3': 2})

    def test014(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = a1 + 2
        self.assertEqual(a2.performances, {'c1': 3, 'c2': 4, 'c3': 5})

    def test015(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = a1 - 2
        self.assertEqual(a2.performances, {'c1': -1, 'c2': 0, 'c3': 1})

    def test016(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = a1 * 2
        self.assertEqual(a2.performances, {'c1': 2, 'c2': 4, 'c3': 6})

    def test017(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = a1 / 2
        self.assertEqual(a2.performances, {'c1': 0.5, 'c2': 1, 'c3': 1.5})

    def test018(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        pt = PerformanceTable([a1, a2])
        a3 = AlternativePerformances('a3', {'c1': 2, 'c2': 1, 'c3': 3})
        pt2 = pt + a3

        self.assertEqual(pt2[a1.id].performances,
                         {'c1': 3, 'c2': 3, 'c3': 6})
        self.assertEqual(pt2[a2.id].performances,
                         {'c1': 6, 'c2': 6, 'c3': 9})

    def test019(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        pt = PerformanceTable([a1, a2])
        a3 = AlternativePerformances('a3', {'c1': 2, 'c2': 1, 'c3': 3})
        pt2 = pt - a3

        self.assertEqual(pt2[a1.id].performances,
                         {'c1': -1, 'c2': 1, 'c3': 0})
        self.assertEqual(pt2[a2.id].performances,
                         {'c1': 2, 'c2': 4, 'c3': 3})
    def test020(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        pt = PerformanceTable([a1, a2])
        a3 = AlternativePerformances('a3', {'c1': 2, 'c2': 1, 'c3': 3})
        pt2 = pt * a3

        self.assertEqual(pt2[a1.id].performances,
                         {'c1': 2, 'c2': 2, 'c3': 9})
        self.assertEqual(pt2[a2.id].performances,
                         {'c1': 8, 'c2': 5, 'c3': 18})
    def test021(self):
        a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 2, 'c3': 3})
        a2 = AlternativePerformances('a2', {'c1': 4, 'c2': 5, 'c3': 6})
        pt = PerformanceTable([a1, a2])
        a3 = AlternativePerformances('a3', {'c1': 2, 'c2': 1, 'c3': 3})
        pt2 = pt / a3

        self.assertEqual(pt2[a1.id].performances,
                         {'c1': 0.5, 'c2': 2, 'c3': 1})
        self.assertEqual(pt2[a2.id].performances,
                         {'c1': 2, 'c2': 5, 'c3': 2})

test_classes = [tests_xmcda, tests_Segment, tests_PiecewiseLinear,
                tests_CategoriesValues, tests_csv, tests_mcda_methods]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
