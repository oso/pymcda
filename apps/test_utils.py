from __future__ import print_function
from __future__ import division
import bz2
import csv
import os
import sys
import time
import traceback
from collections import OrderedDict
from copy import deepcopy
from itertools import product
from xml.etree import ElementTree
from pymcda.types import Alternatives, Criteria, PerformanceTable
from pymcda.types import AlternativesAssignments, Categories

raw_input = input

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

    def summary(self, unique_fields, average_fields, min_fields = None,
                max_fields = None, std_fields = None, ic_fields = None):
        if min_fields is None:
            min_fields = average_fields
        if max_fields is None:
            max_fields = average_fields
        if std_fields is None:
            std_fields = average_fields
        if ic_fields is None:
            ic_fields = average_fields

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

            if len(l) == 0:
                continue

            tr["#"] = len(l)

            for af in average_fields:
                if attributes_size[af] > 1:
                    v = zip(*(r[af] for r in l))
                    avg_values = [ sum(x) / len(x) for x in v ]
                    for i, val in enumerate(avg_values):
                        tr["%s%d_avg" % (af, i)] = val

                    if af in std_fields:
                        std_values = [(1 / len(x) *
                                      sum((xi - sum(x) / len(x)) ** 2
                                          for xi in x)
                                      ) ** 0.5
                                      for x in v]
                        for i, val in enumerate(std_values):
                            tr["%s%d_std" % (af, i)] = val

                    if af in min_fields:
                        min_values = [ min(x) for x in v ]
                        for i, val in enumerate(min_values):
                            tr["%s%d_min" % (af, i)] = val

                    if af in max_fields:
                        max_values = [ max(x) for x in v ]
                        for i, val in enumerate(max_values):
                            tr["%s%d_max" % (af, i)] = val

                    if af in ic_fields:
                        ic_values = [1.83 * len(x) ** -0.5 * (1 / (len(x) - 1) * sum((xi - sum(x) / len(x)) ** 2 for xi in x)) for x in v]
                        for i, val in enumerate(ic_values):
                            tr["%s%d_ic" % (af, i)] = val

                else:
                    v = [ r[af] for r in l ]
                    tr["%s_avg" % af] = sum(v) / len(v)

                    if af in std_fields:
                        tr["%s_std" % af] = (1 / len(v) *
                                             sum((xi - sum(v) / len(v)) ** 2
                                                 for xi in v)) ** 0.5
                    if af in min_fields:
                        tr["%s_min" % af] = min(v)
                    if af in max_fields:
                        tr["%s_max" % af] = max(v)
                    if af in ic_fields:
                        tr["%s_ic" % af] = 1.83 * len(v) ** -0.5 * (1 / (len(v) - 1) * sum((xi - sum(v) / len(v)) ** 2 for xi in v))

            trs.append(tr)

        return trs

    def summary_columns(self, unique_fields, column_fields, column_key):
        # Research uniques values for each field
        unique_values = {}
        for uf in unique_fields:
            unique_values[uf] = self.unique(uf)

        # For each combination perform the average, min and max
        trs = test_results()

        attributes_size = self[0].get_attributes_size()
        keys = unique_values.keys()
        for indices in product(*unique_values.values()):
            tr_unique = test_result(indices)

            params = dict(zip(keys, indices))
            l = self
            for k in unique_fields:
                l = l.get(k, params[k])
                tr_unique[k] = params[k]

            nrows = attributes_size[column_fields[0]]
            for i in range(nrows):
                tr = deepcopy(tr_unique)
                for cf in column_fields:
                    tr["#%s" % cf] = i

                    col = []
                    for t in l:
                        suffix = t[column_key]
                        tr["%s_%s" % (cf, suffix)] = t[cf][i]
                        col += [ t[cf][i] ]

                    avg_value = sum(col) / len(col)
                    min_value = min(col)
                    max_value = max(col)
                    std_value = (1 / len(col) * sum((xi - avg_value) ** 2
                                                    for xi in col)) ** 0.5

                    tr["%s_avg" % cf] = avg_value
                    tr["%s_std" % cf] = std_value
                    tr["%s_min" % cf] = min_value
                    tr["%s_max" % cf] = max_value

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

def read_single_integer(variable, question):
    while not variable:
        variable = raw_input(question + " ? ")
    variable = int(variable)
    return variable

