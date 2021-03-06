import numpy as np 
import string
import veb
import math
from datetime import datetime
import numpy
import random
import scipy.sparse
import scipy.optimize
import time
import csv


demand=80000

speed_stinger = 25 #km/h
#travel efficiency of stinger
E_stinger = 0.7 # can be [0.7,0.8,0.9]
#cost of stinger
C_stinger= 77.67 #$ per hour
#DML of bailer
theta_baler = 0.0
#load mass of stinger
LoadMass_stinger = 4 #assuming 8 bale stinger and 0.5t per bale
#DML of stinger from table 4-2 of thesis
theta_stinger = 0.0084
#DML storage
theta_storage = 0.07
#DML telehandler
theta_loader = 0.0091
#DML truck
theta_truck = 0.0089
#Cost of trailer
C_trailer = 23.39 #$/hour
#cost of truck
C_truck = 97.90 #$/hour
#efficiency truck
E_truck = 0.75 # can be [0.75,0.85,0.95]
#loadmass truck
LoadMass_truck = 15 # 30 bale truck
#speed of truck
speed_truck = 80 #km/h

Amount_transported_to_Storage =1

L1_weight=(2/(speed_stinger*E_stinger)*(1-theta_baler)*C_stinger/LoadMass_stinger + \
2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger)*(1-theta_baler)*(1-theta_stinger)*\
theta_storage)+ (theta_loader*2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger) + (1-theta_loader)*theta_truck*2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger)\
) 

 
highway_weight=2*(C_trailer+C_truck)/(speed_truck*E_truck*LoadMass_truck)

fixedCostStorage =16000 #cost of the telehandler

supply=numpy.load('storage_mass_1280.npy')
harvest_cost=numpy.load('harvest_cost_1280.npy')
L1_distance=numpy.load('average_L1_distances_1280.npy')
highway_distance=numpy.load('highway_distances_1280.npy')

lines=list(csv.reader(open('culled_storage_points.csv')))[1:]
storage_nodes=numpy.array([int(line[0]) for line in lines])



Cost=numpy.zeros(L1_distance.shape)
for i in range(len(Cost)):
    Cost[i]=L1_distance[i]/1000.*L1_weight+highway_distance/1000.*highway_weight
keep_rows=[i for i in range(len(Cost)) if not any(numpy.isnan(Cost[i]))]
storage_nodes=storage_nodes[keep_rows]
supply=supply[keep_rows]
harvest_cost=harvest_cost[keep_rows]
highway_distance=highway_distance[keep_rows]
Cost=Cost[numpy.ix_(keep_rows,keep_rows)]
tups=[(Cost[i,i],i) for i in range(len(Cost))]
tups.sort()
node_order=[tup[1] for tup in tups]
storage_nodes=storage_nodes[node_order]
Cost=Cost[numpy.ix_(node_order,node_order)]
supply=supply[node_order]
highway_distance=highway_distance[node_order]
harvest_cost=harvest_cost[node_order]
C=[Cost[i,i] for i in range(len(Cost))]
Hcost=highway_distance/1000.*highway_weight
alternates=[]
count=0
for i in range(len(Cost)):
    alternates+=[[j for j in range(len(Cost)) if not j==i and supply[i]*(Cost[i,j]-Cost[i,i])<fixedCostStorage]]
diag=[i for i in range(len(Cost)) if len(alternates[i])==0]    
    


cumsupply=numpy.cumsum(supply)
last_node=min([i for i in range(len(supply)) if cumsupply[i]>demand])
partial_order=numpy.zeros(Cost.shape)

for i in range(len(Cost)):
    for j in range(len(Cost)):
        
        if (C[i]-C[j])*min(supply[j],supply[i])>=fixedCostStorage:
            partial_order[i,j]=1
            
feasible_nodes=[]
for i in range(len(C)):
    pos_nodes=[j for j in range(len(C)) if partial_order[i,j]]+[i]
    max_supply=max([supply[j] for j in pos_nodes])
    min_supply=sum(supply[pos_nodes])-max_supply
    if min_supply<=demand:
        feasible_nodes+=[i]


feasible_nodes=[i for i in range(len(C)) if numpy.dot(partial_order,supply)[i]<=demand]
feasible_supply=list(supply[feasible_nodes])
feasible_supply.sort()
feasible_supply.reverse()
discard_nodes=[]
for node in feasible_nodes:
    req=[i for i in range(len(C)) if partial_order[node,i]==1]
    if len(set(req).difference(feasible_nodes))>0:
        discard_nodes+=[node]
feasible_nodes=set(feasible_nodes).difference(discard_nodes)


possible_non_integral=[i for i in range(len(Cost)) if not i in feasible_nodes]

