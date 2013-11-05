from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import traceback
from optparse import OptionParser
from xml.etree import ElementTree
from pymcda.types import *
from pymcda.electre_tri import MRSort
from pymcda.generate import generate_categories_profiles
from pymcda.learning.mip_mrsort import MipMRSort

XMCDA_URL = 'http://www.decision-deck.org/2009/XMCDA-2.1.0'
ElementTree.register_namespace('xmcda', XMCDA_URL)

errormsg = list()

def log_error(msg):
    print(msg, file = sys.stderr)
    errormsg.append(msg)

def parse_cmdline():
    parser = OptionParser(usage = "python %s [options]" % sys.argv[0])
    parser.add_option("-i", "--in", action = "store", type="string",
                      dest = "indir",
                      help = "Input directory")
    parser.add_option("-o", "--out", action = "store", type="string",
                      dest = "outdir",
                      help = "Output directory")

    return parser.parse_args()

def parse_xmcda_file(filepath, tagname, mcda_type):
    if not os.path.isfile(filepath):
        log_error("No %s file" % filepath)
        return None

    try:
        mcda_object = mcda_type()
        tree = ElementTree.parse(filepath)
        root = tree.getroot()
        #ElementTree.dump(root)
        mcda_object.from_xmcda(root.find(tagname))
    except:
        log_error("Cannot parse %s" % filepath)
        log_error(traceback.format_exc())
        mcda_object = None

    return mcda_object

def parse_xmcda_file_lbda(filepath):
    if not os.path.isfile(filepath):
        log_error("No %s file" % filepath)
        return None

    try:
        tree = ElementTree.parse(filepath)
        root = tree.getroot()
        #ElementTree.dump(root)
        tag = root.find("methodParameters/parameter/value/real")
        value = float(tag.text)
    except:
        log_error("Cannot parse %s" % filepath)
        log_error(traceback.format_exc())
        mcda_object = None

    return value

def parse_input_files(indir):
    criteria = parse_xmcda_file(indir + '/criteria.xml',
                                "criteria", Criteria)
    alternatives = parse_xmcda_file(indir + '/alternatives.xml',
                                    "alternatives", Alternatives)
    categories = parse_xmcda_file(indir + '/categories.xml',
                                  "categories", Categories)
    pt = parse_xmcda_file(indir + '/perfs_table.xml',
                          "performanceTable", PerformanceTable)
    assignments = parse_xmcda_file(indir + '/assign.xml',
                                   "alternativesAffectations",
                                   AlternativesAssignments)

    # Partial inference
    categories_profiles = parse_xmcda_file(indir + '/cat_profiles.xml',
                                           "categoriesProfiles",
                                           CategoriesProfiles)
    bpt = parse_xmcda_file(indir + '/reference_alts.xml',
                           "performanceTable", PerformanceTable)
    criteria_values = parse_xmcda_file(indir + '/crit_weights.xml',
                                       "criteriaValues",
                                       CriteriaValues)
    if criteria_values:
        criteria_values.normalize()

    lbda = parse_xmcda_file_lbda(indir + '/lambda.xml')

    if categories_profiles is None:
        categories_profiles = generate_categories_profiles(categories)

    if categories and criteria and pt:
        model = MRSort(criteria, criteria_values, bpt, lbda,
                       categories_profiles)
    else:
        model = None

    return model, assignments, pt

def lambda_to_xmcda(lbda):
    root = ElementTree.Element('methodParameters')
    xmcda = ElementTree.SubElement(root, 'parameter')
    xmcda.set('name', 'lambda')
    xmcda = ElementTree.SubElement(xmcda, 'value')
    xmcda = ElementTree.SubElement(xmcda, 'real')
    xmcda.text = str(lbda)
    return root

def get_compat_alternatives(aa, aa2):
    return [a.id for a in aa if a.category_id == aa2[a.id].category_id]
    l = []
    for a in aa:
        if a.category_id == aa2[a.id].category_id:
            l.append(a.id)
    return l


def to_alternatives(ids):
    return Alternatives([Alternative(id) for id in ids])

def write_xmcda_file(filepath, mcda_object):
    f = open(filepath, "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)
    xmcda.append(mcda_object)
    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def write_message_error(filepath):
    f = open(filepath, "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)
    msg = ElementTree.SubElement(xmcda, 'methodMessages')
    msg = ElementTree.SubElement(msg, 'errorMessage')
    msg = ElementTree.SubElement(msg, 'text')
    msg.text = "<![CDATA[" + str(errormsg) + "]]>"
    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def write_message_ok(filepath):
    f = open(filepath, "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)
    msg = ElementTree.SubElement(xmcda, 'methodMessages')
    msg = ElementTree.SubElement(msg, 'logMessage')
    msg = ElementTree.SubElement(msg, 'text')
    msg.text = "<![CDATA[Execution ok]]>"
    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def main(indir, outdir):
    if indir is None or not os.path.isdir(indir):
        log_error("Invalid input directory (%s)" % indir)
        return 1

    if outdir is None or not os.path.isdir(outdir):
        log_error("Invalid output directory (%s)" % outdir)
        return 1

    model, assignments, pt = parse_input_files(indir)
    if model is None or assignments is None or pt is None:
        log_error("Error while parsing input files")
        write_message_error(outdir + '/messages.xml')
        return 1

    try:
        mip = MipMRSort(model, pt, assignments)
        mip.solve()

        assignments2 = model.get_assignments(pt)
        compat = get_compat_alternatives(assignments, assignments2)
        compat = to_alternatives(compat)

        profiles = to_alternatives(model.categories_profiles.keys())
        xmcda_lbda = lambda_to_xmcda(model.lbda)

        write_xmcda_file(outdir + '/lambda.xml', xmcda_lbda)
        write_xmcda_file(outdir + '/cat_profiles.xml',
                         model.categories_profiles.to_xmcda())
        write_xmcda_file(outdir + '/crit_weights.xml',
                         model.cv.to_xmcda())
        write_xmcda_file(outdir + '/reference_alts.xml',
                         profiles.to_xmcda())
        write_xmcda_file(outdir + '/compatible_alts.xml',
                         compat.to_xmcda())

        write_message_ok(outdir + '/messages.xml')
    except:
        log_error("Cannot solve problem")
        log_error(traceback.format_exc())
        write_message_error(outdir + '/messages.xml')

    return 0

if __name__ == "__main__":
    (options, args) = parse_cmdline()
    indir = options.indir
    outdir = options.outdir

    rc = main(indir, outdir)
    sys.exit(rc)