def read_multiple_integer(variable, question):
    while not variable:
        variable = raw_input(question + " ? ")
    variable = variable.split(",")
    variable = [int(x) for x in variable]
    return variable

def read_multiple_float(variable, question):
    while not variable:
        variable = raw_input(question + " ? ")
    variable = variable.split(",")
    variable = [float(x) for x in variable]
    return variable

def read_csv_filename(variable, default):
    while not variable:
        variable = raw_input("File to save CSV data [%s] ? " % default)
        if not variable:
            variable = default

    if variable[-4:] != ".csv":
        variable += ".csv"

    return variable

def parser_parse_options(*options):

    if "na" in options:
        parser.add_option("-n", "--na", action = "store", type="string",
                          dest = "na",
                          help = "number of assignment examples")

    if "nc" in options:
        parser.add_option("-c", "--nc", action = "store", type="string",
                          dest = "nc",
                          help = "number of criteria")

    if "ncat" in options:
        parser.add_option("-t", "--ncat", action = "store", type="string",
                          dest = "ncat",
                          help = "number of categories")

    if "na_gen" in options:
        parser.add_option("-g", "--na_gen", action = "store", type="string",
                          dest = "na_gen",
                          help = "number of generalization alternatives")

    if "pcerrors" in options:
        parser.add_option("-e", "--errors", action = "store", type="string",
                          dest = "pcerrors",
                          help = "percentage of errors in the learning set")

    if "nseeds" in options:
        parser.add_option("-s", "--nseeds", action = "store", type="string",
                          dest = "nseeds",
                          help = "number of seeds")

    if "max_loops" in options:
        parser.add_option("-l", "--max-loops", action = "store",
                          type = "string", dest = "max_loops",
                          help = "max number of loops for the " \
                                 "metaheuristic " \
                                 "used to find the profiles")

    if "nmodels" in options:
        parser.add_option("-m", "--nmodels", action = "store",
                          type = "string", dest = "nmodels",
                          help = "Size of the population (of models)")

    if "max_oloops" in options:
        parser.add_option("-o", "--max_oloops", action = "store",
                          type = "string", dest = "max_oloops",
                          help = "Max number of loops of the whole " \
                                 "metaheuristic")

    if "filename" in options:
        parser.add_option("-f", "--filename", action = "store",
                          type = "string", dest = "filename",
                          help = "filename to save csv output")

class dataset(object):

    def __init__(self, name):
        self.name = name

    def is_complete(self):
        for obj in self.__dict__:
            if obj is None:
                return False
        return True

def load_mcda_data(csvfile, obj, *field):
    csvfile.seek(0)
    csvreader = csv.reader(csvfile, delimiter = ",")
    try:
        obj = obj(OrderedDict({})).from_csv(csvreader, *field)
    except:
        print("Cannot get %s" % obj())
        return None

    return obj

def load_mcda_input_data(filepath):
    try:
        csvfile = open(filepath, 'rb')
        csvreader = csv.reader(csvfile, delimiter = ",")
    except:
        print("Cannot open file '%s'" % filepath)
        return None

    data = dataset(os.path.basename(filepath))
    data.a = load_mcda_data(csvfile, Alternatives, "pt")
    data.c = load_mcda_data(csvfile, Criteria, "criterion", None, None,
                            'direction')
    data.pt = load_mcda_data(csvfile, PerformanceTable, "pt",
                             [c.id for c in data.c])
    data.pt.round()
    data.aa = load_mcda_data(csvfile, AlternativesAssignments,
                             "pt", "assignment")
    data.cats = load_mcda_data(csvfile, Categories, "category",
                               None, "rank")

    if data.is_complete() is False:
        return None

    return data

def process_time():
    return sum(os.times()[0:-1])

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

XMCDA_URL = 'http://www.decision-deck.org/2009/XMCDA-2.1.0'

def save_to_xmcda(filepath, *elems):
    f = bz2.BZ2File(filepath, "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)

    for elem in elems:
        xmcda.append(elem.to_xmcda())

    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def get_file_compression(filepath):
    magic_dict = {
        "\x1f\x8b\x08": "gz",
        "\x42\x5a\x68": "bz2",
        "\x50\x4b\x03\x04": "zip"
    }

    max_len = max(len(x) for x in magic_dict)

    with open(filepath) as f:
        file_start = f.read(max_len)

    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return filetype

    return "none"

def is_bz2_file(filepath):
    if get_file_compression(filepath) == 'bz2':
        return True

    return False
