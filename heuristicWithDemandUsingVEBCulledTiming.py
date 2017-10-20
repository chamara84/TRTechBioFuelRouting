import numpy
import numpy as np
import random
import math
import scipy.sparse
import scipy.optimize
import time
import csv
import pulp
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import veb
#import heuristicWithDemandUsingVEBCulledVer2 as vebHeu
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

fixed_cost=16000
demandSplit = []
#demand=500000

supply_multiCrop=numpy.load('supply_mass_multiCrop_1280.npy')
harvest_cost_multiCrop=numpy.load('harvest_cost_multiCrop_1280.npy')
L1_distance_multiCrop=numpy.load('L1_distances_multiCrop_1280.npy')
highway_distance_multiCrop=numpy.load('highway_distances_multiCrop_1280.npy')
sink_nodes=numpy.load('sink_nodes_1280.npy')
source_nodes_multiCrop=numpy.load('source_nodes_multiCrop_1280.npy')



Cost_multiCrop=numpy.zeros(L1_distance_multiCrop.shape)
for j in range(L1_distance_multiCrop.shape[0]):
    for i in range(Cost_multiCrop.shape[1]):
        Cost_multiCrop[j,i,:]=harvest_cost_multiCrop[j,i]+L1_distance_multiCrop[j,i]/1000.*L1_weight+highway_distance_multiCrop/1000.*highway_weight
        #Cost[i]=L1_distance[i]/1000.*L1_weight+highway_distance/1000.*highway_weight #just transport

(num_crops,num_sources,num_sinks)=Cost_multiCrop.shape

def findAllocationForGivenActiveStorages(testSet,prevMinSol,prevYVec,costForTotalAvailAscend,fixedCostStorage,availability,demand,B_ij,treeArrayTemp,T_min):
    
    prevTestSet = testSet.copy()
    bestStorageAllocation= []
    bestSourceToDestAlloc = []
    minSol = prevMinSol
    rowChanged = np.ones(availability.shape)*-1
    for testAllocation in prevTestSet:
        sol=0
        rowChanged = []
        allocation = np.zeros((len(availability),len(testAllocation),))
        storageSelDict = np.array(testAllocation)
        columnsToRemove = np.where(storageSelDict==0)[0].tolist()
        columnsToRemove = np.where(storageSelDict==0)[0].tolist()
        columnsToRemoveOld = np.where(prevYVec==0)[0].tolist()
        columnsToRemove = list(set(columnsToRemove).difference(columnsToRemoveOld))
        B_ij_removed = B_ij[:,columnsToRemove]
        supply = 0
        if np.sum(availability)> demand:
            if B_ij_removed.shape[1] > 0:
                
                for row in range(len(availability)):
                  
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
                            pass
                            #print "supply:",supply
                else:
                        allocation[values[1]][values[2]] =  (demand -(supply-availability[values[1]]))/availability[values[1]] 
                        sol+=availability[values[1]]*allocation[values[1]][values[2]]*values[0]

            sol+=sum(storageSelDict)*fixedCostStorage
            #print "sol:", sol
            #print "yj:", storageSelDict  
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
    
    if len(bestStorageAllocation)>0:    
        columnsToRemove = np.where(bestStorageAllocation==0)[0].tolist()
        columnsToRemoveOld = np.where(prevYVec==0)[0].tolist()
        columnsToRemove = list(set(columnsToRemove).difference(columnsToRemoveOld))
        B_ij_removed = B_ij[:,columnsToRemove]
        supply = 0
        
        if B_ij_removed.shape[1] > 0:
                    
                    for row in range(len(availability)):
                    
                        min_row = int(min(B_ij_removed[row]))
                        if  (T_min.__contains__(min_row)):
                            T_min.discard(int(min(B_ij_removed[row])))
                            for removed in B_ij_removed[row]:
                                treeArrayTemp[row].discard(removed)
                            T_min.add(treeArrayTemp[row].min)
                        else:
                            for removed in B_ij_removed[row]:
                                treeArrayTemp[row].discard(removed)    
    #print "best alloc:",bestStorageAllocation       
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


iterations = 100;
demandPoints = 20;

