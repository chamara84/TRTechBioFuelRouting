#optimization problem of IISD as in Mahmood Thesis
from pulp import *
from random import *
import string
import numpy as np
import numpy.matlib
import csv
import  subprocess as sp 
import re
import sys

#Parameters
#number of farms
numFarms = 144
#number of crop types
numCrops = 1

#number of contract years
years = 5
#annual feed stock
A = 65000 #27375 # in tonnes

#balemass
BaleMass =0.442  #in tonnes

#capasity of baler
CAP_baler = 38 #bale/h

#road side storages
storages = []
#farms 
farms =  []  

for i in range(numFarms):
  storages.append(string.join(("s",str(i)),"_"))
  farms.append(string.join(("f",str(i)),"_"))



#maximum capacity of storage
#70% of farms are in the range of 100-900 ha with average crop of 2.15 t/ha
storeCap = [] # generate randomly between 215-1935 t
for index in range(numFarms):
  storeCap.append(np.random.randint(2000,3000))

capacity_storage = makeDict([storages],storeCap,0)

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

#fixed cost of telehandler
C_F_loader = 3895.5 #$/year

#variable cost of telehandler
C_V_loader = 47.25 #$/hour


#Cost of trailer
C_trailer = 23.39 #$/hour

#cost of truck
C_truck = 97.90 #$/hour


#distance between farm and storage assuming 160km supply radius
def empty(x, y):
    return x*0


Distance_ij_raw  = []
with open('Storage2StorageDistance.csv', 'rb') as csvfile:
    Distreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(Distreader, None)
    for row in  Distreader:
      Distance_ij_raw.append([float(entry)+ 0.8 for entry in  row])


#Distance_ij_raw[0]  = []       
#Distance_ij = [float(Distance_ij_raw[row][col])+0.8 for row in range(numFarms) for col in range(numFarms)]
Distance_ij = Distance_ij_raw 
D_FS_ij = makeDict([farms,storages],Distance_ij,0)



#distance between farm j and storage
Distance_storage = []

with open('RoadSideStorage.csv', 'rb') as csvfile:
    DistStoragereader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(DistStoragereader, None)
    for row in  DistStoragereader:
      Distance_storage.append([float(entry) for entry in  row])

#Distance_storage[0] = []

      
yieldBioMFarm =  [[dist[3]] for dist in Distance_storage[0:numFarms]]
Distance_storage = [dist[2] for dist in Distance_storage[0:numFarms]]



D_S_j = makeDict([storages],Distance_storage,0)

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

price = np.random.randint(10,size=numCrops)
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
theta_stinger = 0.0084

#DML storage
theta_storage = 0.07

#DML telehandler
theta_loader = 0.0091

#DML truck
theta_truck = 0.0089

#DML plant
theta_plant = 0.0214

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
Z_j = LpVariable.dicts("SelStorej",storages,0,1,LpInteger)


#whether farm i is assigned to storage j

X_ij = LpVariable.dicts("farmiAssignedj",(farms,storages),0,1,LpInteger)

B_bar_j =  LpVariable.dicts("RouteStore_max",storages,0,None,LpContinuous)


#objective function
prob+=lpSum([((C_baler[i]+C_tractor[i])+((1-theta_baler[i])*C_twine)/BaleMass \
              +theta_baler[i]*P_k[k] \
              +(1-theta_baler[i])*(C_stinger_load[i]+D_FS_ij[i][j]/D_FS_ij[i][i]*C_stinger_travel[i]) \
              +(1-theta_baler[i])*theta_stinger*(P_k[k]+(C_baler[i]+C_tractor[i])+C_twine/BaleMass) \
              +(1-theta_baler[i])*(1-theta_stinger)*theta_storage*(P_k[k]+(C_baler[i]+C_tractor[i])+C_twine/BaleMass+C_stinger_load[i]+C_stinger_travel[i]*D_FS_ij[i][j]/(D_FS_ij[i][i])))*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages for t in periods])\
+ lpSum([C_F_loader*Z_j[j] for j in storages])\
+ lpSum([(C_V_loader*L_loader/(LoadMass_loader*E_loader) \
          +theta_loader*(P_k[k]+(C_baler[i]+C_tractor[i])+C_twine/BaleMass+ C_stinger_load[i] +C_stinger_travel[i]*D_FS_ij[i][j]/( D_FS_ij[i][i] )+C_storage) \
          +(C_trailer+C_truck)*((L_loader+U_loader)/(LoadMass_loader*E_loader)+ 2*D_S_j[j]/(speed_truck*E_truck*LoadMass_truck)) \
          +(1-theta_loader)*theta_truck*(P_k[k]+(C_baler[i]+C_tractor[i])+C_twine/BaleMass+C_stinger_load[i]+C_stinger_travel[i]*D_FS_ij[i][j]/(D_FS_ij[i][i])+C_storage+L_loader*C_V_loader/(LoadMass_loader*E_loader)))*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages for t in periods]) \
+ lpSum([C_storage*B_bar_j[j] for j in storages]) #filled upto 5.21
#constraints
#5.22
for t in periods:
   prob+=lpSum([(1-theta_loader)*(1-theta_truck)*(1-theta_plant)*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages])>=A

#5.23
for j in storages:
    for t in periods:
        prob+= lpSum([(1-theta_baler[i])*(1-theta_stinger)*(1-theta_storage)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass])-lpSum([R_kjt[k][j][t] for k in typesOfBiomass]) >=0

#5.24
for i in farms:
  for k in typesOfBiomass:
    for j in storages:
      for t in periods:
        prob+=B_ikjt[i][k][j][t]- Y_ik[i][k]*X_ij[i][j]<=0


#5.25
for t in periods:
  prob+= lpSum([B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages]) <= H_baler*numFarms # the efficiency should be considered when determining the maximum available baler capacity

#5.26
for t in periods:
  prob+= lpSum([(1-theta_baler)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages]) <= H_stinger*numFarms # the efficiency should be considered when determining the maximum available stinger capacity

#5.27
for t in periods:
   for j in storages:
      prob+=lpSum([R_kjt[k][j][t] for k in typesOfBiomass])<=H_loader # loader efficiency should be included in max available capacity

#5.28

for j in storages:
  prob+= B_bar_j[j]<=capacity_storage[j]

#5.29

for i in farms:
  for j in storages:
    prob+=X_ij[i][j] - Z_j[j]<=0 #if farm i is assigned store j then store j should be selected

#5.30
for i in farms:
  prob+=lpSum([X_ij[i][j] for j in storages])<=1 # each farm is assigned to only one storage or not selected

 
#5.14
for j in storages:
  for t in periods:
    prob+= B_bar_j[j] - lpSum([(1-theta_baler)*(1-theta_stinger)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass])<=0

prob.writeLP("IISD.lp")

file_= open("/home/chamara/Dropbox/TRTech/output.txt", "w+")

#solve using symphony solver

p = sp.Popen(["symphony" , "-p", "4", "-L","IISD.lp"],stdout=file_,cwd='/home/chamara/Dropbox/TRTech/')
#file.close()

(out,err) = p.communicate()

file_.close()
sys.stdout = sys.__stdout__



  #file = open('/home/chamara/Dropbox/TRTech/output.txt', 'r')
file_ = open("./output.txt","r")
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

with open('IISDopt.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter='\t',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in variables:
          out = re.split("\s+",v)
          #print out
          datawriter.writerow(out)


# The optimised objective function value is printed to the screen    
   #datawriter.writerow(["Total Cost of Transportation", value(prob.objective)])
