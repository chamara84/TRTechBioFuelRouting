#optimization problem of IISD as in Mahmood Thesis
from pulp import *
#from random import *
import string
import numpy as np
import numpy.matlib
import csv
import  subprocess as sp 
import re
import sys
import math

#Parameters
#number of farms
numFarms = 144
#number of crop types
numCrops = 1

#number of contract years
years = 1
#annual feed stock
A = 70000 #27375 # in tonnes

#balemass
BaleMass =0.442  #in tonnes

#capasity of baler
CAP_baler = 38 #bale/h

#road side storages
storages = []
#farms 
farms =  []  

for i in range(numFarms):
   farms.append(string.join(("f",str(i)),"_"))





#cost of baler
C_baler = 89.92 #$ per hour

#cost of twine per bale
C_twine = 0.8 #$ per bale

#cost of tractor
C_tractor = 93.67 #$ per hour

#cost of stinger
C_stinger= 77.67 #$ per hour

#cost of storage

# what should it include the ammortized construction cost depending on the type of storage and amount of yield and land value
#assume average tonnes per farm is 400 then according to fire regulations area needed and reusable tarp on crushed rock are used and cost divided equally amoung 5 years land cost not included 
C_storage = 5.86 #$/ t-year

minDistBetSatStores = 1000 #the minimum x dir or y dir distance between satellite stores in m

#fixed cost of telehandler
C_F_loader = 214500 #3895.5 #$/year

#variable cost of telehandler
C_V_loader = 47.25 #$/hour


#Cost of trailer
C_trailer = 23.39 #$/hour

#cost of truck
C_truck = 97.90 #$/hour



def empty(x, y):
    return x*0


store_coordinates_raw  = []
with open('/home/chamara/Dropbox/TRTech/Chamara/culled_storage_points.csv', 'rb') as csvfile:
    satStorePosRead = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(satStorePosRead, None)
    for row in  satStorePosRead:
      store_coordinates_raw.append( [string.join(("s",str(row[0])),"_"),[float(row[1]),float(row[2])]])
csvfile.close()

store_coordinates_raw = dict(store_coordinates_raw)
#satellite storages
satelliteStores = dict()
minSatStorages = 1 #minimum number of satellite storages

expand = 0; 
#while len(satelliteStores)<= minSatStorages:
#    
#    matchingStores = [row for  row in store_coordinates_raw if (row[1]<=622460.662+800*expand) and (row[1]>=612499.088-800*expand) and (row[2]<=5438669.66+800*expand) and (row[2]>=5428689.42-800*expand)]
#    for row in matchingStores:
#           store_coordinates_raw.remove(row)
#           #print "in township"
#           satelliteStores[string.join(("s",str(row[0])),"_")]=[row[1],row[2]]
#           
#              
#           
#                             #print row,len(satelliteStores) 
#    expand+=1
#    
#    
#numSatStores = len(satelliteStores)
satelliteStores[string.join(("s",str(150)),"_")]=[store_coordinates_raw['s_150'][0],store_coordinates_raw['s_150'][1]]
numSatStores = len(satelliteStores)
print "Selected Sat stores",[store for store in  satelliteStores]



#maximum capacity of satellite storage

storeCap = [] # generate randomly 
for index in range(numSatStores):
  storeCap.append(np.random.randint(30000,40000))

for store in  satelliteStores:
   storages.append(store)

capacity_storage = makeDict([storages],storeCap,0)


#Distance_ij_raw[0]  = []       
#Distance_ij = [float(Distance_ij_raw[row][col])+0.8 for row in range(numFarms) for col in range(numFarms)]




#distance between farm i and storage j
Distance_storage = dict()

with open('/home/chamara/Dropbox/TRTech/Chamara/RoadSideStorage.csv', 'rb') as csvfile:
    DistStoragereader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(DistStoragereader, None)
    for row in  DistStoragereader:
      Distance_storage[string.join(("f",str(row[0])),"_")] = [float(entry) for entry in  row[1:5]]
csvfile.close()
   
yieldBioMFarm =  [[Distance_storage[dist][3]] for dist in Distance_storage]
#Distance_storage = [dist[2] for dist in Distance_storage[0:numFarms]]
Distance_ij  = dict()

