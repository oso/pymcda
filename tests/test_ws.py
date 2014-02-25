import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import shutil
import tempfile
import unittest
from pymcda.electre_tri import MRSort
from pymcda.types import Alternatives, CategoriesProfiles
from pymcda.types import CriteriaValues, PerformanceTable
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_random_mrsort_model
from ws.MRSortMIP.MRSortMIP import mrsort_mip
from xml.etree import ElementTree

XMCDA_URL = 'http://www.decision-deck.org/2009/XMCDA-2.1.0'
ElementTree.register_namespace('xmcda', XMCDA_URL)

class tests_electre_tri_bm_inference(unittest.TestCase):

    def setUp(self):
        self.indir = tempfile.mkdtemp()
        self.outdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.outdir)
        shutil.rmtree(self.indir)

    def mcda_object_to_xmcda_file(self, mcda_object, filename):
        f = open(self.indir + "/" + filename, "w")
        xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)
        xmcda.append(mcda_object)
        buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
        f.write(buf)
        f.close()

    def file_exists(self, filename):
        return os.path.exists(self.outdir + "/" + filename)

    def check_output_is_complete(self):
        self.assertEqual(self.file_exists("cat_profiles.xml"), True)
        self.assertEqual(self.file_exists("compatible_alts.xml"), True)
        self.assertEqual(self.file_exists("crit_weights.xml"), True)
        self.assertEqual(self.file_exists("lambda.xml"), True)
        self.assertEqual(self.file_exists("messages.xml"), True)
        self.assertEqual(self.file_exists("profiles_perfs.xml"), True)

    def parse_xmcda_file(self, filename, tagname, mcda_type):
        mcda_object = mcda_type()
        tree = ElementTree.parse(self.outdir + "/" + filename)
        root = tree.getroot()
        #ElementTree.dump(root)
        mcda_object.from_xmcda(root.find(tagname))
        return mcda_object

    def parse_xmcda_file_lbda(self, filename):
        tree = ElementTree.parse(self.outdir + "/" + filename)
        root = tree.getroot()
        #ElementTree.dump(root)
        tag = root.find("methodParameters/parameter/value/real")
        return float(tag.text)

    def get_output_model(self, criteria):
        cat_profiles = self.parse_xmcda_file("cat_profiles.xml",
                                             "categoriesProfiles",
                                             CategoriesProfiles)
        compatible_alts = self.parse_xmcda_file("compatible_alts.xml",
                                                "alternatives",
                                                Alternatives)
        crit_weights = self.parse_xmcda_file("crit_weights.xml",
                                             "criteriaValues",
                                             CriteriaValues)
        profiles_perfs = self.parse_xmcda_file("profiles_perfs.xml",
                                               "performanceTable",
                                               PerformanceTable)
        lbda = self.parse_xmcda_file_lbda("lambda.xml")

        return MRSort(criteria, crit_weights, profiles_perfs,
                      lbda, cat_profiles)

    def lambda_to_xmcda(self, lbda):
        root = ElementTree.Element('methodParameters')
        xmcda = ElementTree.SubElement(root, 'parameter')
        xmcda.set('name', 'lambda')
        xmcda = ElementTree.SubElement(xmcda, 'value')
        xmcda = ElementTree.SubElement(xmcda, 'real')
        xmcda.text = str(lbda)
        return root

    def test001(self):
        model = generate_random_mrsort_model(5, 2, seed = 1)
        a = generate_alternatives(10)
        pt = generate_random_performance_table(a, model.criteria)
        aa = model.get_assignments(pt)

        self.mcda_object_to_xmcda_file(model.criteria.to_xmcda(),
                                       "criteria.xml")
        categories = model.categories_profiles.to_categories()
        self.mcda_object_to_xmcda_file(categories.to_xmcda(),
                                       "categories.xml")
        self.mcda_object_to_xmcda_file(a.to_xmcda(), "alternatives.xml")
        self.mcda_object_to_xmcda_file(pt.to_xmcda(), "perfs_table.xml")
        self.mcda_object_to_xmcda_file(aa.to_xmcda(), "assign.xml")

        mrsort_mip(self.indir, self.outdir)

        self.check_output_is_complete()

        model2 = self.get_output_model(model.criteria)
        aa2 = model2.get_assignments(pt)

        self.assertEqual(aa, aa2)

    def test002(self):
        model = generate_random_mrsort_model(5, 2, seed = 2)
        a = generate_alternatives(10)
        pt = generate_random_performance_table(a, model.criteria)
        aa = model.get_assignments(pt)

        self.mcda_object_to_xmcda_file(model.criteria.to_xmcda(),
                                       "criteria.xml")
        categories = model.categories_profiles.to_categories()
        self.mcda_object_to_xmcda_file(categories.to_xmcda(),
                                       "categories.xml")
        self.mcda_object_to_xmcda_file(a.to_xmcda(), "alternatives.xml")
        self.mcda_object_to_xmcda_file(pt.to_xmcda(), "perfs_table.xml")
        self.mcda_object_to_xmcda_file(aa.to_xmcda(), "assign.xml")
        self.mcda_object_to_xmcda_file(model.cv.to_xmcda(),
                                       "crit_weights.xml")
        self.mcda_object_to_xmcda_file(self.lambda_to_xmcda(model.lbda),
                                       "lambda.xml")

        mrsort_mip(self.indir, self.outdir)

        self.check_output_is_complete()

        model2 = self.get_output_model(model.criteria)
        aa2 = model2.get_assignments(pt)

        self.assertEqual(aa, aa2)
        self.assertEqual(model.lbda, model2.lbda)

    def test003(self):
        model = generate_random_mrsort_model(5, 2, seed = 3)
        a = generate_alternatives(10)
        pt = generate_random_performance_table(a, model.criteria)
        aa = model.get_assignments(pt)

        self.mcda_object_to_xmcda_file(model.criteria.to_xmcda(),
                                       "criteria.xml")
        categories = model.categories_profiles.to_categories()
        self.mcda_object_to_xmcda_file(categories.to_xmcda(),
                                       "categories.xml")
        self.mcda_object_to_xmcda_file(a.to_xmcda(), "alternatives.xml")
        self.mcda_object_to_xmcda_file(pt.to_xmcda(), "perfs_table.xml")
        self.mcda_object_to_xmcda_file(aa.to_xmcda(), "assign.xml")
        self.mcda_object_to_xmcda_file(model.bpt.to_xmcda(),
                                       "profiles_perfs.xml")

        mrsort_mip(self.indir, self.outdir)

        self.check_output_is_complete()

        model2 = self.get_output_model(model.criteria)
        aa2 = model2.get_assignments(pt)

        self.assertEqual(aa, aa2)
        self.assertEqual(model.bpt, model2.bpt)

test_classes = [tests_electre_tri_bm_inference]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
