from __future__ import print_function
import csv
import sys
import time
import traceback
from itertools import product

class test_result():

    def __init__(self, test_name):
        self.test_name = test_name
        self.attributes = []
        self.attributes_size = {}

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        if name not in self.attributes:
            self.attributes.append(name)

        if type(value) == list:
            self.attributes_size[name] = len(value)
        else:
            self.attributes_size[name] = 1

        setattr(self, name, value)

    def __repr__(self):
        return self.test_name

    def set_attributes_order(self, order):
        self.attributes = set(order).union(set(self.attributes))

    def get_attributes(self):
        return self.attributes

    def get_attributes_size(self):
        return self.attributes_size

    def get_header(self):
        header = []
        for attr in self.attributes:
            size = self.attributes_size[attr]
            if size > 1:
                header += [ attr + "%d" % i for i in range(size) ]
            else:
                header += [ attr ]

        return header

    def tocsv(self, writer, fields = None):
        if fields is None:
            fields = self.get_attributes()

        row = []
        for field in fields:
            if type(self[field]) == list:
                for val in self[field]:
                    row += [ val ]
            else:
                row += [ self[field] ]

        writer.writerow(row)

class test_results(list):

    def get(self, name, val):
        l = test_results()
        for tr in self:
            if tr[name] != val:
                continue

            l.append(tr)

        return l

    def unique(self, field):
        unique_values = []
        for tr in self:
            value = tr[field]
            if value not in unique_values:
                unique_values.append(value)

        return unique_values

    def set_attributes_order(self, order):
        for tr in self:
            tr.set_attributes_order(order)

    def summary(self, unique_fields, average_fields):
        # Research uniques values for each field
        unique_values = {}
        for uf in unique_fields:
            unique_values[uf] = self.unique(uf)

        # For each combination perform the average, min and max
        trs = test_results()

        attributes_size = self[0].get_attributes_size()
        keys = unique_values.keys()
        for indices in product(*unique_values.values()):
            tr = test_result(None)

            params = dict(zip(keys, indices))
            l = self
            for k in unique_fields:
                l = l.get(k, params[k])
                tr[k] = params[k]

            tr["#"] = len(l)

            for af in average_fields:
                if attributes_size[af] > 1:
                    n = len(l)
                    v = zip(*(r[af] for r in l))
                    avg_values = [ sum(x) / n for x in v ]
                    min_values = [ min(x) for x in v ]
                    max_values = [ max(x) for x in v ]
                    for i, val in enumerate(avg_values):
                        tr["%s%d_avg" % (af, i)] = val
                    for i, val in enumerate(min_values):
                        tr["%s%d_min" % (af, i)] = val
                    for i, val in enumerate(max_values):
                        tr["%s%d_max" % (af, i)] = val
                else:
                    v = [ r[af] for r in l ]
                    tr["%s_avg" % af] = sum(v) / len(v)
                    tr["%s_min" % af] = min(v)
                    tr["%s_max" % af] = max(v)

            trs.append(tr)

        return trs

    def tocsv(self, writer, fields = None):
        if fields is None:
            fields = self[0].get_attributes()
        writer.writerow(fields)
        for tr in self:
            tr.tocsv(writer, fields)

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