Distance_ij  = {farm: {storage:abs(Distance_storage[farm][0]-satelliteStores[storage][0])+abs(Distance_storage[farm][1]-satelliteStores[storage][1]) for storage in satelliteStores}for farm in Distance_storage }  


D_FS_ij = Distance_ij 

print "Distance From farm to store"
#assume plant to be at the first sat storage
#find the satellite store distance to plant from the file using ID.

DistSatToPlantAll = dict()
csvfile = open('/home/chamara/Dropbox/TRTech/Chamara/culled_storage_points_shortest_path_distances.csv', 'rb')
DistStorageToPlantreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
headers = next(DistStorageToPlantreader, None)
DistSatToPlantAll = {(string.join(("s",str(row[0])),"_"),string.join(("s",str(row[1])),"_")):float(row[2]) for row in  DistStorageToPlantreader}
    
            
plantID = string.join(("s",str(1409)),"_")  #node 1409
DistSatToPlantSel = dict()
for source in satelliteStores:
    DistSatToPlantSel[source] = DistSatToPlantAll[(source,plantID)]
              
#store_distances_dict  = dict()
#with open('/home/chamara/Dropbox/TRTech/Chamara/highway_distances.csv', 'rb') as csvfile:
#    satStoreDistRead = csv.reader(csvfile, delimiter=',', quotechar='|')
#    headers = next(satStoreDistRead, None)
#    for row in satStoreDistRead:
#      try:
#       store_distances_dict[(int(row[1]),int(row[2]))] = float(row[5])
#      except:
#        pass
       # print "error",row[5]
    







D_S_j = DistSatToPlantSel

#efficiency of baler
E_baler = 0.7 #can be one of 0.7,0.8,0.9

#travel efficiency of stinger
E_stinger = 0.7 # can be [0.7,0.8,0.9]

#loading efficiency of stinger
E_stinger_load = 0.65 # can be [0.65,0.75,0.85]


#unloading efficiency of stinger
E_stinger_unload = 0.75 # can be [0.75,0.85,0.95]

# efficiency telehandler
E_loader = 0.7 #can be [0.7,0.8,0.9]

#efficiency truck
E_truck = 0.75 # can be [0.75,0.85,0.95]


#max cap of baler 
#assume 340 8hour days with 1 hour unavailability for 10 hours 38 bales/h 0.5t/bale
H_baler =   46981 # in tonnes per year 

#max cap telehandler
#0.75 mins per bale loading and unloading
H_loader = 98909 #in tonnes per year


#max cap stinger
#1.78mins per bale including loading unloading and travel, travel considered the average distance to be (sqrt(18)+sqrt(2))/2 and speed to be 15km/h

H_stinger = 41675 #in tonnes per year


#load mass of stinger
LoadMass_stinger = 4 #assuming 8 bale stinger and 0.5t per bale
#loadmass telehandler
LoadMass_loader = 1 #assuming 2 bale telehandler
#loadmass truck
LoadMass_truck = 15 # 30 bale truck

#loading time stinger
L_stinger = 0.00417 #h/bale

#loading time telehandler
L_loader = 0.017 # h/load

#Price of biomass k
typesOfBiomass = []

for i in range(numCrops):
   typesOfBiomass.append(string.join(("c",str(i)),"_"))

price = [2] #$2 ber tonn
P_k =makeDict([typesOfBiomass],price,0)

#size of farm i allocated to crop k
percentageFarmAllocated = np.random.rand(numCrops)
percentageFarmAllocated = percentageFarmAllocated/sum(percentageFarmAllocated)

farmSizeOfCrop =  np.fromfunction(empty, (numFarms, numCrops))

for index in range(numFarms):
    #farmSizeOfCrop[index,:] = (np.random.rand()*(900-100)+100)*percentageFarmAllocated
    farmSizeOfCrop[index,:] = percentageFarmAllocated   #Kamal has the total yeild at roadside
     
S_ik =makeDict([farms,typesOfBiomass],farmSizeOfCrop,0) #hectare


#speed of the stinger assuming it travels 50% on farm roads and 50% on paved roads
speed_stinger = 25 #km/h

#speed of truck
speed_truck = 80 #km/h

#unloading time of stinger load is 8 bales, unloading time 1 min/load 
U_stinger = 0.002083 #h/bale


#unloading time of the telehandler load is 2 bales time 0.5 min/load
U_loader = 0.004167 # h/bale


