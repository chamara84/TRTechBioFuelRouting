import string
import numpy as np
import numpy.matlib
import csv
import re
import sys
import math

#the cost of the dry matter at different stages



class parameterStruct:
    def __init__(self):
        #balemass
        self.BaleMass =0.442  #in tonnes
        
        #capasity of baler
        self.CAP_baler = 38 #bale/h
        
        #cost of baler
        self.C_baler = 89.92 #$ per hour
        
        #cost of twine per bale
        self.C_twine = 0.8 #$ per bale
        
        #cost of tractor
        self.C_tractor = 93.67 #$ per hour
        
        #cost of stinger
        self.C_stinger= 77.67 #$ per hour
        
        #cost of storage
        
        # what should it include the ammortized construction cost depending on the type of storage and amount of yield and land value
        #assume average tonnes per farm is 400 then according to fire regulations area needed and reusable tarp on crushed rock are used and cost divided equally amoung 5 years land cost not included 
        self.C_storage = [70.39,53.82,1.47,2.70,0] #$/ m2
        
        self.minDistBetSatStores = 1000 #the minimum x dir or y dir distance between satellite stores in m
        
        #fixed cost of telehandler
        self.C_F_loader = 3895.5 #$/year
        
        #variable cost of telehandler
        self.C_V_loader = 47.25 #$/hour
        
        
        #Cost of trailer
        self.C_trailer = 23.39 #$/hour
        
        #cost of truck
        self.C_truck = 97.90 #$/hour
        
        #efficiency of baler
        self.E_baler = 0.7 #can be one of 0.7,0.8,0.9
        
        #travel efficiency of stinger
        self.E_stinger = 0.7 # can be [0.7,0.8,0.9]
        
        #loading efficiency of stinger
        self.E_stinger_load = 0.65 # can be [0.65,0.75,0.85]
        
        
        #unloading efficiency of stinger
        self.E_stinger_unload = 0.75 # can be [0.75,0.85,0.95]
        
        # efficiency telehandler
        self.E_loader = 0.7 #can be [0.7,0.8,0.9]
        
        #efficiency truck
        self.E_truck = 0.75 # can be [0.75,0.85,0.95]
        
        
        #max cap of baler 
        #assume 340 8hour days with 1 hour unavailability for 10 hours 38 bales/h 0.5t/bale
        self.H_baler =   46981 # in tonnes per year 
        
        #max cap telehandler
        #0.75 mins per bale loading and unloading
        self.H_loader = 98909 #in tonnes per year
        
        
        #max cap stinger
        #1.78mins per bale including loading unloading and travel, travel considered the average distance to be (sqrt(18)+sqrt(2))/2 and speed to be 15km/h
        
        self.H_stinger = 41675 #in tonnes per year
        
        
        #load mass of stinger
        self.LoadMass_stinger = 4 #assuming 8 bale stinger and 0.5t per bale
        #loadmass telehandler
        self.LoadMass_loader = 1 #assuming 2 bale telehandler
        #loadmass truck
        self.LoadMass_truck = 15 # 30 bale truck
        
        #loading time stinger
        self.L_stinger = 0.00417 #h/bale
        
        #loading time telehandler
        self.L_loader = 0.017 # h/load
        
        #speed of the stinger assuming it travels 50% on farm roads and 50% on paved roads
        self.speed_stinger = 25 #km/h
        
        #speed of truck
        self.speed_truck = 80 #km/h
        
        #unloading time of stinger load is 8 bales, unloading time 1 min/load 
        self.U_stinger = 0.002083 #h/bale
        
        
        #unloading time of the telehandler load is 2 bales time 0.5 min/load
        self.U_loader = 0.004167 # h/bale
        
        #all the dry matter losses are percentages of input biomass to the respective processes
        
        #average dry matter loss at on field drying
        #assuming this is equal to the unprotected storage DML
        self.theta_dryField = 0.0
        
        #DML of bailer from table 4-2 of thesis
        self.theta_baler = 0.0
        
        #DML of stinger
        self.theta_stinger = 0.0084
        
        #DML storage
        self.theta_storage = [0.02 ,0.04, 0.07,0.15,0.25 ]
        
        #DML telehandler
        self.theta_loader = 0.0091
        
        #DML truck
        self.theta_truck = 0.0089
        
        #DML plant
        self.theta_plant = 0.0214

#cost per ton of DML at hauling to the storage from farm gate



    
    