max_supply=max([supply[i] for i in possible_non_integral])
cum_supply=numpy.cumsum([supply[i] for i in possible_non_integral])
num_required=min([i for i in range(len(possible_non_integral)) if cum_supply[i]>max_supply])
approximation_indices=feasible_nodes.union(possible_non_integral[:num_required])


possible_users={}
for j in range(len(Cost)):
    possible_users[j]=[i for i in approximation_indices if (Cost[i,j]-Cost[i,i])*supply[i]<fixedCostStorage]
    
column_dominance=numpy.zeros(Cost.shape)
for i in range(len(Cost)):
    for j in range(len(Cost)):
        p_users=possible_users[j]
        if all([Cost[k,i]<=Cost[k,j] for k in p_users]):
            column_dominance[i,j]=1
            
keep_columns=[]
for i in set(range(len(Cost))):
    if not any([column_dominance[k,i] for k in range(len(Cost)) if not k==i]):
        keep_columns+=[i]
        
non_zero=[(i,j) for i in approximation_indices for j in keep_columns if (Cost[i,j]-Cost[i,i])*supply[i]<fixedCostStorage]

source_nodes=storage_nodes[list(approximation_indices)]
sink_nodes=storage_nodes[keep_columns]
non_zero_node_pairs=[(storage_nodes[i],storage_nodes[j]) for (i,j) in non_zero]




      


#the cost from source node i to plant through node j
costPerTon=Cost[numpy.ix_(list(approximation_indices),keep_columns)]
#availability
availability =supply[numpy.ix_(list(approximation_indices))]
#availability = availability[range(5)]
#matrix having the index of the ordered C_ij
B_ij = np.zeros((len(availability),len(keep_columns),),dtype=np.int)
costPerTonArray = []
treeArray = []
for row in range(len(availability)):
    for col in range(len(keep_columns)):
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
startTime = datetime.now()
storageSel =  np.ones((len(keep_columns),), dtype=np.int) #initial storage selection    
#storageSel[list(approximation_indices)] = 1
#set having the tested sequences
testSet = storageSel
#testSet.add(tuple(storageSel))

prevMinSol = float('inf') #initial min value
prevSelVec =  storageSel.copy() # vector having the storage selection for the minimum cost upto now
#set having the tested sequences
prevTestSet = set()

