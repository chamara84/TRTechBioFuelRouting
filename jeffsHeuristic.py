import pulp
import numpy as np 
import string
from operator import itemgetter
import re
import math

#the cost from source node i to plant through node j
CostPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')
availability = availability[range(5)]
fixedCostStorage = 79635 #cost of the telehandler
 
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(len(availability))] for i in range(len(availability))]
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]

#array representing storage selection
storageSel =  np.ones((len(costForTotalAvail),), dtype=np.int)
#storageSel = np.array([1,1,0,1,1])

sol= 0
prevMinSol = 0 #variable having the value of the previous min value

epsilon = 0.01 #the approximation error threshold
maxits = 10000 # the maximum number of iterations
demand =80000 # in tons
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]

costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
storageSelDict =  pulp.makeDict([destLabel],storageSel,0)
availabilityDict = pulp.makeDict([sourceLabel],availability,0)
prevSelVec = storageSelDict # vector having the storage selection for the minimum cost upto now

def flipBitsY(storageSelArray):
    testSet= set()
    storageSelArrayCopy = storageSelArray.copy()
    storeMeetCond = [key[0] for key in storageSelArrayCopy.items() if key[1]==1 ]
    for index in storeMeetCond:
        storageSelArrayCopy = storageSelArray.copy()
        storageSelArrayCopy[index] = 0
        testSet.add(tuple(storageSelArrayCopy.items()))
    return testSet
    
iteration = 0
error = 1
prevMinSol = float('inf')
prevBest = []
bestAllocation = []
allocationDict = dict()
storageSelSet =  set()
storageSelSet.add(tuple(storageSelDict.items()))
bestSourceToDest = dict()
        
while len(storageSelSet)>0 :
  for selAlloc in storageSelSet:
        sol=0
        storageSelDict = dict(selAlloc)
        x_ij =pulp.LpVariable.dicts("RoutePlant",(sourceLabel,destLabel),0,1,pulp.LpContinuous)
        prob = pulp.LpProblem("storage selection Problem",pulp.LpMinimize) 
        prob+= pulp.lpSum([x_ij[i][j]*costForTotalAvailDict[i][j] for i in sourceLabel for j in destLabel]) 
        
        
            
        for j in destLabel:
            for i in sourceLabel:
                    prob+=x_ij[i][j] <= storageSelDict[j]
        for i in sourceLabel:
                    prob+=pulp.lpSum([x_ij[i][j] for j in destLabel])<= 1
                    
        prob+=pulp.lpSum([availabilityDict[i]*x_ij[i][j] for i in sourceLabel for j in destLabel])>=demand
            
        
                
        prob.solve()
        # The status of the solution is printed to the screen
        #print "Status:", pulp.LpStatus[prob.status]
        
        # Each of the variables with it's resolved optimum value
        for v in prob.variables():
                allocationDict[v.name] = v.varValue
                #if v.varValue >0 and v.varValue <1:
                #    fractional =  re.search("RoutePlant_s_([0-9]+)_d_([0-9]+)",v.name)
                #    routeTuple = fractional.groups()
                #    source = string.join(("s",routeTuple[0]),"_")
                #    dest = string.join(("d",routeTuple[1]),"_")
                #    costForTotalAvailDict[source][dest]=costForTotalAvailDict[source][dest]*float(v.varValue)
                #    availabilityDict[source]=availabilityDict[source]*float(v.varValue)
        
        # The optimised objective function value 
        if prob.status==1:
            sol = pulp.value(prob.objective)+fixedCostStorage*np.sum(storageSelDict.values())
        else:
            sol = float('inf')
        print "sol:", sol
        print "yj:", storageSelDict    
        
        if prevMinSol > sol:
            bestAllocation = storageSelDict.copy()
            bestSourceToDest = allocationDict.copy()
            prevMinSol = sol
            
            
            
  storageSelSet.clear()
            
  if len(bestAllocation)>0 and prob.status==1:
      storageSelSet = flipBitsY(bestAllocation)
      prevBest = bestAllocation.copy()
  
  bestAllocation=[]
 
        
            
        

    

