import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import Criterion, Criteria
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import Alternative, Alternatives
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import Threshold, Thresholds, Constant
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import Category, Categories
from pymcda.types import CategoryProfile, CategoriesProfiles, Limits
from pymcda.types import AlternativeCriteriaValues, AlternativesCriteriaValues
from pymcda.types import CriteriaValuesSet

# Weights
g1 = Criterion('g01', 'g1', False, 1, 0.02)
g2 = Criterion('g02', 'g2', False, 1, 0.05)
g3 = Criterion('g03', 'g3', False, 1, 0.06)
g4 = Criterion('g04', 'g4', False, 1, 0.06)
g5 = Criterion('g05', 'g5', False, 1, 0.07)
g6 = Criterion('g06', 'g6', False, 1, 0.09)
g7 = Criterion('g07', 'g7', False, 1, 0.09)
g8 = Criterion('g08', 'g8', False, 1, 0.11)
g9 = Criterion('g09', 'g9', False, 1, 0.13)
g10 = Criterion('g10', 'g10', False, 1, 0.15)
g11 = Criterion('g11', 'g11', False, 1, 0.17)
c = Criteria([ g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11 ])

cv_g1 = CriterionValue('g01', 0.02)
cv_g2 = CriterionValue('g02', 0.05)
cv_g3 = CriterionValue('g03', 0.06)
cv_g4 = CriterionValue('g04', 0.06)
cv_g5 = CriterionValue('g05', 0.07)
cv_g6 = CriterionValue('g06', 0.09)
cv_g7 = CriterionValue('g07', 0.09)
cv_g8 = CriterionValue('g08', 0.11)
cv_g9 = CriterionValue('g09', 0.13)
cv_g10 = CriterionValue('g10', 0.15)
cv_g11 = CriterionValue('g11', 0.17)
cv = CriteriaValues([ cv_g1, cv_g2, cv_g3, cv_g4, cv_g5, cv_g6, cv_g7,
                       cv_g8, cv_g9, cv_g10, cv_g11 ])

# Actions
a0 = Alternative('a0')
a1 = Alternative('a1')
a2 = Alternative('a2')
a3 = Alternative('a3')
a4 = Alternative('a4')
a5 = Alternative('a5')
a6 = Alternative('a6')
a7 = Alternative('a7')
a8 = Alternative('a8')
a9 = Alternative('a9')
a10 = Alternative('a10')
a11 = Alternative('a11')
a12 = Alternative('a12')
a13 = Alternative('a13')
a14 = Alternative('a14')
a15 = Alternative('a15')
a16 = Alternative('a16')
a17 = Alternative('a17')
a18 = Alternative('a18')
a19 = Alternative('a19')
a20 = Alternative('a20')
a21 = Alternative('a21')
a22 = Alternative('a22')
a23 = Alternative('a23')
a24 = Alternative('a24')
a25 = Alternative('a25')
a26 = Alternative('a26')
a27 = Alternative('a27')
a28 = Alternative('a28')
a29 = Alternative('a29')
a30 = Alternative('a30')
a31 = Alternative('a31')
a32 = Alternative('a32')
a33 = Alternative('a33')
a34 = Alternative('a34')
a35 = Alternative('a35')
a36 = Alternative('a36')
a37 = Alternative('a37')
a38 = Alternative('a38')
a39 = Alternative('a39')
a40 = Alternative('a40')
a41 = Alternative('a41')
a42 = Alternative('a42')
a43 = Alternative('a43')
a44 = Alternative('a44')
a45 = Alternative('a45')
a46 = Alternative('a46')
a47 = Alternative('a47')
a48 = Alternative('a48')
a49 = Alternative('a49')
a50 = Alternative('a50')
a51 = Alternative('a51')
a52 = Alternative('a52')
a53 = Alternative('a53')
a54 = Alternative('a54')
a55 = Alternative('a55')
a56 = Alternative('a56')
a57 = Alternative('a57')
a58 = Alternative('a58')
a59 = Alternative('a59')
a60 = Alternative('a60')
a61 = Alternative('a61')
a62 = Alternative('a62')
a63 = Alternative('a63')
a64 = Alternative('a64')
a65 = Alternative('a65')
a66 = Alternative('a66')
a67 = Alternative('a67')
a68 = Alternative('a68')
a69 = Alternative('a69')
a70 = Alternative('a70')
a71 = Alternative('a71')
a72 = Alternative('a72')
a73 = Alternative('a73')
a74 = Alternative('a74')
a75 = Alternative('a75')
a76 = Alternative('a76')
a77 = Alternative('a77')
a78 = Alternative('a78')
a79 = Alternative('a79')
a80 = Alternative('a80')
a81 = Alternative('a81')
a82 = Alternative('a82')
a83 = Alternative('a83')
a84 = Alternative('a84')
a85 = Alternative('a85')
a86 = Alternative('a86')
a87 = Alternative('a87')
a88 = Alternative('a88')
a89 = Alternative('a89')
a90 = Alternative('a90')
a91 = Alternative('a91')
a92 = Alternative('a92')
a93 = Alternative('a93')
a94 = Alternative('a94')
a95 = Alternative('a95')
a96 = Alternative('a96')
a97 = Alternative('a97')
a98 = Alternative('a98')
a99 = Alternative('a99')
a100 = Alternative('a100')
a101 = Alternative('a101')
a102 = Alternative('a102')
a103 = Alternative('a103')
a104 = Alternative('a104')
a105 = Alternative('a105')
a106 = Alternative('a106')
a107 = Alternative('a107')
a108 = Alternative('a108')
a109 = Alternative('a109')
a110 = Alternative('a110')
a111 = Alternative('a111')
a112 = Alternative('a112')
a113 = Alternative('a113')
a114 = Alternative('a114')
a115 = Alternative('a115')
a116 = Alternative('a116')
a117 = Alternative('a117')
a118 = Alternative('a118')
a119 = Alternative('a119')
a120 = Alternative('a120')
a121 = Alternative('a121')
a122 = Alternative('a122')
a123 = Alternative('a123')
a124 = Alternative('a124')
a125 = Alternative('a125')
a126 = Alternative('a126')
a127 = Alternative('a127')
a128 = Alternative('a128')
a129 = Alternative('a129')
a130 = Alternative('a130')
a131 = Alternative('a131')
a132 = Alternative('a132')
a133 = Alternative('a133')
a134 = Alternative('a134')
a135 = Alternative('a135')
a136 = Alternative('a136')
a137 = Alternative('a137')
a138 = Alternative('a138')
a139 = Alternative('a139')
a140 = Alternative('a140')
a141 = Alternative('a141')
a142 = Alternative('a142')
a143 = Alternative('a143')
a144 = Alternative('a144')
a145 = Alternative('a145')
a146 = Alternative('a146')
a147 = Alternative('a147')
a148 = Alternative('a148')
a149 = Alternative('a149')
a150 = Alternative('a150')
a151 = Alternative('a151')
a152 = Alternative('a152')
a153 = Alternative('a153')
a154 = Alternative('a154')
a155 = Alternative('a155')
a156 = Alternative('a156')
a157 = Alternative('a157')
a158 = Alternative('a158')
a159 = Alternative('a159')
a160 = Alternative('a160')
a161 = Alternative('a161')
a162 = Alternative('a162')
a163 = Alternative('a163')
a164 = Alternative('a164')
a165 = Alternative('a165')
a166 = Alternative('a166')
a167 = Alternative('a167')
a168 = Alternative('a168')
a169 = Alternative('a169')
a170 = Alternative('a170')
a171 = Alternative('a171')
a172 = Alternative('a172')
a173 = Alternative('a173')
a174 = Alternative('a174')
a175 = Alternative('a175')
a176 = Alternative('a176')
a177 = Alternative('a177')
a178 = Alternative('a178')
a179 = Alternative('a179')
a180 = Alternative('a180')
a181 = Alternative('a181')
a182 = Alternative('a182')
a183 = Alternative('a183')
a184 = Alternative('a184')
a185 = Alternative('a185')
a186 = Alternative('a186')
a187 = Alternative('a187')
a188 = Alternative('a188')
a189 = Alternative('a189')
a190 = Alternative('a190')
a191 = Alternative('a191')
a192 = Alternative('a192')
a193 = Alternative('a193')
a194 = Alternative('a194')
a195 = Alternative('a195')
a196 = Alternative('a196')
a197 = Alternative('a197')
a198 = Alternative('a198')
a199 = Alternative('a199')
a200 = Alternative('a200')
a201 = Alternative('a201')
a202 = Alternative('a202')
a203 = Alternative('a203')
a204 = Alternative('a204')
a205 = Alternative('a205')
a206 = Alternative('a206')
a207 = Alternative('a207')
a208 = Alternative('a208')
a209 = Alternative('a209')
a210 = Alternative('a210')
a211 = Alternative('a211')
a212 = Alternative('a212')
a213 = Alternative('a213')
a214 = Alternative('a214')
a215 = Alternative('a215')
a216 = Alternative('a216')
a217 = Alternative('a217')
a218 = Alternative('a218')
a219 = Alternative('a219')
a220 = Alternative('a220')
a221 = Alternative('a221')
a222 = Alternative('a222')
a223 = Alternative('a223')
a224 = Alternative('a224')
a225 = Alternative('a225')
a226 = Alternative('a226')
a227 = Alternative('a227')
a228 = Alternative('a228')

