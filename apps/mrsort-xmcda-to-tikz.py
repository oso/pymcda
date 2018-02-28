#!/usr/bin/env python

from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from xml.etree import ElementTree
from itertools import product
import bz2

from pymcda.electre_tri import MRSort
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.learning.lp_mrsort_post_weights import LpMRSortPostWeights
from test_utils import is_bz2_file

tikzcmd = """
\\newcommand{\\tikzmrsort}[6] {

\\pgfplotstablegetcolsof{#1};
\\pgfmathsetmacro{\\ncriteria}{\\pgfplotsretval - 1};
\\pgfplotstablegetrowsof{#1};
\\pgfmathsetmacro{\\nprofiles}{\\pgfplotsretval - 1};

\\pgfplotstableforeachcolumn#1\\as\\col{
	\\pgfmathsetmacro{\\i}{\\pgfplotstablecol};

	\\pgfplotstablegetelem{0}{[index]\\i}\\of{#1};
	\\pgfmathsetmacro{\\vmax}{\\pgfplotsretval};

	\\pgfplotstablegetelem{\\nprofiles}{[index]\\i}\\of{#1};
	\\pgfmathsetmacro{\\vmin}{\\pgfplotsretval};

	\\draw[thick,->] (\\i*#6, #4 - 0.5) -- (\\i*#6, #5 + 0.5);

	\\if\\relax\\detokenize{#3}\\relax
		\\node[align=left, rotate=90, anchor=east]
			at (\\i*#6, #4 - 0.5) {\\col{}};
	\\else
		\\pgfplotstablegetelem{\\i}{[index]1}\\of{#3};
		\\pgfmathsetmacro{\\weight}{\\pgfplotsretval};
		\\pgfplotstablegetelem{1}{[index]\\i}\\of{#1};
		\\pgfmathsetmacro{\\bp}{\\pgfplotsretval};

		\\pgfmathparse{(\\weight > 0) || (\\bp > \\vmin) ? 1 : 0}
		\\ifthenelse{\\pgfmathresult > 0} {
			\\node[align=left, rotate=90, anchor=east]
				at (\\i*#6, #4 - 0.5) {\\col{}
				\\rotatebox[origin=c]{270}{($\\weight$)}};
		} {
			\\node[align=left, rotate=90, anchor=east]
				at (\\i*#6, #4 - 0.5) {\\sout{\\col{}}
				\\rotatebox[origin=c]{270}{($\\weight$)}};
		}
	\\fi

	\\pgfplotstablemodifyeachcolumnelement{\\col}\\of#1\\as\\cell{
		\\pgfmathsetmacro{\\j}{\\pgfplotstablerow};

		\\pgfmathsetmacro{\\yval}{#4 + (\\cell - \\vmin) /
					(\\vmax - \\vmin) * (#5 - #4)};

		\\coordinate (y_\\i\\j) at (\\i*#6, \\yval);
		\\fill[black] (y_\\i\\j) circle (1pt);

		\\ifthenelse{\\j < \\nprofiles \\AND \\j > 0} {
			\\pgfmathparse{((\\yval - #4 < 0.00001) ||
				       (#5 - \\yval) < 0.00001) ? 0 : 1};
			\\ifthenelse{\\pgfmathresult > 0} {
			\\node[right] at (y_\\i\\j) {\\scriptsize \\cell};
			}
		} {
			\\ifthenelse{\\j = 0} {
				\\node[above right] at (y_\\i\\j) {\\cell};
			} {
				\\node[below right] at (y_\\i\\j) {\\cell};
			}
		}
	}
}

\\begin{pgfonlayer}{background}
\\coordinate (c0) at (\\ncriteria * #6 + #6 + 5mm, #5);

\\foreach \\j [evaluate=\\j as \\p using int(\\j - 1)] in {1,...,\\nprofiles} {
	\\pgfmathsetmacro{\\tmp}{(20 + \\p * (100 / (\\nprofiles - 1)))};
	\\def\\colorz{gray!\\tmp}

	\\foreach \\i [evaluate=\\i as \\c using int(\\i - 1)] in {1, ...,\\ncriteria} {
		\\fill[color=\\colorz] (y_\\i\\j) -- (y_\\i\\p) -- (y_\\c\\p) -- (y_\\c\\j);
	}

	\\if\\not\\relax\\detokenize{#2}\\relax
		\\pgfplotstablegetelem{\\p}{[index]0}\\of{#2};
		\\node[anchor=right, below=1mm of c0, fill=\\colorz] (c0) {\\pgfplotsretval};
	\\fi
}

\\foreach \\j in {0,...,\\nprofiles} {
	\\foreach \\i [evaluate=\\i as \\c using int(\\i - 1)] in {1, ...,\\ncriteria} {
		\\draw[thin, dotted] (y_\\i\\j) -- (y_\\c\\j);
	}
}
\\end{pgfonlayer}

\\pgfplotstableforeachcolumn#3\\as\\col{
	\\pgfmathsetmacro{\\i}{\\pgfplotstablecol};
	\\ifthenelse{\\i = 1} {
		\\def\\lbdavalue{\\col{}};
	}
}

\\if\\not\\relax\\detokenize{#3}\\relax
	\\node[] at (\\ncriteria*#6 + #6 + 5mm, #4 - 8mm)
		{$\\lambda = \\lbdavalue$};
\\fi

}
"""

