import csv
import re
from matplotlib import pyplot
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import string


Distance_storage = dict()

with open('/home/chamara/Dropbox/TRTech/Chamara/RoadSideStorage.csv', 'rb') as csvfile:
    DistStoragereader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(DistStoragereader, None)
    for row in  DistStoragereader:
      Distance_storage[string.join(("f",str(row[0])),"_")] = [float(entry) for entry in  row[1:5]]

store_coordinates_raw  = []
with open('/home/chamara/Dropbox/TRTech/Chamara/highway_nodes.csv', 'rb') as csvfile:
    satStorePosRead = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(satStorePosRead, None)
    for row in  satStorePosRead:
      store_coordinates_raw.append([int(row[2]),[float(row[0]),float(row[1])]])

satelliteStores = dict(store_coordinates_raw)
#satellite storages
#reading the output of the optimization problem
file_ = open("/home/chamara/Dropbox/TRTech/Chamara/IISDopt.csv","r")
variables_all = file_.readlines() #variable containing sol
headerNames = ['Roadside E', 'Roadside N','Storage E', 'Storage N', 'BioMass Type','TimePeriod','Amount']
headerDict = dict([[headerNames[i],i] for i in range(len(headerNames))])
writeAmtTransported = []
writeAmtTransported.append(headerNames)
farmToStorage = []
farmToStorageAmt = [] 
bioMassSatellite = dict()
bioMassRoadSide = dict()
bioMassPlant = []
#print variables_all
for line in variables_all:
    cropType =  re.search("RouteStore_f_([0-9]+)_c_([0-9]+)_s_([0-9]+)_t_([0-9]+)",line)
    amountTrnsported = re.split("\s+",line)
      #print amountTrnsported[1]
    
      #print line
    if cropType:
      try:
        farmToStorageAmt = float(amountTrnsported[1])
      except:
            print 'error',amountTrnsported[1] 
      #print cropType.groups()
      routeTuple = [int(i) for i in cropType.groups()]
      writeAmtTransported.append([Distance_storage[string.join(("f",str(routeTuple[0])),"_")][0],Distance_storage[string.join(("f",str(routeTuple[0])),"_")][1],satelliteStores[routeTuple[2]][0],satelliteStores[routeTuple[2]][1],routeTuple[1],routeTuple[3],farmToStorageAmt])        
      if string.join(("f",str(routeTuple[0])),"_") in bioMassRoadSide:
          if routeTuple[2]==139:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [farmToStorageAmt,0,0]
          elif routeTuple[2]==508:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [0,farmToStorageAmt,0]
          elif routeTuple[2]==421:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [0,0,farmToStorageAmt]
              
      else:
          if routeTuple[2]==139:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [farmToStorageAmt,0,0]
          elif routeTuple[2]==508:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [0,farmToStorageAmt,0]
          elif routeTuple[2]==421:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [0,0,farmToStorageAmt]
         
      if string.join(("s",str(routeTuple[2])),"_") in bioMassSatellite:
          bioMassSatellite[string.join(("s",str(routeTuple[2])),"_")]+= farmToStorageAmt
      else:
         bioMassSatellite[string.join(("s",str(routeTuple[2])),"_")]= farmToStorageAmt
         
                    
with open('/home/chamara/Dropbox/TRTech/Chamara/IISDBioMassRouting.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in writeAmtTransported:
          datawriter.writerow(v)   
IISD_optVar.close()      



#roadside storage to satellite store 
xroad = [Distance_storage[index][0] for index in bioMassRoadSide]
yroad = [Distance_storage[index][1] for index in bioMassRoadSide]
zroad139 = {index:bioMassRoadSide[index][0] for index in bioMassRoadSide}
zroad508 = {index:bioMassRoadSide[index][1] for index in bioMassRoadSide}
zroad421 = {index:bioMassRoadSide[index][2] for index in bioMassRoadSide}   
#satellite
coordSat139 = [["x","y","ID"]]
coordSat508 = [["x","y","ID"]]
coordSat421 = [["x","y","ID"]]

for index in bioMassRoadSide:
    if zroad139[index] > 0.001:
        coordSat139.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif zroad508[index] > 0.001:
        coordSat508.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif zroad421[index] > 0.001:
        coordSat421.append([Distance_storage[index][0],Distance_storage[index][1],index])
        
with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide139.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat139:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide508.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat508:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide421.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat421:
          datawriter.writerow(v)          

IISD_optVar.close()


#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#bar1 = ax.scatter(xroad, yroad,zroad139,   c='red', marker = 'o')
##red_proxy = plt.Rectangle((0, 0), 1, 1, fc="r")
#bar2 =ax.scatter(xroad, yroad, zroad508, c='black', marker = 'x')
##blue_proxy = plt.Rectangle((0, 0), 1, 1, fc="b")
#bar3 =ax.scatter(xroad, yroad,zroad421,   c='cyan', marker = 's')
##cyan_proxy = plt.Rectangle((0, 0), 1, 1, fc="c")
#ax.set_xlabel('X')
#ax.set_ylabel('Y')
#ax.set_zlabel('Amount transported')
#
#ax.legend([bar1, bar2, bar3], ['Storage139', 'Storage508','Storage421'])

# Put a nicer background color on the legend.


#plt.show()
