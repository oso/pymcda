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

class criteria(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "criteria(%s)" % self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, c):
        self[c.id] = c

    def display(self, header=True, criterion_ids=None):
        self[0].display(header)
        for aa in self[1:]:
            aa.display(False)

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

class criterion(object):

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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s" % self.id

    def copy(self):
        return deepcopy(self)

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

class criteria_values(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __str__(self):
        return "criteria_values(%s)" % self.values()

    def append(self, c):
        self[c.id] = c

    def copy(self):
        return deepcopy(self)

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

    def display(self, header=True, criterion_ids=None, name='w'):
        if criterion_ids is None:
            for cv in self:
                criterion_ids.append(cv.id)

        if header is True:
            for cid in criterion_ids:
                print("\t%.6s" % cid),
            print('')

        print('%.6s\t' % name),
        for cid in criterion_ids:
            cv = self[cid]
            print("%-6.5f" % cv.value),
        print('')

class criterion_value(object):

    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def copy(self):
        return deepcopy(self)

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

class alternatives(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "alternatives(%s)" % self.values()

    def append(self, a):
        self[a.id] = a

    def copy(self):
        return deepcopy(self)

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

class alternative(object):

    def __init__(self, id=None, name=None, disabled=False):
        self.id = id
        self.name = name
        self.disabled = disabled

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s" % self.id

    def copy(self):
        return deepcopy(self)

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

class performance_table(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.alternative_id] = i

    def __iter__(self):
        return self.itervalues()

    def __call__(self, id):
        return self[id].performances

    def __repr__(self):
        return "performance_table(%s)" % self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, ap):
        self[ap.alternative_id] = ap

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

    def display(self, header = True, criterion_ids = None,
                append = '', alternative_ids = None):
        show_header = header
        if criterion_ids is None:
            criterion_ids = next(self.itervalues()).performances.keys()
        if alternative_ids is None:
            alternative_ids = self.keys()
        for aid in alternative_ids:
            ap = self[aid]
            ap.display(show_header, criterion_ids, append)
            show_header = False

class alternative_performances(object):

    def __init__(self, alternative_id=None, performances=None):
        self.alternative_id = alternative_id
        if performances is None:
            self.performances = {}
        else:
            self.performances = performances

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __call__(self, criterion_id):
        return self.performances[criterion_id]

    def __repr__(self):
        return "%s: %s" % (self.alternative_id, self.performances)

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativePerformances')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.alternative_id

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
        self.alternative_id = altid.text

        tag_list = xmcda.getiterator('performance')
        for tag in tag_list:
            crit_id = tag.find('.//criterionID').text
            value = tag.find('.//value')
            crit_val = unmarshal(value.getchildren()[0])
            self.performances[crit_id] = crit_val

        return self

    def display(self, header=True, criterion_ids=None, append=''):
        if criterion_ids is None:
            criterion_ids = self.performances.keys()

        if header is True:
            for c in criterion_ids:
                print("\t%.7s" % c),
            print('')

        print("%.7s\t" % str(self.alternative_id+append)),
        for c in criterion_ids:
            print("%-6.5f" % self.performances[c]),
        print('')

class categories_values(dict):

    def __init__(self, l = []):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "categories_values(%s)" % self.values()

    def append(self, cv):
        self[cv.id] = cv

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

class category_value(object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

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

class interval(object):

    def __init__(self, lower = float("-inf"), upper = float("inf")):
        self.lower = lower
        self.upper = upper

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "interval(%s,%s)" % (self.lower, self.upper)

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

class alternatives_values(dict):

    def __init__(self, l = []):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "alternatives_values(%s)" % self.values()

    def append(self, av):
        self[av.id] = av

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

class alternative_value(object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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

class criteria_functions(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "criteria_functions(%s)" % self.values()

    def append(self, c):
        self[c.id] = c

    def to_xmcda(self):
        root = ElementTree.Element('criteriaFunctions')
        for a_value in self:
            xmcda = a_value.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda)
        if xmcda.tag != 'criteriaFunctions':
            raise TypeError('criteria_functions::invalid tag')

        tag_list = xmcda.getiterator('criterionFunction')
        for tag in tag_list:
            cf = criterion_function().from_xmcda(tag)
            self.append(cf)

        return self

class criterion_function(object):

    def __init__(self, id, function):
        self.id = id
        self.function = function

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "criterion_function(%s)" % self.function

    def y(self, x):
        return self.function.y(x)

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

class segment(object):

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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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
            raise ValueError("No segment found for this value")

        return s.y(x)

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

class point(object):

    def __init__(self, x, y, id = None):
        self.id = id
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "(%g,%g)" % (self.x, self.y)

    def copy(self):
        return deepcopy(self)

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

class constant(object):

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s", (self.id, self.value)

    def copy(self):
        return deepcopy(self)

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

class thresholds(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "thresholds(%s)", self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, threshold):
        self[threshold.id] = threshold

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

class threshold(object):

    def __init__(self, id, name=None, values=None):
        self.id = id
        self.name = name
        self.values = values

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s" % (self.id, self.values)

    def copy(self):
        return deepcopy(self)

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

class categories(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "categories(%s)" % self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, c):
        self[c.id] = c

    def copy(self):
        return deepcopy(self)

    def get_ids(self):
        return self.keys()

    def to_xmcda(self):
        root = ElementTree.Element('categories')
        for c in self:
            xmcda = c.to_xmcda()
            root.append(xmcda)
        return root

    def get_ordered_categories(self):
        return [ cat.id for cat in self ]

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'categories':
            raise TypeError('categories::invalid tag')

        tag_list = xmcda.getiterator('category')
        for tag in tag_list:
            c = category()
            c.from_xmcda(tag)
            self.append(c)

        return self

class category(object):

    def __init__(self, id=None, name=None, disabled=False, rank=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.rank = rank

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %d" % (self.id, self.rank)

    def copy(self):
        return deepcopy(self)

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

class limits(object):

    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper  = upper

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "limits(%s,%s)" % (self.lower, self.upper)

    def copy(self):
        return deepcopy(self)

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

class categories_profiles(dict):

    def __init__(self, l=[]):
        for cp in l:
            self[cp.id] = cp

    def __iter__(self):
        return self.itervalues()

    def __repr__(self):
        return "categories_profiles(%s)" % self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, cp):
        self[cp.id] = cp

    def copy(self):
        return deepcopy(self)

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

class category_profile(object):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def copy(self):
        return deepcopy(self)

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

class alternatives_affectations(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.alternative_id] = i

    def __iter__(self):
        return self.itervalues()

    def __call__(self, id):
        return self[id].category_id

    def __repr__(self):
        return "alternatives_affectations(%s)" % self.values()

    def copy(self):
        return deepcopy(self)

    def append(self, aa):
        self[aa.alternative_id] = aa

    def display(self, header=True, criterion_ids=None):
        self[0].display(header)
        for aa in self[1:]:
            aa.display(False)

    def to_xmcda(self):
        root = ElementTree.Element('alternativesAffectations')
        for aa in self:
            xmcda = aa.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativesAffectations':
            raise TypeError('alternatives_affectations::invalid tag')

        tag_list = xmcda.getiterator('alternativeAffectation')
        for tag in tag_list:
            aa = alternative_affectation()
            aa.from_xmcda(tag)
            self.append(aa)

        return self

class alternative_affectation(object):

    def __init__(self, alternative_id=None, category_id=None):
        self.alternative_id = alternative_id
        self.category_id = category_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "%s: %s" % (self.alternative_id, self.category_id)

    def copy(self):
        return deepcopy(self)

    def display(self, header=True):
        if header is True:
            print('\tcateg.\n')

        print("%-6s\t%-6s" % (self.alternative_id, self.category_id))

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativeAffectation')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.alternative_id
        catid = ElementTree.SubElement(xmcda, 'categoryID')
        catid.text = self.category_id
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'alternativeAffectation':
            raise TypeError('alternativeAffectation::invalid tag')

        altid = xmcda.find('alternativeID')
        self.alternative_id = altid.text
        catid = xmcda.find('categoryID')
        self.category_id = catid.text

        return self
