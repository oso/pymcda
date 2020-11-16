from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from pymcda.types import Criterion
from pymcda.types import Criteria
from pymcda.types import AlternativePerformances
from pymcda.types import PerformanceTable
from pymcda.types import PairwiseRelation
from pymcda.types import PairwiseRelations
from pymcda.rmp import RMP
from pymcda.learning.sat_rmp import SatRMP

c1 = Criterion("pp")
c2 = Criterion("tp")
c3 = Criterion("vi")
c4 = Criterion("lc")
c5 = Criterion("nf")
c6 = Criterion("it")
c7 = Criterion("oc")
c = Criteria([c1, c2, c3, c4, c5, c6, c7])

a1 = AlternativePerformances('Air_A', {'pp': 1461, 'tp': 1484, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 11050, 'oc': 3768.3})
a2 = AlternativePerformances('Air_B', {'pp': 3170, 'tp': 1757, 'vi': 3, 'lc': 2, 'nf': 1, 'it': 10450, 'oc': 3561.8})
a3 = AlternativePerformances('Bri_A', {'pp': 1356, 'tp': 974, 'vi': 4, 'lc': 2, 'nf': 2, 'it': 6750, 'oc': 2186.5})
a4 = AlternativePerformances('Bur_A', {'pp': 867, 'tp': 341, 'vi': 3, 'lc': 1, 'nf': 2, 'it': 8000, 'oc': 2864.3})
a5 = AlternativePerformances('Bur_B', {'pp': 623, 'tp': 225, 'vi': 3, 'lc': 1, 'nf': 1, 'it': 6500, 'oc': 2050.9})
a6 = AlternativePerformances('Caf_A', {'pp': 1356, 'tp': 693, 'vi': 3, 'lc': 3, 'nf': 4, 'it': 15150, 'oc': 5179.6})
a7 = AlternativePerformances('Cav_A', {'pp': 384, 'tp': 69, 'vi': 4, 'lc': 3, 'nf': 0, 'it': 16650, 'oc': 5695.9})
a8 = AlternativePerformances('Crc_A', {'pp': 345, 'tp': 15, 'vi': 3, 'lc': 1, 'nf': 0, 'it': 9200, 'oc': 3131.4})
a9 = AlternativePerformances('Cum_A', {'pp': 1859, 'tp': 684, 'vi': 2, 'lc': 4, 'nf': 2, 'it': 7850, 'oc': 2782.9})
a10 = AlternativePerformances('Cum_B', {'pp': 313, 'tp': 148, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 11450, 'oc': 3905.9})
a11 = AlternativePerformances('Frs_A', {'pp': 140, 'tp': 507, 'vi': 3, 'lc': 4, 'nf': 0, 'it': 8400, 'oc': 2856.1})
a12 = AlternativePerformances('Frs_B', {'pp': 192, 'tp': 563, 'vi': 3, 'lc': 3, 'nf': 0, 'it': 8000, 'oc': 2810.1})
a13 = AlternativePerformances('Mac_A', {'pp': 1062, 'tp': 438, 'vi': 4, 'lc': 3, 'nf': 2, 'it': 8200, 'oc': 2918.5})
a14 = AlternativePerformances('Non_A', {'pp': 337, 'tp': 182, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 20550, 'oc': 7038.5})
a15 = AlternativePerformances('Osa_A', {'pp': 981, 'tp': 569, 'vi': 4, 'lc': 2, 'nf': 5, 'it': 7450, 'oc': 2566.1})
a16 = AlternativePerformances('Pin_A', {'pp': 643, 'tp': 90, 'vi': 4, 'lc': 2, 'nf': 1, 'it': 4150, 'oc': 4800.3})
a17 = AlternativePerformances('Pin_B', {'pp': 1472, 'tp': 777, 'vi': 4, 'lc': 2, 'nf': 2, 'it': 6600, 'oc': 2105.2})
a18 = AlternativePerformances('Pis_A', {'pp': 1398, 'tp': 1242, 'vi': 3, 'lc': 2, 'nf': 2, 'it': 8750, 'oc': 2976.5})
a19 = AlternativePerformances('Ssp_A', {'pp': 3969, 'tp': 1397, 'vi': 4, 'lc': 2, 'nf': 2, 'it': 5694, 'oc': 1613.9})
a20 = AlternativePerformances('Vig_A', {'pp': 248, 'tp': 20, 'vi': 4, 'lc': 2, 'nf': 1, 'it': 15000, 'oc': 5127.9})
a21 = AlternativePerformances('Vil_A', {'pp': 433, 'tp': 25, 'vi': 4, 'lc': 2, 'nf': 0, 'it': 19200, 'oc': 6573.7})
a22 = AlternativePerformances('Vol_A', {'pp': 1139, 'tp': 445, 'vi': 3, 'lc': 2, 'nf': 2, 'it': 18650, 'oc': 6384.4})
a23 = AlternativePerformances('Air_2', {'pp': 2759, 'tp': 2072, 'vi': 3, 'lc': 2, 'nf': 2, 'it': 10450, 'oc': 3681.7})
a24 = AlternativePerformances('Air_3', {'pp': 1974, 'tp': 1561, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 10950, 'oc': 3389.6})
a25 = AlternativePerformances('Air_4', {'pp': 1699, 'tp': 1527, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 10950, 'oc': 3389.6})
a26 = AlternativePerformances('Non_1', {'pp': 242, 'tp': 369, 'vi': 3, 'lc': 3, 'nf': 0, 'it': 21570, 'oc': 7389.5})
a27 = AlternativePerformances('Fros_1', {'pp': 792, 'tp': 1128, 'vi': 3, 'lc': 2, 'nf': 1, 'it': 5250, 'oc': 1373.2})
a28 = AlternativePerformances('Fros_2', {'pp': 918, 'tp': 1530, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 5250, 'oc': 1373.2})
a29 = AlternativePerformances('Pin_1', {'pp': 494, 'tp': 279, 'vi': 3, 'lc': 1, 'nf': 2, 'it': 4700, 'oc': 1074.9})
a30 = AlternativePerformances('Pin_2', {'pp': 525, 'tp': 125, 'vi': 3, 'lc': 1, 'nf': 2, 'it': 4350, 'oc': 885.2})
a31 = AlternativePerformances('Pin_3', {'pp': 485, 'tp': 119, 'vi': 3, 'lc': 1, 'nf': 2, 'it': 5050, 'oc': 1264.7})
a32 = AlternativePerformances('Pin_4', {'pp': 1043, 'tp': 455, 'vi': 2, 'lc': 2, 'nf': 3, 'it': 4950, 'oc': 1454.5})
a33 = AlternativePerformances('Pin_5', {'pp': 445, 'tp': 96, 'vi': 2, 'lc': 2, 'nf': 3, 'it': 4950, 'oc': 1454.5})
a34 = AlternativePerformances('Rol_1', {'pp': 1021, 'tp': 1486, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 5400, 'oc': 1454.5})
a35 = AlternativePerformances('Sca_1', {'pp': 491, 'tp': 53, 'vi': 3, 'lc': 2, 'nf': 3, 'it': 9850, 'oc': 3355.2})
a36 = AlternativePerformances('Sca_2', {'pp': 454, 'tp': 42, 'vi': 3, 'lc': 2, 'nf': 3, 'it': 9850, 'oc': 3355.2})
a37 = AlternativePerformances('Sca_3', {'pp': 535, 'tp': 89, 'vi': 3, 'lc': 2, 'nf': 3, 'it': 9850, 'oc': 3355.2})
a38 = AlternativePerformances('Sca_4', {'pp': 310, 'tp': 15, 'vi': 3, 'lc': 1, 'nf': 0, 'it': 9200, 'oc': 3131.5})
a39 = AlternativePerformances('Vol_2', {'pp': 550, 'tp': 464, 'vi': 3, 'lc': 2, 'nf': 0, 'it': 17350, 'oc': 5936.9})