def findAllocationForGivenActiveStorages(testSet,prevMinSol,prevYVec,prevBestSourceToDest,costForTotalAvailAscend,fixedCostStorage,availability,demand,B_ij,treeArrayTemp,T_min):
    
    prevTestSet = np.copy(testSet)
    bestStorageAllocation= []
    bestSourceToDestAlloc = []  
    prevBestSourceToDest = np.array(list(prevBestSourceToDest))
    minSol = prevMinSol
    rowChanged = np.ones(availability.shape)*-1
    if len(prevTestSet.shape) == 1:
        numRows = 1
    else:
        numRows = prevTestSet.shape[0] 
    for index in range(numRows):
        if prevMinSol<float('inf'):
            sol=prevMinSol
            supply = demand
        else:
            sol = 0
            supply = 0
            
        rowChanged = []
        fractionalAllocIndex = float('inf')
        allocation = np.array(prevBestSourceToDest.copy())
        if numRows ==1:
            storageSelDict = prevTestSet
        else:
            storageSelDict = prevTestSet[index,:]
            
        columnsToRemove = np.where(storageSelDict==0)[0].tolist()
        columnsToRemoveOld = np.where(prevYVec==0)[0].tolist()
        columnsToRemove = list(set(columnsToRemove).difference(columnsToRemoveOld))
        
        B_ij_removed = B_ij[:,columnsToRemove]
       
        if np.sum(availability)> demand:
            if B_ij_removed.shape[1] > 0:
                
                for row in range(len(availability)):
                    rowMax = max(allocation[row,:])
                    min_row = int(B_ij_removed[row])
                    column = columnsToRemove
                    if  (T_min.__contains__(min_row)):
                        nextBest = T_min.successor(min_row)
                        T_min.discard(min_row)
                        prevTransVal = costForTotalAvailAscend[min_row][0]*prevBestSourceToDest[row,column]*availability[row]
                        allocation[row,column] = 0
                        supply-=availability[row]
                        sol-=prevTransVal
                        treeArrayTemp[row].discard(B_ij_removed[row])
                        T_min.add(treeArrayTemp[row].min)
                        rowChanged.append((min_row,treeArrayTemp[row].min,nextBest,))
                        treeArrayTemp[row].add(B_ij_removed[row])
                        
                    elif  rowMax>0 and rowMax< 1:
                         fractionalAllocIndex = treeArrayTemp[row].min
                         column = np.where(B_ij[row,:]==treeArrayTemp[row].min)
                         rowChanged.append((-1,-1,fractionalAllocIndex,))
                         prevTransVal = costForTotalAvailAscend[int(treeArrayTemp[row].min)][0]*prevBestSourceToDest[row,column]*availability[row]
                         allocation[row,column] = 0
                         supply-=availability[row]
                         sol-=prevTransVal[0]
            entry = -1              
            if len(rowChanged)>0:
                    
                
                removedItemsSorted = sorted(rowChanged, key= lambda x:x[2])
                try:
                    
                    if int(removedItemsSorted[0][2])<fractionalAllocIndex:
                        nextSmallest =int(removedItemsSorted[0][2]) 
                    else:
                        nextSmallest=fractionalAllocIndex
                except:
                    if fractionalAllocIndex < float('inf'):
                        nextSmallest=fractionalAllocIndex  
                    else:
                         nextSmallest=T_min.min
            else:
                nextSmallest=T_min.min
                
            while supply< demand :
                
                entry+=1
                values = costForTotalAvailAscend[int(nextSmallest)]
                
                if allocation[values[1]][values[2]] < 1: 
                    supply+=availability[values[1]]
                
                    if supply<demand:
                            sol+=availability[values[1]]*values[0]
                            allocation[values[1]][values[2]] = 1
                            
                    else:
                            allocation[values[1]][values[2]] =  (demand -(supply-availability[values[1]]))/availability[values[1]] 
                            sol+=availability[values[1]]*allocation[values[1]][values[2]]*values[0]
                try:
                    nextSmallest =int(T_min.successor(nextSmallest))
                except:
                            
                    print "supply:",supply        
                        
            if prevMinSol< float('inf'):
                sol-=fixedCostStorage
            else:
                sol+=fixedCostStorage*sum(storageSelDict)
            print "sol:", sol
            print "yj:", storageSelDict  
            for item in rowChanged:
                #creating the orginial tree having minimum of each row
                if item[0]>=0:
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
            
    if len(bestStorageAllocation)>0:    
        columnsToRemove = np.where(bestStorageAllocation==0)[0].tolist()
        columnsToRemoveOld = np.where(prevYVec==0)[0].tolist()
        columnsToRemove = list(set(columnsToRemove).difference(columnsToRemoveOld))
        B_ij_removed = B_ij[:,columnsToRemove]
        supply = 0
        
        if B_ij_removed.shape[1] > 0:
                    
                    for row in range(len(availability)):
                    
                        min_row = int(B_ij_removed[row])
                        if  (T_min.__contains__(min_row)):
                            T_min.discard(int(min(B_ij_removed[row])))
                            treeArrayTemp[row].discard(B_ij_removed[row])
                            T_min.add(treeArrayTemp[row].min)
                        else:
                            treeArrayTemp[row].discard(B_ij_removed[row])
                        
    print "best alloc:",bestStorageAllocation       
    return bestStorageAllocation, minSol,bestSourceToDestAlloc 
    
def flipBitsY(storageSelArray):
   
    #storageSelArrayCopy = storageSelArray.copy()
    #storeMeetCond = np.nonzero(storageSelArray)
    zeroCols = np.where(storageSelArray==0)
    numNonZeroCols = int(len(storageSelArray)-len(zeroCols[0]))
    matNonZero = np.ones((numNonZeroCols,numNonZeroCols,),dtype=np.int)-np.eye(numNonZeroCols,dtype=np.int)
    for index in zeroCols[0]:
        if index!=0 and index!=matNonZero.shape[0]-1:
            matNonZero = np.c_[matNonZero[:,:index],np.zeros(numNonZeroCols),matNonZero[:,index:]]
        elif index==0:
            matNonZero = np.c_[np.zeros(numNonZeroCols),matNonZero]
        else:
            matNonZero = np.c_[matNonZero, np.zeros(numNonZeroCols)]
            
            
    
    return matNonZero
    
prevBestStorage = []
prevBestSourceToDest= np.zeros((len(availability),len(keep_columns),))
while len(testSet)>0:
    bestStorageAllocation,prevMinSol,bestSourceToDestAlloc =  findAllocationForGivenActiveStorages(testSet,prevMinSol,prevBestStorage,prevBestSourceToDest,costPerTonArrayAscend,fixedCostStorage,availability,demand,B_ij,treeArray,T_min)     
    testSet =[]
    if len(bestStorageAllocation)>0:
        prevBestStorage = np.copy(bestStorageAllocation)
        prevBestSourceToDest = np.copy(bestSourceToDestAlloc)
        
        testSet=flipBitsY(prevBestStorage)
        print "time:",datetime.now() - startTime
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


    