#!/usr/bin/python
import sys
sys.path.append("..")
from pymcda.electre_tri import electre_tri
from pymcda.ui.graphic import display_electre_tri_models
from datasets import ticino
from datasets import loulouka

if __name__ == "__main__":
    etri = electre_tri(ticino.c, ticino.cv, ticino.ptb,
                       ticino.lbda, ticino.cps)
    etri2 = electre_tri(loulouka.c, loulouka.cv,
                        loulouka.ptb, loulouka.lbda,
                        loulouka.cps)

    worst_ticino = ticino.pt.get_worst(ticino.c)
    worst_loulouka = loulouka.pt.get_worst(loulouka.c)

    best_ticino = ticino.pt.get_best(ticino.c)
    best_loulouka = loulouka.pt.get_best(loulouka.c)

    display_electre_tri_models([etri, etri2],
                               [worst_ticino, worst_loulouka],
                               [best_ticino, best_loulouka])
