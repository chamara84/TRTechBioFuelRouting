import numpy
import random
import math
import scipy.sparse
import scipy.optimize
import time
import csv

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
    alternates+=[[j for j in range(len(Cost)) if not j==i and supply[i]*(Cost[i,j]-Cost[i,i])<fixed_cost]]
diag=[i for i in range(len(Cost)) if len(alternates[i])==0]    
    

demand=532510.55347270658
cumsupply=numpy.cumsum(supply)
last_node=min([i for i in range(len(supply)) if cumsupply[i]>demand])
partial_order=numpy.zeros(Cost.shape)

for i in range(len(Cost)):
    for j in range(len(Cost)):
        
        if (C[i]-C[j])*min(supply[j],supply[i])>=fixed_cost:
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
    possible_users[j]=[i for i in approximation_indices if (Cost[i,j]-Cost[i,i])*supply[i]<fixed_cost]
    
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
        
non_zero=[(i,j) for i in approximation_indices for j in keep_columns if (Cost[i,j]-Cost[i,i])*supply[i]<fixed_cost]

source_nodes=storage_nodes[approximation_indices]
sink_nodes=storage_nodes[keep_columns]
non_zero_node_pairs=[(storage_nodes[i],storage_nodes[j]) for (i,j) in non_zero]

numpy.save('source_nodes_1280.npy',source_nodes)
numpy.save('sink_nodes_1280.npy',sink_nodes)
numpy.save('non_zero_node_pairs_1280.npy',non_zero_node_pairs)
