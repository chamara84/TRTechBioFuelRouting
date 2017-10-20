import pulp
import numpy as np 
import string
import re

#the cost from source node i to plant through node j
CostPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')


fixedCostStorage = 79635 #cost of the telehandler
 
allocationDict = dict() 
 
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(len(availability))] for i in range(len(availability))]
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]

costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
x_ij =pulp.LpVariable.dicts("RoutePlant",(sourceLabel,destLabel),0,1,pulp.LpContinuous)
y_j =pulp.LpVariable.dicts("RoutePlant",destLabel,0,1,pulp.LpContinuous)

prob = pulp.LpProblem("storage selection Problem",pulp.LpMinimize) 
prob+= pulp.lpSum([x_ij[i][j]*costForTotalAvailDict[i][j] for i in sourceLabel for j in destLabel])+pulp.lpSum([fixedCostStorage*y_j[j] for j in destLabel]) 

for i in sourceLabel:
        prob+=pulp.lpSum([x_ij[i][j] for j in destLabel])==1
        
for j in destLabel:
    for i in sourceLabel:
        prob+=x_ij[i][j]<= y_j[j]
        
prob.solve()
# The status of the solution is printed to the screen
print "Status:", pulp.LpStatus[prob.status]

# Each of the variables with it's resolved optimum value
for v in prob.variables():
        allocationDict[v.name] = v.varValue
        if re.search("(?<=Selection)",v.name):
            print v.name, ":", v.varValue 


# The optimised objective function value    
sol = pulp.value(prob.objective)
    