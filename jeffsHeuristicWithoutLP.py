import pulp
import numpy as np 
import string
from operator import itemgetter

#the cost from source node i to plant through node j
CostPerTon=np.load('/home/chamara/Dropbox/TRTech/Chamara/average_transport_costs_1280.npy')

#availability
availability = np.load('/home/chamara/Dropbox/TRTech/Chamara/storage_mass_1280.npy')
fixedCostStorage = 20000000  #79635 #cost of the telehandler
costForTotalAvail = [[CostPerTon[i][j]*availability[i] for j in range(10)] for i in range(10)]

sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]


#array representing storage selection
storageSel =  np.ones((len(costForTotalAvail),), dtype=np.int)
allocation = np.zeros((len(costForTotalAvail),len(costForTotalAvail),), dtype=np.int)
allocationDict = pulp.makeDict([sourceLabel,destLabel],allocation,0)
allocationDictTemp = allocationDict.copy()
#set having the tested sequences
testSet = set()
testSet.add(str(storageSel))


def flipBitsY(storageSelArray):
    testSet= set()
    storageSelArrayCopy = storageSelArray.copy()
    storeMeetCond = [storename for storename, used in storageSelArrayCopy.items() if used != 0]
    for key in storeMeetCond:
        storageSelArrayCopy = storageSelArray.copy()
        storageSelArrayCopy[key] = 0
        testSet.add(tuple(storageSelArrayCopy.items()))
    return testSet
  

def findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvailFunc,sourceLabel,destLabel,fixedCostStorage):
    
    prevTestSet = testSet.copy()
    testSet.clear()
    
    
    minSol = prevMinSol
    
    for testAllocation in prevTestSet:
        sol=0
        tempCostForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvailFunc,0)
        storageSelDict = dict(testAllocation)
        for source in sourceLabel:
            for dest in destLabel:
                if storageSelDict[dest]==0:
                    tempCostForTotalAvailDict[source][dest] = float('inf')
                
            minimum = min(tempCostForTotalAvailDict[source].items(), key=lambda x: x[1])
            sol+=minimum[1]
        sol+=sum(storageSelDict.values())*fixedCostStorage
        
        if prevMinSol>sol:
            testSet.add(testAllocation)
        if sol<minSol:
            minSol=sol
          
    return testSet, minSol 
        

prevMinSol = float('inf') #initial min value

maxits = 2000 # the maximum number of iterations

sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]

costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)

storageSelDict =  {dest:1 for dest in destLabel}
prevSelVec =  {dest:1 for dest in destLabel} # vector having the storage selection for the minimum cost upto now
#set having the tested sequences
prevTestSet = set()
testSet = set()
testSet.add(tuple(storageSelDict.items()))

newTestSet = set()
while len(testSet)>0:
    costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
    testSet,prevMinSol =  findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvail,sourceLabel,destLabel,fixedCostStorage)     
    if len(testSet)>0:
        prevTestSet = testSet.copy()
        testSet.clear()
        for item in prevTestSet:
            storageSelDict = dict(item)
            testSet.update(flipBitsY(storageSelDict))
        
        

minSol = prevMinSol

for testAllocation in prevTestSet:
    costForTotalAvailDictCopy = costForTotalAvailDict.copy()
    sol=0
    storageSelDict = dict(testAllocation)
    for source in sourceLabel:
        for dest in destLabel:
            if storageSelDict[dest]==0:
                costForTotalAvailDictCopy[source][dest] = float('inf')
            
        minimum = min(costForTotalAvailDictCopy[source].items(), key=lambda x: x[1])
        sol+=minimum[1]
        allocationDictTemp[source][minimum[0]] = 1
    sol+=sum(storageSelDict.values())*fixedCostStorage
    
    if prevMinSol>=sol:
        allocationDict = allocationDictTemp.copy()
        prevSelVec = storageSelDict.copy()
    
          

print 'Storages:',prevSelVec

print 'Assignment:'
for source in sourceLabel:
    print source,':' , allocationDict[source]
print 'optSolution:',prevMinSol
#print costForTotalAvailDict            
        

    

