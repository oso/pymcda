"""
.. module:: types
.. moduleauthor:: Olivier Sobrie <olivier@sobrie.be>
"""

from __future__ import division, print_function
import random
import sys
from itertools import product
from functools import cmp_to_key
from xml.etree import ElementTree
from copy import deepcopy
from collections import OrderedDict

type2tag = {
    int: 'integer',
    float: 'real',
    str: 'label',
}

unmarshallers = {
    'integer': lambda x: int(x.text),
    'real': lambda x: float(x.text),
    'label': lambda x: str(x.text),
}

def marshal(value):
    tag = type2tag.get(type(value))
    e = ElementTree.Element(tag)
    e.text = str(value)
    return e

def unmarshal(xml):
    m = unmarshallers.get(xml.tag)
    return m(xml)

def find_xmcda_tag(xmcda, tag, id = None):
    if xmcda.tag == tag and (id is None or xmcda.get('id') == id):
        return xmcda

    if id is None:
        search_str = ".//%s" % tag
    else:
        search_str = ".//%s[@id='%s']" % (tag, id)

    xmcda = xmcda.find(search_str)
    if xmcda is None:
        raise TypeError("%s::invalid tag" % tag)

    return xmcda

class McdaDict(object):
    """This class allows to declare an MCDA dictionnary element.
    It contains usefull methods to manipulate MCDA data.
    """

    def __init__(self, l = list(), id = None):
        """Create a new MCDA dictionnary instance

        Kwargs:
           l (list): A list containing a set of MCDA objects
           id (str): The identifier of the dictionnary
        """
        self.id = id
        self._d = OrderedDict()
        for i in l:
            self._d[i.id] = i

    def __contains__(self, key):
        """Check if a MCDA object is present in the dictionnary. If the
        object is contained in the dictionnary, True is returned,
        otherwise False is returned."""

        return self._d.__contains__(key)

    def __eq__(self, mcda_dict):
        """This method allows to compare the current MCDA dictionnary to
        another MCDA dictionnary. If the two MCDA dictionnaries are
        equal, then True is returned, otherwise False is returned."""

        return self._d.__eq__(dict(mcda_dict._d))

    def __hash__(self):
        return hash(frozenset(self._d.iteritems()))

    def __iter__(self):
        """Return an iterator object for the MCDA dictionnary."""

        try:
            return self._d.itervalues()
        except:
            return iter(self._d.values())

    def __getitem__(self, key):
        """Lookup for an MCDA object in the dictionnary on basis of its
        identifier. If there is no object with idenfier 'id' in the
        MCDA dictionnary, then KeyError exception is returned."""

        return self._d.__getitem__(key)

    def __len__(self):
        """Return the number of elements contained in the MCDA
        dictionnary."""

        return self._d.__len__()

    def append(self, mcda_object):
        """Add an MCDA object in the MCDA dictionnary"""

        self._d[mcda_object.id] = mcda_object

    def copy(self):
        """Perform a full copy of the MCDA dictionnary"""

        return deepcopy(self)

    def has_key(self, key):
        """Check if MCDA object id is in the dictionnary"""

        return self._d.has_key(key)

    def items(self):
        """Return a copy of the MCDA dictionary's list of (id, mcda_object)
        pairs"""

        return self._d.items()

    def iterkeys(self):
        """Return an iterator over the MCDA dictionary's object IDs"""

        return self._d.iterkeys()

    def itervalues(self):
        """Return an iterator over the MCDA dictionary's object IDs"""

        return self._d.itervalues()

    def keys(self):
        """Return the list of MCDA object IDs contained in the MCDA
        dictionnary"""

        return self._d.keys()

    def remove(self, key):
        """This method allows to remove an element from the dictionnary"""

        del self._d[key]

    def update(self, mcda_dict):
        """Add the object of a second MCDA dictionnary into the current
        dictionnary"""

        self._d.update(mcda_dict)

    def values(self):
        """Return the list of MCDA objects contained in the MCDA
        dictionnary"""

        return self._d.values()

    def to_list(self):
        """Return a list of MCDA objects contained in the MCDA dictionnary
        ordered by MCDA object ID"""

        l = self._d.values()
        l.sort(key = lambda x: x.id)
        return l

    def get_subset(self, ids):
        """Return a subset of the current MCDA dictionnary containing the
        MCDA object IDs"""

        return type(self)([self._d[id] for id in ids])

    def split(self, n, proportions = None, randomize = True):
        """Split the MCDA dictionnary into two or several parts

        Kargs:
           n (integer): Number of parts in which the MCDA dictionnary
                        should be split

        Kwargs:
           propostions (list): A list containing the proportions of
                               subset
           randomize (bool): Wheter or not the split should be randomize
        """

        if proportions is None:
            proportions = [1 / n] * n
        elif len(proportions) == n:
            t = sum(proportions)
            proportions = [proportion / t for proportion in proportions]
        else:
            raise ValueError('%s::split invalid proportions')

        keys, nkeys = list(self._d.keys()), len(self._d.keys())
        j, subsets = 0, []

        if randomize is True:
            random.shuffle(keys)

        for proportion in proportions:
            j2 = int(j + proportion * nkeys)
            subset = type(self)(self._d[i] for i in keys[j:j2])
            j = j2
            subsets.append(subset)

        subset = type(self)(self._d[i] for i in keys[j2:nkeys])
        subsets[-1].update(subset)

        return tuple(subsets)

class McdaObject(object):

    def __eq__(self, other):
        """Return True if the two MCDA objects are equal, otherwise
        return False"""

        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.id)

    def copy(self):
        """Return a copy of the current MCDA object"""

        return deepcopy(self)

