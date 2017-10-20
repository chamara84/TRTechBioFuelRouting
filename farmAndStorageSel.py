import csv
import re
from matplotlib import pyplot
import math

roadSideCoord = []
#putting the coordinates into a dictionary of storages
with open('RoadSideStorage.csv', 'rb') as csvfile:
    roadsideCoordReader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(roadsideCoordReader, None)
    rowNum = 0;
    for row in  roadsideCoordReader:
      roadSideCoord.append((str(rowNum) ,(float(row[0]),float(row[1]))))
      rowNum+=1

roadSideCoord = dict(roadSideCoord)

store_coordinates_raw  = []
with open('/home/chamara/Dropbox/TRTech/Chamara/highway_nodes.csv', 'rb') as csvfile:
    satStorePosRead = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(satStorePosRead, None)
    for row in  satStorePosRead:
      store_coordinates_raw.append([float(row[0]),float(row[1]), int(row[2])])


#satellite storages
satelliteStores = []
minDistBetSatStores = 1000 #the minimum x dir or y dir distance between satellite stores in m
satStoreIDSet = set()
minSatStorages = 5  #minimum number of satellite storages

expand = 0; 
while len(satelliteStores)<= minSatStorages:
    
    matchingStores = [row for  row in store_coordinates_raw if (row[0]<=622460.662+800*expand) and (row[0]>=612499.088-800*expand) and (row[1]<=5438669.66+800*expand) and (row[1]>=5428689.42-800*expand)]
    for row in matchingStores:
           store_coordinates_raw.remove(row)
           #print "in township"
           if len(satelliteStores)== 0:
              satelliteStores.append(row)
              satStoreIDSet.add(row[2])
              
           minL2Distance =min([math.sqrt(math.pow(row[0]-store[0],2)+math.pow(row[1]-store[1],2)) for store in satelliteStores]) 
           
           if minL2Distance>=minDistBetSatStores:
                if row[2] not in satStoreIDSet:
                  satelliteStores.append(row)
                  satStoreIDSet.add(row[2])
                  #print row,len(satelliteStores) 
    expand+=1
    
    
numSatStores = len(satelliteStores)

#reading the output of the optimization problem
file_ = open("./IISDopt.csv","r")
variables_all = file_.readlines() #variable containing sol

farmToStorage = []
farmToStorageAmt = []
satellite = set()
roadSide = set()
roadSideToSatellite = set()
#print variables_all
for line in variables_all:
    cropType =  re.search("RouteStore_f_([0-9]+)_c_([0-9]+)_s_([0-9]+)_t_([0-9]+)",line)
      #print line
    if cropType:
      print cropType.groups()
      routeTuple = cropType.groups()
      if routeTuple[0] == routeTuple[2]:
          if routeTuple[2] not in satellite:
            roadSide.add(roadSideCoord[routeTuple[2]])
      elif  routeTuple[0] != routeTuple[2]:
        roadSideToSatellite.add(roadSideCoord[routeTuple[0]])
        satellite.add(roadSideCoord[routeTuple[2]])
        if  roadSideCoord[routeTuple[2]] in roadSide:
          roadSide.remove(roadSideCoord[routeTuple[2]])
          
        
      
      farmToStorage.append(cropType.groups())
      amountTrnsported = re.split("\s+",line)
      #print amountTrnsported[1]
      farmToStorageAmt.append(amountTrnsported[1])

roadSide = roadSide.difference(satellite)
roadSideToSatellite = roadSideToSatellite.difference(satellite)
#print list(roadSide)
#print list(satellite)

xRoadside = [x for (x,y) in list(roadSide)]
yRoadside  = [y for (x,y) in list(roadSide)]

xSatellite = [x for (x,y) in list(satellite)]
ySatellite  = [y for (x,y) in list(satellite)]

xroadToSat = [x for (x,y) in list(roadSideToSatellite)]
yroadToSat = [y for (x,y) in list(roadSideToSatellite)]

pyplot.scatter(xRoadside, yRoadside, s=20, c=u'b', marker=u'o', label='Roadside storages')
pyplot.hold
pyplot.scatter(xSatellite, ySatellite, s=30, c=u'k', marker=u'^', label='Satellite storages')
pyplot.scatter(xroadToSat, yroadToSat, s=15, c=u'r', marker=u's', label='Roadside to Satellite')
legend = pyplot.legend(loc='best', shadow=True, fontsize='x-large')

# Put a nicer background color on the legend.
legend.get_frame().set_facecolor('#00FFCC')


pyplot.show()


      
