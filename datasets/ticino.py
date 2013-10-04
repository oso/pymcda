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

# Criteria
prix = Criterion('prix', 'prix', False, -1, 25)
transport = Criterion('transport', 'transport', False, -1, 45)
envir = Criterion('envir', 'environment', False, 1, 10)
residents = Criterion('residents', 'residents', False, 1, 12)
competition = Criterion('competition', 'competition', False, 1, 8)
c = Criteria([ prix, transport, envir, residents, competition ])

# Criteria values
cv_prix = CriterionValue('prix', 25)
cv_transport = CriterionValue('transport', 45)
cv_envir = CriterionValue('envir', 10)
cv_residents = CriterionValue('residents', 12)
cv_competition = CriterionValue('competition', 8)
cv = CriteriaValues([ cv_prix, cv_transport, cv_envir, cv_residents,
                       cv_competition ])

# Actions
a1 = Alternative('a1', 'a1')
a2 = Alternative('a2', 'a2')
a3 = Alternative('a3', 'a3')
a4 = Alternative('a4', 'a4')
a5 = Alternative('a5', 'a5')
a6 = Alternative('a6', 'a6')
a7 = Alternative('a7', 'a7')
a = Alternatives([ a1, a2, a3, a4, a5, a6, a7 ])

# Performance table
p1 = AlternativePerformances('a1', {'prix': 120, 'transport':  284, 'envir': 5, 'residents': 3.5, 'competition': 18})
p2 = AlternativePerformances('a2', {'prix': 150, 'transport':  269, 'envir': 2, 'residents': 4.5, 'competition': 24})
p3 = AlternativePerformances('a3', {'prix': 100, 'transport':  413, 'envir': 4, 'residents': 5.5, 'competition': 17})
p4 = AlternativePerformances('a4', {'prix':  60, 'transport':  596, 'envir': 6, 'residents': 8.0, 'competition': 20})
p5 = AlternativePerformances('a5', {'prix':  30, 'transport': 1321, 'envir': 8, 'residents': 7.5, 'competition': 16})
p6 = AlternativePerformances('a6', {'prix':  80, 'transport':  734, 'envir': 5, 'residents': 4.0, 'competition': 21})
p7 = AlternativePerformances('a7', {'prix':  45, 'transport':  982, 'envir': 7, 'residents': 8.5, 'competition': 13})
pt = PerformanceTable([ p1, p2, p3, p4, p5, p6, p7 ])

# Reference actions
b1 = Alternative('b1')
b2 = Alternative('b2')
b = Alternatives([b1, b2])

# Performance table of reference actions
pb1 = AlternativePerformances('b1', {'prix': 100, 'transport': 1000, 'envir': 4, 'residents': 4, 'competition': 15})
pb2 = AlternativePerformances('b2', {'prix':  50, 'transport':  500, 'envir': 7, 'residents': 7, 'competition': 20})
ptb = PerformanceTable([pb1, pb2])

# Indifference threshold
q_prix = Threshold('q', 'indifference', Constant(None, 15))
q_transport = Threshold('q', 'indifference', Constant(None, 80))
q_envir = Threshold('q', 'indifference', Constant(None, 1))
q_residents = Threshold('q', 'indifference', Constant(None, 0.5))
q_competition = Threshold('q', 'indifference', Constant(None, 1))

# Preference threshold
p_prix = Threshold('p', 'preference', Constant(None, 40))
p_transport = Threshold('p', 'preference', Constant(None, 350))
p_envir = Threshold('p', 'preference', Constant(None, 3))
p_residents = Threshold('p', 'preference', Constant(None, 3.5))
p_competition = Threshold('p', 'preference', Constant(None, 5))

# Veto threshold
v_prix = Threshold('v', 'veto', Constant(None, 100))
v_transport = Threshold('v', 'veto', Constant(None, 850))
v_envir = Threshold('v', 'veto', Constant(None, 5))
v_residents = Threshold('v', 'veto', Constant(None, 4.5))
v_competition = Threshold('v', 'veto', Constant(None, 8))

