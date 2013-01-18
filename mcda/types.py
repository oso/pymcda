from __future__ import division, print_function
import sys
from itertools import product
from xml.etree import ElementTree
from copy import deepcopy

type2tag = {
    int: 'integer',
    float: 'real'
}

unmarshallers = {
    'integer': lambda x: int(x.text),
    'real': lambda x: float(x.text),
}

def marshal(value):
    tag = type2tag.get(type(value))
    e = ElementTree.Element(tag)
    e.text = str(value)
    return e

def unmarshal(xml):
    m = unmarshallers.get(xml.tag)
    return m(xml)

class mcda_dict(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def copy(self):
        return deepcopy(self)

    def append(self, c):
        self[c.id] = c

class mcda_object(object):

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def copy(self):
        return deepcopy(self)

class criteria(mcda_dict):

    def __repr__(self):
        return "criteria(%s)" % self.values()

    def to_xmcda(self):
        root = ElementTree.Element('criteria')
        for crit in self:
            crit_xmcda = crit.to_xmcda()
            root.append(crit_xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'criteria':
            raise TypeError('criteria::invalid tag')

        tag_list = xmcda.getiterator('criterion')
        for tag in tag_list:
            c = criterion().from_xmcda(tag)
            self.append(c)

        return self

    def from_csv(self, csvreader, crit_col, name_col = None,
                 disabled_col = None, direction_col = None):
        cols = None
        for row in csvreader:
            if row[0] == crit_col:
                cols = {}
                for i, val in enumerate(row[1:]):
                    if val == name_col:
                        cols[i + 1] = "name"
                    if val == disabled_col:
                        cols[i + 1] = "disabled"
                    if val == direction_col:
                        cols[i + 1] = "direction"
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                c = criterion(row[0])
                for i in cols.keys():
                    setattr(c, cols[i], row[i])
                self.append(c)

        return self


class criterion(mcda_object):

    MINIMIZE = -1
    MAXIMIZE = 1

    def __init__(self, id=None, name=None, disabled=False,
                 direction=MAXIMIZE, weight=None, thresholds=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.direction = direction
        self.weight = weight
        self.thresholds = thresholds

    def __repr__(self):
        return "%s" % self.id

    def to_xmcda(self):
        xmcda = ElementTree.Element('criterion')
        if self.id is not None:
            xmcda.set('id', self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        active = ElementTree.SubElement(xmcda, 'active')
        if self.disabled is False:
            active.text = 'true'
        else:
            active.text = 'false'

        scale = ElementTree.SubElement(xmcda, 'scale')
        quant = ElementTree.SubElement(scale, 'quantitative')
        prefd = ElementTree.SubElement(quant, 'preferenceDirection')
        if self.direction == 1:
            prefd.text = 'max'
        else:
            prefd.text = 'min'

        if self.weight:
            crit_val = ElementTree.SubElement(xmcda, 'criterionValue')
            value = ElementTree.SubElement(crit_val, 'value')
            weight = marshal(self.weight)
            value.append(weight)

        if self.thresholds:
            thresholds = self.thresholds.to_xmcda()
            xmcda.append(thresholds)

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'criterion':
            raise TypeError('criterion::invalid tag')

        c_id = xmcda.get('id')
        if c_id is not None:
            self.id = c_id

        name = xmcda.get('name')
        if name is not None:
            self.name = name

        active = xmcda.find('.//active')
        if active is not None:
            if active.text == 'false':
                self.disabled = True
            else:
                self.disabled = False

        pdir = xmcda.find('.//scale/quantitative/preferenceDirection')
        if pdir is not None:
            if pdir.text == 'max':
                self.direction = 1
            elif pdir.text == 'min':
                self.direction = -1
            else:
                raise TypeError('criterion::invalid preferenceDirection')

        value = xmcda.find('.//criterionValue/value')
        if value is not None:
            self.weight = unmarshal(value.getchildren()[0])

        return self

class criteria_values(mcda_dict):

    def __repr__(self):
        return "criteria_values(%s)" % self.values()

    def to_xmcda(self):
        xmcda = ElementTree.Element('criteriaValues')
        for cval in self:
            cv = cval.to_xmcda()
            xmcda.append(cv)
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'criteriaValues':
            raise TypeError('criteriaValues::invalid tag')

        tag_list = xmcda.getiterator('criterionValue')
        for tag in tag_list:
            cv = criterion_value().from_xmcda(tag)
            self.append(cv)

        return self

    def display(self, criterion_ids = None, fmt = None, out = sys.stdout):
        if criterion_ids is None:
            criterion_ids = self.keys()
            criterion_ids.sort()
        if fmt is None:
            fmt = "%5g"

        # Compute max column length
        cols_max = { }
        for cid in criterion_ids:
            cols_max[cid] = max([len(fmt % self[cid].value), len(cid)])

        # Print header
        line = "  "
        for cid in criterion_ids:
            line += " " * (cols_max[cid] - len(cid)) + str(cid) + " "
        print(line, file = out)

        # Print values
        line = "w" + " "
        for cid in criterion_ids:
            val = fmt % self[cid].value
            line += " " * (cols_max[cid] - len(val)) + val + " "
        print(line, file = out)

class criterion_value(mcda_object):

    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def to_xmcda(self, id=None):
        xmcda = ElementTree.Element('criterionValue')
        if id is not None:
            xmcda.set('id', id)
        critid = ElementTree.SubElement(xmcda, 'criterionID')
        critid.text = self.id
        val = ElementTree.SubElement(xmcda, 'value')
        val.append(marshal(self.value))
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'criterionValue':
            raise TypeError('criterionValue::invalid tag')

        name = xmcda.get('id')
        if name is not None:
            self.id = id

        criterion_id = xmcda.find('.//criterionID')
        self.id = criterion_id.text

        value = xmcda.find('.//value')
        if value is not None:
            self.value = unmarshal(value.getchildren()[0])

        return self

class alternatives(mcda_dict):

    def __repr__(self):
        return "alternatives(%s)" % self.values()

    def to_xmcda(self):
        root = ElementTree.Element('alternatives')
        for action in self:
            alt = action.to_xmcda()
            root.append(alt)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternatives':
            raise TypeError('alternatives::invalid tag')

        tag_list = xmcda.getiterator('alternative')
        for tag in tag_list:
            alt = alternative().from_xmcda(tag)
            self.append(alt)

        return self

    def from_csv(self, csvreader, alt_col, name_col = None,
                 disabled_col = None):
        cols = None
        for row in csvreader:
            if row[0] == alt_col:
                cols = {}
                for i, val in enumerate(row[1:]):
                    if val == name_col:
                        cols[i + 1] = "name"
                    if val == disabled_col:
                        cols[i + 1] = "disabled"
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                a = alternative(row[0])
                for i in cols.keys():
                    setattr(a, cols[i], row[i])
                self.append(a)

        return self

class alternative(mcda_object):

    def __init__(self, id=None, name=None, disabled=False):
        self.id = id
        self.name = name
        self.disabled = disabled

    def __repr__(self):
        return "%s" % self.id

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternative', id=self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        active = ElementTree.SubElement(xmcda, 'active')
        if self.disabled is False:
            active.text = 'true'
        else:
            active.text = 'false'

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternative':
            raise TypeError('alternative::invalid tag')

        self.id = xmcda.get('id')
        name = xmcda.get('name')
        if name:
            self.name = name

        active = xmcda.find('active')
        if active is not None and active.text == 'false':
            self.disabled = True
        else:
            self.disabled = False

        return self

class performance_table(mcda_dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def append(self, ap):
        self[ap.id] = ap

    def __call__(self, id):
        return self[id].performances

    def __repr__(self):
        return "performance_table(%s)" % self.values()

    def get_best(self, c):
        perfs = next(self.itervalues()).performances
        wa = alternative_performances('best', perfs.copy())
        for ap, crit in product(self, c):
            wperf = wa.performances[crit.id] * crit.direction
            perf = ap.performances[crit.id] * crit.direction
            if wperf < perf:
                wa.performances[crit.id] = ap.performances[crit.id]
        return wa

    def get_worst(self, c):
        perfs = next(self.itervalues()).performances
        wa = alternative_performances('worst', perfs.copy())
        for ap, crit in product(self, c):
            wperf = wa.performances[crit.id] * crit.direction
            perf = ap.performances[crit.id] * crit.direction
            if wperf > perf:
                wa.performances[crit.id] = ap.performances[crit.id]
        return wa

    def get_min(self):
        perfs = next(self.itervalues()).performances
        a = alternative_performances('min', perfs.copy())
        for ap, cid in product(self, perfs.keys()):
            perf = ap.performances[cid]
            if perf < a.performances[cid]:
                a.performances[cid] = perf
        return a

    def get_max(self):
        perfs = next(self.itervalues()).performances
        a = alternative_performances('max', perfs.copy())
        for ap, cid in product(self, perfs.keys()):
            perf = ap.performances[cid]
            if perf > a.performances[cid]:
                a.performances[cid] = perf
        return a

    def get_mean(self):
        cids = next(self.itervalues()).performances.keys()
        a = alternative_performances('mean', {cid: 0 for cid in cids})
        for ap, cid in product(self, cids):
            perf = ap.performances[cid]
            a.performances[cid] += perf

        for cid in cids:
            a.performances[cid] /= len(self)

        return a

    def get_subset(self, alternatives):
        return performance_table([self[a] for a in alternatives])

    def to_xmcda(self):
        root = ElementTree.Element('performanceTable')
        for alt_perfs in self:
            xmcda = alt_perfs.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'performanceTable':
            raise TypeError('performanceTable::invalid tag')

        tag_list = xmcda.getiterator('alternativePerformances')
        for tag in tag_list:
            altp = alternative_performances().from_xmcda(tag)
            self.append(altp)

        return self

    def display(self, criterion_ids = None, alternative_ids = None,
                fmt = None, out = sys.stdout):
        if criterion_ids is None:
            criterion_ids = next(self.itervalues()).performances.keys()
            criterion_ids.sort()
        if alternative_ids is None:
            alternative_ids = self.keys()
            alternative_ids.sort()
        if fmt is None:
            fmt = {cid: "%5g" for cid in criterion_ids}

        # Compute max column length
        cols_max = { "aids": (max([len(aid) for aid in self.keys()])) }
        for cid in criterion_ids:
            cols_max[cid] = max([len(fmt[cid] % ap.performances[cid])
                                 for ap in self.values()] + [len(cid)])

        # Print header
        line = " " * (cols_max["aids"] + 1)
        for cid in criterion_ids:
            line += " " * (cols_max[cid] - len(cid)) + str(cid) + " "
        print(line, file = out)

        # Print values
        for aid in alternative_ids:
            line = str(aid) \
                   + " " * (cols_max["aids"] - len(str(aid))) \
                   + " "
            for cid in criterion_ids:
                perf = fmt[cid] % self[aid].performances[cid]
                line += " " * (cols_max[cid] - len(perf)) + perf + " "

            print(line, file = out)

    def from_csv(self, csvreader, alt_col, perf_cols):
        cols = None
        for row in csvreader:
            if row[0] == alt_col:
                cols = {}
                for i, val in enumerate(row[1:]):
                    if val not in perf_cols:
                        continue

                    cols[i + 1] = val
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                ap = alternative_performances(row[0])
                for i in cols.keys():
                    cid = cols[i]
                    perf = float(row[i])
                    ap.performances[cid] = perf
                self.append(ap)

        return self

class alternative_performances(mcda_object):

    def __init__(self, id=None, performances=None):
        self.id = id
        if performances is None:
            self.performances = {}
        else:
            self.performances = performances

    def __call__(self, criterion_id):
        return self.performances[criterion_id]

    def __repr__(self):
        return "%s: %s" % (self.id, self.performances)

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativePerformances')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.id

        for crit_id, val in self.performances.iteritems():
            perf = ElementTree.SubElement(xmcda, 'performance')
            critid = ElementTree.SubElement(perf, 'criterionID')
            critid.text = crit_id
            value = ElementTree.SubElement(perf, 'value')
            p = marshal(val)
            value.append(p)

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativePerformances':
            raise TypeError('alternativePerformances::invalid tag')

        altid = xmcda.find('.//alternativeID')
        self.id = altid.text

        tag_list = xmcda.getiterator('performance')
        for tag in tag_list:
            crit_id = tag.find('.//criterionID').text
            value = tag.find('.//value')
            crit_val = unmarshal(value.getchildren()[0])
            self.performances[crit_id] = crit_val

        return self

class categories_values(mcda_dict):

    def __repr__(self):
        return "categories_values(%s)" % self.values()

    def display(self, out = sys.stdout):
        for cv in self:
            cv.display(out)

    def to_xmcda(self):
        root = ElementTree.Element('categoriesValues')
        for cat_value in self:
            xmcda = cat_value.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categoriesValues':
            raise TypeError('categoriesValues::invalid tag')

        tag_list = xmcda.getiterator('categoryValue')
        for tag in tag_list:
            altp = category_value().from_xmcda(tag)
            self.append(altp)

        return self

class category_value(mcda_object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def pprint(self):
        return "%s: %s" % (self.id, self.value.pprint())

    def display(self, out = sys.stdout):
        print(self.pprint(), file = out)

    def to_xmcda(self):
        xmcda = ElementTree.Element('categoryValue')
        catid = ElementTree.SubElement(xmcda, 'categoryID')
        catid.text = self.id
        value = ElementTree.SubElement(xmcda, 'value')
        value.append(self.value.to_xmcda())
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categoryValue':
            raise TypeError('categoryValue::invalid tag')

        self.id = xmcda.find('.//categoryID').text
        value = xmcda.find('.//value').getchildren()[0]
        if value.tag == 'interval':
            self.value = interval().from_xmcda(value)
        else:
            self.value = unmarshal(value)

        return self

class interval(mcda_object):

    def __init__(self, lower = float("-inf"), upper = float("inf")):
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return "interval(%s,%s)" % (self.lower, self.upper)

    def pprint(self):
        return "%s - %s" % (self.lower, self.upper)

    def display(self):
        print(self.pprint())

    def included(self, value):
        if lower and value < lower:
            return False

        if upper and value > upper:
            return False

        return True

    def to_xmcda(self):
        xmcda = ElementTree.Element('interval')
        lower = ElementTree.SubElement(xmcda, "lowerBound")
        lower.append(marshal(self.lower))
        upper = ElementTree.SubElement(xmcda, "upperBound")
        upper.append(marshal(self.upper))
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'interval':
            raise TypeError('interval::invalid tag')

        lower = xmcda.find('.//lowerBound')
        self.lower = unmarshal(lower.getchildren()[0])
        upper = xmcda.find('.//upperBound')
        self.upper = unmarshal(upper.getchildren()[0])
        return self

class alternatives_values(mcda_dict):

    def __repr__(self):
        return "alternatives_values(%s)" % self.values()

    def to_xmcda(self):
        root = ElementTree.Element('alternativesValues')
        for a_value in self:
            xmcda = a_value.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativesValues':
            raise TypeError('alternativesValues::invalid tag')

        tag_list = xmcda.getiterator('alternativeValue')
        for tag in tag_list:
            altp = alternative_value().from_xmcda(tag)
            self.append(altp)

        return self

class alternative_value(mcda_object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativeValue')
        lower = ElementTree.SubElement(xmcda, "alternativeID")
        lower.text = str(self.id)
        value = ElementTree.SubElement(xmcda, "value")
        value.append(marshal(self.value))
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativeValue':
            raise TypeError('alternativesValues::invalid tag')

        self.id = xmcda.find('.//alternativeID').text
        value = xmcda.find('.//value').getchildren()[0]
        self.value = unmarshal(value)

        return self

class criteria_functions(mcda_dict):

    def __repr__(self):
        return "criteria_functions(%s)" % self.values()

    def pprint(self, criterion_ids = None):
        if criterion_ids is None:
            criterion_ids = []
            for cv in self:
                criterion_ids.append(cv.id)

        string = ""
        for cid in criterion_ids:
            cf = self[cid]
            string += cf.pprint() + '\n'

        return string[:-1]

    def display(self, criterion_ids = None):
        print(self.pprint(criterion_ids))

    def to_xmcda(self):
        root = ElementTree.Element('criteriaFunctions')
        for a_value in self:
            xmcda = a_value.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'criteriaFunctions':
            raise TypeError('criteria_functions::invalid tag')

        tag_list = xmcda.getiterator('criterionFunction')
        for tag in tag_list:
            cf = criterion_function().from_xmcda(tag)
            self.append(cf)

        return self

class criterion_function(mcda_object):

    def __init__(self, id, function):
        self.id = id
        self.function = function

    def __repr__(self):
        return "criterion_function(%s)" % self.function

    def y(self, x):
        return self.function.y(x)

    def pprint(self):
        return "%s:\t%s" % (self.id, self.function.pprint())

    def display(self):
        print(self.pprint())

    def to_xmcda(self):
        root = ElementTree.Element('criterionFunction')
        critid = ElementTree.SubElement(xmcda, 'criterionID')
        critid.text = self.id
        function = self.function.to_xmcda()
        root.append(function)
        return root

    def from_xmcda(self):
        if xmcda.tag != 'criterionFunction':
            raise TypeError('criterion_function::invalid tag')

        self.id = xmcda.find('.//criterionID').text

        value = xmcda.find('.//piecewise_linear')
        if value:
            self.function = piecewise_linear().from_xmcda(value)

        value = xmcda.find('.//points')
        if value:
            self.function = points().from_xmcda(value)

        return self

class linear(object):

    def __init__(self, slope, intercept):
        self.slope = slope
        self.intercept = intercept

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "linear(%sx + %d)" % (self.slope, self.intercept)

    def y(self, x):
        return self.slope * x + self.intercept

    def x(self, y):
        return (y - self.intercept) / self.slope

class segment(mcda_object):

    def __init__(self, p1, p2, p1_in = True, p2_in = False):
        if p1.x <= p2.x:
            self.pl = p1
            self.ph = p2
            self.pl_in = p1_in
            self.ph_in = p2_in
        else:
            self.pl = p2
            self.ph = p1
            self.pl_in = p2_in
            self.ph_in = p1_in

    def __repr__(self):
        return "segment(%s,%s)" % (self.pl, self.ph)

    def slope(self):
        d = self.ph.x - self.pl.x
        if d == 0:
            return float("inf")
        else:
            return (self.ph.y - self.pl.y) / d

    def y(self, x):
        if x < self.pl.x or x > self.ph.x:
            raise ValueError("Value out of the segment")
        if x == self.pl.x and self.pl_in is False:
            raise ValueError("Value out of the segment")
        if x == self.ph.x and self.ph_in is False:
            raise ValueError("Value out of the segment")

        k = self.slope()
        return self.pl.y + k * (x - self.pl.x)

    def pprint(self):
        return "%s-%s" % (self.pl, self.ph)

    def display(self):
        print(self.pprint())

    def to_xmcda(self):
        root = ElementTree.Element('segment')
        for elem in self:
            xmcda = elem.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self):
        if xmcda.tag != 'segment':
            raise TypeError('segment::invalid tag')

        tag_list = xmcda.getiterator('point')
        if tag_list != 2:
            raise ValueError('segment:: invalid number of points')

        p1 = point().from_xmcda(tag_list[0])
        p2 = point().from_xmcda(tag_list[1])

        return self

class piecewise_linear(list):

    def __repr__(self):
        return "piecewise_linear(%s)" % self[:]

    def find_segment(self, x):
        for s in self:
            if s.pl.x > x or s.ph.x < x:
                continue

            if s.pl.x == x and s.pl_in is False:
                continue

            if s.ph.x == x and s.ph_in is False:
                continue

            return s

        return None

    def y(self, x):
        s = self.find_segment(x)
        if s is None:
            raise ValueError("No segment found for this value (%g)" % x)

        return s.y(x)

    def pprint(self):
        string = "f("
        for seg in self:
            string += seg.pprint() + ';'
        string = string[:-1] + ")"
        return string

    def display(self):
        print(self.pprint())

    def to_xmcda(self):
        root = ElementTree.Element('piecewiseLinear')
        for elem in self:
            xmcda = elem.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self):
        if xmcda.tag != 'piecewiseLinear':
            raise TypeError('piecewise_linear::invalid tag')

        tag_list = xmcda.getiterator('segment')
        for tag in tag_list:
            s = segment().from_xmcda(tag)
            self.append(s)

        return self

class points(list):

    def __call__(self, id):
        p = None
        for point in self:
            if point.id == id:
                p = point

        return p

    def __repr__(self):
        return "points(%s)" % self[:]

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        root = ElementTree.Element('points')
        for p in self:
            xmcda = p.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'points':
            raise TypeError('points::invalid tag')

        tag_list = xmcda.getiterator('point')
        for tag in tag_list:
            p = point().from_xmcda(tag)
            self.append(p)

        return self

class point(mcda_object):

    def __init__(self, x, y, id = None):
        self.id = id
        self.x = x
        self.y = y

    def __repr__(self):
        return "(%g,%g)" % (self.x, self.y)

    def to_xmcda(self):
        xmcda = ElementTree.Element('point')
        abscissa = ElementTree.SubElement('abscissa')
        abscissa.append(marshal(self.x))
        ordinate = ElementTree.SubElement('ordinate')
        ordinate.append(marshal(self.y))
        return xmcda

    def from_xmcda(self):
        if xmcda.tag != 'point':
            raise TypeError('point::invalid tag')

        id = xmcda.get('id')
        if id is not None:
            self.id = id

        x = xmcda.find('.//abscissa').getchildren()[0]
        self.x = unmarshal(x)
        y = xmcda.find('.//ordinate').getchildren()[0]
        self.y = unmarshal(y)

        return self

class constant(mcda_object):

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s", (self.id, self.value)

    def to_xmcda(self):
        xmcda = ElementTree.Element('constant')
        if self.id is not None:
            xmcda.set('id', self.id)
        value = marshal(self.value)
        xmcda.append(value)
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'constant':
            raise TypeError('constant::invalid tag')

        self.id = constant.get('id')
        self.value = unmarshal(constant.getchildren()[0])

class thresholds(mcda_dict):

    def __repr__(self):
        return "thresholds(%s)", self.values()

    def to_xmcda(self):
        root = ElementTree.Element('thresholds')
        for t in self:
            xmcda = t.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'thresholds':
            raise TypeError('thresholds::invalid tag')

        tag_list = thresholds.getiterator('threshold')
        for tag in tag_list:
            t = threshold(None)
            t.from_xmcda(tag)
            self.append(t)

class threshold(mcda_object):

    def __init__(self, id, name=None, values=None):
        self.id = id
        self.name = name
        self.values = values

    def __repr__(self):
        return "%s: %s" % (self.id, self.values)

    def to_xmcda(self):
        xmcda = ElementTree.Element('threshold', id=self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        values = self.values.to_xmcda()
        xmcda.append(values)

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'threshold':
            raise TypeError('threshold::invalid tag')

        self.id = threshold.get('id')
        self.name = threshold.get('name')
        values = threshold.getchildren()[0]
        if values.tag == 'constant':
            c = constant(None, 0)
            c.from_xmcda(values)

class categories(mcda_dict):

    def __repr__(self):
        return "categories(%s)" % self.values()

    def get_ids(self):
        return self.keys()

    def to_xmcda(self):
        root = ElementTree.Element('categories')
        for c in self:
            xmcda = c.to_xmcda()
            root.append(xmcda)
        return root

    def get_ordered_categories(self):
        d = {c.id: c.rank for c in self}
        return sorted(d, key = lambda key: d[key])

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categories':
            raise TypeError('categories::invalid tag')

        tag_list = xmcda.getiterator('category')
        for tag in tag_list:
            c = category()
            c.from_xmcda(tag)
            self.append(c)

        return self

    def from_csv(self, csvreader, cat_col, name_col = None,
                 rank_col = None, disabled_col = None):
        cols = None
        for row in csvreader:
            if row[0] == cat_col:
                cols = {}
                for i, val in enumerate(row[1:]):
                    if val == rank_col:
                        cols[i + 1] = "rank"
                    if val == name_col:
                        cols[i + 1] = "name"
                    if val == disabled_col:
                        cols[i + 1] = "disabled"
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                c = category(row[0])
                for i in cols.keys():
                    if cols[i] == 'rank':
                        setattr(c, cols[i], int(row[i]))
                    else:
                        setattr(c, cols[i], row[i])
                self.append(c)
        return self

class category(mcda_object):

    def __init__(self, id=None, name=None, disabled=False, rank=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.rank = rank

    def __repr__(self):
        return "%s: %d" % (self.id, self.rank)

    def to_xmcda(self):
        xmcda = ElementTree.Element('category')
        xmcda.set('id', self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        active = ElementTree.SubElement(xmcda, 'active')
        if self.disabled is False:
            active.text = 'true'
        else:
            active.text = 'false'

        rank = ElementTree.SubElement(xmcda, 'rank')
        rank.append(marshal(self.rank))

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'category':
            raise TypeError('category::invalid tag')

        self.id = xmcda.get('id')
        self.name = xmcda.get('name')
        active = xmcda.find('.//active')
        if active is not None:
            if active.text == 'false':
                self.disabled = True
            else:
                self.disabled = False

        rank = xmcda.find('.//rank')
        self.rank = unmarshal(rank.getchildren()[0])

        return self

class limits(mcda_object):

    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper  = upper

    def __repr__(self):
        return "limits(%s,%s)" % (self.lower, self.upper)

    def to_xmcda(self):
        xmcda = ElementTree.Element('limits')

        if self.lower:
            lower = ElementTree.SubElement(xmcda, 'lowerCategory')
            catid = ElementTree.SubElement(lower, 'categoryID')
            catid.text = str(self.lower)

        if self.upper:
            upper = ElementTree.SubElement(xmcda, 'upperCategory')
            catid = ElementTree.SubElement(upper, 'categoryID')
            catid.text = str(self.upper)

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'limits':
            raise TypeError('limits::invalid tag')

        lower = xmcda.find('.//lowerCategory/categoryID')
        self.lower = lower.text
        upper = xmcda.find('.//upperCategory/categoryID')
        self.upper = upper.text

        return self

class categories_profiles(mcda_dict):

    def __repr__(self):
        return "categories_profiles(%s)" % self.values()

    def append(self, cp):
        self[cp.id] = cp

    def get_ordered_profiles(self):
        lower_cat = { cp.value.lower: cp.id for cp in self }
        upper_cat = { cp.value.upper: cp.id for cp in self }

        lowest_highest = set(lower_cat.keys()) ^ set(upper_cat.keys())
        lowest = list(set(lower_cat.keys()) & lowest_highest)

        profiles = [ lower_cat[lowest[0]] ]
        for i in range(1, len(self)):
            ucat = self[profiles[-1]].value.upper
            profiles.append(lower_cat[ucat])

        return profiles

    def get_ordered_categories(self):
        profiles = self.get_ordered_profiles()
        categories = [ self[profiles[0]].value.lower ]
        for profile in profiles:
            categories.append(self[profile].value.upper)
        return categories

    def to_xmcda(self):
        root = ElementTree.Element('categoriesProfiles')
        for cp in self:
            xmcda = cp.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categoriesProfiles':
            raise TypeError('categories_profiles::invalid tag')

        tag_list = xmcda.getiterator('categoryProfile')
        for tag in tag_list:
            catp = category_profile().from_xmcda(tag)
            self.append(catp)

        return self

class category_profile(mcda_object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def to_xmcda(self):
        xmcda = ElementTree.Element('categoryProfile')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = str(self.id)
        value = self.value.to_xmcda()
        xmcda.append(value)
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categoryProfile':
            raise TypeError('category_profile::invalid tag')

        self.id = xmcda.find('.//alternativeID').text

        value = xmcda.find('.//limits')
        if value is not None:
            self.value = limits().from_xmcda(value)

        return self

class alternatives_assignments(mcda_dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __call__(self, id):
        return self[id].category_id

    def __repr__(self):
        return "alternatives_assignments(%s)" % self.values()

    def append(self, aa):
        self[aa.id] = aa

    def get_alternatives_in_category(self, category_id):
        l = []
        for aa in self:
            if aa.is_in_category(category_id):
                l.append(aa.id)

        return l

    def display(self, alternative_ids = None, out = sys.stdout):
        if alternative_ids is None:
            alternative_ids = self.keys()
            alternative_ids.sort()

        # Compute max column length
        cols_max = {"aids": max([len(aid) for aid in alternative_ids]),
                    "category": max([len(aa.category_id)
                                    for aa in self.values()] \
                                    + [len("category")])}

        # Print header
        line = " " * (cols_max["aids"] + 1)
        line += " " * (cols_max["category"] - len("category")) \
                + "category"
        print(line)

        # Print values
        for aid in alternative_ids:
            category_id = str(self[aid].category_id)
            line = str(aid) + " " * (cols_max["aids"] - len(str(aid)) + 1)
            line += " " * (cols_max["category"] - len(category_id)) \
                    + category_id
            print(line)

    def to_xmcda(self):
        root = ElementTree.Element('alternativesAffectations')
        for aa in self:
            xmcda = aa.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativesAffectations':
            raise TypeError('alternatives_assignments::invalid tag')

        tag_list = xmcda.getiterator('alternativeAffectation')
        for tag in tag_list:
            aa = alternative_assignment()
            aa.from_xmcda(tag)
            self.append(aa)

        return self

    def from_csv(self, csvreader, alt_col, assign_col):
        col = None
        for row in csvreader:
            if row[0] == alt_col:
                col = row.index(assign_col)
            elif col and row[0] == '':
                break
            elif col is not None:
                aa = alternative_assignment(row[0])
                aa.category_id = row[col]
                self.append(aa)

        return self

class alternative_assignment(mcda_object):

    def __init__(self, id=None, category_id=None):
        self.id = id
        self.category_id = category_id

    def __repr__(self):
        return "%s: %s" % (self.id, self.category_id)

    def is_in_category(self, category_id):
        if self.category_id == category_id:
            return True

        return False

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativeAffectation')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.id
        catid = ElementTree.SubElement(xmcda, 'categoryID')
        catid.text = self.category_id
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativeAffectation':
            raise TypeError('alternativeAffectation::invalid tag')

        altid = xmcda.find('alternativeID')
        self.id = altid.text
        catid = xmcda.find('categoryID')
        self.category_id = catid.text

        return self