#average yield of biomass k in farm i

#yield of bioMass is in the range 2.61 t/ha-3.44 t/ha the amount that should be left on land to stop erosion range from 30%-70% 

#yieldBioMFarm = np.fromfunction(empty, (numFarms, numCrops)) 

#for farm in range(numFarms):
#    for crop in range(numCrops):
#        yieldBioMFarm[farm,crop]=(np.random.rand()*(3.44-2.61)+2.61)*(np.random.rand()*(0.7-0.3)+0.30)

#print yieldBioMFarm

Y_ik = makeDict([farms,typesOfBiomass],yieldBioMFarm,0)


#average dry matter loss at on field drying
#assuming this is equal to the unprotected storage DML
theta_dryField = 0.0

#DML of bailer from table 4-2 of thesis
theta_baler = 0.0

#DML of stinger
theta_stinger = 0.0 #0.0084

#DML storage
theta_storage =  0.0 #0.07

#DML telehandler
theta_loader = 0.0 #0.0091

#DML truck
theta_truck = 0.0 #0.0089

#DML plant
theta_plant = 0.0 #0.0214

# creation of the problem variable
prob = LpProblem("storage selection and biomass transpotation Problem",LpMinimize) 

#Decision varables



#create time label vec
periods = []

for time in range(years):
     periods.append(string.join(("t",str(time)),"_"))

#amount of biomass k collected from farm i and transported to storage j in period t
B_ikjt = LpVariable.dicts("RouteStore",(farms,typesOfBiomass,storages,periods),0,None,LpContinuous)

#amount of biomass k transported from strage j in period t
R_kjt =LpVariable.dicts("RoutePlant",(typesOfBiomass,storages,periods),0,None,LpContinuous)

#whether roadside storage of farm j selected as storage
#Z_j = LpVariable.dicts("SelStorej",storages,0,1,LpInteger)


#whether farm i is assigned to storage j

#X_ij = LpVariable.dicts("farmiAssignedj",(farms,storages),0,1,LpInteger)

#B_bar_j =  LpVariable.dicts("RouteStore_max",storages,0,None,LpContinuous)


#objective function
prob+=lpSum([(2*D_FS_ij[i][j]/(speed_stinger*E_stinger*1000)*(1-theta_baler)*C_stinger/LoadMass_stinger)\
*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages for t in periods]) \
+lpSum([2*(C_trailer+C_truck)*D_S_j[j]/(speed_truck*E_truck*LoadMass_truck*1000)*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages for t in periods])
 #lpSum([C_F_loader*Z_j[j] for j in storages])  

#prob+=lpSum([((C_baler+C_tractor)/(CAP_baler*E_baler)+((1-theta_baler)*C_twine)/BaleMass+theta_baler*P_k[k] \
#+(1-theta_baler)/BaleMass*(L_stinger/E_stinger_load+U_stinger/E_stinger_unload)*C_stinger \
#+2*D_FS_ij[i][j]/(speed_stinger*E_stinger)*(1-theta_baler)*C_stinger/LoadMass_stinger \
#+(1-theta_baler)*theta_stinger*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler)) \
#+(1-theta_baler)*theta_stinger*C_twine/BaleMass \
#+(1-theta_baler)*(1-theta_stinger)*theta_storage*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler)\
#+C_twine/BaleMass+C_stinger/BaleMass*(L_stinger/E_stinger_load+U_stinger/E_stinger_unload) \
#+ 2*C_stinger*D_FS_ij[i][j]/(speed_stinger*E_stinger*LoadMass_stinger))+C_storage)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages for t in periods]) \
##+ lpSum([C_F_loader*Z_j[j] for j in storages]) \
#+ lpSum([(C_V_loader*L_loader/(LoadMass_loader*E_loader)+theta_loader*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler) \
#+C_twine/BaleMass+C_stinger*(L_stinger/E_stinger_load+U_stinger/E_stinger_unload)/BaleMass \
#+2*C_stinger*lpSum([D_FS_ij[i][j] for i in farms])/(len(farms)*speed_stinger*E_stinger*LoadMass_stinger)+C_storage)  \
#+ (C_trailer+C_truck)*(L_loader+U_loader)/(LoadMass_loader*E_loader)+ 2*(C_trailer+C_truck)*D_S_j[j]/(speed_truck*E_truck*LoadMass_truck) \
#+(1-theta_loader)*theta_truck*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler) \
#+C_twine/BaleMass+C_stinger*(L_stinger/E_stinger_load+U_stinger/E_stinger_unload)/BaleMass \
#+2*C_stinger*lpSum([D_FS_ij[i][j] for i in farms])/(len(farms)*speed_stinger*E_stinger*LoadMass_stinger)+C_storage \
#+L_loader*C_V_loader/(LoadMass_loader*E_loader)))*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages for t in periods]) \
##+ lpSum([C_storage*B_bar_j[j] for j in storages]) #filled upto 5.21
#constraints
#5.22
for t in periods:
   prob+=lpSum([(1-theta_loader)*(1-theta_truck)*(1-theta_plant)*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages])>=A


