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
            c = criterion(None)
            c.from_xmcda(tag)
            self.append(c)

class criterion:

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
        if self.name is not None:
            return "%s" % self.name
        else:
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

        c_id = crit.get('id')
        if c_id is not None:
            self.id = c_id

        name = crit.get('name')
        if name is not None:
            self.name = name

        active = crit.find('.//active')
        if active is not None:
            if active.text == 'false':
                self.disabled = True
            else:
                self.disabled = False

        pdir = crit.find('.//scale/quantitative/preferenceDirection')
        if pdir is not None:
            if pdir.text == 'max':
                self.direction = 1
            elif pdir.text == 'min':
                self.direction = -1
            else:
                raise TypeError('criterion::invalid preferenceDirection')

        value = crit.find('.//criterionValue/value')
        if value is not None:
            self.weight = unmarshal(value.getchildren()[0])

class criteria_values(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

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

class criterion_value():

    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value

    def __repr__(self):
        return "%s: %s" % (self.id, self.value)

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self, id=None, name=None):
        xmcda = ElementTree.Element('criterionValue')
        if id is not None:
            xmcda.set('id', id)
        critid = ElementTree.SubElement(xmcda, 'criterionID')
        critid.text = self.id
        val = ElementTree.SubElement(xmcda, 'value')
        val.append(marshal(self.value))
        return xmcda

class alternatives(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

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

        tag_list = alternatives.getiterator('alternative')
        for tag in tag_list:
            alt = alternative(None)
            alt.from_xmcda(tag)
            self.append(alt)

class alternative:

    def __init__(self, id=None, name=None, disabled=False):
        self.id = id
        self.name = name
        self.disabled = disabled

    def __repr__(self):
        if self.name is not None:
            return "%s" % self.name
        else:
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

        self.id = alternative.get('id')
        name = alternative.get('name')
        if name:
            self.name = name

        active = alternative.find('active')
        if active is not None and active.text == 'false':
            self.disabled = True
        else:
            self.disabled = False

class performance_table(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.alternative_id] = i

    def __iter__(self):
        return self.itervalues()

    def __call__(self, id):
        return self[id].performances

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

        tag_list = pt.getiterator('alternativePerformances')
        for tag in tag_list:
            altp = alternative_performances(0, {})
            altp.from_xmcda(tag)
            self.append(altp)

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

class alternative_performances():

    def __init__(self, alternative_id=None, performances=None):
        self.alternative_id = alternative_id
        self.performances = performances

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

        altid = altp.find('.//alternativeID')
        self.alternative_id = altid.text

        tag_list = altp.getiterator('performance')
        for tag in tag_list:
            crit_id = tag.find('.//criterionID').text
            value = tag.find('.//value')
            crit_val = unmarshal(value.getchildren()[0])
            self.performances[crit_id] = crit_val

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

class category_values(dict):

    def __init__(self, l = []):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

    def to_xmcda(self):
        root = ElementTree.Element('categoriesValues')
        for cat_value in self:
            xmcda = cat_value.to_xmcda()
            root.append(xmcda)
        return root

class category_value():

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def to_xmcda(self):
        xmcda = ElementTree.Element('categoryValue')
        catid = ElementTree.SubElement(xmcda, 'categoryID')
        catid.text = self.id
        value = ElementTree.SubElement(xmcda, 'value')
        value.append(self.value.to_xmcda())
        return xmcda

class interval():

    def __init__(self, lower = float("-inf"), upper = float("inf")):
        self.lower = lower
        self.upper = upper

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

class alternative_values(dict):

    def __init__(self, l = []):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

class alternative_value():

    def __init__(self, id, value):
        self.id = id
        self.value = value

class criterion_functions(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.id] = i

    def __iter__(self):
        return self.itervalues()

class criterion_function():

    def __init__(self, id, function):
        self.id = id
        self.function = function

    def y(self, x):
        return self.function.y(x)

class linear():

    def __init__(self, slope, intercept):
        self.slope = slope
        self.intercept = intercept

    def y(self, x):
        return self.slope * x + self.intercept

    def x(self, y):
        return (y - self.intercept) / self.slope

class segment():

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

class piecewise_linear(list):

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

class points(list):

    def __call__(self, id):
        p = None
        for point in self:
            if point.id == id:
                p = point

        return p

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        root = ElementTree.Element('points')
        for p in self:
            xmcda = p.to_xmcda()
            root.append(xmcda)
        return root

class point():

    def __init__(self, x, y, id = None):
        self.id = id
        self.x = x
        self.y = y

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        xmcda = ElementTree.Element('point')
        abscissa = ElementTree.SubElement('abscissa')
        abscissa.append(marshal(self.x))
        ordinate = ElementTree.SubElement('ordinate')
        ordinate.append(marshal(self.y))
        return xmcda

class constant():

    def __init__(self, id, value):
        self.id = id
        self.value = value

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

class threshold():

    def __init__(self, id, name=None, values=None):
        self.id = id
        self.name = name
        self.values = values

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

class category():

    def __init__(self, id=None, name=None, disabled=False, rank=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.rank = rank

    def __repr__(self):
        if self.name is not None:
            return "%s" % self.name
        else:
            return "%s" % self.id

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        xmcda = ElementTree.Element('category', self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        active = ElementTree.SubElement(xmcda, 'active')
        if self.disabled is False:
            active.text = 'true'
        else:
            active.text = 'false'

        rank = ElementTree.SubElement(xmcda, 'rank')
        rank.text = marshal(self.rank)

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

class limits():

    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper  = upper

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        xmcda = ElementTree.Element('limits')

        if self.lower:
            lower = ElementTree.SubElement(xmcda, 'lowerCategory')
            catid = ElementTree.SubElement(lower, 'categoryID')
            catid.text = lower

        if self.upper:
            upper = ElementTree.SubElement(xmcda, 'upperCategory')
            catid = ElementTree.SubElement(upper, 'categoryID')
            catid.text = upper

        return xmcda

class categories_profiles(dict):

    def __init__(self, l=[]):
        for cp in l:
            self[cp.id] = cp

    def __iter__(self):
        return self.itervalues()

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

class category_profile():

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        xmcda = ElementTree.Element('categoryProfile')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.id
        value = self.value.to_xmcda()
        xmcda.append(value)
        return xmcda

class alternatives_affectations(dict):

    def __init__(self, l=[]):
        for i in l:
            self[i.alternative_id] = i

    def __iter__(self):
        return self.itervalues()

    def __call__(self, id):
        return self[id].category_id

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
        if xmcda.tag != 'alternatives_affectations':
            raise TypeError('alternatives_affectations::invalid tag')

        tag_list = xmcda.getiterator('alternativeAffectation')
        for tag in tag_list:
            aa = alternative_affectation()
            aa.from_xmcda(tag)
            self.append(aa)

class alternative_affectation():

    def __init__(self, alternative_id=None, category_id=None):
        self.alternative_id = alternative_id
        self.category_id = category_id

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
        if xmcda.tag != 'alternative_affectation':
            raise TypeError('alternative_affectation::invalid tag')

        altid = xmcda.find('alternativeID')
        self.alternative_id = altid.text 
        catid = xmcda.find('categoryID')
        self.category_id = catid.text