class CriteriaSets(object):

    def __init__(self, cs = None, id = None):
        self.id = id
        self.cs = cs if cs is not None else set()

    def __iter__(self):
        """Return an iterator object for the MCDA dictionnary."""

        return self.cs.__iter__()

    def __len__(self):
        return len(self.cs)

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "CriteriaSets(%s)" % ', '.join(map(str, self.cs))

    def add(self, cs):
        return self.cs.add(cs)

    def copy(self):
        """Perform a full copy of the Criteria set"""

        return deepcopy(self)

    def remove(self, x):
        return self.cs.remove(x)

    def discard(self, x):
        return self.cs.discard(x)

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('CriteriaSets')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for cs in self:
            xmcda = cs.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criteriaSets', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('criteriaSet')
        for tag in tag_list:
            cs = CriteriaSet().from_xmcda(tag)
            self.add(cs)

        return self

class CriteriaSet(object):

    def __init__(self, criteria = None):
        self.criteria = set(criteria) if criteria is not None else set()

    def __repr__(self):
        return "CriteriaSet(%s)" % ', '.join(map(str, self.criteria))

    def __eq__(self, other):
        return set(self.criteria) == set(other.criteria)

    def __hash__(self):
        return hash(frozenset(self.criteria))

    def __iter__(self):
        return self.criteria.__iter__()

    def __len__(self):
        return len(self.criteria)

    def __str__(self):
        return '[%s]' % ', '.join(map(str, self.criteria))

    def add(self, x):
        return self.criteria.add(x)

    def copy(self):
        """Return a copy of the current MCDA object"""

        return deepcopy(self)

    def remove(self, x):
        return self.criteria.remove(x)

    def discard(self, x):
        return self.criteria.discard(x)

    def issubset(self, criteria):
        if isinstance(criteria, CriteriaSet) is False \
           and isinstance(criteria, set) is False \
           and isinstance(criteria, frozenset) is False:
            return criteria in self.criteria

        return self.criteria.issubset(criteria)

    def issuperset(self, criteria):
        if isinstance(criteria, CriteriaSet) is False \
           and isinstance(criteria, set) is False \
           and isinstance(criteria, frozenset) is False:
            return criteria in self.criteria

        return self.criteria.issuperset(criteria)

    def to_xmcda(self):
        """Convert the CriteriaSet into XMCDA"""

        root = ElementTree.Element('criteriaSet')
        for c in self.criteria:
            el = ElementTree.SubElement(root, 'element')
            cid = ElementTree.SubElement(el, 'criterionID')
            cid.text = str(c)

        return root

    def from_xmcda(self, xmcda):
        """Read the MCDA object from XMCDA input"""
        xmcda = find_xmcda_tag(xmcda, 'criteriaSet')

        tag_list = xmcda.getiterator('criterionID')
        for tag in tag_list:
            self.criteria.add(tag.text)

        return self

