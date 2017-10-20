#optimization problem of IISD as in Mahmood Thesis
from pulp import *
#from random import *
import string
import numpy as np
import numpy.matlib
import csv
import  subprocess as sp 
import math
from operator import itemgetter
#Parameters
#number of farms
numFarms = 144
#number of crop types
numCrops = 1

#number of contract years
years = 1
#annual feed stock
A = 68500 #27375 # in tonnes

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
C_F_loader = 3895.5 #$/year

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
      store_coordinates_raw.append( [int(row[0]),float(row[1]),float(row[2])])
csvfile.close()

#satellite storages
satelliteStores = dict()
satStoreIDSet = set()
minSatStorages = 3  #minimum number of satellite storages

expand = 0; 
while len(satelliteStores)<= minSatStorages:
    
    matchingStores = [row for  row in store_coordinates_raw if (row[1]<=622460.662+800*expand) and (row[1]>=612499.088-800*expand) and (row[2]<=5438669.66+800*expand) and (row[2]>=5428689.42-800*expand)]
    for row in matchingStores:
           store_coordinates_raw.remove(row)
           #print "in township"
           satelliteStores[string.join(("s",str(row[0])),"_")]=[row[1],row[2]]
           satStoreIDSet.add(row[0])
              
           
                             #print row,len(satelliteStores) 
    expand+=1
    
    
numSatStores = len(satelliteStores)


print "Selected Sat stores",[store for store in  satelliteStores]



#maximum capacity of satellite storage

storeCap = [] # generate randomly 
for index in range(numSatStores):
  storeCap.append(np.random.randint(30000,40000))

for store in  satelliteStores:
   storages.append(store)

#maximum capacity of satellite storage

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
 

yieldBioMFarm =  [[Distance_storage[dist][2]] for dist in Distance_storage]
#Distance_storage = [dist[2] for dist in Distance_storage[0:numFarms]]
Distance_ij  = []



Distance_ij  = dict()

Distance_ij  = {farm: {storage:abs(Distance_storage[farm][0]-satelliteStores[storage][0])+abs(Distance_storage[farm][1]-satelliteStores[storage][1]) for storage in satelliteStores}for farm in Distance_storage }  



D_FS_ij = Distance_ij

print "Distance From farm to store"
DistSatToPlantAll = dict()
csvfile = open('/home/chamara/Dropbox/TRTech/Chamara/culled_storage_points_shortest_path_distances.csv', 'rb')
DistStorageToPlantreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
headers = next(DistStorageToPlantreader, None)
DistSatToPlantAll = {(string.join(("s",str(row[0])),"_"),string.join(("s",str(row[1])),"_")):float(row[2]) for row in  DistStorageToPlantreader}
    
            
plantID = string.join(("s",str(1409)),"_")  #node 1409
DistSatToPlantSel = dict()
for source in satelliteStores:
    DistSatToPlantSel[source] = DistSatToPlantAll[(source,plantID)]
              


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

#price = 2 #$2 ber tonn
#P_k =makeDict([typesOfBiomass],price,0)

#size of farm i allocated to crop k
percentageFarmAllocated = np.random.rand(numCrops)
percentageFarmAllocated = percentageFarmAllocated/sum(percentageFarmAllocated)




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

#Y_ik = makeDict([farms,typesOfBiomass],yieldBioMFarm,0)


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



storageAssignment = dict()
value=dict()
for i in farms:
    my_list = {j:(2*D_FS_ij[i][j]/(speed_stinger*E_stinger)*(1-theta_baler)*C_stinger/LoadMass_stinger \
     +2*(C_trailer+C_truck)*D_S_j[j]/(speed_truck*E_truck*LoadMass_truck)\
     )for j in storages}
    print sorted(my_list.items(),)
    #my_list=[D_FS_ij[i][j] for j in storages]
    val,idx = min((val, idx) for (val, idx) in enumerate(my_list))
    value[i] = min(my_list)
    storageAssignment[i] =storages[min(enumerate(my_list), key=itemgetter(1))[0]]
   

#objective function
#prob+=lpSum([(2*D_FS_ij[i][j]/(speed_stinger*E_stinger)*(1-theta_baler)*C_stinger/LoadMass_stinger \
#+(1-theta_baler)*theta_stinger*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler)) \
#+(1-theta_baler)*theta_stinger*C_twine/BaleMass \
#+(1-theta_baler)*(1-theta_stinger)*theta_storage*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler)\
#+C_twine/BaleMass+C_stinger/BaleMass*(L_stinger/E_stinger_load+U_stinger/E_stinger_unload) \
#+ 2*C_stinger*D_FS_ij[i][j]/(speed_stinger*E_stinger*LoadMass_stinger))+C_storage)*B_ikjt[i][k][j][t] for i in farms for k in typesOfBiomass for j in storages for t in periods]) \
##+ lpSum([C_F_loader*Z_j[j] for j in storages]) \
#+ lpSum([+2*C_stinger*D_FS_ij[i][j]/(speed_stinger*E_stinger*LoadMass_stinger)+C_storage)  \
#+ C_V_loader*(L_loader+U_loader)/(LoadMass_loader*E_loader)+ 2*(C_trailer+C_truck)*D_S_j[j]/(speed_truck*E_truck*LoadMass_truck) \
#+(1-theta_loader)*theta_truck*(P_k[k]+(C_baler+C_tractor)/(CAP_baler*E_baler) \
#+C_twine/BaleMass+(L_stinger/E_stinger_load+U_stinger/E_stinger_unload)/BaleMass \
#+2*C_stinger*D_FS_ij[i][j]/(speed_stinger*E_stinger*LoadMass_stinger)+C_storage \
#+L_loader*C_V_loader/(LoadMass_loader*E_loader)))*R_kjt[k][j][t] for  k in typesOfBiomass for j in storages for t in periods]) \



coordSat150 = [["x","y","ID"]]
coordSat152 = [["x","y","ID"]]
coordSat1027 = [["x","y","ID"]]
coordSat1225 = [["x","y","ID"]]


for index in storageAssignment:
    if storageAssignment[index] == "s_150":
        coordSat150.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif storageAssignment[index] == "s_152":
        coordSat152.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif storageAssignment[index] == "s_1027":
        coordSat1027.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif storageAssignment[index] == "s_1225":
        coordSat1225.append([Distance_storage[index][0],Distance_storage[index][1],index])
        
with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide150_weigtedDistance.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat150:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide152_weigtedDistance.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat152:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide1027_weigtedDistance.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat1027:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide1225_weigtedDistance.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat1225:
          datawriter.writerow(v)          

IISD_optVar.close()