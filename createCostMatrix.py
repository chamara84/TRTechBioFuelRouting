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
import DMLcostEstimates as dml

speed_stinger = 25 #km/h
#travel efficiency of stinger
E_stinger = 0.9 # can be [0.7,0.8,0.9]
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

L1_weight=2/(speed_stinger*E_stinger)*C_stinger/LoadMass_stinger #+ \
#2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger)*(1-theta_baler)*(1-theta_stinger)*\
#theta_storage)+ (theta_loader*2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger) + (1-theta_loader)*theta_truck*2*C_stinger/(speed_stinger*E_stinger*LoadMass_stinger)) 

 
highway_weight=2*(C_trailer+C_truck)/(speed_truck*E_truck*LoadMass_truck)*(1-theta_stinger)*(1-theta_loader)

fixed_cost=16000
demandSplit = []
demand=500000



def costDMLL1Transport(P_k, D_FS_ij, bioMassType, source):
    parameter = dml.parameterStruct()
    num_stores=D_FS_ij.shape[0]
    costPerTon=np.zeros((num_stores*len(parameter.theta_storage),))
    costPerTon=np.repeat(parameter.theta_stinger*(P_k),num_stores*len(parameter.theta_storage))
    return costPerTon




#cost per ton of DML at storage
def costDMLStorage(P_k,D_FS_ij,bioMassType,source):
    #can replace D_FS_ij with the average _L1_distance for each storage as an approximation for given biomass type
    #P_k is the price vector of biomass type k
    #D_FS_ij is the distance matrix from each farm to the storages
    parameter = dml.parameterStruct()
    num_stores=D_FS_ij.shape[0]
    costPerTon=np.zeros((num_stores*len(parameter.theta_storage),))
    for k in range(len(parameter.theta_storage)*num_stores):
        
        costPerTon[k] = (1-parameter.theta_stinger)*parameter.theta_storage[int(math.fmod(k,len(parameter.theta_storage)))]*((P_k \
        +parameter.C_stinger/parameter.BaleMass*parameter.L_stinger/parameter.E_stinger_load+parameter.U_stinger/parameter.E_stinger_unload) \
        +2*parameter.C_stinger*D_FS_ij[int(math.floor(k/len(parameter.theta_storage)))]/(parameter.speed_stinger*parameter.E_stinger*parameter.LoadMass_stinger))
        
    return costPerTon
    
#cost of DML at the storage when loading to trucks    
def costDMLLoading(P_k,D_FS_ij,bioMassType,source):
    #can replace D_FS_ij with the average _L1_distance for each storage as an approximation
    #P_k is the price vector of biomass type k
    #D_FS_ij is the distance matrix from each farm to the storages
    #assume that even though there is dry matter loss the amount pulled from farms are approxmately equal to amount purshed towards plant
    parameter = dml.parameterStruct()
    num_stores=D_FS_ij.shape[0]
    costPerTon=np.zeros((num_stores*len(parameter.theta_storage),))
    for k in range(len(parameter.theta_storage)*num_stores):
            costPerTon[k]=(1-parameter.theta_stinger)*(1-parameter.theta_storage[int(math.fmod(k,len(parameter.theta_storage)))])*parameter.theta_loader*(P_k \
                +parameter.C_stinger*(parameter.L_stinger/parameter.E_stinger_load+parameter.U_stinger/parameter.E_stinger_unload)/parameter.BaleMass \
                +2*parameter.C_stinger*D_FS_ij[int(math.floor(k/len(parameter.theta_storage)))]/(parameter.speed_stinger*parameter.E_stinger*parameter.LoadMass_stinger)+parameter.C_storage[int(math.fmod(k,len(parameter.theta_storage)))]) 
    return costPerTon

    
        
