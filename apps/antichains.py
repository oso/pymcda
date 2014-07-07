from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from itertools import combinations, chain
from xml.etree import ElementTree
from test_utils import save_to_xmcda
import math
import bz2

# FIXME
class CriteriaSets(set):

    def __repr__(self):
        return "CriteriaSets(%s)" % ', '.join(map(str, self))

    def __hash__(self):
        return hash(frozenset(self))

    def to_xmcda(self):
        root = ElementTree.Element('criteriaSets')
        for cs in self:
            root.append(cs.to_xmcda())

        return root

class CriteriaSet(set):

    def __repr__(self):
        return "CriteriaSet(%s)" % ', '.join(map(str, self))

    def __hash__(self):
        return hash(frozenset(self))

    def to_xmcda(self):
        root = ElementTree.Element('criteriaSet')
        for c in self:
            el = ElementTree.SubElement(root, 'element')
            cid = ElementTree.SubElement(el, 'criterionID')
            cid.text = str(c)

        return root

def remove_supersets_and_smaller_sets(combis, combi):
    combis2 = []
    for combi2 in combis:
        if combi2.issuperset(combi):
            continue

        if len(combi2) < len(combi):
            continue

        combis2.append(combi2)

    return combis2

def __antichains(chain, combi, combis, antichains):
    antichains.add(chain)
    combis2 = remove_supersets_and_smaller_sets(combis, combi)
    for combi2 in combis2:
        _chain = chain | frozenset([combi2])
        antichains.add(_chain)
        __antichains(_chain, combi2, combis2, antichains)

    return antichains

def antichains(s):
    antichains = set([None, CriteriaSet([])])
    combis = [CriteriaSet(c) for i in range(1, len(s) + 1) \
                             for c in combinations(s, i)]
    for combi in combis:
        __antichains(CriteriaSets([combi]), combi, combis, antichains)

    return antichains

XMCDA_URL = 'http://www.decision-deck.org/2009/XMCDA-2.1.0'

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s n filename" % sys.argv[0])
        sys.exit(1)

    n = int(sys.argv[1])
    c = set(['c%d' % i for i in range(1, n + 1)])
    print(c)

    a = antichains(c)

    f = bz2.BZ2File("%s" % sys.argv[2], "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)

    i = 1
    for anti in a:
        print(anti)
        if anti is not None:
            xmcda.append(anti.to_xmcda())
            i += 1

    print(len(a))

    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()
