import unittest

test_modules = ['test_mcda', 'test_uta', 'test_electre_tri']

test_classes = []
for tmodule in test_modules:
    exec("import " + tmodule)
    test_classes += eval(tmodule).test_classes

suite = []
for tclass in test_classes:
    suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
alltests = unittest.TestSuite(suite)
unittest.TextTestRunner(verbosity=2).run(alltests)