# Thresholds by criterion
prix.thresholds = Thresholds([q_prix, p_prix, v_prix])
transport.thresholds = Thresholds([q_transport, p_transport, v_transport])
envir.thresholds = Thresholds([q_envir, p_envir, v_envir])
residents.thresholds = Thresholds([q_residents, p_residents, v_residents])
competition.thresholds = Thresholds([q_competition, p_competition, v_competition])

# New manner to define thresholds
q2_prix = CriterionValue('prix', 15)
q2_transport = CriterionValue('transport', 80)
q2_envir = CriterionValue('envir', 1)
q2_residents = CriterionValue('residents', 0.5)
q2_competition = CriterionValue('competition', 1)
q2b = CriteriaValues([q2_prix, q2_transport, q2_envir, q2_residents,
                      q2_competition], "q")
q2b1 = AlternativeCriteriaValues("b1", CriteriaValuesSet([q2b]))
q2b2 = AlternativeCriteriaValues("b2", CriteriaValuesSet([q2b]))
q2 = AlternativesCriteriaValues([q2b1, q2b2])

p2_prix = CriterionValue('prix', 40)
p2_transport = CriterionValue('transport', 350)
p2_envir = CriterionValue('envir', 3)
p2_residents = CriterionValue('residents', 3.5)
p2_competition = CriterionValue('competition', 5)
p2b = CriteriaValues([p2_prix, p2_transport, p2_envir, p2_residents,
                      p2_competition], "p")
p2b1 = AlternativeCriteriaValues("b1", CriteriaValuesSet([p2b]))
p2b2 = AlternativeCriteriaValues("b2", CriteriaValuesSet([p2b]))
p2 = AlternativesCriteriaValues([p2b1, p2b2])

v2_prix = CriterionValue('prix', 40)
v2_transport = CriterionValue('transport', 350)
v2_envir = CriterionValue('envir', 3)
v2_residents = CriterionValue('residents', 3.5)
v2_competition = CriterionValue('competition', 5)
v2b = CriteriaValues([v2_prix, v2_transport, v2_envir, v2_residents,
                      v2_competition], "v")
v2b1 = AlternativeCriteriaValues("b1", CriteriaValuesSet([v2b]))
v2b2 = AlternativeCriteriaValues("b2", CriteriaValuesSet([v2b]))
v2 = AlternativesCriteriaValues([v2b1, v2b2])

# Lambda
lbda = 0.75

# Categories
cat1 = Category('cat1', rank=1)
cat2 = Category('cat2', rank=2)
cat3 = Category('cat3', rank=3)
cats = Categories([cat1, cat2, cat3])

# Categories profiles
cp1 = CategoryProfile('b1', Limits('cat1', 'cat2'))
cp2 = CategoryProfile('b2', Limits('cat2', 'cat3'))
cps = CategoriesProfiles([cp1, cp2])

# Alternatives assignments
aap1 = AlternativeAssignment('a1', 'cat2')
aap2 = AlternativeAssignment('a2', 'cat1')
aap3 = AlternativeAssignment('a3', 'cat2')
aap4 = AlternativeAssignment('a4', 'cat3')
aap5 = AlternativeAssignment('a5', 'cat1')
aap6 = AlternativeAssignment('a6', 'cat2')
aap7 = AlternativeAssignment('a7', 'cat2')
aap = AlternativesAssignments([aap1, aap2, aap3, aap4, aap5, aap6, aap7])

aao1 = AlternativeAssignment('a1', 'cat2')
aao2 = AlternativeAssignment('a2', 'cat3')
aao3 = AlternativeAssignment('a3', 'cat2')
aao4 = AlternativeAssignment('a4', 'cat3')
aao5 = AlternativeAssignment('a5', 'cat2')
aao6 = AlternativeAssignment('a6', 'cat2')
aao7 = AlternativeAssignment('a7', 'cat2')
aao = AlternativesAssignments([aao1, aao2, aao3, aao4, aao5, aao6, aao7])
