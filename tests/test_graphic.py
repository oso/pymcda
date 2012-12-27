#!/usr/bin/python
import sys
sys.path.append("..")
from mcda.electre_tri import electre_tri
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances
from ui.graphic import display_electre_tri_models
import data_ticino
import data_loulouka

if __name__ == "__main__":
    etri = electre_tri(data_ticino.c, data_ticino.cv, data_ticino.ptb,
                       data_ticino.lbda, data_ticino.cps)
    etri2 = electre_tri(data_loulouka.c, data_loulouka.cv,
                        data_loulouka.ptb, data_loulouka.lbda,
                        data_loulouka.cps)

    worst_ticino = get_worst_alternative_performances(data_ticino.pt,
                                                      data_ticino.c)
    worst_loulouka = get_worst_alternative_performances(data_loulouka.pt,
                                                        data_loulouka.c)

    best_ticino = get_best_alternative_performances(data_ticino.pt,
                                                    data_ticino.c)
    best_loulouka = get_best_alternative_performances(data_loulouka.pt,
                                                      data_loulouka.c)

    display_electre_tri_models([etri, etri2],
                               [worst_ticino, worst_loulouka],
                               [best_ticino, best_loulouka])