def usage(pname):
    print("usage: %s xmcdafile" % pname)

def tikz_header(tikzfile):
    print("\\begin{tikzpicture}", file = tikzfile)
    print("", file = tikzfile)
    print(tikzcmd, file = tikzfile)

def tikz_footer(tikzfile):
    print("\\tikzmrsort{\\profiles}{\\categories}{\\weights}{0}{5}{1.25cm}", file = tikzfile)
    print("", file = tikzfile)
    print("\\end{tikzpicture}", file = tikzfile)

def tikz_save_weights(tikzfile, model):
    print("\\pgfplotstableread{", file = tikzfile)
    print("{lambda} %s" % model.lbda, file = tikzfile)
    criteria = model.criteria.keys()
    for c in criteria:
        print("{%s} %s" % (c.replace("_", "-"), model.cv[c].value), file = tikzfile)
    print("}\\weights;", file = tikzfile)

def tikz_save_profiles(tikzfile, model, worst, best):
    print("\\pgfplotstableread{", file = tikzfile)
    criteria = model.criteria.keys()
    for c in criteria:
        print("{%s} " % c.replace("_", "-"), end = '', file = tikzfile)
    print('', file = tikzfile)

    for c in criteria:
        print("%s " % best.performances[c], end = '', file = tikzfile)
    print('', file = tikzfile)

    profiles = reversed(model.categories_profiles.get_ordered_profiles())
    for p in profiles:
        for c in criteria:
            print("%s " % model.bpt[p].performances[c], end = '', file = tikzfile)
        print('', file = tikzfile)

    for c in criteria:
        print("%s " % worst.performances[c], end = '', file = tikzfile)
    print('', file = tikzfile)

    print("}\\profiles;", file = tikzfile)

def tikz_save_categories(tikzfile, model):
    print("\\pgfplotstableread{", file = tikzfile)
    print("categories", file = tikzfile)
    for cat in reversed(model.categories):
        print("%s" % cat, file = tikzfile);
    print("}\\categories;", file = tikzfile)

def mrsort_xmcda_to_tikz(xmcdafile, updateweights = False):
    if is_bz2_file(xmcdafile) is True:
        xmcdafile = bz2.BZ2File(xmcdafile)

    tree = ElementTree.parse(xmcdafile)
    root = tree.getroot()

    xmcda_models =  root.findall(".//ElectreTri")
    m = MRSort().from_xmcda(xmcda_models[0])

    if updateweights is True:
        wsum = 10
        while wsum < 100000:
            try:
                lp = LpMRSortPostWeights(m.cv, m.lbda, wsum)
                obj, m.cv, m.lbda = lp.solve()
                break
            except:
                wsum = wsum * 10

    pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
    aworst = pt_learning.get_worst(m.criteria)
    abest = pt_learning.get_best(m.criteria)

    bname = os.path.basename(os.path.splitext(xmcdafile.name)[0])
    dname = os.path.dirname(xmcdafile.name)
    tikzfile = open("%s/%s-%s.tikz" % (dname, bname, m.id), "w+")

    tikz_header(tikzfile)
    print("", file = tikzfile)
    tikz_save_profiles(tikzfile, m, aworst, abest)
    print("", file = tikzfile)
    tikz_save_weights(tikzfile, m)
    print("", file = tikzfile)
    tikz_save_categories(tikzfile, m)
    print("", file = tikzfile)
    tikz_footer(tikzfile)

    tikzfile.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        usage(argv[0])
        sys.exit(1)

    updateweights = False
    if '--updateweights' in sys.argv:
        updateweights = True
        sys.argv.remove("--updateweights")

    for arg in sys.argv[1:]:
        mrsort_xmcda_to_tikz(arg, updateweights)
