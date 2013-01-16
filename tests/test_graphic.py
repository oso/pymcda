#!/usr/bin/python
import sys
sys.path.append("..")
from mcda.electre_tri import electre_tri
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances
from ui.graphic import display_electre_tri_models
from datasets import ticino
from datasets import loulouka

if __name__ == "__main__":
    etri = electre_tri(ticino.c, ticino.cv, ticino.ptb,
                       ticino.lbda, ticino.cps)
    etri2 = electre_tri(loulouka.c, loulouka.cv,
                        loulouka.ptb, loulouka.lbda,
                        loulouka.cps)

    worst_ticino = get_worst_alternative_performances(ticino.pt,
                                                      ticino.c)
    worst_loulouka = get_worst_alternative_performances(loulouka.pt,
                                                        loulouka.c)

    best_ticino = get_best_alternative_performances(ticino.pt,
                                                    ticino.c)
    best_loulouka = get_best_alternative_performances(loulouka.pt,
                                                      loulouka.c)

    display_electre_tri_models([etri, etri2],
                               [worst_ticino, worst_loulouka],
                               [best_ticino, best_loulouka])