#for t in periods:
#     for j in storages:
#         prob+=lpSum([(1-theta_loader)*(1-theta_truck)*(1-theta_plant)*R_kjt[k][j][t] for  k in typesOfBiomass])-A*Z_j[j]<=0
#5.23
for j in storages:
    for t in periods:
        prob+= lpSum([(1-theta_baler)*(1-theta_stinger)*(1-theta_storage)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass])\
        -lpSum([R_kjt[k][j][t] for k in typesOfBiomass]) >=0

#5.24
for i in farms:
  for k in typesOfBiomass:
     for t in periods:
        prob+=lpSum([B_ikjt[i][k][j][t] for j in storages])- (1-theta_dryField)*Y_ik[i][k]*S_ik[i][k]<=0


##5.25
#for t in periods:
#  prob+= lpSum([B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages]) <= H_baler*numFarms # the efficiency should be considered when determining the maximum available baler capacity

##5.26
#for t in periods:
#  prob+= lpSum([(1-theta_baler)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages]) <= H_stinger*numFarms # the efficiency should be considered when determining the maximum available stinger capacity

#5.27
#for t in periods:
#   for j in storages:
#      prob+=lpSum([R_kjt[k][j][t] for k in typesOfBiomass])<=H_loader*numFarms # loader efficiency should be included in max available capacity

#5.28

#for j in storages:
#  prob+= B_bar_j[j]<=capacity_storage[j]

#5.29

#for i in farms:
#  for j in storages:
#    prob+=X_ij[i][j] - Z_j[j]<=0 #if farm i is assigned store j then store j should be selected

#5.30
#for i in farms:
#  prob+=lpSum([X_ij[i][j] for j in storages])<=1 # each farm is assigned to only one storage or not selected

 
#5.14
#for j in storages:
#  for t in periods:
#    prob+= B_bar_j[j] - lpSum([(1-theta_baler)*(1-theta_stinger)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass])>=0

prob.writeLP("IISD.lp")

file_= open("/home/chamara/Dropbox/TRTech/Chamara/output.txt", "w+")

#solve using symphony solver

p = sp.Popen(["symphony" , "-p", "4", "-L","IISD.lp"],stdout=file_,cwd='/home/chamara/Dropbox/TRTech/Chamara')
#file.close()

(out,err) = p.communicate()

file_.close()
sys.stdout = sys.__stdout__



  #file = open('/home/chamara/Dropbox/TRTech/output.txt', 'r')
file_ = open("/home/chamara/Dropbox/TRTech/Chamara/output.txt","r")
variables_all = file_.readlines() #variable containing sol

variables = [];
#print variables_all
for line in variables_all:
    if re.match("Optimal(\s+)|Route(.*)|SelStore(.*)|farmiAssigned(.*)",line):
      #print line
      variables.append(line)
    elif re.match("Solution(.*)",line):
      #print line
      variables.append(line)


# The status of the solution is printed to the screen
#print "Status:", LpStatus[prob.status]

# Each of the variables is printed with it's resolved optimum value
#for v in variables:
#    print v.name, "=", v.varValue

# The optimised objective function value is printed to the screen    
#print "Total Cost of Transportation = ", value(prob.objective)

#f = open('workfile', 'w')

with open('IISDoptWithFixed.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in variables:
          out = re.split("\s+",v)
          #print out
          datawriter.writerow(out)


# The optimised objective function value is printed to the screen    
   #datawriter.writerow(["Total Cost of Transportation", value(prob.objective)])