a = Alternatives([ a0, a1, a2, a3, a4, a5, a6, a7,
              a8, a9, a10, a11, a12, a13, a14, a15,
              a16, a17, a18, a19, a20, a21, a22, a23,
              a24, a25, a26, a27, a28, a29, a30, a31,
              a32, a33, a34, a35, a36, a37, a38, a39,
              a40, a41, a42, a43, a44, a45, a46, a47,
              a48, a49, a50, a51, a52, a53, a54, a55,
              a56, a57, a58, a59, a60, a61, a62, a63,
              a64, a65, a66, a67, a68, a69, a70, a71,
              a72, a73, a74, a75, a76, a77, a78, a79,
              a80, a81, a82, a83, a84, a85, a86, a87,
              a88, a89, a90, a91, a92, a93, a94, a95,
              a96, a97, a98, a99, a100, a101, a102, a103,
              a104, a105, a106, a107, a108, a109, a110, a111,
              a112, a113, a114, a115, a116, a117, a118, a119,
              a120, a121, a122, a123, a124, a125, a126, a127,
              a128, a129, a130, a131, a132, a133, a134, a135,
              a136, a137, a138, a139, a140, a141, a142, a143,
              a144, a145, a146, a147, a148, a149, a150, a151,
              a152, a153, a154, a155, a156, a157, a158, a159,
              a160, a161, a162, a163, a164, a165, a166, a167,
              a168, a169, a170, a171, a172, a173, a174, a175,
              a176, a177, a178, a179, a180, a181, a182, a183,
              a184, a185, a186, a187, a188, a189, a190, a191,
              a192, a193, a194, a195, a196, a197, a198, a199,
              a200, a201, a202, a203, a204, a205, a206, a207,
              a208, a209, a210, a211, a212, a213, a214, a215,
              a216, a217, a218, a219, a220, a221, a222, a223,
              a224, a225, a226, a227, a228 ])

