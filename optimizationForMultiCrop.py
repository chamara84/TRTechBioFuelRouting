import numpy
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


supply_multiCrop=numpy.load('supply_mass_multiCrop_1280.npy')
harvest_cost_multiCrop=numpy.load('harvest_cost_multiCrop_1280.npy')
L1_distance_multiCrop=numpy.load('L1_distances_multiCrop_1280.npy')
highway_distance_multiCrop=numpy.load('highway_distances_multiCrop_1280.npy')
sink_nodes=numpy.load('sink_nodes_1280.npy')
source_nodes_multiCrop=numpy.load('source_nodes_multiCrop_1280.npy')
cropnames = numpy.load('cropTypes.npy')
cropnames = dict([(tup[1],tup[0]) for tup in tuple(cropnames)])  

(num_crops,num_sources,num_sinks)=L1_distance_multiCrop.shape
Cost_multiCrop=numpy.ones((num_sources*num_crops,num_sinks))*float('inf')
supply=numpy.zeros((num_sources*num_crops,))
source_nodes=numpy.zeros((num_sources*num_crops,))


for j in range(L1_distance_multiCrop.shape[0]):
    for i in range(L1_distance_multiCrop.shape[1]):
        Cost_multiCrop[j*(num_sources)+i]=harvest_cost_multiCrop[j,i]+L1_distance_multiCrop[j,i]/1000.*L1_weight+highway_distance_multiCrop/1000.*highway_weight
    
    supply[j*(num_sources):(j+1)*(num_sources)]=supply_multiCrop[j]
    source_nodes[j*(num_sources):(j+1)*(num_sources)]=source_nodes_multiCrop[j]
    
(num_sources,num_sinks)=Cost_multiCrop.shape


Cost=Cost_multiCrop
   
    
keep_rows = numpy.where(supply>0)[0]
supply=supply[keep_rows]
#harvest_cost=harvest_cost[keep_rows]

#highway_distance=highway_distance[keep_rows]
Cost=Cost[numpy.ix_(keep_rows,range(num_sinks))]
(num_sources,num_sinks)=Cost.shape
tups=[(min(Cost[i]),i) for i in range(num_sources)]
tups.sort()
source_node_order=[tup[1] for tup in tups]
ordered_source_nodes=source_nodes[source_node_order]
supply=supply[source_node_order]

Cost=Cost[numpy.ix_(source_node_order,range(num_sinks))]
Cost1=Cost
sink_node_order=[]
for i in range(num_sinks):
        min_element=numpy.argmin(Cost1[i])
        sink_node_order+=[min_element]

ordered_sink_nodes=sink_nodes[sink_node_order]
    
Cost=Cost[numpy.ix_(range(num_sources),sink_node_order)]

    



partial_order=numpy.zeros((num_sources,num_sources))
Cmin=numpy.min(Cost,1)
for i in range(num_sources):
    for j in range(num_sources):
        if (Cmin[i]-Cmin[j])*min(supply[j],supply[i])>=fixed_cost:
            partial_order[i,j]=1
            


x={}
y={}
save_supply=supply
for percent_harvested in [100, 50, 25]:
        
        supply=float(percent_harvested)/100*save_supply
        x[percent_harvested]=[]
        y[percent_harvested]=[]
        step= 50000
        
        for demand in [i*step for i in range(1,21)]:
            if sum(supply)>=demand:
                feasible_nodes=[i for i in range(num_sources) if numpy.dot(partial_order,supply)[i]<demand]
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
            
                prob = pulp.LpProblem("Approximate Biomass Problem", pulp.LpMinimize)
                xvars=dict([((i,j),pulp.LpVariable("x_"+str(i)+'_'+str(j),0,1,"Continuous")) \
                            for i in sources for j in sinks if (i,j) in non_zero_node_pairs])
                yvars=dict([(j,pulp.LpVariable('y_'+str(j),0,1,cat="Continuous")) for j in sinks])
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
                prob.writeLP("mylp.lp")
                t1=time.time()
                prob.solve()
                print percent_harvested,demand,time.time()-t1,pulp.value(prob.objective)/D
                print len(sinks), len(sources)
                cost_per_ton=pulp.value(prob.objective)/D
                x[percent_harvested]+=[D]
                y[percent_harvested]+=[cost_per_ton]
                
                
                
                sinks=sink_nodes
                sources=source_nodes
                non_zero_x=[(sources[i],j) for (i,j) in xvars if xvars[(i,j)].varValue>0]
                non_zero_y=[j for j in yvars if yvars[j].varValue>0]
            else:
                print "Not enough"
                break
            #numpy.save('source_nodes_1280_'+str(demand)+'.npy',source_nodes)
            #numpy.save('sink_nodes_1280_'+str(demand)+'.npy',sink_nodes)
            #numpy.save('non_zero_node_pairs_1280_'+str(demand)+'.npy',non_zero_node_pairs)


plt.clf()

for p in [100,50,25]:
    plt.plot(x[p],y[p],label='percent harvested = '+str(p))
plt.title('Transport Cost of biomass mix per Ton at Plant Gate')
plt.xlabel('Total Demand (Tons)')
plt.ylabel('Cost in $/ton')
plt.legend(loc=4)
plt.savefig('Centreport Cost Estimates',format='pdf')
#

