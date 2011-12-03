from xml.etree import ElementTree

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

class criteria(list):

    def __call__(self, criterion_id):
        for crit in self:
            if crit.id == criterion_id:
                return crit

        raise KeyError, "Criterion %s not found" % criterion_id

    def has_criterion(self, criterion_id):
        for crit in self:
            if crit.id == criterion_id:
                return True

        return False

    def to_xmcda(self):
        root = ElementTree.Element('criteria')
        for crit in self:
            crit_xmcda = crit.to_xmcda()
            root.append(crit_xmcda)
        return root

    def from_xmcda(self, xmcda, xmcda_critval=None):
        tag_list = xmcda.getiterator('criterion')
        for tag in tag_list:
            c = criterion(None)
            c.from_xmcda(tag)
            self.append(c)

        if xmcda_critval is not None:
            tag_list = xmcda_critval.getiterator('criterionValue')
            for tag in tag_list:
                c_id = tag.find('criterionID')
                if c_id is not None:
                    c_id = c_id.text

                if self.has_criterion(c_id):
                    c = self(c_id)
                    c.from_xmcda(xmcda_critval=tag)

class criterion:

    DISABLED = 1
    ENABLED = 0

    def __init__(self, id, name=None, disabled=False, direction=1,
                 weight=None, thresholds=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.direction = direction
        self.weight = weight
        self.thresholds = thresholds

    def __repr__(self):
        if self.name is not None:
            return "%s (%s)" % (self.id, self.name)
        else:
            return "%s" % self.id

    def to_xmcda(self):
        xmcda = ElementTree.Element('criterion', id=self.id)
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

    def from_xmcda(self, xmcda=None, xmcda_critval=None):
        if xmcda is not None:
            if xmcda.tag == 'criterion':
                crit = xmcda
            else:
                crit = xmcda.find('.//criterion')
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
                    raise TypeError, 'criterion::invalid preferenceDirection'
            value = crit.find('.//criterionValue/value')
            if value is not None:
                self.weight = unmarshal(value.getchildren()[0])

        if xmcda_critval is not None:
            if xmcda_critval.tag == 'criterionValue':
                critval = xmcda_critval
            else:
                critval = xmcda_critval.find('.//criterionValue')
            value = critval.find('.//value')
            if value is not None:
                self.weight = unmarshal(value.getchildren()[0])

class alternatives(list):

    def to_xmcda(self):
        root = ElementTree.Element('alternatives')
        root2 = ElementTree.Element('performanceTable')
        for action in self:
            alt, perf = action.to_xmcda()
            root.append(alt)
            root2.append(perf)
        return (root, root2)

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'alternatives':
            alternatives = xmcda
        else:
            alternatives = xmcda.find('.//alternatives')

        tag_list = alternatives.getiterator('alternative')
        for tag in tag_list:
            alt = alternative(None)
            alt.from_xmcda(tag)
            self.append(alt)

class alternative:

    def __init__(self, id=None, name=None, performances=None, disabled=False):
        self.id = id
        self.name = name
        self.performances = performances
        self.disabled = disabled

    def __repr__(self):
        if self.name is not None:
            return "%s (%s)" % (self.id, self.name)
        else:
            return "%s" % self.id

    def __add__(self, other):
        a = self.performances
        b = other.performances
        return dict( (n, a.get(n, 0)+b.get(n, 0)) for n in set(a)|set(b) )

    def __sub__(self, other):
        a = self.performances
        b = other.performances
        return dict( (n, a.get(n, 0)-b.get(n, 0)) for n in set(a)|set(b) )

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternative', id=self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        active = ElementTree.SubElement(xmcda, 'active')
        if self.disabled is False:
            active.text = 'true'
        else:
            active.text = 'false'

        if self.performances:
            xmcda2 = ElementTree.Element('alternativePerformances')
            altid = ElementTree.SubElement(xmcda2, 'alternativeID')
            altid.text = self.id

            for crit, val in self.performances.iteritems():
                perf = ElementTree.SubElement(xmcda2, 'performance')

                critid = ElementTree.SubElement(perf, 'criterionID')
                critid.text = crit.id

                value = ElementTree.SubElement(perf, 'value')
                p = marshal(val)
                value.append(p)
        else:
            xmcda2 = None

        return (xmcda, xmcda2)

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'alternative':
            alternative = xmcda
        else:
            alternative = xmcda.find('.//alternative')

        self.id = alternative.get('id')
        name = alternative.get('name')
        if name:
            self.name = name

        active = alternative.find('active')
        if active is not None and active.text == 'false':
            self.disabled = True
        else:
            self.disabled = False

class performance_table(list):

    def __call__(self, alternative_id, criterion_id=None):
        alt_perfs = None
        for altp in self:
            if altp.alternative_id == alternative_id:
                alt_perfs = altp
                break

        # FIXME: to remove
        if alt_perfs is None:
            raise KeyError, "Alternative %s not found" % alternative_id

        if criterion_id is None:
            return alt_perfs
        else:
            return alt_perfs(criterion_id)

    def has_alternative(self, alternative):
        for altp in self:
            if altp.alternative_id == alternative.id:
                return True

        return False

    def to_xmcda(self):
        root = ElementTree.Element('performanceTable')
        for alt_perfs in self:
            xmcda = alt_perfs.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'performanceTable':
            pt = xmcda
        else:
            pt = xmcda.find('.//performanceTable')

        tag_list = pt.getiterator('alternativePerformances')
        for tag in tag_list:
            altp = alternative_performances(0, {})
            altp.from_xmcda(tag)
            self.append(altp)

class alternative_performances():

    def __init__(self, alternative_id, performances):
        self.alternative_id = alternative_id
        self.performances = performances

    def __call__(self, criterion_id):
        return self.performances[criterion_id]

    def __repr__(self):
        return "%s: %s" % (self.alternative_id, self.performances)

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
        if xmcda.tag == 'alternativePerformances':
            altp = xmcda
        else:
            altp = xmcda.find('.//alternativePerformances')

        altid = altp.find('.//alternativeID')
        self.alternative_id = altid.text

        tag_list = altp.getiterator('performance')
        for tag in tag_list:
            crit_id = tag.find('.//criterionID').text
            value = tag.find('.//value')
            crit_val = unmarshal(value.getchildren()[0])
            self.performances[crit_id] = crit_val

class points(list):

    def __call__(self, id):
        p = None
        for point in self:
            if point.id == id:
                p = point

        return p

    def to_xmcda(self):
        root = ElementTree.Element('points')
        for p in self:
            xmcda = p.to_xmcda()
            root.append(xmcda)
        return root

class point():

    def __init__(self, id, abscissa, ordinate):
        self.id = id
        self.abscissa = abscissa
        self.ordinate = ordinate

    def to_xmcda(self):
        xmcda = ElementTree.Element('point')
        abscissa = ElementTree.SubElement('abscissa')
        abscissa.append(marshal(self.abscissa))
        ordinate = ElementTree.SubElement('ordinate')
        ordinate.append(marshal(self.ordinate))
        return xmcda

class constant():

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def to_xmcda(self):
        xmcda = ElementTree.Element('constant')
        if self.id is not None:
            xmcda.set('id', self.id)
        value = marshal(self.value)
        xmcda.append(value)
        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'constant':
            constant = xmcda
        else:
            constant = xmcda.find('.//constant')
        self.id = constant.get('id')
        self.value = unmarshal(constant.getchildren()[0])

class thresholds(list):

    def __call__(self, id):
        threshold = None
        for t in self:
            if t.id == id:
                threshold = t

        if threshold is None:
            raise KeyError, "Threshold %s not found" % id

        return threshold

    def has_threshold(self, threshold_id):
        for t in self:
            if t.id == threshold_id:
                return True

        return False

    def to_xmcda(self):
        root = ElementTree.Element('thresholds')
        for t in self:
            xmcda = t.to_xmcda()
            root.append(xmcda)
        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'thresholds':
            thresholds = xmcda
        else:
            thresholds = xmcda.find('.//thresholds')

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

    def to_xmcda(self):
        xmcda = ElementTree.Element('threshold', id=self.id)
        if self.name is not None:
            xmcda.set('name', self.name)

        values = self.values.to_xmcda()
        xmcda.append(values)

        return xmcda

    def from_xmcda(self, xmcda):
        if xmcda.tag == 'threshold':
            threshold = xmcda
        else:
            threshold = xmcda.find('.//threshold')
        self.id = threshold.get('id')
        self.name = threshold.get('name')
        values = threshold.getchildren()[0]
        if values.tag == 'constant':
            c = constant(None, 0)
            c.from_xmcda(values)

class categories(list):

    def to_xmcda(self):
        root = ElementTree.Element('categories')
        for c in self:
            xmcda = c.to_xmcda()
            root.append(xmcda)
        return root

class category():

    def __init__(self, id, name=None, disabled=False, rank=None):
        self.id = id
        self.name = name
        self.disabled = disabled
        self.rank = rank

    def to_xmcda(self):
        xmcda = ElementTree.Element('threshold', self.id)
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

class limits():

    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper  = upper

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

class categories_profiles(list):

    def to_xmcda(self):
        root = ElementTree.Element('categoriesProfiles')
        for cp in self:
            xmcda = cp.to_xmcda()
            root.append(xmcda)
        return root

class category_profile():

    def __init__(self, alternative_id, value):
        self.alternative_id = alternative_id
        self.value = value

    def to_xmcda(self):
        xmcda = ElementTree.Element('categoryProfile')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.alternative_id
        value = self.value.to_xmcda()
        xmcda.append(value)
        return xmcda

class alternatives_affectations(list):

    def __call__(self, id):
        for a in self:
            if a.alternative_id == id:
                return a.category_id
        return None

    def to_xmcda(self):
        root = ElementTree.Element('alternativesAffectations')
        for aa in self:
            xmcda = aa.to_xmcda()
            root.append(xmcda)
        return root

class alternative_affectation():

    def __init__(self, alternative_id, category_id):
        self.alternative_id = alternative_id
        self.category_id = category_id

    def __repr__(self):
        return "%s: %s" % (self.alternative_id, self.category_id)

    def to_xmcda(self):
        xmcda = ElementTree.Element('alternativeAffectation')
        altid = ElementTree.SubElement(xmcda, 'alternativeID')
        altid.text = self.alternative_id
        catid = ElementTree.SubElement(xmcda, 'categoryID')
        catid.text = self.category_id
        return xmcda

class threshold_old(alternative):
    pass

class profile(alternative):

    def __init__(self, id=None, name=None, performances=None,
                 indifference=None, preference=None, veto=None):
        alternative.__init__(self, id, name, performances)
        self.indifference = indifference
        self.preference = preference
        self.veto = veto
