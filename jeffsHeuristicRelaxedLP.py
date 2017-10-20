import pulp
import numpy as np 
import string
from operator import itemgetter
import re
import csv

#the cost from source node i to plant through node j
CostPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')
#availability = availability[range(5)]
fixedCostStorage = 16000#cost of the telehandler
 
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(len(availability))] for i in range(len(availability))]
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]


sol= 0


demand =100000 # in tons
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]
costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
availabilityDict = pulp.makeDict([sourceLabel],availability,0)
allocationDict = dict()


        

sol=0
#source to dest mapping
x_ij =pulp.LpVariable.dicts("RoutePlant",(sourceLabel,destLabel),0,1,pulp.LpContinuous)
#existance of storage j
y_j =pulp.LpVariable.dicts("RoutePlant",destLabel,0,1,pulp.LpContinuous)

prob = pulp.LpProblem("storage selection Problem",pulp.LpMinimize) 
prob+= pulp.lpSum([x_ij[i][j]*costForTotalAvailDict[i][j] for i in sourceLabel for j in destLabel])+ pulp.lpSum([y_j[j]*fixedCostStorage for j in destLabel])


    
for j in destLabel:
    for i in sourceLabel:
            prob+=x_ij[i][j] <= y_j[j]
for i in sourceLabel:
            prob+=pulp.lpSum([x_ij[i][j] for j in destLabel])<= 1
            
prob+=pulp.lpSum([availabilityDict[i]*x_ij[i][j] for i in sourceLabel for j in destLabel])>=demand
    

        
prob.solve()
# The status of the solution is printed to the screen
print "Status:", pulp.LpStatus[prob.status]
sol = pulp.value(prob.objective)
# Each of the variables with it's resolved optimum value
for v in prob.variables():
        allocationDict[v.name] = v.varValue
        

# The optimised objective function value 

solution =  ["Solution", sol]
   
with open('IISDoptWithFixedRelaxedLP.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in allocationDict.items():
          
          #print out
          datawriter.writerow(v)
       
        datawriter.writerow(solution)           
  
        
            
        

    

