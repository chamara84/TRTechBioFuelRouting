import numpy as np 
import string
import math
from datetime import datetime
import numpy
import random
import scipy.sparse
import scipy.optimize
import time
import csv
import pulp
import  subprocess as sp 
import re
import sys


demand=1000000

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


startTime = datetime.now()

      
      


#the cost from source node i to plant through node j
costPerTon=Cost[numpy.ix_(list(approximation_indices),keep_columns)]
#availability
availability =supply[numpy.ix_(list(approximation_indices))]

#cost of available load
costForTotalAvail = [[costPerTon[i][j]*availability[i] for j in range(len(keep_columns))] for i in range(len(availability))]
sourceLabel = [string.join(('s',str(index)),'_') for index in range(len(availability))]
destLabel =  [string.join(('d',str(index)),'_') for index in range(len(keep_columns))]
costForTotalAvailDict = pulp.makeDict([sourceLabel,destLabel],costForTotalAvail,0)
availabilityDict = pulp.makeDict([sourceLabel],availability,0)
allocationDict = dict()


        

sol=0
#source to dest mapping
x_ij =pulp.LpVariable.dicts("RoutePlant",(sourceLabel,destLabel),0,1,pulp.LpBinary)
#existance of storage j
y_j =pulp.LpVariable.dicts("Storage",destLabel,0,1,pulp.LpBinary)

prob = pulp.LpProblem("storage selection Problem",pulp.LpMinimize) 
prob+= pulp.lpSum([x_ij[i][j]*costForTotalAvailDict[i][j] for i in sourceLabel for j in destLabel])+ pulp.lpSum([y_j[j]*fixedCostStorage for j in destLabel])


    
for j in destLabel:
    for i in sourceLabel:
            prob+=x_ij[i][j] <= y_j[j]
for i in sourceLabel:
            prob+=pulp.lpSum([x_ij[i][j] for j in destLabel])<= 1
            
prob+=pulp.lpSum([availabilityDict[i]*x_ij[i][j] for i in sourceLabel for j in destLabel])>=demand
    

        
#prob.solve()
## The status of the solution is printed to the screen
#print "Status:", pulp.LpStatus[prob.status]
#sol = pulp.value(prob.objective)
## Each of the variables with it's resolved optimum value
#for v in prob.variables():
#        allocationDict[v.name] = v.varValue
#        
#
## The optimised objective function value 
prob.writeLP("IISD.lp")

file_= open("./output.txt", "w+")

#solve using symphony solver

p = sp.Popen(["symphony" , "-p", "4", "-L","IISD.lp"],stdout=file_,cwd='/home/chamara/Dropbox/TRTech/Chamara')
#file.close()

(out,err) = p.communicate()

file_.close()
sys.stdout = sys.__stdout__

print "time:",datetime.now() - startTime

  #file = open('/home/chamara/Dropbox/TRTech/output.txt', 'r')
file_ = open("/home/chamara/Dropbox/TRTech/Chamara/output.txt","r")
variables_all = file_.readlines() #variable containing sol

variables = [];
#print variables_all
for line in variables_all:
    if re.match("Optimal(\s+)|Route(.*)|Storage(.*)",line):
      #print line
      variables.append(line)
    elif re.match("Solution(.*)",line):
      print line
      variables.append(line)




with open('IISDoptWithFixedMILP.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in variables:
          out = re.split("\s+",v)
          #print out
          datawriter.writerow(out)
        
  
        
            
        

    

