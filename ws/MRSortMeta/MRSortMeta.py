from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")
import traceback
from optparse import OptionParser
from xml.etree import ElementTree
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.types import *
from pymcda.electre_tri import MRSort
from pymcda.generate import generate_categories_profiles
from pymcda.learning.meta_mrsort3 import MetaMRSortPop3

SOLVERS_LIST = [ 'cplex', 'glpk' ]
DEFAULT_SOLVER = 'glpk'

XMCDA_URL = 'http://www.decision-deck.org/2009/XMCDA-2.1.0'
ElementTree.register_namespace('xmcda', XMCDA_URL)

errormsg = list()

def CDATA(text = None):
    element = ElementTree.Element('![CDATA[')
    element.text = text
    return element

ElementTree._original_serialize_xml = ElementTree._serialize_xml
def _serialize_xml(write, elem, encoding, qnames, namespaces):
    if elem.tag == '![CDATA[':
        text = elem.text.encode(encoding)
        write("<%s%s]]>" % (elem.tag, elem.text))
        return
    return ElementTree._original_serialize_xml(write, elem, encoding, qnames,
                                      namespaces)
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml

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

def parse_xmcda_file_elem(filepath, elem):
    if not os.path.isfile(filepath):
        log_error("No %s file" % filepath)
        return None

    try:
        tree = ElementTree.parse(filepath)
        root = tree.getroot()
        #ElementTree.dump(root)
        tag = root.find("methodParameters/parameter/value/%s" % elem)
        value = tag.text
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
    meta_params = parse_xmcda_file(indir + '/params.xml',
                                   "methodParameters",
                                   Parameters)
    categories_profiles = generate_categories_profiles(categories)

    if categories and criteria and pt:
        model = MRSort(criteria, None, None, None, categories_profiles)
    else:
        model = None

    # Get solver (optional)
    solver = parse_xmcda_file_elem(indir + '/solver.xml', 'label')
    if solver is None:
        solver = DEFAULT_SOLVER

    return solver, model, assignments, pt, meta_params

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
    cdata = CDATA(str(errormsg))
    msg.append(cdata)
    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def write_message_ok(filepath):
    f = open(filepath, "w")
    xmcda = ElementTree.Element("{%s}XMCDA" % XMCDA_URL)
    msg = ElementTree.SubElement(xmcda, 'methodMessages')
    msg = ElementTree.SubElement(msg, 'logMessage')
    msg = ElementTree.SubElement(msg, 'text')
    cdata = CDATA("Execution ok")
    msg.append(cdata)
    buf = ElementTree.tostring(xmcda, encoding="UTF-8", method="xml")
    f.write(buf)
    f.close()

def mrsort_meta_inference(indir, outdir):
    if indir is None or not os.path.isdir(indir):
        log_error("Invalid input directory (%s)" % indir)
        return 1

    if outdir is None or not os.path.isdir(outdir):
        log_error("Invalid output directory (%s)" % outdir)
        return 1

    solver, model, assignments, pt, params = parse_input_files(indir)

    if solver not in SOLVERS_LIST:
        log_error("Invalid solver selected (%s)" % solver)
        write_message_error(outdir + '/messages.xml')
        return 1

    os.environ["SOLVER"] = solver

    if model is None or assignments is None or pt is None or params is None:
        log_error("Error while parsing input files")
        write_message_error(outdir + '/messages.xml')
        return 1

    if 'nmodels' in params:
        nmodels = params['nmodels'].value
    else:
        log_error("Invalid number of models (nmodels)")
        write_message_error(outdir + '/messages.xml')
        return 1

    if 'niter_meta' in params:
        niter_meta = params['niter_meta'].value
    else:
        log_error("Invalid number of iterations (niter_meta)")
        write_message_error(outdir + '/messages.xml')
        return 1

    if 'niter_heur' in params:
        niter_heur = params['niter_heur'].value
    else:
        log_error("Invalid number of iterations (niter_heur)")
        write_message_error(outdir + '/messages.xml')
        return 1

    try:
        pt_sorted = SortedPerformanceTable(pt)
        meta = MetaMRSortPop3(nmodels, model.criteria,
                              model.categories_profiles.to_categories(),
                              pt_sorted, assignments)
        for i in range(niter_meta):
            model, ca = meta.optimize(niter_heur)

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
                         model.bpt.to_xmcda())
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

    rc = mrsort_meta_inference(indir, outdir)
    sys.exit(rc)
