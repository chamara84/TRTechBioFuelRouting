import pulp
import numpy as np 
import string
from operator import itemgetter

#the cost from source node i to plant through node j
CostPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')


        
        
fixedCostStorage =79635 #cost of the telehandler

costForTotalAvail = np.array([[CostPerTon[i][j]*availability[i] for j in range(len(CostPerTon))] for i in range(len(CostPerTon))])

sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]



allocation = np.zeros((len(costForTotalAvail),len(costForTotalAvail),), dtype=np.int)
allocationDict = pulp.makeDict([sourceLabel,destLabel],allocation,0)
allocationDictTemp = allocationDict.copy()
storageSel =  np.ones((len(costForTotalAvail),), dtype=np.int) #initial storage selection

#set having the tested sequences
testSet = set()
testSet.add(tuple(storageSel))

prevMinSol = float('inf') #initial min value

sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]



 
prevSelVec =  storageSel.copy() # vector having the storage selection for the minimum cost upto now
#set having the tested sequences
prevTestSet = set()


def flipBitsY(storageSelArray):
    testSet= set()
    storageSelArrayCopy = storageSelArray.copy()
    storeMeetCond = np.nonzero(storageSelArrayCopy)
    for index in storeMeetCond[0].tolist():
        storageSelArrayCopy = storageSelArray.copy()
        storageSelArrayCopy[index] = 0
        testSet.add(tuple(storageSelArrayCopy))
    return testSet
  

def findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvailFunc,fixedCostStorage,availability):
    
    prevTestSet = testSet.copy()
    
    bestStorageAllocation= []
    
    minSol = prevMinSol
    
    for testAllocation in prevTestSet:
        sol=0
        storageSelDict = np.array(testAllocation)
        nonZeroAvailability =  np.nonzero(availability)[0].tolist()
        
        for index in range(len(storageSelDict)):
            if index in nonZeroAvailability:
                tempCostForTotalAvailDict = costForTotalAvailFunc[index][np.nonzero(storageSelDict)[0].tolist()]
                minimum=np.amin(tempCostForTotalAvailDict)
                sol+=minimum
                
            else:
                storageSelDict[index] =0
            
        sol+=sum(storageSelDict[nonZeroAvailability])*fixedCostStorage
        
        if prevMinSol>sol:
           bestStorageAllocation = storageSelDict.copy()
        if sol<minSol:
            minSol=sol
        
    return bestStorageAllocation, minSol 


prevBestStorage = []

while len(testSet)>0:
    bestStorageAllocation,prevMinSol =  findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvail,fixedCostStorage,availability)     
    testSet.clear()
    if len(bestStorageAllocation)>0:
        prevBestStorage = bestStorageAllocation
        testSet.update(flipBitsY(bestStorageAllocation))
        
sol=0

#For creating the output
nonZeroAvailability =  np.nonzero(availability)[0].tolist()
for index in range(len(prevBestStorage)):
    if index in nonZeroAvailability:
                
                tempCostForTotalAvailDict = costForTotalAvail[index][np.nonzero(prevBestStorage)]
                sol+=np.amin(tempCostForTotalAvailDict)
                allocationDictTemp[sourceLabel[index]][destLabel[np.argmin(tempCostForTotalAvailDict)]] = 1
    else:
                prevBestStorage[index] =0
            
sol+=sum(prevBestStorage[nonZeroAvailability])*fixedCostStorage
    
print 'Storages:',prevBestStorage

#print 'Assignment:'
#for source in sourceLabel:
#    print source,':' , allocationDictTemp[source]
print 'optSolution:',sol
#print costForTotalAvailDict            

        


        