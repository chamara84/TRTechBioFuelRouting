import csv
import re
from matplotlib import pyplot
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import string
import numpy as np




sourceNodes = np.load("source_nodes_1280.npy")
sinkNodes = np.load("sink_nodes_1280.npy")
store_coordinates_raw  = []
with open('./culled_storage_points.csv', 'rb') as csvfile:
    satStorePosRead = csv.reader(csvfile, delimiter=',', quotechar='|')
    headers = next(satStorePosRead, None)
    for row in  satStorePosRead:
      store_coordinates_raw.append([int(row[0]),[float(row[1]),float(row[2])]])

satelliteStores = dict(store_coordinates_raw)
#satellite storages
#reading the output of the optimization problem
file_ = open("./IISDoptWithFixedMILP.csv","r")
variables_all = file_.readlines() #variable containing sol
headerNames = ['source','x', 'y','Storage ', 'Used']
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
    cropType =  re.search("RoutePlant_s_([0-9]+)_d_([0-9]+)",line)
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
      writeAmtTransported.append([sourceNodes[routeTuple[0]], satelliteStores[sourceNodes[routeTuple[0]]][0],satelliteStores[sourceNodes[routeTuple[0]]][1],sinkNodes[routeTuple[1]],farmToStorageAmt])  
      
filePlot = open("./IISDoptWithFixedMILPPlot100k.csv","w")
datawriter = csv.writer(filePlot, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL) 
for line in writeAmtTransported:
     datawriter.writerow(line)
     print line
     
filePlot.close()