import numpy as np 
import string
import veb
import math
from datetime import datetime

startTime = datetime.now()

demand = 800000        
      
fixedCostStorage =16000 #cost of the telehandler

#the cost from source node i to plant through node j
costPerTon=np.load('AverageCostPerTon.npy')

#availability
availability = np.load('Availabilty.npy')
#availability = availability[range(5)]
#matrix having the index of the ordered C_ij
B_ij = np.zeros((len(availability),len(availability),),dtype=np.int)
costPerTonArray = []
treeArray = []
for row in range(len(availability)):
    for col in range(len(availability)):
        costPerTonArray.append((costPerTon[row][col],row,col))
        
costPerTonArrayAscend = sorted(costPerTonArray,key=lambda x:x[0])

for itemNo in range(len(costPerTonArrayAscend)):
    
            B_ij[costPerTonArrayAscend[itemNo][1]][costPerTonArrayAscend[itemNo][2]] = itemNo

m = math.ceil(math.log(len(costPerTonArrayAscend),2))
            
for row in range(len(availability)):
    T = veb.vEBTree.of_size(pow(2,m))
    T.update(B_ij[row])
    treeArray.append(T) #list having the trees for each row having the indices of the ordered list of cost

T_min = veb.vEBTree.of_size(pow(2,m)) 

for row in range(len(availability)): #tree having the minimum of each row
    T_min.add(treeArray[row].min)

storageSel =  np.ones((len(availability),), dtype=np.int) #initial storage selection    
#storageSel = np.array([1,1,0,1,1])
#set having the tested sequences
testSet = set()
testSet.add(tuple(storageSel))

prevMinSol = float('inf') #initial min value
prevSelVec =  storageSel.copy() # vector having the storage selection for the minimum cost upto now
#set having the tested sequences
prevTestSet = set()

def findAllocationForGivenActiveStorages(testSet,prevMinSol,costForTotalAvailAscend,fixedCostStorage,availability,demand,B_ij,treeArrayTemp,T_min):
    
    prevTestSet = testSet.copy()
    bestStorageAllocation= []
    bestSourceToDestAlloc = []
    minSol = prevMinSol
    rowChanged = np.ones(availability.shape)*-1
    for testAllocation in prevTestSet:
        sol=0
        rowChanged = []
        allocation = np.zeros((len(availability),len(availability),))
        storageSelDict = np.array(testAllocation)
        columnsToRemove = np.where(storageSelDict==0)[0].tolist()
        B_ij_removed = B_ij[:,columnsToRemove]
        supply = 0
        if np.sum(availability)> demand:
            if B_ij_removed.shape[1] > 0:
                
                for row in range(len(storageSelDict)):
                
                    min_row = int(min(B_ij_removed[row]))
                    if  (T_min.__contains__(min_row)):
                        T_min.discard(int(min(B_ij_removed[row])))
                        for value in B_ij_removed[row]:
                            treeArrayTemp[row].discard(value)
                        T_min.add(treeArrayTemp[row].min)
                        rowChanged.append((min_row,treeArrayTemp[row].min))
                        for value in B_ij_removed[row]:
                            treeArrayTemp[row].add(value)
                        
                          
                
            entry = -1
            nextSmallest =int(T_min.min)     
            while supply< demand :
                entry+=1
                values = costForTotalAvailAscend[nextSmallest]
                
                    
                supply+=availability[values[1]]
                
                if supply<demand:
                        sol+=availability[values[1]]*values[0]
                        allocation[values[1]][values[2]] = 1
                        try:
                            nextSmallest =int(T_min.successor(nextSmallest))
                        except:
                            print "supply:",supply
                else:
                        allocation[values[1]][values[2]] =  (demand -(supply-availability[values[1]]))/availability[values[1]] 
                        sol+=availability[values[1]]*allocation[values[1]][values[2]]*values[0]

            sol+=sum(storageSelDict)*fixedCostStorage
            print "sol:", sol
            print "yj:", storageSelDict  
            for item in rowChanged:
                #creating the orginial tree having minimum of each row
                T_min.discard(int(item[1]))
                T_min.add(int(item[0]))
                
            
            if sol<minSol:
                minSol=sol
                bestStorageAllocation = np.copy(storageSelDict)
                bestSourceToDestAlloc = np.copy(allocation)
        else :
            print "not enough"
            sol = float('inf')
            minSol =prevMinSol
            continue
    print "best alloc:",bestStorageAllocation       
    return bestStorageAllocation, minSol,bestSourceToDestAlloc 
    
def flipBitsY(storageSelArray):
    testSet= set()
    storageSelArrayCopy = storageSelArray.copy()
    storeMeetCond = np.nonzero(storageSelArrayCopy)
    for index in storeMeetCond[0].tolist():
        storageSelArrayCopy = storageSelArray.copy()
        storageSelArrayCopy[index] = 0
        testSet.add(tuple(storageSelArrayCopy))
    return testSet
    
prevBestStorage = []

while len(testSet)>0:
    bestStorageAllocation,prevMinSol,bestSourceToDestAlloc =  findAllocationForGivenActiveStorages(testSet,prevMinSol,costPerTonArrayAscend,fixedCostStorage,availability,demand,B_ij,treeArray,T_min)     
    testSet.clear()
    if len(bestStorageAllocation)>0:
        prevBestStorage = np.copy(bestStorageAllocation)
        prevBestSourceToDest = np.copy(bestSourceToDestAlloc)
        testSet.update(flipBitsY(prevBestStorage))
        
sol=0
print "time:",datetime.now() - startTime
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


    