x=numpy.zeros((1,demandPoints,))
yMILP=numpy.zeros((iterations,demandPoints,))
yvEB = numpy.zeros((iterations,demandPoints,))
for iteration in range(iterations):
    
    cropType = 0;
    Cost = Cost_multiCrop[cropType,:,:]
    supply=supply_multiCrop[cropType,:]
    keep_rows = numpy.where(supply>0)[0]
    source_nodes = source_nodes_multiCrop[cropType,:]
    harvest_cost=harvest_cost_multiCrop[cropType,:]
    highway_distance=highway_distance_multiCrop
    supply=supply[keep_rows]
    harvest_cost=harvest_cost[keep_rows]
    highway_distance=highway_distance[keep_rows]
    Cost=Cost[numpy.ix_(keep_rows,range(num_sinks))]
    (num_sources,num_sinks)=Cost.shape
    tups=[(min(Cost[i]),i) for i in range(num_sources)]
    tups.sort()
    source_node_order=[tup[1] for tup in tups]
    ordered_source_nodes=source_nodes[source_node_order]
    supply=supply[source_node_order]
    
    Cost1=Cost[numpy.ix_(source_node_order,range(num_sinks))]
    sink_node_order=[]
    for i in range(len(Cost1)):
        min_element=numpy.argmin(Cost1[i])
        sink_node_order+=[min_element]
    other_sink_nodes=list(set(range(len(sink_nodes))).difference(sink_node_order))
    other_sink_nodes.sort()
    sink_node_order+=other_sink_nodes
    ordered_sink_nodes=sink_nodes[sink_node_order]
    
    Cost2=[]
    for i in range(num_sources):
        Cost2+=[Cost1[i][sink_node_order]]
    Cost2=numpy.array(Cost2)
    Cost=Cost2                                           
    
    
    
    
    partial_order=numpy.zeros((num_sources,num_sources))
    Cmin=numpy.min(Cost,1)
    for i in range(num_sources):
        for j in range(num_sources):
            if (Cmin[i]-Cmin[j])*min(supply[j],supply[i])>=fixed_cost:
                partial_order[i,j]=1
                
    
    
   
    save_supply=supply
    for percent_harvested in [100]:
            
            supply=float(percent_harvested)/100*save_supply
            
            
            
            for demand in [i*20000 for i in range(1,demandPoints+1)]:
                if sum(supply)>=demand:
                    feasible_nodes=[i for i in range(num_sources) if numpy.dot(partial_order,supply)[i]<=demand]
                    possible_non_integral=[i for i in range(num_sources) if  i not in feasible_nodes]
                    if len(possible_non_integral)> 0:
                         max_supply=max([supply[i] for i in possible_non_integral])
                         cum_supply=numpy.cumsum([supply[i] for i in possible_non_integral])
                         num_required=min([i for i in range(len(possible_non_integral)) if cum_supply[i]>=max_supply])
                         approximation_indices=list(set(feasible_nodes).union(possible_non_integral[:num_required]))
                    else:
                        approximation_indices=feasible_nodes

                    
                
                
                    possible_sources_for_storage_node={}
                    for j in range(len(sink_nodes)):
                        possible_sources_for_storage_node[j]=[i for i in approximation_indices \
                                                        if (Cost[i,j]-Cmin[i])*supply[i]<fixed_cost]
                                                    
                        
                    column_dominance=numpy.zeros((num_sinks,num_sinks))
                    for i in range(num_sinks):
                        for j in range(num_sinks):
                            p_users=possible_sources_for_storage_node[j]
                            if all([Cost[k,i]<=Cost[k,j] for k in p_users]):
                                column_dominance[i,j]=1
                                
                    keep_columns=[]
                    for i in range(num_sinks):
                        if not any([column_dominance[k,i] for k in range(num_sinks) if not k==i]):
                            keep_columns+=[i]
                            
                    non_zero=[(i,j) for i in approximation_indices for j in keep_columns if (Cost[i,j]-Cmin[i])*supply[i]<fixed_cost]
                    
                    
                    
                    sinks=keep_columns
                    sources=approximation_indices
                    non_zero_node_pairs=[(i,j) for (i,j) in non_zero]
                    #insert the MILP and VEB heuristic
                    t1=time.time()
                    prob = pulp.LpProblem("MILP Problem", pulp.LpMinimize)
                    xvars=dict([((i,j),pulp.LpVariable("x_"+str(i)+'_'+str(j),0,1,"Binary")) \
                                for i in sources for j in sinks if (i,j) in non_zero_node_pairs])
                    yvars=dict([(j,pulp.LpVariable('y_'+str(j),0,1,cat="Binary")) for j in sinks])
                    C=dict([((i,j),Cost[i,j]) for i in approximation_indices for j in keep_columns \
                                if (i,j) in non_zero])
                    S=dict([(i,float(supply[i])) for i in approximation_indices])
                    D=demand
                    prob += pulp.lpSum([S[i]*C[(i,j)]*xvars[(i,j)] for (i,j) in non_zero_node_pairs])+pulp.lpSum([fixed_cost*yvars[i] \
                                                                                                                    for i in yvars])
                    for (i,j) in xvars:
                        prob+= xvars[(i,j)] - yvars[j] <=0
                    for i in sources:
                        prob += pulp.lpSum([xvars[(j,k)] for (j,k) in non_zero_node_pairs if j==i]) <= 1
                    prob += pulp.lpSum([S[i]*xvars[(i,j)] for (i,j) in non_zero_node_pairs]) >= D
                    #prob.writeLP("mylp.lp")
                    
                    prob.solve()
                    print 'MILP time',demand,time.time()-t1,pulp.value(prob.objective)
                    
                    x[0,demand/20000-1] = D
                    yMILP[iteration,demand/20000-1]=time.time()-t1
                    
 #####################             #vEB algorithm      ########################################
                    #the cost from source node i to plant through node j
                    t2 = time.time()
                    costPerTon=Cost[numpy.ix_(list(approximation_indices),keep_columns)]
                    #availability
                    availability =supply[numpy.ix_(list(approximation_indices))]
                    #availability = availability[range(5)]
                    #matrix having the index of the ordered C_ij
                    B_ij = numpy.zeros((len(availability),len(keep_columns),),dtype=numpy.int)
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
                        
                        
                    t2 = time.time()
                    probLP = pulp.LpProblem("LP Problem", pulp.LpMinimize)
                    xvarsLP=dict([((i,j),pulp.LpVariable("xLP_"+str(i)+'_'+str(j),0,1,"Continuous")) \
                                for i in sources for j in sinks if (i,j) in non_zero_node_pairs])
                    yvarsLP=dict([(j,pulp.LpVariable('yLP_'+str(j),0,1,"Continuous")) for j in sinks])
                    C=dict([((i,j),Cost[i,j]) for i in approximation_indices for j in keep_columns \
                                if (i,j) in non_zero])
                    S=dict([(i,float(supply[i])) for i in approximation_indices])
                    D=demand
                    probLP += pulp.lpSum([S[i]*C[(i,j)]*xvarsLP[(i,j)] for (i,j) in non_zero_node_pairs])+pulp.lpSum([fixed_cost*yvarsLP[i] \
                                                                                                                    for i in yvarsLP])
                    for (i,j) in xvars:
                        probLP+= xvarsLP[(i,j)] - yvarsLP[j] <=0
                    for i in sources:
                        probLP += pulp.lpSum([xvarsLP[(j,k)] for (j,k) in non_zero_node_pairs if j==i]) <= 1
                    probLP += pulp.lpSum([S[i]*xvarsLP[(i,j)] for (i,j) in non_zero_node_pairs]) >= D
                    #probLP.writeLP("mylp2.lp")
                    
                    probLP.solve()
                    
                    storageSel =  numpy.zeros((len(yvarsLP),), dtype=numpy.int) #initial storage selection    
                    for yLP in range(len(yvarsLP)):
                        if yvarsLP[yvarsLP.keys()[yLP]].varValue > 0.0:
                            storageSel[yLP] = 1
                        else:
                            storageSel[yLP] = 0
                        
                    #storageSel[list(approximation_indices)] = 1
                    #set having the tested sequences
                    testSet = set()
                    testSet.add(tuple(storageSel))
                    
                    prevMinSol = float('inf') #initial min value
                    prevSelVec =  storageSel.copy() # vector having the storage selection for the minimum cost upto now
                    #set having the tested sequences
                    prevTestSet = set()
                    
                    prevBestStorage = []

                    while len(testSet)>0:
                        bestStorageAllocation,prevMinSol,bestSourceToDestAlloc =  findAllocationForGivenActiveStorages(testSet,prevMinSol,prevBestStorage,costPerTonArrayAscend,fixed_cost,availability,demand,B_ij,treeArray,T_min)     
                        testSet.clear()
                        if len(bestStorageAllocation)>0 and sum(bestStorageAllocation)>1:
                            prevBestStorage = numpy.copy(bestStorageAllocation)
                            prevBestSourceToDest = numpy.copy(bestSourceToDestAlloc)
                            testSet.update(flipBitsY(prevBestStorage))
                            
                    sol=0
                    print "Vebtime:",demand,time.time() - t2,prevMinSol
                    yvEB[iteration,demand/20000-1]=time.time()-t2
 ################################################################################################
                    
                    #sinks=sink_nodes[keep_columns]
                    #sources=source_nodes[approximation_indices]
                    #non_zero_x=[(sources[i],j) for (i,j) in xvars if xvars[(i,j)].varValue>0]
                    #non_zero_y=[j for j in yvars if yvars[j].varValue>0]
                else:
                    print "Not enough"
                    break
                #numpy.save('source_nodes_1280_'+str(demand)+'.npy',source_nodes)
                #numpy.save('sink_nodes_1280_'+str(demand)+'.npy',sink_nodes)
                #numpy.save('non_zero_node_pairs_1280_'+str(demand)+'.npy',non_zero_node_pairs)

cropnames = numpy.load('cropTypes.npy')
cropnames = dict([(tup[1],tup[0]) for tup in tuple(cropnames)])  
plt.clf()

yMILPmean=numpy.mean(yMILP,axis=0)
yvEBmean=numpy.mean(yvEB,axis=0)


for p in [100]:
    plt.plot(x[0,:],yMILPmean,label='Time for MILP')
    plt.plot(x[0,:],yvEBmean,label='Time for vEB')
plt.title('Veb MILP time comparison')
plt.xlabel('Total Demand (Tons)')
plt.ylabel('Time taken in sec')
plt.legend(loc=2)
plt.savefig('Veb MILP time comparison'+str(iterations)+'.png')

#