# Performance table
p0 = AlternativePerformances('a0', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':2, 'g10':3, 'g11':5})
p1 = AlternativePerformances('a1', {'g01': 1, 'g02':2, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p2 = AlternativePerformances('a2', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p3 = AlternativePerformances('a3', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p4 = AlternativePerformances('a4', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p5 = AlternativePerformances('a5', {'g01': 1, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p6 = AlternativePerformances('a6', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p7 = AlternativePerformances('a7', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':2, 'g10':3, 'g11':5})
p8 = AlternativePerformances('a8', {'g01': 1, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':1, 'g09':2, 'g10':3, 'g11':4})
p9 = AlternativePerformances('a9', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p10 = AlternativePerformances('a10', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p11 = AlternativePerformances('a11', {'g01': 2, 'g02':3, 'g03':3, 'g04':2, 'g05':3, 'g06':4, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p12 = AlternativePerformances('a12', {'g01': 2, 'g02':3, 'g03':3, 'g04':2, 'g05':3, 'g06':4, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p13 = AlternativePerformances('a13', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p14 = AlternativePerformances('a14', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p15 = AlternativePerformances('a15', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p16 = AlternativePerformances('a16', {'g01': 1, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':4, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p17 = AlternativePerformances('a17', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':3, 'g10':1, 'g11':1})
p18 = AlternativePerformances('a18', {'g01': 1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p19 = AlternativePerformances('a19', {'g01': 2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p20 = AlternativePerformances('a20', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':1, 'g07':3, 'g08':4, 'g09':3, 'g10':3, 'g11':4})
p21 = AlternativePerformances('a21', {'g01': 1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p22 = AlternativePerformances('a22', {'g01': 1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p23 = AlternativePerformances('a23', {'g01': 2, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p24 = AlternativePerformances('a24', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p25 = AlternativePerformances('a25', {'g01': 2, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p26 = AlternativePerformances('a26', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p27 = AlternativePerformances('a27', {'g01': 1, 'g02':2, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p28 = AlternativePerformances('a28', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p29 = AlternativePerformances('a29', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p30 = AlternativePerformances('a30', {'g01': 1, 'g02':2, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p31 = AlternativePerformances('a31', {'g01': 3, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p32 = AlternativePerformances('a32', {'g01': 1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':3, 'g10':1, 'g11':4})
p33 = AlternativePerformances('a33', {'g01': 1, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p34 = AlternativePerformances('a34', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':3, 'g06':1, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p35 = AlternativePerformances('a35', {'g01': 1, 'g02':3, 'g03':2, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':1, 'g11':4})
p36 = AlternativePerformances('a36', {'g01': 2, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p37 = AlternativePerformances('a37', {'g01': 1, 'g02':2, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p38 = AlternativePerformances('a38', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':4, 'g06':1, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':1})
p39 = AlternativePerformances('a39', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p40 = AlternativePerformances('a40', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p41 = AlternativePerformances('a41', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':3, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p42 = AlternativePerformances('a42', {'g01': 2, 'g02':2, 'g03':2, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p43 = AlternativePerformances('a43', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p44 = AlternativePerformances('a44', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p45 = AlternativePerformances('a45', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p46 = AlternativePerformances('a46', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':1, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p47 = AlternativePerformances('a47', {'g01': 1, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p48 = AlternativePerformances('a48', {'g01': 2, 'g02':2, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p49 = AlternativePerformances('a49', {'g01': 2, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':4})
p50 = AlternativePerformances('a50', {'g01': 1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p51 = AlternativePerformances('a51', {'g01': 1, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p52 = AlternativePerformances('a52', {'g01': 1, 'g02':3, 'g03':1, 'g04':2, 'g05':3, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p53 = AlternativePerformances('a53', {'g01': 2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p54 = AlternativePerformances('a54', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':1, 'g08':4, 'g09':2, 'g10':1, 'g11':1})
p55 = AlternativePerformances('a55', {'g01': 1, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p56 = AlternativePerformances('a56', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p57 = AlternativePerformances('a57', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p58 = AlternativePerformances('a58', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p59 = AlternativePerformances('a59', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p60 = AlternativePerformances('a60', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p61 = AlternativePerformances('a61', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p62 = AlternativePerformances('a62', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p63 = AlternativePerformances('a63', {'g01': 2, 'g02':2, 'g03':1, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p64 = AlternativePerformances('a64', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p65 = AlternativePerformances('a65', {'g01': 1, 'g02':3, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p66 = AlternativePerformances('a66', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p67 = AlternativePerformances('a67', {'g01': 1, 'g02':2, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p68 = AlternativePerformances('a68', {'g01': 1, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p69 = AlternativePerformances('a69', {'g01': 2, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p70 = AlternativePerformances('a70', {'g01': 2, 'g02':3, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p71 = AlternativePerformances('a71', {'g01': 2, 'g02':2, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p72 = AlternativePerformances('a72', {'g01': 1, 'g02':3, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p73 = AlternativePerformances('a73', {'g01': 1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p74 = AlternativePerformances('a74', {'g01': 1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':1})
p75 = AlternativePerformances('a75', {'g01': 2, 'g02':1, 'g03':3, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p76 = AlternativePerformances('a76', {'g01': 2, 'g02':2, 'g03':2, 'g04':2, 'g05':3, 'g06':3, 'g07':1, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p77 = AlternativePerformances('a77', {'g01': 2, 'g02':2, 'g03':2, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p78 = AlternativePerformances('a78', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p79 = AlternativePerformances('a79', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p80 = AlternativePerformances('a80', {'g01': 1, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':4})
p81 = AlternativePerformances('a81', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p82 = AlternativePerformances('a82', {'g01': 1, 'g02':2, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p83 = AlternativePerformances('a83', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p84 = AlternativePerformances('a84', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p85 = AlternativePerformances('a85', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p86 = AlternativePerformances('a86', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p87 = AlternativePerformances('a87', {'g01': 1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p88 = AlternativePerformances('a88', {'g01': 1, 'g02':2, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p89 = AlternativePerformances('a89', {'g01': 2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p90 = AlternativePerformances('a90', {'g01': 1, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p91 = AlternativePerformances('a91', {'g01': 1, 'g02':2, 'g03':2, 'g04':1, 'g05':3, 'g06':1, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':4})
p92 = AlternativePerformances('a92', {'g01': 3, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p93 = AlternativePerformances('a93', {'g01': 2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p94 = AlternativePerformances('a94', {'g01': 2, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p95 = AlternativePerformances('a95', {'g01': 1, 'g02':3, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p96 = AlternativePerformances('a96', {'g01': 1, 'g02':2, 'g03':1, 'g04':2, 'g05':3, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p97 = AlternativePerformances('a97', {'g01': 2, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p98 = AlternativePerformances('a98', {'g01': 1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p99 = AlternativePerformances('a99', {'g01': 2, 'g02':2, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p100 = AlternativePerformances('a100', {'g01':2, 'g02':1, 'g03':2, 'g04':2, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p101 = AlternativePerformances('a101', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p102 = AlternativePerformances('a102', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p103 = AlternativePerformances('a103', {'g01':1, 'g02':2, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':3, 'g10':3, 'g11':1})
p104 = AlternativePerformances('a104', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p105 = AlternativePerformances('a105', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p106 = AlternativePerformances('a106', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p107 = AlternativePerformances('a107', {'g01':2, 'g02':3, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p108 = AlternativePerformances('a108', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p109 = AlternativePerformances('a109', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':1})
p110 = AlternativePerformances('a110', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p111 = AlternativePerformances('a111', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p112 = AlternativePerformances('a112', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p113 = AlternativePerformances('a113', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p114 = AlternativePerformances('a114', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':4})
p115 = AlternativePerformances('a115', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':1})
p116 = AlternativePerformances('a116', {'g01':1, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':1, 'g09':3, 'g10':3, 'g11':5})
p117 = AlternativePerformances('a117', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':3, 'g06':4, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p118 = AlternativePerformances('a118', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p119 = AlternativePerformances('a119', {'g01':2, 'g02':2, 'g03':1, 'g04':2, 'g05':3, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p120 = AlternativePerformances('a120', {'g01':2, 'g02':2, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p121 = AlternativePerformances('a121', {'g01':2, 'g02':2, 'g03':3, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p122 = AlternativePerformances('a122', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p123 = AlternativePerformances('a123', {'g01':2, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p124 = AlternativePerformances('a124', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p125 = AlternativePerformances('a125', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p126 = AlternativePerformances('a126', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':4, 'g06':1, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':4})
p127 = AlternativePerformances('a127', {'g01':2, 'g02':3, 'g03':3, 'g04':1, 'g05':3, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p128 = AlternativePerformances('a128', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p129 = AlternativePerformances('a129', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p130 = AlternativePerformances('a130', {'g01':1, 'g02':3, 'g03':2, 'g04':2, 'g05':3, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p131 = AlternativePerformances('a131', {'g01':2, 'g02':3, 'g03':2, 'g04':1, 'g05':4, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p132 = AlternativePerformances('a132', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p133 = AlternativePerformances('a133', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p134 = AlternativePerformances('a134', {'g01':1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':4})
p135 = AlternativePerformances('a135', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p136 = AlternativePerformances('a136', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p137 = AlternativePerformances('a137', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':5})
p138 = AlternativePerformances('a138', {'g01':2, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':4})
p139 = AlternativePerformances('a139', {'g01':1, 'g02':3, 'g03':3, 'g04':1, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p140 = AlternativePerformances('a140', {'g01':2, 'g02':3, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p141 = AlternativePerformances('a141', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p142 = AlternativePerformances('a142', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p143 = AlternativePerformances('a143', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p144 = AlternativePerformances('a144', {'g01':2, 'g02':3, 'g03':2, 'g04':2, 'g05':3, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p145 = AlternativePerformances('a145', {'g01':2, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p146 = AlternativePerformances('a146', {'g01':1, 'g02':2, 'g03':1, 'g04':2, 'g05':3, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p147 = AlternativePerformances('a147', {'g01':2, 'g02':3, 'g03':2, 'g04':1, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p148 = AlternativePerformances('a148', {'g01':1, 'g02':2, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p149 = AlternativePerformances('a149', {'g01':1, 'g02':2, 'g03':2, 'g04':2, 'g05':3, 'g06':4, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p150 = AlternativePerformances('a150', {'g01':1, 'g02':2, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p151 = AlternativePerformances('a151', {'g01':1, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p152 = AlternativePerformances('a152', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p153 = AlternativePerformances('a153', {'g01':2, 'g02':3, 'g03':2, 'g04':1, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':2, 'g10':3, 'g11':5})
p154 = AlternativePerformances('a154', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p155 = AlternativePerformances('a155', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':4, 'g09':3, 'g10':1, 'g11':5})
p156 = AlternativePerformances('a156', {'g01':2, 'g02':1, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p157 = AlternativePerformances('a157', {'g01':1, 'g02':3, 'g03':2, 'g04':2, 'g05':3, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':4})
p158 = AlternativePerformances('a158', {'g01':2, 'g02':3, 'g03':3, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p159 = AlternativePerformances('a159', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p160 = AlternativePerformances('a160', {'g01':1, 'g02':3, 'g03':3, 'g04':1, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':2, 'g10':3, 'g11':5})
p161 = AlternativePerformances('a161', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p162 = AlternativePerformances('a162', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p163 = AlternativePerformances('a163', {'g01':2, 'g02':2, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p164 = AlternativePerformances('a164', {'g01':2, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p165 = AlternativePerformances('a165', {'g01':2, 'g02':1, 'g03':2, 'g04':2, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p166 = AlternativePerformances('a166', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p167 = AlternativePerformances('a167', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':1, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':1})
p168 = AlternativePerformances('a168', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p169 = AlternativePerformances('a169', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':1})
p170 = AlternativePerformances('a170', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p171 = AlternativePerformances('a171', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p172 = AlternativePerformances('a172', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p173 = AlternativePerformances('a173', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':4})
p174 = AlternativePerformances('a174', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p175 = AlternativePerformances('a175', {'g01':1, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':4, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':4})
p176 = AlternativePerformances('a176', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':1})
p177 = AlternativePerformances('a177', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':5, 'g09':2, 'g10':3, 'g11':4})
p178 = AlternativePerformances('a178', {'g01':2, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p179 = AlternativePerformances('a179', {'g01':2, 'g02':2, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p180 = AlternativePerformances('a180', {'g01':1, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':1, 'g09':2, 'g10':3, 'g11':4})
p181 = AlternativePerformances('a181', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p182 = AlternativePerformances('a182', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p183 = AlternativePerformances('a183', {'g01':1, 'g02':3, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p184 = AlternativePerformances('a184', {'g01':1, 'g02':1, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p185 = AlternativePerformances('a185', {'g01':1, 'g02':1, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':1, 'g09':2, 'g10':1, 'g11':1})
p186 = AlternativePerformances('a186', {'g01':1, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':1, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p187 = AlternativePerformances('a187', {'g01':1, 'g02':3, 'g03':2, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p188 = AlternativePerformances('a188', {'g01':3, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p189 = AlternativePerformances('a189', {'g01':1, 'g02':3, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p190 = AlternativePerformances('a190', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':1})
p191 = AlternativePerformances('a191', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':3, 'g10':3, 'g11':4})
p192 = AlternativePerformances('a192', {'g01':1, 'g02':3, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p193 = AlternativePerformances('a193', {'g01':1, 'g02':2, 'g03':2, 'g04':1, 'g05':3, 'g06':1, 'g07':2, 'g08':4, 'g09':2, 'g10':3, 'g11':4})
p194 = AlternativePerformances('a194', {'g01':2, 'g02':2, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p195 = AlternativePerformances('a195', {'g01':2, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p196 = AlternativePerformances('a196', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p197 = AlternativePerformances('a197', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p198 = AlternativePerformances('a198', {'g01':1, 'g02':2, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':1, 'g08':5, 'g09':1, 'g10':3, 'g11':5})
p199 = AlternativePerformances('a199', {'g01':1, 'g02':2, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p200 = AlternativePerformances('a200', {'g01':3, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p201 = AlternativePerformances('a201', {'g01':1, 'g02':2, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':4})
p202 = AlternativePerformances('a202', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p203 = AlternativePerformances('a203', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p204 = AlternativePerformances('a204', {'g01':1, 'g02':2, 'g03':2, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':1, 'g09':2, 'g10':3, 'g11':1})
p205 = AlternativePerformances('a205', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':4, 'g09':1, 'g10':1, 'g11':1})
p206 = AlternativePerformances('a206', {'g01':2, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p207 = AlternativePerformances('a207', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p208 = AlternativePerformances('a208', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p209 = AlternativePerformances('a209', {'g01':1, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p210 = AlternativePerformances('a210', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p211 = AlternativePerformances('a211', {'g01':3, 'g02':2, 'g03':1, 'g04':1, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':1})
p212 = AlternativePerformances('a212', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':4, 'g06':3, 'g07':3, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p213 = AlternativePerformances('a213', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p214 = AlternativePerformances('a214', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':3, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p215 = AlternativePerformances('a215', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p216 = AlternativePerformances('a216', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p217 = AlternativePerformances('a217', {'g01':2, 'g02':3, 'g03':1, 'g04':2, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p218 = AlternativePerformances('a218', {'g01':1, 'g02':3, 'g03':1, 'g04':1, 'g05':3, 'g06':3, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p219 = AlternativePerformances('a219', {'g01':3, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':4, 'g09':1, 'g10':3, 'g11':5})
p220 = AlternativePerformances('a220', {'g01':1, 'g02':2, 'g03':3, 'g04':2, 'g05':1, 'g06':3, 'g07':2, 'g08':1, 'g09':3, 'g10':1, 'g11':1})
p221 = AlternativePerformances('a221', {'g01':1, 'g02':3, 'g03':2, 'g04':1, 'g05':3, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p222 = AlternativePerformances('a222', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':1})
p223 = AlternativePerformances('a223', {'g01':1, 'g02':3, 'g03':3, 'g04':1, 'g05':1, 'g06':3, 'g07':3, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p224 = AlternativePerformances('a224', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p225 = AlternativePerformances('a225', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':1, 'g08':1, 'g09':1, 'g10':1, 'g11':1})
p226 = AlternativePerformances('a226', {'g01':1, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':1, 'g07':2, 'g08':1, 'g09':1, 'g10':3, 'g11':5})
p227 = AlternativePerformances('a227', {'g01':2, 'g02':1, 'g03':1, 'g04':1, 'g05':1, 'g06':3, 'g07':1, 'g08':1, 'g09':1, 'g10':3, 'g11':4})
p228 = AlternativePerformances('a228', {'g01':2, 'g02':3, 'g03':3, 'g04':2, 'g05':4, 'g06':3, 'g07':2, 'g08':5, 'g09':3, 'g10':3, 'g11':5})

pt = PerformanceTable([ p0, p1, p2, p3, p4, p5, p6, p7,
              p8, p9, p10, p11, p12, p13, p14, p15,
              p16, p17, p18, p19, p20, p21, p22, p23,
              p24, p25, p26, p27, p28, p29, p30, p31,
              p32, p33, p34, p35, p36, p37, p38, p39,
              p40, p41, p42, p43, p44, p45, p46, p47,
              p48, p49, p50, p51, p52, p53, p54, p55,
              p56, p57, p58, p59, p60, p61, p62, p63,
              p64, p65, p66, p67, p68, p69, p70, p71,
              p72, p73, p74, p75, p76, p77, p78, p79,
              p80, p81, p82, p83, p84, p85, p86, p87,
              p88, p89, p90, p91, p92, p93, p94, p95,
              p96, p97, p98, p99, p100, p101, p102, p103,
              p104, p105, p106, p107, p108, p109, p110, p111,
              p112, p113, p114, p115, p116, p117, p118, p119,
              p120, p121, p122, p123, p124, p125, p126, p127,
              p128, p129, p130, p131, p132, p133, p134, p135,
              p136, p137, p138, p139, p140, p141, p142, p143,
              p144, p145, p146, p147, p148, p149, p150, p151,
              p152, p153, p154, p155, p156, p157, p158, p159,
              p160, p161, p162, p163, p164, p165, p166, p167,
              p168, p169, p170, p171, p172, p173, p174, p175,
              p176, p177, p178, p179, p180, p181, p182, p183,
              p184, p185, p186, p187, p188, p189, p190, p191,
              p192, p193, p194, p195, p196, p197, p198, p199,
              p200, p201, p202, p203, p204, p205, p206, p207,
              p208, p209, p210, p211, p212, p213, p214, p215,
              p216, p217, p218, p219, p220, p221, p222, p223,
              p224, p225, p226, p227, p228 ])

# Reference actions
b1 = Alternative('b1')
b2 = Alternative('b2')
b3 = Alternative('b3')
b = Alternatives([b1, b2, b3])

# Performance table of reference actions
pb1 = AlternativePerformances('b1', {'g01': 1, 'g02': 2, 'g03': 1, 'g04': 1, 'g05': 1, 'g06': 1, 'g07': 2, 'g08': 4, 'g09': 1, 'g10': 1, 'g11': 1})
pb2 = AlternativePerformances('b2', {'g01': 2, 'g02': 2, 'g03': 2, 'g04': 2, 'g05': 3, 'g06': 1, 'g07': 3, 'g08': 4, 'g09': 2, 'g10': 3, 'g11': 4})
pb3 = AlternativePerformances('b3', {'g01': 2, 'g02': 3, 'g03': 3, 'g04': 2, 'g05': 3, 'g06': 1, 'g07': 3, 'g08': 5, 'g09': 3, 'g10': 3, 'g11': 5})
ptb = PerformanceTable([pb1, pb2, pb3])

# Indifference thresholds
q_g1 = Threshold('q', 'indifference', Constant(None, 0))
q_g2 = Threshold('q', 'indifference', Constant(None, 0))
q_g3 = Threshold('q', 'indifference', Constant(None, 0))
q_g4 = Threshold('q', 'indifference', Constant(None, 0))
q_g5 = Threshold('q', 'indifference', Constant(None, 0))
q_g6 = Threshold('q', 'indifference', Constant(None, 0))
q_g7 = Threshold('q', 'indifference', Constant(None, 0))
q_g8 = Threshold('q', 'indifference', Constant(None, 0))
q_g9 = Threshold('q', 'indifference', Constant(None, 0))
q_g10 = Threshold('q', 'indifference', Constant(None,0))
q_g11 = Threshold('q', 'indifference', Constant(None, 0))

# Preference thresholds
p_g1 = Threshold('p', 'preference', Constant(None, 1))
p_g2 = Threshold('p', 'preference', Constant(None, 1))
p_g3 = Threshold('p', 'preference', Constant(None, 1))
p_g4 = Threshold('p', 'preference', Constant(None, 1))
p_g5 = Threshold('p', 'preference', Constant(None, 1))
p_g6 = Threshold('p', 'preference', Constant(None, 1))
p_g7 = Threshold('p', 'preference', Constant(None, 1))
p_g8 = Threshold('p', 'preference', Constant(None, 1))
p_g9 = Threshold('p', 'preference', Constant(None, 1))
p_g10 = Threshold('p', 'preference', Constant(None, 2))
p_g11 = Threshold('p', 'preference', Constant(None, 1))

# Veto thresholds
v_g11 = Threshold('v', 'veto', Constant(None, 4))

# Thresholds by criterion
g1.thresholds = Thresholds([q_g1, p_g1])
g2.thresholds = Thresholds([q_g2, p_g2])
g3.thresholds = Thresholds([q_g3, p_g3])
g4.thresholds = Thresholds([q_g4, p_g4])
g5.thresholds = Thresholds([q_g5, p_g5])
g6.thresholds = Thresholds([q_g6, p_g6])
g7.thresholds = Thresholds([q_g7, p_g7])
g8.thresholds = Thresholds([q_g8, p_g8])
g9.thresholds = Thresholds([q_g9, p_g9])
g10.thresholds = Thresholds([q_g10, p_g10])
g11.thresholds = Thresholds([q_g11, p_g11, v_g11])

# New manner to define the thresholds
q2perfs = {'g01': 0, 'g02': 0, 'g03': 0, 'g04': 0, 'g05': 0, 'g06': 0, 'g07': 0, 'g08': 0, 'g09': 0, 'g10': 0, 'g11': 0}
q2b1 = AlternativePerformances('qb1', q2perfs, 'b1')
q2b2 = AlternativePerformances('qb2', q2perfs, 'b2')
q2b3 = AlternativePerformances('qb3', q2perfs, 'b3')
q2 = PerformanceTable([q2b1, q2b2, q2b3])

p2perfs = {'g01': 1, 'g02': 1, 'g03': 1, 'g04': 1, 'g05': 1, 'g06': 1, 'g07': 1, 'g08': 1, 'g09': 1, 'g10': 1, 'g11': 1}
p2b1 = AlternativePerformances('pb1', p2perfs, 'b1')
p2b2 = AlternativePerformances('pb2', p2perfs, 'b2')
p2b3 = AlternativePerformances('pb3', p2perfs, 'b3')
p2 = PerformanceTable([q2b1, q2b2, q2b3])

v2perfs = {'g01': None, 'g02': None, 'g03': None, 'g04': None, 'g05': None, 'g06': None, 'g07': None, 'g08': None, 'g09': None, 'g10': None, 'g11': 4}
v2b1 = AlternativePerformances('vb1', v2perfs, 'b1')
v2b2 = AlternativePerformances('vb2', v2perfs, 'b2')
v2b3 = AlternativePerformances('vb3', v2perfs, 'b3')
v2 = PerformanceTable([v2b1, v2b2, v2b3])

# Lambda
lbda = 0.76

# Categories
cat1 = Category('cat1', rank=1)
cat2 = Category('cat2', rank=2)
cat3 = Category('cat3', rank=3)
cat4 = Category('cat4', rank=4)
cats = Categories([cat1, cat2, cat3, cat4])

# Categories profiles
cp1 = CategoryProfile('b1', Limits('cat1', 'cat2'))
cp2 = CategoryProfile('b2', Limits('cat2', 'cat3'))
cp3 = CategoryProfile('b3', Limits('cat3', 'cat4'))
cps = CategoriesProfiles([cp1, cp2, cp3])

# Alternatives assignments
aap = AlternativesAssignments([
AlternativeAssignment('a0', 'cat2'),
AlternativeAssignment('a1', 'cat2'),
AlternativeAssignment('a2', 'cat1'),
AlternativeAssignment('a3', 'cat2'),
AlternativeAssignment('a4', 'cat2'),
AlternativeAssignment('a5', 'cat2'),
AlternativeAssignment('a6', 'cat2'),
AlternativeAssignment('a7', 'cat2'),
AlternativeAssignment('a8', 'cat3'),
AlternativeAssignment('a9', 'cat1'),
AlternativeAssignment('a10', 'cat2'),
AlternativeAssignment('a11', 'cat3'),
AlternativeAssignment('a12', 'cat3'),
AlternativeAssignment('a13', 'cat1'),
AlternativeAssignment('a14', 'cat2'),
AlternativeAssignment('a15', 'cat1'),
AlternativeAssignment('a16', 'cat2'),
AlternativeAssignment('a17', 'cat2'),
AlternativeAssignment('a18', 'cat2'),
AlternativeAssignment('a19', 'cat2'),
AlternativeAssignment('a20', 'cat3'),
AlternativeAssignment('a21', 'cat2'),
AlternativeAssignment('a22', 'cat2'),
AlternativeAssignment('a23', 'cat2'),
AlternativeAssignment('a24', 'cat2'),
AlternativeAssignment('a25', 'cat2'),
AlternativeAssignment('a26', 'cat1'),
AlternativeAssignment('a27', 'cat2'),
AlternativeAssignment('a28', 'cat2'),
AlternativeAssignment('a29', 'cat2'),
AlternativeAssignment('a30', 'cat2'),
AlternativeAssignment('a31', 'cat4'),
AlternativeAssignment('a32', 'cat2'),
AlternativeAssignment('a33', 'cat2'),
AlternativeAssignment('a34', 'cat2'),
AlternativeAssignment('a35', 'cat2'),
AlternativeAssignment('a36', 'cat2'),
AlternativeAssignment('a37', 'cat2'),
AlternativeAssignment('a38', 'cat2'),
AlternativeAssignment('a39', 'cat1'),
AlternativeAssignment('a40', 'cat1'),
AlternativeAssignment('a41', 'cat2'),
AlternativeAssignment('a42', 'cat2'),
AlternativeAssignment('a43', 'cat2'),
AlternativeAssignment('a44', 'cat1'),
AlternativeAssignment('a45', 'cat2'),
AlternativeAssignment('a46', 'cat2'),
AlternativeAssignment('a47', 'cat2'),
AlternativeAssignment('a48', 'cat2'),
AlternativeAssignment('a49', 'cat2'),
AlternativeAssignment('a50', 'cat2'),
AlternativeAssignment('a51', 'cat2'),
AlternativeAssignment('a52', 'cat2'),
AlternativeAssignment('a53', 'cat2'),
AlternativeAssignment('a54', 'cat2'),
AlternativeAssignment('a55', 'cat2'),
AlternativeAssignment('a56', 'cat1'),
AlternativeAssignment('a57', 'cat2'),
AlternativeAssignment('a58', 'cat1'),
AlternativeAssignment('a59', 'cat1'),
AlternativeAssignment('a60', 'cat1'),
AlternativeAssignment('a61', 'cat1'),
AlternativeAssignment('a62', 'cat1'),
AlternativeAssignment('a63', 'cat2'),
AlternativeAssignment('a64', 'cat2'),
AlternativeAssignment('a65', 'cat2'),
AlternativeAssignment('a66', 'cat2'),
AlternativeAssignment('a67', 'cat2'),
AlternativeAssignment('a68', 'cat2'),
AlternativeAssignment('a69', 'cat2'),
AlternativeAssignment('a70', 'cat3'),
AlternativeAssignment('a71', 'cat2'),
AlternativeAssignment('a72', 'cat2'),
AlternativeAssignment('a73', 'cat2'),
AlternativeAssignment('a74', 'cat2'),
AlternativeAssignment('a75', 'cat2'),
AlternativeAssignment('a76', 'cat2'),
AlternativeAssignment('a77', 'cat2'),
AlternativeAssignment('a78', 'cat2'),
AlternativeAssignment('a79', 'cat2'),
AlternativeAssignment('a80', 'cat3'),
AlternativeAssignment('a81', 'cat2'),
AlternativeAssignment('a82', 'cat2'),
AlternativeAssignment('a83', 'cat1'),
AlternativeAssignment('a84', 'cat1'),
AlternativeAssignment('a85', 'cat1'),
AlternativeAssignment('a86', 'cat1'),
AlternativeAssignment('a87', 'cat2'),
AlternativeAssignment('a88', 'cat2'),
AlternativeAssignment('a89', 'cat4'),
AlternativeAssignment('a90', 'cat2'),
AlternativeAssignment('a91', 'cat2'),
AlternativeAssignment('a92', 'cat1'),
AlternativeAssignment('a93', 'cat3'),
AlternativeAssignment('a94', 'cat2'),
AlternativeAssignment('a95', 'cat2'),
AlternativeAssignment('a96', 'cat2'),
AlternativeAssignment('a97', 'cat2'),
AlternativeAssignment('a98', 'cat2'),
AlternativeAssignment('a99', 'cat2'),
AlternativeAssignment('a100', 'cat2'),
AlternativeAssignment('a101', 'cat2'),
AlternativeAssignment('a102', 'cat2'),
AlternativeAssignment('a103', 'cat2'),
AlternativeAssignment('a104', 'cat4'),
AlternativeAssignment('a105', 'cat2'),
AlternativeAssignment('a106', 'cat2'),
AlternativeAssignment('a107', 'cat2'),
AlternativeAssignment('a108', 'cat1'),
AlternativeAssignment('a109', 'cat2'),
AlternativeAssignment('a110', 'cat2'),
AlternativeAssignment('a111', 'cat2'),
AlternativeAssignment('a112', 'cat2'),
AlternativeAssignment('a113', 'cat2'),
AlternativeAssignment('a114', 'cat2'),
AlternativeAssignment('a115', 'cat2'),
AlternativeAssignment('a116', 'cat4'),
AlternativeAssignment('a117', 'cat3'),
AlternativeAssignment('a118', 'cat2'),
AlternativeAssignment('a119', 'cat2'),
AlternativeAssignment('a120', 'cat2'),
AlternativeAssignment('a121', 'cat2'),
AlternativeAssignment('a122', 'cat2'),
AlternativeAssignment('a123', 'cat2'),
AlternativeAssignment('a124', 'cat2'),
AlternativeAssignment('a125', 'cat2'),
AlternativeAssignment('a126', 'cat2'),
AlternativeAssignment('a127', 'cat2'),
AlternativeAssignment('a128', 'cat2'),
AlternativeAssignment('a129', 'cat2'),
AlternativeAssignment('a130', 'cat2'),
AlternativeAssignment('a131', 'cat2'),
AlternativeAssignment('a132', 'cat2'),
AlternativeAssignment('a133', 'cat3'),
AlternativeAssignment('a134', 'cat2'),
AlternativeAssignment('a135', 'cat2'),
AlternativeAssignment('a136', 'cat2'),
AlternativeAssignment('a137', 'cat2'),
AlternativeAssignment('a138', 'cat2'),
AlternativeAssignment('a139', 'cat2'),
AlternativeAssignment('a140', 'cat3'),
AlternativeAssignment('a141', 'cat2'),
AlternativeAssignment('a142', 'cat2'),
AlternativeAssignment('a143', 'cat2'),
AlternativeAssignment('a144', 'cat2'),
AlternativeAssignment('a145', 'cat2'),
AlternativeAssignment('a146', 'cat2'),
AlternativeAssignment('a147', 'cat2'),
AlternativeAssignment('a148', 'cat2'),
AlternativeAssignment('a149', 'cat2'),
AlternativeAssignment('a150', 'cat2'),
AlternativeAssignment('a151', 'cat2'),
AlternativeAssignment('a152', 'cat2'),
AlternativeAssignment('a153', 'cat3'),
AlternativeAssignment('a154', 'cat2'),
AlternativeAssignment('a155', 'cat3'),
AlternativeAssignment('a156', 'cat2'),
AlternativeAssignment('a157', 'cat3'),
AlternativeAssignment('a158', 'cat2'),
AlternativeAssignment('a159', 'cat2'),
AlternativeAssignment('a160', 'cat2'),
AlternativeAssignment('a161', 'cat2'),
AlternativeAssignment('a162', 'cat2'),
AlternativeAssignment('a163', 'cat2'),
AlternativeAssignment('a164', 'cat2'),
AlternativeAssignment('a165', 'cat1'),
AlternativeAssignment('a166', 'cat1'),
AlternativeAssignment('a167', 'cat2'),
AlternativeAssignment('a168', 'cat2'),
AlternativeAssignment('a169', 'cat2'),
AlternativeAssignment('a170', 'cat1'),
AlternativeAssignment('a171', 'cat2'),
AlternativeAssignment('a172', 'cat2'),
AlternativeAssignment('a173', 'cat2'),
AlternativeAssignment('a174', 'cat2'),
AlternativeAssignment('a175', 'cat2'),
AlternativeAssignment('a176', 'cat2'),
AlternativeAssignment('a177', 'cat2'),
AlternativeAssignment('a178', 'cat2'),
AlternativeAssignment('a179', 'cat2'),
AlternativeAssignment('a180', 'cat3'),
AlternativeAssignment('a181', 'cat2'),
AlternativeAssignment('a182', 'cat4'),
AlternativeAssignment('a183', 'cat2'),
AlternativeAssignment('a184', 'cat2'),
AlternativeAssignment('a185', 'cat1'),
AlternativeAssignment('a186', 'cat2'),
AlternativeAssignment('a187', 'cat2'),
AlternativeAssignment('a188', 'cat1'),
AlternativeAssignment('a189', 'cat2'),
AlternativeAssignment('a190', 'cat2'),
AlternativeAssignment('a191', 'cat2'),
AlternativeAssignment('a192', 'cat2'),
AlternativeAssignment('a193', 'cat3'),
AlternativeAssignment('a194', 'cat2'),
AlternativeAssignment('a195', 'cat3'),
AlternativeAssignment('a196', 'cat4'),
AlternativeAssignment('a197', 'cat2'),
AlternativeAssignment('a198', 'cat2'),
AlternativeAssignment('a199', 'cat2'),
AlternativeAssignment('a200', 'cat1'),
AlternativeAssignment('a201', 'cat2'),
AlternativeAssignment('a202', 'cat2'),
AlternativeAssignment('a203', 'cat2'),
AlternativeAssignment('a204', 'cat2'),
AlternativeAssignment('a205', 'cat2'),
AlternativeAssignment('a206', 'cat2'),
AlternativeAssignment('a207', 'cat2'),
AlternativeAssignment('a208', 'cat4'),
AlternativeAssignment('a209', 'cat2'),
AlternativeAssignment('a210', 'cat1'),
AlternativeAssignment('a211', 'cat2'),
AlternativeAssignment('a212', 'cat2'),
AlternativeAssignment('a213', 'cat2'),
AlternativeAssignment('a214', 'cat2'),
AlternativeAssignment('a215', 'cat2'),
AlternativeAssignment('a216', 'cat1'),
AlternativeAssignment('a217', 'cat2'),
AlternativeAssignment('a218', 'cat2'),
AlternativeAssignment('a219', 'cat3'),
AlternativeAssignment('a220', 'cat2'),
AlternativeAssignment('a221', 'cat2'),
AlternativeAssignment('a222', 'cat1'),
AlternativeAssignment('a223', 'cat2'),
AlternativeAssignment('a224', 'cat2'),
AlternativeAssignment('a225', 'cat1'),
AlternativeAssignment('a226', 'cat2'),
AlternativeAssignment('a227', 'cat1'),
AlternativeAssignment('a228', 'cat4')])

aao = AlternativesAssignments([
AlternativeAssignment('a0', 'cat2'),
AlternativeAssignment('a1', 'cat2'),
AlternativeAssignment('a2', 'cat1'),
AlternativeAssignment('a3', 'cat2'),
AlternativeAssignment('a4', 'cat2'),
AlternativeAssignment('a5', 'cat2'),
AlternativeAssignment('a6', 'cat2'),
AlternativeAssignment('a7', 'cat2'),
AlternativeAssignment('a8', 'cat3'),
AlternativeAssignment('a9', 'cat1'),
AlternativeAssignment('a10', 'cat2'),
AlternativeAssignment('a11', 'cat3'),
AlternativeAssignment('a12', 'cat3'),
AlternativeAssignment('a13', 'cat1'),
AlternativeAssignment('a14', 'cat2'),
AlternativeAssignment('a15', 'cat2'),
AlternativeAssignment('a16', 'cat2'),
AlternativeAssignment('a17', 'cat2'),
AlternativeAssignment('a18', 'cat2'),
AlternativeAssignment('a19', 'cat2'),
AlternativeAssignment('a20', 'cat3'),
AlternativeAssignment('a21', 'cat2'),
AlternativeAssignment('a22', 'cat2'),
AlternativeAssignment('a23', 'cat3'),
AlternativeAssignment('a24', 'cat2'),
AlternativeAssignment('a25', 'cat2'),
AlternativeAssignment('a26', 'cat1'),
AlternativeAssignment('a27', 'cat2'),
AlternativeAssignment('a28', 'cat2'),
AlternativeAssignment('a29', 'cat2'),
AlternativeAssignment('a30', 'cat2'),
AlternativeAssignment('a31', 'cat4'),
AlternativeAssignment('a32', 'cat2'),
AlternativeAssignment('a33', 'cat2'),
AlternativeAssignment('a34', 'cat2'),
AlternativeAssignment('a35', 'cat2'),
AlternativeAssignment('a36', 'cat2'),
AlternativeAssignment('a37', 'cat2'),
AlternativeAssignment('a38', 'cat2'),
AlternativeAssignment('a39', 'cat2'),
AlternativeAssignment('a40', 'cat1'),
AlternativeAssignment('a41', 'cat2'),
AlternativeAssignment('a42', 'cat2'),
AlternativeAssignment('a43', 'cat2'),
AlternativeAssignment('a44', 'cat2'),
AlternativeAssignment('a45', 'cat2'),
AlternativeAssignment('a46', 'cat2'),
AlternativeAssignment('a47', 'cat2'),
AlternativeAssignment('a48', 'cat2'),
AlternativeAssignment('a49', 'cat2'),
AlternativeAssignment('a50', 'cat2'),
AlternativeAssignment('a51', 'cat3'),
AlternativeAssignment('a52', 'cat2'),
AlternativeAssignment('a53', 'cat2'),
AlternativeAssignment('a54', 'cat2'),
AlternativeAssignment('a55', 'cat2'),
AlternativeAssignment('a56', 'cat2'),
AlternativeAssignment('a57', 'cat2'),
AlternativeAssignment('a58', 'cat2'),
AlternativeAssignment('a59', 'cat2'),
AlternativeAssignment('a60', 'cat1'),
AlternativeAssignment('a61', 'cat1'),
AlternativeAssignment('a62', 'cat1'),
AlternativeAssignment('a63', 'cat2'),
AlternativeAssignment('a64', 'cat2'),
AlternativeAssignment('a65', 'cat3'),
AlternativeAssignment('a66', 'cat2'),
AlternativeAssignment('a67', 'cat2'),
AlternativeAssignment('a68', 'cat3'),
AlternativeAssignment('a69', 'cat2'),
AlternativeAssignment('a70', 'cat3'),
AlternativeAssignment('a71', 'cat2'),
AlternativeAssignment('a72', 'cat2'),
AlternativeAssignment('a73', 'cat2'),
AlternativeAssignment('a74', 'cat2'),
AlternativeAssignment('a75', 'cat2'),
AlternativeAssignment('a76', 'cat2'),
AlternativeAssignment('a77', 'cat3'),
AlternativeAssignment('a78', 'cat2'),
AlternativeAssignment('a79', 'cat2'),
AlternativeAssignment('a80', 'cat3'),
AlternativeAssignment('a81', 'cat3'),
AlternativeAssignment('a82', 'cat2'),
AlternativeAssignment('a83', 'cat1'),
AlternativeAssignment('a84', 'cat1'),
AlternativeAssignment('a85', 'cat1'),
AlternativeAssignment('a86', 'cat1'),
AlternativeAssignment('a87', 'cat2'),
AlternativeAssignment('a88', 'cat2'),
AlternativeAssignment('a89', 'cat4'),
AlternativeAssignment('a90', 'cat2'),
AlternativeAssignment('a91', 'cat2'),
AlternativeAssignment('a92', 'cat1'),
AlternativeAssignment('a93', 'cat3'),
AlternativeAssignment('a94', 'cat2'),
AlternativeAssignment('a95', 'cat2'),
AlternativeAssignment('a96', 'cat3'),
AlternativeAssignment('a97', 'cat3'),
AlternativeAssignment('a98', 'cat2'),
AlternativeAssignment('a99', 'cat2'),
AlternativeAssignment('a100', 'cat2'),
AlternativeAssignment('a101', 'cat2'),
AlternativeAssignment('a102', 'cat2'),
AlternativeAssignment('a103', 'cat3'),
AlternativeAssignment('a104', 'cat4'),
AlternativeAssignment('a105', 'cat3'),
AlternativeAssignment('a106', 'cat2'),
AlternativeAssignment('a107', 'cat2'),
AlternativeAssignment('a108', 'cat1'),
AlternativeAssignment('a109', 'cat2'),
AlternativeAssignment('a110', 'cat2'),
AlternativeAssignment('a111', 'cat2'),
AlternativeAssignment('a112', 'cat2'),
AlternativeAssignment('a113', 'cat2'),
AlternativeAssignment('a114', 'cat3'),
AlternativeAssignment('a115', 'cat3'),
AlternativeAssignment('a116', 'cat4'),
AlternativeAssignment('a117', 'cat3'),
AlternativeAssignment('a118', 'cat2'),
AlternativeAssignment('a119', 'cat3'),
AlternativeAssignment('a120', 'cat2'),
AlternativeAssignment('a121', 'cat2'),
AlternativeAssignment('a122', 'cat2'),
AlternativeAssignment('a123', 'cat2'),
AlternativeAssignment('a124', 'cat2'),
AlternativeAssignment('a125', 'cat2'),
AlternativeAssignment('a126', 'cat2'),
AlternativeAssignment('a127', 'cat2'),
AlternativeAssignment('a128', 'cat2'),
AlternativeAssignment('a129', 'cat3'),
AlternativeAssignment('a130', 'cat2'),
AlternativeAssignment('a131', 'cat2'),
AlternativeAssignment('a132', 'cat2'),
AlternativeAssignment('a133', 'cat3'),
AlternativeAssignment('a134', 'cat2'),
AlternativeAssignment('a135', 'cat2'),
AlternativeAssignment('a136', 'cat2'),
AlternativeAssignment('a137', 'cat3'),
AlternativeAssignment('a138', 'cat3'),
AlternativeAssignment('a139', 'cat3'),
AlternativeAssignment('a140', 'cat3'),
AlternativeAssignment('a141', 'cat2'),
AlternativeAssignment('a142', 'cat2'),
AlternativeAssignment('a143', 'cat2'),
AlternativeAssignment('a144', 'cat2'),
AlternativeAssignment('a145', 'cat2'),
AlternativeAssignment('a146', 'cat2'),
AlternativeAssignment('a147', 'cat2'),
AlternativeAssignment('a148', 'cat2'),
AlternativeAssignment('a149', 'cat2'),
AlternativeAssignment('a150', 'cat2'),
AlternativeAssignment('a151', 'cat2'),
AlternativeAssignment('a152', 'cat2'),
AlternativeAssignment('a153', 'cat3'),
AlternativeAssignment('a154', 'cat2'),
AlternativeAssignment('a155', 'cat3'),
AlternativeAssignment('a156', 'cat2'),
AlternativeAssignment('a157', 'cat3'),
AlternativeAssignment('a158', 'cat2'),
AlternativeAssignment('a159', 'cat3'),
AlternativeAssignment('a160', 'cat3'),
AlternativeAssignment('a161', 'cat2'),
AlternativeAssignment('a162', 'cat3'),
AlternativeAssignment('a163', 'cat2'),
AlternativeAssignment('a164', 'cat2'),
AlternativeAssignment('a165', 'cat1'),
AlternativeAssignment('a166', 'cat1'),
AlternativeAssignment('a167', 'cat2'),
AlternativeAssignment('a168', 'cat2'),
AlternativeAssignment('a169', 'cat2'),
AlternativeAssignment('a170', 'cat1'),
AlternativeAssignment('a171', 'cat2'),
AlternativeAssignment('a172', 'cat2'),
AlternativeAssignment('a173', 'cat2'),
AlternativeAssignment('a174', 'cat3'),
AlternativeAssignment('a175', 'cat3'),
AlternativeAssignment('a176', 'cat3'),
AlternativeAssignment('a177', 'cat3'),
AlternativeAssignment('a178', 'cat2'),
AlternativeAssignment('a179', 'cat3'),
AlternativeAssignment('a180', 'cat3'),
AlternativeAssignment('a181', 'cat2'),
AlternativeAssignment('a182', 'cat4'),
AlternativeAssignment('a183', 'cat2'),
AlternativeAssignment('a184', 'cat2'),
AlternativeAssignment('a185', 'cat2'),
AlternativeAssignment('a186', 'cat2'),
AlternativeAssignment('a187', 'cat2'),
AlternativeAssignment('a188', 'cat1'),
AlternativeAssignment('a189', 'cat2'),
AlternativeAssignment('a190', 'cat2'),
AlternativeAssignment('a191', 'cat2'),
AlternativeAssignment('a192', 'cat2'),
AlternativeAssignment('a193', 'cat3'),
AlternativeAssignment('a194', 'cat3'),
AlternativeAssignment('a195', 'cat3'),
AlternativeAssignment('a196', 'cat4'),
AlternativeAssignment('a197', 'cat2'),
AlternativeAssignment('a198', 'cat3'),
AlternativeAssignment('a199', 'cat2'),
AlternativeAssignment('a200', 'cat1'),
AlternativeAssignment('a201', 'cat2'),
AlternativeAssignment('a202', 'cat2'),
AlternativeAssignment('a203', 'cat2'),
AlternativeAssignment('a204', 'cat2'),
AlternativeAssignment('a205', 'cat2'),
AlternativeAssignment('a206', 'cat2'),
AlternativeAssignment('a207', 'cat2'),
AlternativeAssignment('a208', 'cat4'),
AlternativeAssignment('a209', 'cat2'),
AlternativeAssignment('a210', 'cat2'),
AlternativeAssignment('a211', 'cat2'),
AlternativeAssignment('a212', 'cat3'),
AlternativeAssignment('a213', 'cat2'),
AlternativeAssignment('a214', 'cat2'),
AlternativeAssignment('a215', 'cat2'),
AlternativeAssignment('a216', 'cat1'),
AlternativeAssignment('a217', 'cat2'),
AlternativeAssignment('a218', 'cat2'),
AlternativeAssignment('a219', 'cat3'),
AlternativeAssignment('a220', 'cat3'),
AlternativeAssignment('a221', 'cat2'),
AlternativeAssignment('a222', 'cat1'),
AlternativeAssignment('a223', 'cat3'),
AlternativeAssignment('a224', 'cat2'),
AlternativeAssignment('a225', 'cat1'),
AlternativeAssignment('a226', 'cat2'),
AlternativeAssignment('a227', 'cat2'),
AlternativeAssignment('a228', 'cat4')])
