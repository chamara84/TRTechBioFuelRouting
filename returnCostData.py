
#reads the cost data from Kamals file and put them into variables
from pulp import *
from random import *
import string
import numpy as np
import numpy.matlib
import csv
import  subprocess as sp 
import re
import sys

#cost of baler
C_baler = 89.92 #$ per hour

#cost of tractor
C_tractor = 93.67 #$ per hour


#cost of stinger
C_stinger_travel =

C_stinger_load =


#DML of the baler
theta_baler = 


#farm key to index dicts
farm_keys = dict()

#biomass type keys to index
biomass_keys = dict()

#available shedded biomass of each type k at farm i
Y_ik = 