class Criteria(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "Criteria(%s)" % self.values()

    def get_active(self):
        return Criteria([c for c in self if c.disabled is not True])

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('criteria')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for crit in self:
            crit_xmcda = crit.to_xmcda()
            root.append(crit_xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criteria', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('criterion')
        for tag in tag_list:
            c = Criterion().from_xmcda(tag)
            self.append(c)

        return self

    def from_csv(self, csvreader, crit_col, name_col = None,
                 disabled_col = None, direction_col = None):
        """Read the MCDA dictionnary from CSV input"""

        cols = None
        for row in csvreader:
            if row[0] == crit_col:
                cols = OrderedDict({})
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
                c = Criterion(row[0])
                for i in cols.keys():
                    if cols[i] == 'direction':
                        row[i] = int(row[i])
                    setattr(c, cols[i], row[i])
                self.append(c)

        return self


class Criterion(McdaObject):

    MINIMIZE = -1
    MAXIMIZE = 1

    def __init__(self, id=None, name=None, disabled=False,
                 direction=MAXIMIZE, weight=None, thresholds=None):
        """Create a new Criterion instance

        Kwargs:
           id (str): Identifier of the criterion
           name (str): A friendly name for the criterion
           disabled (bool): Whether or not this criterion is disabled
           direction (integer): Equal to -1 if criterion is to minimize,
                                1 if the criterion is to maximize
           weight (float): Deprecated
           thresholds (list): List of threshold associated to the criterion
        """

        self.id = id
        self.name = name
        self.disabled = disabled
        self.direction = direction
        self.weight = weight
        self.thresholds = thresholds

    def __repr__(self):
        """Manner to represent the MCDA object"""
        direction = "+" if self.direction == 1 else "-"
        return "%s (%s)" % (self.id, direction)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('criterion')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        if self.name is not None:
            root.set('name', self.name)

        active = ElementTree.SubElement(root, 'active')
        active.text = 'true' if self.disabled is False else 'false'

        scale = ElementTree.SubElement(root, 'scale')
        quant = ElementTree.SubElement(scale, 'quantitative')
        prefd = ElementTree.SubElement(quant, 'preferenceDirection')
        prefd.text = 'max' if self.direction == 1 else 'min'

        if self.weight:
            crit_val = ElementTree.SubElement(root, 'criterionValue')
            value = ElementTree.SubElement(crit_val, 'value')
            weight = marshal(self.weight)
            value.append(weight)

        if self.thresholds:
            thresholds = self.thresholds.to_xmcda()
            root.append(thresholds)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criterion', id)

        self.id = xmcda.get('id')
        self.name = xmcda.get('name')

        active = xmcda.find('.//active')
        if active is not None:
            self.disabled = True if active.text == 'false' else False

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

        value = xmcda.find('.//thresholds')
        if value is not None:
            self.thresholds = Thresholds().from_xmcda(value)

        return self

class CriteriaValues(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "CriteriaValues(%s)" % self.values()

    def __str__(self):
        l = 0
        for cv in self:
            l = max(len("%s" % cv.id), l)

        string = ""
        for cv in self:
            string += "%*s: %s\n" % (l, cv.id, cv.value)

        return string[:-1]

    def min(self):
        return min([cv.value for cv in self])

    def max(self):
        return max([cv.value for cv in self])

    def sum(self):
        return sum([cv.value for cv in self])

    def normalize(self, vmin = None, vmax = None):
        vmin = self.min() if vmin is None else vmin
        vmax = self.max() if vmax is None else vmax

        for cv in self:
            cv.value = (cv.value - vmin) / (vmax - vmin)

    def normalize_sum_to_unity(self):
        """Method that allow to  normalize all the criteria values
        contained in the MCDA dictionnary"""

        total = sum([cv.value for cv in self])

        for cv in self:
            cv.value /= total

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('criteriaValues')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for cval in self:
            cv = cval.to_xmcda()
            root.append(cv)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criteriaValues', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('criterionValue')
        for tag in tag_list:
            cv = CriterionValue().from_xmcda(tag)
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
            cols_max[cid] = max([len(fmt % self[cid].value), len("%s" % cid)])

        # Print header
        line = "  "
        for cid in criterion_ids:
            line += " " * (cols_max[cid] - len("%s" % cid)) + str(cid) + " "
        print(line, file = out)

        # Print values
        line = "w" + " "
        for cid in criterion_ids:
            val = fmt % self[cid].value
            line += " " * (cols_max[cid] - len(val)) + val + " "
        print(line, file = out)

class CriterionValue(McdaObject):

    def __init__(self, id=None, value=None):
        """Create a new CriterionValue instance

        Kwargs:
           id (str): Identifier of the Criterion
           value (float): The value associated to the criterion
        """

        self.id = id
        self.value = value

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "CriterionValue(%s: %s)" % (self.id, self.value)

    def __str__(self):
        return "%s: %s" % (self.id, self.value)

    def id_issubset(self, ids):
        if isinstance(self.id, CriteriaSet) or isinstance(self.id, set) \
           or isinstance(self.id, frozenset):
            return self.id.issubset(ids)
        elif isinstance(ids, CriteriaSet) or isinstance(ids, set) \
           or isinstance(ids, frozenset):
            if isinstance(self.id, str):
                return self.id in ids
            else:
                return ids.issuperset(self.id)
        else:
            return self.id is ids

    def to_xmcda(self, id=None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('criterionValue')

        if id is not None:
            root.set('id', str(id))
        elif self.id is not None:
            root.set('id', str(self.id))

        critid = ElementTree.SubElement(root, 'criterionID')
        if isinstance(self.id, CriteriaSet):
            critid.append(self.id.to_xmcda())
        else:
            critid.text = self.id
        val = ElementTree.SubElement(root, 'value')
        val.append(marshal(self.value))

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criterionValue', id)

        self.id = xmcda.get('id')

        cid = xmcda.find('.//criterionID')
        cset = cid.find('.//criteriaSet')
        self.id = CriteriaSet().from_xmcda(cset) if cset is not None \
                                                 else cid.text

        value = xmcda.find('.//value')
        if value is not None:
            self.value = unmarshal(value.getchildren()[0])

        return self

class Alternatives(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "Alternatives(%s)" % self.values()

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('alternatives')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for action in self:
            alt = action.to_xmcda()
            root.append(alt)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternatives', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('alternative')
        for tag in tag_list:
            alt = Alternative().from_xmcda(tag)
            self.append(alt)

        return self

    def from_csv(self, csvreader, alt_col, name_col = None,
                 disabled_col = None):
        """Read the MCDA dictionnary from CSV input"""

        cols = None
        for row in csvreader:
            if row[0] == alt_col:
                cols = OrderedDict({})
                for i, val in enumerate(row[1:]):
                    if val == name_col:
                        cols[i + 1] = "name"
                    if val == disabled_col:
                        cols[i + 1] = "disabled"
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                a = Alternative(row[0])
                for i in cols.keys():
                    setattr(a, cols[i], row[i])
                self.append(a)

        return self

class Alternative(McdaObject):

    def __init__(self, id=None, name=None, disabled=False):
        """Create a new Alternative instance

        Kwargs:
           id (str): Identifier of the alternative
           name (str): A friendly name for the alternative
           disabled (bool): Whether or not this alternative is disabled
        """

        self.id = id
        self.name = name
        self.disabled = disabled

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "Alternative(%s)" % self.id

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('alternative')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        if self.name is not None:
            root.set('name', self.name)

        active = ElementTree.SubElement(root, 'active')
        active.text = 'true' if self.disabled is False else 'false'

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternative', id)

        self.id = xmcda.get('id')
        self.name = xmcda.get('name')

        active = xmcda.find('active')
        self.disabled = True if active is not None and active.text == 'false' \
                             else False

        return self

class PerformanceTable(McdaDict):

    def __call__(self, id):
        return self[id].performances

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "PerformanceTable(%s)" % self.values()

    def __str__(self):
        l = 0 if self.id is None else len(self.id)
        col = OrderedDict()
        for ap in self:
            l = max(len(ap.id), l)
            for k, v in ap.performances.items():
                m = max(len(k), len("%s" % v))
                col[k] = m if k not in col else max(col[k], m)

        crit = list(col.keys())

        string = "%*s" % (l, self.id) if self.id is not None else " " * l

        for c in crit:
            string += " %*s" % (col[c], c)

        string += "\n"
        for ap in self:
            string += "%*s" % (l, ap.id)
            for c in crit:
                if c in ap.performances:
                    string += " %*s" % (col[c], ap.performances[c])
                else:
                    string += " " * (col[c] + 1)

            string += "\n"

        return string[:-1]

    def __mathop(self, value, op):
        out = PerformanceTable([], self.id)
        if type(value) == float or type(value) == int \
           or type(AlternativePerformances):
            for key, val in self.items():
                if op == "add":
                    ap = val + value
                elif op == "sub":
                    ap = val - value
                elif op == "mul":
                    ap = val * value
                elif op == "div":
                    ap = val / value
                out.append(ap)
        elif type(PerformanceTable):
            for key, val in self.items():
                ap = val * value[key]
                out.append(ap)
        else:
            raise TypeError("Invalid value type (%s)" % type(value))

        return out

    def __add__(self, value):
        """Add value to the performances"""

        return self.__mathop(value, "add")

    def __sub__(self, value):
        """Substract value to the performances"""

        return self.__mathop(value, "sub")

    def __mul__(self, value):
        """Multiply performances by value"""

        return self.__mathop(value, "mul")

    def __div__(self, value):
        return self.__truediv__(value)

    def __truediv__(self, value):
        """Divide performances by value"""

        return self.__mathop(value, "div")

    def get_criteria_ids(self):
        return next(self.itervalues()).performances.keys()

    def update_direction(self, c):
        """Multiply all performances by -1 if the criterion is to
        minimize"""

        for ap in self._d.values():
            ap.update_direction(c)

    def round(self, k = 3, cids = None):
        """Round all performances on criteria cids to maximum k digit

        Kwargs:
           k (int): max number of digit
           cids (list): list of criteria which should be rounded to k
                        digit
        """

        if cids is None:
            cids = next(self._d.itervalues()).performances.keys()

        for ap in self._d.values():
            ap.round(k, cids)

    def multiply(self, value, cids = None):
        """Multiply all performance on criteria cids by value

        Kwargs:
           value (float): value by which each performance should be
                          multiplied
           cids (list): list of criteria which should be multiplied by
                        value
        """

        if cids is None:
            cids = next(self._d.itervalues()).performances.keys()

        for ap in self._d.values():
            ap.multiply(value, cids)

    def get_best(self, c):
        """Return the best possible fictive alternative performances"""

        perfs = next(self.itervalues()).performances
        wa = AlternativePerformances('best', perfs.copy())
        for ap, crit in product(self, c):
            wperf = wa.performances[crit.id] * crit.direction
            perf = ap.performances[crit.id] * crit.direction
            if wperf < perf:
                wa.performances[crit.id] = ap.performances[crit.id]
        return wa

    def get_worst(self, c):
        """Return the worst possible fictive alternative performances"""

        perfs = next(self.itervalues()).performances
        wa = AlternativePerformances('worst', perfs.copy())
        for ap, crit in product(self, c):
            wperf = wa.performances[crit.id] * crit.direction
            perf = ap.performances[crit.id] * crit.direction
            if wperf > perf:
                wa.performances[crit.id] = ap.performances[crit.id]
        return wa

    def get_min(self):
        """Return an alternative which has the minimal performances on all
        criteria"""

        perfs = next(self.itervalues()).performances
        a = AlternativePerformances('min', perfs.copy())
        for ap, cid in product(self, perfs.keys()):
            perf = ap.performances[cid]
            if perf < a.performances[cid]:
                a.performances[cid] = perf
        return a

    def get_max(self):
        """Return an alternative which has the maximal performances on all
        criteria"""

        perfs = next(self.itervalues()).performances
        a = AlternativePerformances('max', perfs.copy())
        for ap, cid in product(self, perfs.keys()):
            perf = ap.performances[cid]
            if perf > a.performances[cid]:
                a.performances[cid] = perf
        return a

    def get_mean(self):
        """Return an alternative which has the mean performances on all
        criteria"""

        cids = next(self.itervalues()).performances.keys()
        a = AlternativePerformances('mean', {cid: 0 for cid in cids})
        for ap, cid in product(self, cids):
            perf = ap.performances[cid]
            a.performances[cid] += perf

        for cid in cids:
            a.performances[cid] /= len(self)

        return a

    def get_range(self):
        """Return the range of the evaluations on each criterion"""

        ap_min = self.get_min().performances
        ap_max = self.get_max().performances

        cids = next(self.itervalues()).performances.keys()
        a = AlternativePerformances('range')
        for cid in cids:
            a.performances[cid] = ap_max[cid] - ap_min[cid]

        return a

    def get_unique_values(self):
        """Return the unique values on each criterion"""

        cids = next(self.itervalues()).performances.keys()
        a = {cid: set() for cid in cids}
        for ap, cid in product(self, cids):
            perf = ap.performances[cid]
            a[cid].add(perf)

        for key, val in a.items():
            a[key] = sorted(list(val))

        return a

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('performanceTable')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for alt_perfs in self:
            xmcda = alt_perfs.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'performanceTable', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('alternativePerformances')
        for tag in tag_list:
            altp = AlternativePerformances().from_xmcda(tag)
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
        """Read the MCDA dictionnary from CSV input"""

        cols = None
        for row in csvreader:
            if row[0] == alt_col:
                cols = OrderedDict({})
                for i, val in enumerate(row[1:]):
                    if val not in perf_cols:
                        continue

                    cols[i + 1] = val
            elif cols is not None and row[0] == '':
                break
            elif cols is not None:
                ap = AlternativePerformances(row[0])
                for i in cols.keys():
                    cid = cols[i]
                    perf = float(row[i])
                    ap.performances[cid] = perf
                self.append(ap)

        return self

class AlternativePerformances(McdaObject):

    def __init__(self, id=None, performances=None, alternative_id=None):
        """Create a new AlternativePerformances instance

        Kwargs:
           id (str): Identifier of the alternative
           performances (dict): Alternatives' performances on the
                                different criteria
        """

        self.id = id
        self.altid = alternative_id
        if self.altid is None:
            self.altid = id

        self.performances = OrderedDict({}) if performances is None else performances

    def __call__(self, criterion_id):
        """Return the performance of the alternative on criterion_id"""
        return self.performances[criterion_id]

    def __repr__(self):
        """Manner to represent the MCDA object"""
        return "AlternativePerformances(%s: %s)" % (self.id, self.performances)

    def __str__(self):
        l = 0
        for k in self.performances.keys():
            l = max(len(k), l)

        l += len(self.id)

        string = "%s:" % self.id
        for k, v in self.performances.items():
            string += " %s: %f\n" % (k, v)
            string += " " * (len(self.id) + 1)

        return string[:string.rfind('\n')]

    def __mathop(self, value, op):
        out = AlternativePerformances(self.id)
        if type(value) == float or type(value) == int:
            for key in self.performances.keys():
                if op == 'add':
                    out.performances[key] = self.performances[key] + value
                elif op == 'sub':
                    out.performances[key] = self.performances[key] - value
                elif op == 'mul':
                    out.performances[key] = self.performances[key] * value
                elif op == 'div':
                    out.performances[key] = self.performances[key] / value
        elif type(value) == AlternativePerformances:
            for key in self.performances.keys():
                if op == 'add':
                    out.performances[key] = self.performances[key] + \
                                            value.performances[key]
                elif op == 'sub':
                    out.performances[key] = self.performances[key] - \
                                            value.performances[key]
                elif op == 'mul':
                    out.performances[key] = self.performances[key] * \
                                            value.performances[key]
                elif op == 'div':
                    out.performances[key] = self.performances[key] / \
                                            value.performances[key]
        else:
            raise TypeError("Invalid value type (%s)" % type(value))

        return out

    def __add__(self, value):
        """Add value to the performances"""

        return self.__mathop(value, "add")

    def __sub__(self, value):
        """Substract value to the performances"""

        return self.__mathop(value, "sub")

    def __mul__(self, value):
        """Multiply performances by value"""

        return self.__mathop(value, "mul")

    def __div__(self, value):
        return self.__truediv__(value)

    def __truediv__(self, value):
        """Divide performances by value"""

        return self.__mathop(value, "div")

    def update_direction(self, c):
        """Multiply all performances by -1 if the criterion is to
        minimize"""

        for crit in c:
            self.performances[crit.id] *= crit.direction

    def round(self, k = 3, cids = None):
        """Round all performances on criteria cids to maximum k digit
        Kwargs:
           k (int): max number of digit
           cids (list): list of criteria which should be rounded to k
                        digit
        """

        if cids is None:
            cids = self.performances.keys()

        for key, value in self.performances.items():
            self.performances[key] = round(value, k)

    def multiply(self, value, cids = None):
        """Multiply all performance on criteria cids by value

        Kwargs:
           value (float): value by which each performance should be
                          multiplied
           cids (list): list of criteria which should be multiplied by
                        value
        """

        if cids is None:
            cids = self.performances.keys()

        for key in self.performances:
            self.performances[key] *= value

    def is_as_good_as(self, ap, criteria):
        for crit_id, val in self.performances.items():
            direction = criteria[crit_id].direction
            val2 = ap.performances[crit_id] * direction
            val = val * direction
            if val2 > val:
                return False

        return True

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('alternativePerformances')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        altid = ElementTree.SubElement(root, 'alternativeID')
        altid.text = self.altid

        for crit_id, val in self.performances.items():
            perf = ElementTree.SubElement(root, 'performance')
            critid = ElementTree.SubElement(perf, 'criterionID')
            critid.text = crit_id
            value = ElementTree.SubElement(perf, 'value')
            p = marshal(val)
            value.append(p)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternativePerformances', id)

        self.id = xmcda.get('id')

        altid = xmcda.find('.//alternativeID')
        self.altid = altid.text
        if self.id is None:
            self.id = altid.text

        tag_list = xmcda.getiterator('performance')
        for tag in tag_list:
            crit_id = tag.find('.//criterionID').text
            value = tag.find('.//value')
            crit_val = unmarshal(value.getchildren()[0])
            self.performances[crit_id] = crit_val

        return self

class CategoriesValues(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "CategoriesValues(%s)" % self.values()

    def display(self, out = sys.stdout):
        for cv in self:
            cv.display(out)

    def get_upper_limits(self):
        d = {}
        for cv in self:
            d[cv.id] = cv.value.upper
        return d

    def get_lower_limits(self):
        d = {}
        for cv in self:
            d[cv.id] = cv.value.lower
        return d

    def __cmp_categories_values(self, catva, catvb):
        if catva.value.lower > catvb.value.lower:
            return 1
        elif catva.value.lower < catvb.value.lower:
            return 0
        elif catva.value.upper > catvb.value.upper:
            return 1
        else:
            return 0

    def get_ordered_categories(self):
        """Get the list of ordered categories"""

        catvs = sorted(self, key = cmp_to_key(self.__cmp_categories_values))
        return [catv.id for catv in catvs]

    def to_categories(self):
        """Convert the content of the dictionnary into Categories()"""

        cats = Categories()
        for i, cat in enumerate(reversed(self.get_ordered_categories())):
            cat = Category(cat, rank = i + 1)
            cats.append(cat)
        return cats

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('categoriesValues')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for cat_value in self:
            xmcda = cat_value.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'categoriesValues', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('categoryValue')
        for tag in tag_list:
            altp = CategoryValue().from_xmcda(tag)
            self.append(altp)

        return self

class CategoryValue(McdaObject):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "CategoryValue(%s: %s)" % (self.id, self.value)

    def pprint(self):
        return "%s: %s" % (self.id, self.value.pprint())

    def display(self, out = sys.stdout):
        print(self.pprint(), file = out)

    def to_xmcda(self):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('categoryValue')

        catid = ElementTree.SubElement(root, 'categoryID')
        catid.text = self.id
        value = ElementTree.SubElement(root, 'value')
        value.append(self.value.to_xmcda())

        return root

    def from_xmcda(self, xmcda):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'categoryValue', None)

        self.id = xmcda.find('.//categoryID').text

        value = xmcda.find('.//value').getchildren()[0]
        if value.tag == 'interval':
            self.value = Interval().from_xmcda(value)
        else:
            self.value = unmarshal(value)

        return self

class Interval(McdaObject):

    def __init__(self, lower = float("-inf"), upper = float("inf")):
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "Interval(%s,%s)" % (self.lower, self.upper)

    def pprint(self):
        return "%s - %s" % (self.lower, self.upper)

    def display(self):
        print(self.pprint())

    def included(self, value):
        if self.lower and value < self.lower:
            return False

        if self.upper and value > self.upper:
            return False

        return True

    def to_xmcda(self):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('interval')

        lower = ElementTree.SubElement(root, "lowerBound")
        lower.append(marshal(self.lower))
        upper = ElementTree.SubElement(root, "upperBound")
        upper.append(marshal(self.upper))

        return root

    def from_xmcda(self, xmcda):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'interval')

        lower = xmcda.find('.//lowerBound')
        self.lower = unmarshal(lower.getchildren()[0])
        upper = xmcda.find('.//upperBound')
        self.upper = unmarshal(upper.getchildren()[0])

        return self

class AlternativesValues(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "AlternativesValues(%s)" % self.values()

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('alternativesValues')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for a_value in self:
            xmcda = a_value.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternativesValues', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('alternativeValue')
        for tag in tag_list:
            altp = AlternativeValue().from_xmcda(tag)
            self.append(altp)

        return self

class AlternativeValue(McdaObject):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "AlternativeValue(%s: %s)" % (self.id, self.value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('alternativeValue')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        lower = ElementTree.SubElement(root, "alternativeID")
        lower.text = str(self.id)
        value = ElementTree.SubElement(root, "value")
        value.append(marshal(self.value))

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternativeValue', id)

        self.id = xmcda.find('.//alternativeID').text
        value = xmcda.find('.//value').getchildren()[0]
        self.value = unmarshal(value)

        return self

class CriteriaFunctions(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "CriteriaFunctions(%s)" % self.values()

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

    def multiply_y(self, cvs):
        for cf in self:
            cf.multiply_y(cvs[cf.id].value)

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('criteriaFunctions')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for a_value in self:
            xmcda = a_value.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criteriaFunctions', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('criterionFunction')
        for tag in tag_list:
            cf = CriterionFunction().from_xmcda(tag)
            self.append(cf)

        return self

class CriterionFunction(McdaObject):

    def __init__(self, id = None, function = None):
        self.id = id
        self.function = function

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "CriterionFunction(%s: %s)" % (self.id, self.function)

    def y(self, x):
        return self.function.y(x)

    def pprint(self):
        return "%s:\t%s" % (self.id, self.function.pprint())

    def display(self):
        print(self.pprint())

    def multiply_y(self, value):
        self.function.multiply_y(value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('criterionFunction')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        critid = ElementTree.SubElement(root, 'criterionID')
        critid.text = self.id
        function = self.function.to_xmcda()
        root.append(function)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'criterionFunction', id)

        self.id = xmcda.find('.//criterionID').text

        value = xmcda.find('.//piecewiseLinear')
        if value is not None:
            self.function = PiecewiseLinear().from_xmcda(value)

        value = xmcda.find('.//points')
        if value is not None:
            self.function = Points().from_xmcda(value)

        return self

class Linear(object):

    def __init__(self, slope, intercept):
        self.slope = slope
        self.intercept = intercept

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "Linear(%sx + %d)" % (self.slope, self.intercept)

    def y(self, x):
        return self.slope * x + self.intercept

    def x(self, y):
        return (y - self.intercept) / self.slope

class Segment(McdaObject):

    def __init__(self, id = None, p1 = None, p2 = None,
                       p1_in = True, p2_in = False):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.p1_in = p1_in
        self.p2_in = p2_in

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "Segment[%s](%s,%s)" % (self.id, self.p1, self.p2)

    @property
    def xmin(self):
        return min([self.p1.x, self.p2.x])

    @property
    def xmax(self):
        return max([self.p1.x, self.p2.x])

    @property
    def ymin(self):
        return min([self.p1.y, self.p2.y])

    @property
    def ymax(self):
        return max([self.p1.y, self.p2.y])

    def slope(self):
        d = self.p2.x - self.p1.x
        return float("inf") if d == 0 else (self.p2.y - self.p1.y) / d

    def y(self, x):
        if x < self.xmin or x > self.xmax:
            raise ValueError("Value out of the segment")
        if x == self.p1.x and self.p1_in is False:
            raise ValueError("Value out of the segment")
        if x == self.p2.x and self.p2_in is False:
            raise ValueError("Value out of the segment")

        k = self.slope()
        if k == 0:
            return self.p1.y

        return self.p1.y + k * (x - self.p1.x)

    def x_is_included(self, x):
        if x > self.xmax or x < self.xmin:
            return False

        if x == self.p1.x and self.p1_in is False:
            return False

        if x == self.p2.x and self.p2_in is False:
            return False

        return True

    def pprint(self):
        return "%s-%s" % (self.p1, self.p2)

    def display(self):
        print(self.pprint())

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('segment')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for obj in ['p1', 'p2']:
            mcda = getattr(self, obj)
            mcda.id = obj
            xmcda = mcda.to_xmcda()
            root.append(xmcda)

        p1_in = ElementTree.SubElement(root, 'p1_in')
        p1_in.text = str(self.p1_in)
        p2_in = ElementTree.SubElement(root, 'p2_in')
        p2_in.text = str(self.p2_in)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'segment', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('point')
        if len(tag_list) != 2:
            raise ValueError('segment:: invalid number of points')

        self.p1 = Point().from_xmcda(tag_list[0])
        self.p2 = Point().from_xmcda(tag_list[1])

        p1_in = xmcda.find('.//p1_in')
        self.p1_in = eval(p1_in.text)
        p2_in = xmcda.find('.//p2_in')
        self.p2_in = eval(p2_in.text)

        return self

class PiecewiseLinear(McdaDict):

    def __repr__(self):
        return "PiecewiseLinear[%s](%s)" % (self.id, self.values())

    def find_segment(self, x):
        for s in self:
            if s.x_is_included(x) is True:
                return s

        return None

    def y(self, x):
        s = self.find_segment(x)
        if s is None:
            raise ValueError("No segment found for this value (%g)" % x)

        return s.y(x)

    def multiply_y(self, value):
        for s in self:
            s.p1.y *= value
            s.p2.y *= value

    @property
    def xmin(self):
        x = [s.xmin for s in self]
        return min(x)

    @property
    def xmax(self):
        x = [s.xmax for s in self]
        return max(x)

    @property
    def ymin(self):
        y = [s.ymin for s in self]
        return min(y)

    @property
    def ymax(self):
        y = [s.ymax for s in self]
        return max(y)

    def get_ordered(self):
        """Return segments ordered by x value"""

        return sorted(self, key = lambda s: s.xmin)

    def pprint(self):
        string = "f("
        for seg in self:
            string += seg.pprint() + ';'
        string = string[:-1] + ")"
        return string

    def display(self):
        print(self.pprint())

    def to_xmcda(self):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('piecewiseLinear')

        for elem in self:
            xmcda = elem.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'piecewiseLinear', id)

        tag_list = xmcda.getiterator('segment')
        for tag in tag_list:
            s = Segment().from_xmcda(tag)
            self.append(s)

        return self

class Points(list):

    def __call__(self, id):
        p = None
        for point in self:
            if point.id == id:
                p = point

        return p

    def __repr__(self):
        return "Points(%s)" % self[:]

    def copy(self):
        return deepcopy(self)

    def to_xmcda(self):
        root = ElementTree.Element('points')

        for p in self:
            xmcda = p.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda):
        xmcda = find_xmcda_tag(xmcda, 'points', id)

        tag_list = xmcda.getiterator('point')
        for tag in tag_list:
            p = Point().from_xmcda(tag)
            self.append(p)

        return self

class Point(McdaObject):

    def __init__(self, x = None, y = None, id = None):
        self.id = id
        self.x = x
        self.y = y

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "Point(%g,%g)" % (self.x, self.y)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('point')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        abscissa = ElementTree.SubElement(root, 'abscissa')
        abscissa.append(marshal(self.x))
        ordinate = ElementTree.SubElement(root, 'ordinate')
        ordinate.append(marshal(self.y))

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'point', id)

        self.id = xmcda.get('id')

        x = xmcda.find('.//abscissa').getchildren()[0]
        self.x = unmarshal(x)
        y = xmcda.find('.//ordinate').getchildren()[0]
        self.y = unmarshal(y)

        return self

class Constant(McdaObject):

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "%s: %s", (self.id, self.value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('constant')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        value = marshal(self.value)
        root.append(value)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'constant', id)

        self.id = xmcda.get('id')
        self.value = unmarshal(xmcda.getchildren()[0])

class Thresholds(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "Thresholds(%s)", self.values()

    def has_threshold(self, threshold_id):
        for t in self:
            if t.id == threshold_id:
                return True

        return False

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('thresholds')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for t in self:
            xmcda = t.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'thresholds', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('threshold')
        for tag in tag_list:
            t = Threshold(None)
            t.from_xmcda(tag)
            self.append(t)

        return self

class Threshold(McdaObject):

    def __init__(self, id, name=None, values=None):
        self.id = id
        self.name = name
        self.values = values

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "%s: %s" % (self.id, self.values.value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('threshold')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        if self.name is not None:
            root.set('name', self.name)

        values = self.values.to_xmcda()
        root.append(values)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'threshold', id)

        self.id = xmcda.get('id')
        self.name = xmcda.get('name')
        values = xmcda.getchildren()[0]
        if values.tag == 'constant':
            c = Constant(None, 0)
            c.from_xmcda(values)
            self.values = c

        return self

class Categories(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "Categories(%s)" % self.values()

    def get_ids(self):
        return self.keys()

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('categories')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for c in self:
            xmcda = c.to_xmcda()
            root.append(xmcda)

        return root

    def get_ordered_categories(self):
        d = {c.id: c.rank for c in self}
        return sorted(d, key = lambda key: d[key], reverse = True)

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'categories', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('category')
        for tag in tag_list:
            c = Category()
            c.from_xmcda(tag)
            self.append(c)

        return self

    def from_csv(self, csvreader, cat_col, name_col = None,
                 rank_col = None, disabled_col = None):
        """Read the MCDA dictionnary from CSV input"""

        cols = None
        for row in csvreader:
            if row[0] == cat_col:
                cols = OrderedDict({})
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
                c = Category(row[0])
                for i in cols.keys():
                    if cols[i] == 'rank':
                        setattr(c, cols[i], int(row[i]))
                    else:
                        setattr(c, cols[i], row[i])
                self.append(c)
        return self

class Category(McdaObject):

    def __init__(self, id=None, name=None, disabled=False, rank=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.rank = rank

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "%s: %d" % (self.id, self.rank)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('category')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        if self.name is not None:
            root.set('name', self.name)

        active = ElementTree.SubElement(root, 'active')
        active.text = 'true' if self.disabled is False else 'false'

        rank = ElementTree.SubElement(root, 'rank')
        rank.append(marshal(self.rank))

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'category', id)

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

class Limits(McdaObject):

    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper  = upper

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "Limits(%s,%s)" % (self.lower, self.upper)

    def to_xmcda(self):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('limits')

        if self.lower:
            lower = ElementTree.SubElement(root, 'lowerCategory')
            catid = ElementTree.SubElement(lower, 'categoryID')
            catid.text = str(self.lower)

        if self.upper:
            upper = ElementTree.SubElement(root, 'upperCategory')
            catid = ElementTree.SubElement(upper, 'categoryID')
            catid.text = str(self.upper)

        return root

    def from_xmcda(self, xmcda):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'limits', None)

        lower = xmcda.find('.//lowerCategory/categoryID')
        self.lower = lower.text
        upper = xmcda.find('.//upperCategory/categoryID')
        self.upper = upper.text

        return self

class CategoriesProfiles(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "CategoriesProfiles(%s)" % self.values()

    def get_ordered_profiles(self):
        lower_cat = { cp.value.lower: cp.id for cp in self }
        upper_cat = { cp.value.upper: cp.id for cp in self }

        lowest_highest = set(lower_cat.keys()) ^ set(upper_cat.keys())
        lowest = list(set(lower_cat.keys()) & lowest_highest)

        profiles = [ lower_cat[lowest[0]] ]
        for i in range(1, len(self)):
            ucat = self[profiles[-1]].value.upper
            profiles.insert(i, lower_cat[ucat])

        return profiles

    def get_ordered_categories(self):
        profiles = self.get_ordered_profiles()
        categories = [ self[profiles[0]].value.lower ]
        for profile in profiles:
            categories.append(self[profile].value.upper)
        return categories

    def to_categories(self):
        cats = Categories()
        for i, cat in enumerate(reversed(self.get_ordered_categories())):
            cat = Category(cat, rank = i + 1)
            cats.append(cat)
        return cats

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('categoriesProfiles')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for cp in self:
            xmcda = cp.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'categoriesProfiles', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('categoryProfile')
        for tag in tag_list:
            catp = CategoryProfile().from_xmcda(tag)
            self.append(catp)

        return self

class CategoryProfile(McdaObject):

    def __init__(self, id = None, value = None):
        self.id = id
        self.value = value

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "%s: %s" % (self.id, self.value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('categoryProfile')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        altid = ElementTree.SubElement(root, 'alternativeID')
        altid.text = str(self.id)
        value = self.value.to_xmcda()
        root.append(value)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'categoryProfile', id)

        self.id = xmcda.find('.//alternativeID').text

        value = xmcda.find('.//limits')
        if value is not None:
            self.value = Limits().from_xmcda(value)

        return self

class AlternativesAssignments(McdaDict):

    def __call__(self, id):
        return self._d[id].category_id

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "AlternativesAssignments(%s)" % self.values()

    def __str__(self):
        l = 0
        for aa in self:
            l = max(len(aa.id), l)

        string = ""
        for aa in self:
            string += "%*s: %s\n" % (l, aa.id, aa.category_id)

        return string[:-1]

    def get_alternatives_in_category(self, category_id):
        l = []
        for aa in self:
            if aa.is_in_category(category_id):
                l.append(aa.id)

        return l

    def get_alternatives_in_categories(self, *category_ids):
        l = []
        for aa, cat in product(self, *category_ids):
            if aa.is_in_category(cat):
                l.append(aa.id)

        return l

    def to_alternatives(self):
        alternatives = Alternatives()
        for aa in self:
            alternatives.append(Alternative(aa.id))

        return alternatives

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
        print(line, file = out)

        # Print values
        for aid in alternative_ids:
            category_id = str(self[aid].category_id)
            line = str(aid) + " " * (cols_max["aids"] - len(str(aid)) + 1)
            line += " " * (cols_max["category"] - len(category_id)) \
                    + category_id
            print(line, file = out)

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('alternativesAffectations')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for aa in self:
            xmcda = aa.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternativesAffectations', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('alternativeAffectation')
        for tag in tag_list:
            aa = AlternativeAssignment()
            aa.from_xmcda(tag)
            self.append(aa)

        return self

    def from_csv(self, csvreader, alt_col, assign_col):
        """Read the MCDA dictionnary from CSV input"""

        col = None
        for row in csvreader:
            if row[0] == alt_col:
                col = row.index(assign_col)
            elif col and row[0] == '':
                break
            elif col is not None:
                aa = AlternativeAssignment(row[0])
                aa.category_id = row[col]
                self.append(aa)

        return self

class AlternativeAssignment(McdaObject):

    def __init__(self, id=None, category_id=None):
        self.id = id
        self.category_id = category_id

    def __repr__(self):
        """Manner to represent the MCDA object"""

        return "%s: %s" % (self.id, self.category_id)

    def __str__(self):
        return "%s: %s" % (self.id, self.category_id)

    def is_in_category(self, category_id):
        if self.category_id == category_id:
            return True

        return False

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('alternativeAffectation')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        altid = ElementTree.SubElement(root, 'alternativeID')
        altid.text = self.id
        catid = ElementTree.SubElement(root, 'categoryID')
        catid.text = self.category_id

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'alternativeAffectation', id)

        altid = xmcda.find('alternativeID')
        self.id = altid.text
        catid = xmcda.find('categoryID')
        self.category_id = catid.text

        return self

class Parameters(McdaDict):

    def __repr__(self):
        """Manner to represent the MCDA dictionnary"""

        return "Parameters(%s)" % self.values()

    def to_xmcda(self, id = None):
        """Convert the MCDA dictionnary into XMCDA output"""

        root = ElementTree.Element('methodParameters')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        for param in self:
            xmcda = param.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA dictionnary from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'methodParameters', id)

        self.id = xmcda.get('id')

        tag_list = xmcda.getiterator('parameter')
        for tag in tag_list:
            param = Parameter()
            param.from_xmcda(tag)
            self.append(param)

        return self

class Parameter(McdaObject):

    def __init__(self, id = None, value = None, name = None):
        self.id = id
        self.value = value
        self.name = name

    def __repr__(self):
        """Manner to represent the MCDA object"""
        return "%s: %s" % (self.id, self.value)

    def to_xmcda(self, id = None):
        """Convert the MCDA object into XMCDA output"""

        root = ElementTree.Element('parameter')

        if id is not None:
            root.set('id', id)
        elif self.id is not None:
            root.set('id', self.id)

        value = ElementTree.SubElement(root, 'value')
        value.append(marshal(self.value))

        return root

    def from_xmcda(self, xmcda, id = None):
        """Read the MCDA object from XMCDA input"""

        xmcda = find_xmcda_tag(xmcda, 'parameter', id)

        self.id = xmcda.get('id')
        self.name = xmcda.get('name')
        value = xmcda.find('value')
        if value is not None:
            self.value = unmarshal(value.getchildren()[0])

        return self
