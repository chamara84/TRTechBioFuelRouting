#solution based on the notes on Biofuel harvest optimization problem

import numpy as np 
import string
import pulp

CostPerTon=np.load('./average_transport_costs_1280.npy')

#availability
availability = np.load('./storage_mass_1280.npy')

fixedCostStorage = 20000000#79635 #cost of the telehandler
demand = 500000

 
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(len(CostPerTon))] for i in range(len(CostPerTon))]
#array representing storage selection
storageSel =  np.ones((len(costForTotalAvail),), dtype=np.int)
allocation = np.zeros((len(costForTotalAvail),len(costForTotalAvail),), dtype=np.int)
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]
costPerTonDict = pulp.makeDict([sourceLabel,destLabel],CostPerTon,0)
allocationDict = pulp.makeDict([sourceLabel,destLabel],allocation,0)
costPerTonSorted = dict()
availabilityDict = pulp.makeDict([sourceLabel],availability,0)


for source in sourceLabel:
    costPerTonSorted[source] = sorted(costPerTonDict[source].items(), key=lambda x:x[1])

minCostDict = dict() #the minimum cost per ton for each storage
minCostDestDict =dict() #the satellite storage for the source storage having minimum cost

pulledAmtDict = {source:0 for source in sourceLabel}

for source in sourceLabel:
    minimum = min(costPerTonDict[source].items(), key= lambda x:x[1])
    minCostDict[source] = minimum[1]
    minCostDestDict[source] = minimum[0]
        
minCostSorted = sorted(minCostDict.items(), key=lambda x:x[1]) # cost of using a storage in the ascending order    
item = 0

while sum(pulledAmtDict.values())<demand and item<len(minCostDict):
    pulledAmtDict[minCostSorted[item][0]] =availabilityDict[minCostSorted[item][0]]
    item+=1
    
if  sum(pulledAmtDict.values())<demand:
    print 'infeasible'
elif sum(pulledAmtDict.values())==demand:
    sourcesFullyUsed = [minCostSorted[i][0] for i in range(item-1)]
    print 'Optimal found'
    for source in sourcesFullyUsed:
        allocationDict[source][minCostDestDict[source]] = 1
else:
    print 'other'
    sourcesFullyUsed = [minCostSorted[i][0] for i in range(item-1)]
    sourcePartiallyUsed = minCostSorted[item-1][0]
    #implement proposition 1
    sourceSet=set(source)
    sourcesFullyUsedSet = set(sourcesFullyUsed)
    for source in sourcesFullyUsed:
        costOfFullyUsed = costPerTonDict[source][minCostDestDict[source]]
        for storage in sourceSet.difference(sourcesFullyUsedSet):
            for satellite in destLabel:
                if (costOfFullyUsed-costPerTonDict[storage][satellite])*min([availabilityDict[source],availabilityDict[storage]]) > fixedCostStorage:
                    sourcesFullyUsedSet.add(storage)
                    
    
     
#minCostDict={source:{minimum[0]:minimum[1] } for source in sourceLabel minimum = min(costPerTonDict[source].items(), key= lambda x:x[1])}