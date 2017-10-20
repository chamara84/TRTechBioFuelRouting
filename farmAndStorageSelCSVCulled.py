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
with open('/home/chamara/Dropbox/TRTech/Chamara/culled_storage_points.csv', 'rb') as csvfile:
    satStorePosRead = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(satStorePosRead, None)
    for row in  satStorePosRead:
      store_coordinates_raw.append([string.join(("s",str(row[0])),"_"),[float(row[1]),float(row[2])]])

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
      writeAmtTransported.append([Distance_storage[string.join(("f",str(routeTuple[0])),"_")][0],Distance_storage[string.join(("f",str(routeTuple[0])),"_")][1],satelliteStores[string.join(("s",str(routeTuple[2])),"_")][0],satelliteStores[string.join(("s",str(routeTuple[2])),"_")][1],routeTuple[1],routeTuple[3],farmToStorageAmt])        
      if string.join(("f",str(routeTuple[0])),"_") in bioMassRoadSide:
          if routeTuple[2]==150:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [farmToStorageAmt,0,0,0]
          elif routeTuple[2]==152:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [0,farmToStorageAmt,0,0]
          elif routeTuple[2]==1027:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [0,0,farmToStorageAmt,0]
          elif routeTuple[2]==1225:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]+= [0,0,0,farmToStorageAmt]
              
      else:
          if routeTuple[2]==150:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [farmToStorageAmt,0,0,0]
          elif routeTuple[2]==152:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [0,farmToStorageAmt,0,0]
          elif routeTuple[2]==1027:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [0,0,farmToStorageAmt,0]
          elif routeTuple[2]==1225:
              bioMassRoadSide[string.join(("f",str(routeTuple[0])),"_")]= [0,0,0,farmToStorageAmt]
         
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
zroad150 = {index:bioMassRoadSide[index][0] for index in bioMassRoadSide}
zroad152 = {index:bioMassRoadSide[index][1] for index in bioMassRoadSide}
zroad1027 = {index:bioMassRoadSide[index][2] for index in bioMassRoadSide}  
zroad1225 = {index:bioMassRoadSide[index][3] for index in bioMassRoadSide}  
#satellite
coordSat150 = [["x","y","ID"]]
coordSat152 = [["x","y","ID"]]
coordSat1027 = [["x","y","ID"]]
coordSat1225 = [["x","y","ID"]]

for index in bioMassRoadSide:
    if zroad150[index] > 0.001:
        coordSat150.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif zroad152[index] > 0.001:
        coordSat152.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif zroad1027[index] > 0.001:
        coordSat1027.append([Distance_storage[index][0],Distance_storage[index][1],index])
    elif zroad1225[index] > 0.001:
        coordSat1225.append([Distance_storage[index][0],Distance_storage[index][1],index])
        
with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide150.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat150:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide152.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat152:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide1027.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat1027:
          datawriter.writerow(v)          

IISD_optVar.close()

with open('/home/chamara/Dropbox/TRTech/Chamara/IISDRoadSide1225.csv', 'w') as IISD_optVar:
        datawriter = csv.writer(IISD_optVar, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for v in coordSat1225:
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
