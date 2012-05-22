#!/usr/bin/python
import sys
sys.path.append("..")
from mcda.electre_tri import electre_tri
from ui.graphic import display_electre_tri_models
import data_ticino
import data_loulouka

if __name__ == "__main__":
    etri = electre_tri(data_ticino.c, data_ticino.cv, data_ticino.ptb,
                       data_ticino.lbda, data_ticino.cps)
    etri2 = electre_tri(data_loulouka.c, data_loulouka.cv,
                        data_loulouka.ptb, data_loulouka.lbda,
                        data_loulouka.cps)

    display_electre_tri_models([etri, etri2],
                               [data_ticino.pt, data_loulouka.pt])