#cost of DML when transporting from storage to plant                
def costDMLRoadTransport(P_k,D_FS_ij,bioMassType,source):
    #can replace D_FS_ij with the average_L1_distance for each storage as an approximation
    #P_k is the price vector of biomass type k (harvest cost)
    #D_FS_ij is the distance matrix from each farm to the storages
    #assume that even though there is dry matter loss the amount pulled from farms are approxmately equal to amount purshed towards plant
    parameter = dml.parameterStruct()
    num_stores=D_FS_ij.shape[0]
    costPerTon=np.zeros((num_stores*len(parameter.theta_storage),))
    for k in range(len(parameter.theta_storage)*num_stores):
            
            costPerTon[k]=(1-parameter.theta_stinger)*(1-parameter.theta_storage[int(math.fmod(k,len(parameter.theta_storage)))])*(1-parameter.theta_loader)*parameter.theta_truck*(P_k \
               +parameter.C_twine/parameter.BaleMass+(parameter.L_stinger/parameter.E_stinger_load+parameter.U_stinger/parameter.E_stinger_unload)/parameter.BaleMass \
               +2*parameter.C_stinger*D_FS_ij[int(math.floor(k/len(parameter.theta_storage)))]/(parameter.speed_stinger*parameter.E_stinger*parameter.LoadMass_stinger)+parameter.C_storage[int(math.fmod(k,len(parameter.theta_storage)))] \
               +parameter.L_loader*parameter.C_V_loader/(parameter.LoadMass_loader*parameter.E_loader))
               
    return costPerTon
    

supply_multiCrop=numpy.load('supply_mass_multiCrop_1280.npy')
harvest_cost_multiCrop=numpy.load('harvest_cost_multiCrop_1280.npy')
L1_distance_multiCrop=numpy.load('L1_distances_multiCrop_1280.npy')
highway_distance_multiCrop=numpy.load('highway_distances_multiCrop_1280.npy')
sink_nodes=numpy.load('sink_nodes_1280.npy')
source_nodes_multiCrop=numpy.load('source_nodes_multiCrop_1280.npy')
parameters = dml.parameterStruct()
numStorageTypes = len(parameters.C_storage)

(cropTypes,sources,dest) = L1_distance_multiCrop.shape
Cost_multiCrop=numpy.zeros((cropTypes,sources,dest*numStorageTypes,))
Cost_multiCropL1=numpy.zeros((cropTypes,sources,dest*numStorageTypes,))
Cost_multiCropStorage=numpy.zeros((cropTypes,sources,dest*numStorageTypes,))
Cost_multiCropLoad=numpy.zeros((cropTypes,sources,dest*numStorageTypes,))
Cost_multiCropTransport=numpy.zeros((cropTypes,sources,dest*numStorageTypes,))
for j in range(L1_distance_multiCrop.shape[0]):
    
    for i in range(Cost_multiCrop.shape[1]):
        costForGivenBioSource = harvest_cost_multiCrop[j,i]+L1_distance_multiCrop[j,i,:]/1000.*L1_weight+highway_distance_multiCrop/1000.*highway_weight
        Cost_multiCrop[j,i,:]=numpy.repeat(costForGivenBioSource,numStorageTypes)
        
        if harvest_cost_multiCrop[j,i]<float('inf'):
            
            Cost_multiCropL1[j,i,:]=costDMLL1Transport(harvest_cost_multiCrop[j,i], L1_distance_multiCrop[j,i,:]/1000, j, i) #DML of L1 transport
            Cost_multiCropStorage[j,i,:]=costDMLStorage(harvest_cost_multiCrop[j,i],L1_distance_multiCrop[j,i,:]/1000,j,i)
            Cost_multiCropLoad[j,i,:]=costDMLLoading(harvest_cost_multiCrop[j,i],L1_distance_multiCrop[j,i,:]/1000,j,i)
            Cost_multiCropTransport[j,i,:]=costDMLRoadTransport(harvest_cost_multiCrop[j,i],L1_distance_multiCrop[j,i,:]/1000,j,i)
        #Cost[i]=L1_distance[i]/1000.*L1_weight+highway_distance/1000.*highway_weight #just transport


np.save('Cost_multicrop',Cost_multiCrop)
np.save('Cost_multicrop_L1_DML',Cost_multiCropL1)
np.save('Cost_multicrop_storage_DML',Cost_multiCropStorage)
np.save('Cost_multicrop_Load_DML',Cost_multiCropLoad)
np.save('Cost_multicrop_Transport_DML',Cost_multiCropTransport)

CostMultiCropTotal= Cost_multiCrop+Cost_multiCropL1+Cost_multiCropStorage+Cost_multiCropLoad+Cost_multiCropTransport
DMLCostMultiCrop = Cost_multiCropL1+Cost_multiCropStorage+Cost_multiCropLoad+Cost_multiCropTransport

np.save('Cost_multicrop_with_DML',CostMultiCropTotal)
np.save('DML_Cost_multicrop',DMLCostMultiCrop)