pt = PerformanceTable([eval("a%d" % i) for i in range(1, 40)])
print(pt)

pwc1 = PairwiseRelation("Pin_2", "Fros_2", PairwiseRelation.PREFERRED)
pwc2 = PairwiseRelation("Fros_2", "Pin_1", PairwiseRelation.PREFERRED)
pwc3 = PairwiseRelation("Pin_1", "Pin_3", PairwiseRelation.PREFERRED)
pwc4 = PairwiseRelation("Pin_3", "Pin_5", PairwiseRelation.PREFERRED)
pwc5 = PairwiseRelation("Pin_5", "Rol_1", PairwiseRelation.PREFERRED)
pwc6 = PairwiseRelation("Rol_1", "Sca_4", PairwiseRelation.PREFERRED)
pwc7 = PairwiseRelation("Sca_4", "Crc_A", PairwiseRelation.PREFERRED)
pwc8 = PairwiseRelation("Crc_A", "Bur_A", PairwiseRelation.PREFERRED)
pwc9 = PairwiseRelation("Bur_A", "Frs_A", PairwiseRelation.PREFERRED)
pwc10 = PairwiseRelation("Frs_A", "Pin_A", PairwiseRelation.PREFERRED)
pwc11 = PairwiseRelation("Pin_A", "Bur_B", PairwiseRelation.PREFERRED)
pwc12 = PairwiseRelation("Bur_B", "Cum_B", PairwiseRelation.PREFERRED)
pwc13 = PairwiseRelation("Cum_B", "Air_A", PairwiseRelation.PREFERRED)
pwc14 = PairwiseRelation("Air_A", "Pin_4", PairwiseRelation.PREFERRED)
pwc15 = PairwiseRelation("Pin_4", "Cum_A", PairwiseRelation.PREFERRED)
pwc16 = PairwiseRelation("Cum_A", "Fros_1", PairwiseRelation.PREFERRED)
pwc17 = PairwiseRelation("Fros_1", "Frs_B", PairwiseRelation.PREFERRED)
pwc18 = PairwiseRelation("Frs_B", "Sca_2", PairwiseRelation.PREFERRED)
pwc19 = PairwiseRelation("Sca_2", "Pis_A", PairwiseRelation.PREFERRED)
pwc20 = PairwiseRelation("Pis_A", "Air_4", PairwiseRelation.PREFERRED)
pwc21 = PairwiseRelation("Air_4", "Non_A", PairwiseRelation.PREFERRED)
pwc22 = PairwiseRelation("Non_A", "Sca_1", PairwiseRelation.PREFERRED)
pwc23 = PairwiseRelation("Sca_1", "Sca_3", PairwiseRelation.PREFERRED)
pwc24 = PairwiseRelation("Sca_3", "Vol_2", PairwiseRelation.PREFERRED)
pwc25 = PairwiseRelation("Vol_2", "Air_3", PairwiseRelation.PREFERRED)
pwc26 = PairwiseRelation("Air_3", "Non_1", PairwiseRelation.PREFERRED)
pwc27 = PairwiseRelation("Non_1", "Cav_A", PairwiseRelation.PREFERRED)
pwc28 = PairwiseRelation("Cav_A", "Mac_A", PairwiseRelation.PREFERRED)
pwc29 = PairwiseRelation("Mac_A", "Air_2", PairwiseRelation.PREFERRED)
pwc30 = PairwiseRelation("Air_2", "Air_B", PairwiseRelation.PREFERRED)
pwc31 = PairwiseRelation("Air_B", "Caf_A", PairwiseRelation.PREFERRED)
pwc32 = PairwiseRelation("Caf_A", "Bri_A", PairwiseRelation.PREFERRED)
pwc33 = PairwiseRelation("Bri_A", "Pin_B", PairwiseRelation.PREFERRED)
pwc34 = PairwiseRelation("Pin_B", "Ssp_A", PairwiseRelation.PREFERRED)
pwc35 = PairwiseRelation("Ssp_A", "Osa_A",  PairwiseRelation.PREFERRED)
pwc36 = PairwiseRelation("Osa_A", "Vig_A", PairwiseRelation.PREFERRED)
pwc37 = PairwiseRelation("Vig_A", "Vol_A", PairwiseRelation.PREFERRED)
pwc38 = PairwiseRelation("Vol_A", "Vil_A", PairwiseRelation.PREFERRED)
pwcs = PairwiseRelations([eval("pwc%d" % i) for i in range(1, 39)])
print(pwcs)

nprofiles = 3
b = [ "b%d" % i for i in range(1, nprofiles + 1)]
model = RMP(c, None, b, None)

satrmp = SatRMP(model, pt, pwcs)
solution = satrmp.solve()

if solution is False:
    print("Warning: solution is UNSAT")
    solution = satrmp.solve(True)
    if solution is False:
        print("Warning: no MaxSAT solution")
        sys.exit(1)

pwcs2 = PairwiseRelations()
for pwc in pwcs:
    pwc2 = model.compare(pt[pwc.a], pt[pwc.b])

    if pwc != pwc2:
        print("%s != %s" % (pwc, pwc2))
        print(pt[pwc.a])
        print(pt[pwc.b])

print(model.profiles)
print(model.bpt)
#print(model.coalition_relations)
