from __future__ import print_function
import sys
import time
import traceback

def printc(*args):
    print("\033[93m", end = '')
    try:
        print(*args)
    except:
        print("\033[0m", end = '')
        traceback.print_exc(sys.stderr)
    print("\033[0m", end = '')

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
        print('coucou!')

    def test002_b(self):
        print('beuh!')
        time.sleep(2)

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
