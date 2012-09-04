from __future__ import print_function
import sys
import time
import traceback

class test_result():

    def __init__(self, test_name):
        self.test_name = test_name

    def __getitem__(self, name):
        if not hasattr(self, name):
            return None
        return getattr(self, name)

    def __repr__(self):
        return self.test_name

    def get_params(self):
        return self.__dict__.keys()

class tests_results(list):

    def get(self, name, val):
        l = tests_results()
        for tr in self:
            if tr[name] != val:
                continue

            l.append(tr)

        return l

#following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False
has_colours = has_colours(sys.stdout)

def printc(*args):
    if has_colours:
        print("\033[93m", end = '')
        print(*args, end = "\033[0m\n" )
    else:
        print(*args)

class test_list():

    def __init__(self, classes_list = None):
        self.test_list = dict()
        if classes_list:
            for c in classes_list:
                self.get(c)

    def get(self, object):
        i = len(self.test_list)
        name_list = dir(object)
        for name in name_list:
            if not name.startswith('test'):
                continue

            method = getattr(object, name)
            i += 1

            self.test_list[i] = dict()
            self.test_list[i]['name'] = name
            self.test_list[i]['method'] = method
            self.test_list[i]['desc'] = method.__doc__

    def show(self, ids = None):
        for test in self.test_list:
            if ids and test not in ids:
                continue

            printc("* %3d. %s" % (test, self.test_list[test]['name']))

    def run(self, ids = None):
        printc("* Tests to be run:");
        if ids is None:
            ids = [ i for i in range(1, len(self.test_list)+1) ]
        self.show(ids)

        for id in ids:
            if id not in self.test_list:
                printc("* Test id %s not found!" % id)
                continue

            printc("* Running %s..." % self.test_list[id]['name'])
            if self.test_list[id]['desc']:
                printc("* Description: %s" % self.test_list[id]['desc'])

            try:
                t1 = time.time()
                self.test_list[id]['method']()
                t2 = time.time()
                printc("* %s done! (after %f seconds)" %
                      (self.test_list[id]['name'], t2-t1))
            except:
                printc("* %s error" % (self.test_list[id]['name']))
                traceback.print_exc(sys.stderr)

class test_list_example():

    def a(self):
        pass

    def test001_test_a(self):
        """Just print coucou"""
        print('coucou!')

    def test002_b(self):
        print('beuh!')
        time.sleep(2)

def test_init(l = []):
    from optparse import OptionParser

    parser = OptionParser(usage = "-t <test_ids>")
    parser.add_option("-l", "--list",  action="store_true", dest="show",
                      help = "show list of tests")
    parser.add_option("-t", "--tests", dest = "tests", default="all",
                      help = "run tests ids (all = All tests;" \
                             "ask = Display list and ask)",
                      metavar = "test_ids")

    (options, args) = parser.parse_args()

    tests = test_list(l)

    if options.show is True:
        tests.show()

    if options.tests == 'all':
        tests.run()
    elif options.tests == 'ask':
        tests.show()
        to_run = input("Which test(s) should be run? ")
        if type(to_run) == int:
            to_run = [ to_run ]
        elif type(to_run) != tuple:
            print('Invalid input');
            exit(1)
        tests.run(to_run)
    elif options.tests == 'none':
        pass
    else:
        tests.run()

if __name__ == "__main__":
    a = test_list_example()
    tests = test_list([a])
    tests.show()
    try:
        to_run = input("Which one(s)? ")
    except:
        print('Invalid input!')
        exit(1)

    if type(to_run) == int:
        to_run = [ to_run ]
    elif type(to_run) != tuple:
        print('Invalid input');
        exit(1)

    tests.run(to_run)
