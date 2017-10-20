import pulp
import numpy as np 
import string

#the cost from source node i to plant through node j
CostPerTon=np.load('/home/chamara/Dropbox/TRTech/Chamara/average_transport_costs_1280.npy')

#availability
availability = np.load('/home/chamara/Dropbox/TRTech/Chamara/storage_mass_1280.npy')

fixedCostStorage = 79635 #cost of the telehandler
demand = 50000
  
allocationDict = dict() 
 
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(10)] for i in range(10)]
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]

costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
availabilityDict = pulp.makeDict([sourceLabel],availability,0)



x_ij =pulp.LpVariable.dicts("",(sourceLabel,destLabel),0,1,pulp.LpContinuous)
y_j =pulp.LpVariable.dicts("",destLabel,0,1,pulp.LpContinuous)

lagrangianMul = 10;

#while lagrangianMul*(demand - sum([]))
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

# The optimised objective function value    
sol = pulp.value(prob.objective)
    