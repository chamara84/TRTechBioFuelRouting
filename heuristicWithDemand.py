import pulp
import numpy as np 
import string
from operator import itemgetter

#the cost from source node i to plant through node j
CostPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')


demand = 80000        
        
fixedCostStorage =79635 #cost of the telehandler

costForTotalAvail = np.array([[CostPerTon[i][j] for j in range(5)] for i in range(5)])

sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(costForTotalAvail))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(costForTotalAvail))]



allocation = np.zeros((len(costForTotalAvail),len(costForTotalAvail),))
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
  

def findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvailFunc,fixedCostStorage,availability,demand):
    
    prevTestSet = testSet.copy()
    
    bestStorageAllocation= []
    bestSourceToDestAlloc = []
    minSol = prevMinSol
    
    for testAllocation in prevTestSet:
        sol=0
        allocation = np.zeros((len(costForTotalAvailFunc),len(costForTotalAvailFunc),))
        storageSelDict = np.array(testAllocation)
        minimumArg = []
        minimum = []
        usedStorages = np.nonzero(storageSelDict)[0].tolist()
        if np.sum(availability)> demand:
            for index in range(len(storageSelDict)):
                            
                if index not in usedStorages:
                    tempCostForTotalAvailDict = costForTotalAvailFunc[index][np.nonzero(storageSelDict)[0].tolist()]
                    minimum.append([np.amin(tempCostForTotalAvailDict),index]) #min cost and source
                    minimumArg.append(np.argmin(tempCostForTotalAvailDict))   #destination
                                    
                else:
                    minimum.append([costForTotalAvailFunc[index][index],index])#min cost and source
                    minimumArg.append(index)                                  #destination
                
            minimumDict = {minimumArg[index]:minimum[index] for index in range(len(storageSelDict))}
            minimumAscend = sorted(minimumDict.items(), key=lambda x:x[1][0])
            supply = 0
            entry = -1
                
            while supply< demand and entry < len(minimumAscend)-1:
                entry+=1
                
                supply+=availability[minimumAscend[entry][1][1]]
                
                if supply<demand:
                        sol+=availability[minimumAscend[entry][1][1]]*minimumAscend[entry][1][0]
                        allocation[minimumAscend[entry][1][1]][minimumAscend[entry][0]] = 1
                else:
                        allocation[minimumAscend[entry][1][1]][minimumAscend[entry][0]] =  (demand -(supply-availability[minimumAscend[entry][0]]))/availability[minimumAscend[entry][0]]  
                        sol+=availability[minimumAscend[entry][1][1]]*allocation[minimumAscend[entry][1][1]][minimumAscend[entry][0]]*minimumAscend[entry][1][0]

            sol+=sum(storageSelDict)*fixedCostStorage
        
            if prevMinSol>sol:
                bestStorageAllocation = storageSelDict.copy()
                bestSourceToDestAlloc = allocation.copy()
            if sol<minSol:
                minSol=sol
        else :
            print "not enough"
            sol = float('inf')
            minSol =prevMinSol
            continue
    return bestStorageAllocation, minSol,bestSourceToDestAlloc 


prevBestStorage = []

while len(testSet)>0:
    bestStorageAllocation,prevMinSol,bestSourceToDestAlloc =  findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvail,fixedCostStorage,availability,demand)     
    testSet.clear()
    if len(bestStorageAllocation)>0:
        prevBestStorage = bestStorageAllocation.copy()
        prevBestSourceToDest = bestSourceToDestAlloc.copy()
        testSet.update(flipBitsY(bestStorageAllocation))
        
sol=0

#For creating the output
#nonZeroAvailability =  np.nonzero(availability)[0].tolist()
#for index in range(len(prevBestStorage)):
#    if index in nonZeroAvailability:
#                
#                tempCostForTotalAvailDict = costForTotalAvail[index][np.nonzero(prevBestStorage)]
#                sol+=np.amin(tempCostForTotalAvailDict)
#                allocationDictTemp[sourceLabel[index]][destLabel[np.argmin(tempCostForTotalAvailDict)]] = 1
#    else:
#                prevBestStorage[index] =0
#            
#sol+=sum(prevBestStorage[nonZeroAvailability])*fixedCostStorage
#    
print 'Storages:',prevBestStorage

#print 'Assignment:'
#for source in sourceLabel:
#    print source,':' , allocationDictTemp[source]
print 'optSolution:',prevMinSol
#print costForTotalAvailDict            

        


        