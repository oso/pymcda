import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
import unittest
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_capacities
from pymcda.choquet import capacities_to_mobius
from pymcda.choquet import mobius_to_capacities
from pymcda.choquet import mobius_truncate
from pymcda.choquet import capacities_are_monotone

class tests_mobius(unittest.TestCase):

    def test001(self):
        random.seed(3)
        c = generate_criteria(3)
        capacities = generate_random_capacities(c)
        mobius = capacities_to_mobius(c, capacities)
        capacities2 = mobius_to_capacities(c, mobius)

        mobius_truncate(mobius, 2)

        self.assertEqual(capacities, capacities2)

    def test002(self):
        random.seed(1)
        c = generate_criteria(10)
        capacities = generate_random_capacities(c)

        self.assertTrue(capacities_are_monotone(c, capacities))

test_classes = [tests_mobius]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
