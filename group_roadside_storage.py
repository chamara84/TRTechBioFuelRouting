import csv
import numpy
import cPickle

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


#Get locations of perspective storage site locations
lines=list(csv.reader(open('culled_storage_points.csv')))[1:]
storage_nodes=dict([(int(line[0]),(float(line[1]),float(line[2]))) for line in lines if min(map(len,line))>0])
xcoords=numpy.array([tup[0] for tup in storage_nodes.values()])
ycoords=numpy.array([tup[1] for tup in storage_nodes.values()])


lines=list(csv.reader(open('culled_storage_points_shortest_path_distances.csv')))[1:]
highway_distance=dict([((int(line[0]),int(line[1])),float(line[2])) for line in lines if min(map(len,line))>0])
H=numpy.array([[highway_distance[i,j] for j in storage_nodes] for i in storage_nodes])
 
#Get amount of biomass stored at each roadside location
lines=list(csv.reader(open('Output.csv')))
headers=lines[0]
lines=lines[1:]
header2col=dict([(headers[i],i) for i in range(len(headers))])
qs_data={}
for line in lines:
    if 'Not A Farm' in line:
        continue
    qs_data[line[header2col['QS Key']]]=\
    {'X':float(line[header2col['StorageE']]),\
    'Y':float(line[header2col['StorageN']]),\
    'mass':float(line[header2col['Biomass after Baling (Ton)']]),\
    'cost':sum([float(line[j]) for j in [4,5,6,7,8,9]])}
    
 

num_done=0
for plant_location in range(len(storage_nodes)):
    if not storage_nodes.keys()[plant_location]==1280:
        continue
    Mass_L1_distance=numpy.zeros(2*(len(storage_nodes),))
    node_mass=numpy.zeros(len(storage_nodes))
    harvest_cost=numpy.zeros(len(storage_nodes))
    best_node_assignment={}
    highway_distances=H[plant_location]
    for qs in qs_data:
        x=qs_data[qs]['X']
        y=qs_data[qs]['Y']
        mass=qs_data[qs]['mass']
        cost=qs_data[qs]['cost']
        L1_distances=numpy.abs(x-xcoords)+numpy.abs(y-ycoords)
        best_node=numpy.argmin(L1_weight*L1_distances+highway_weight*highway_distances)
        best_node_assignment[qs]=storage_nodes.keys()[best_node]
        Mass_L1_distance[best_node,:]+=mass*L1_distances
        node_mass[best_node]+=mass
        harvest_cost[best_node]+=cost*mass
    nodes_used=[i for i in range(len(storage_nodes)) if node_mass[i]>0]
    average_L1_distance=numpy.zeros((len(nodes_used),len(storage_nodes)))
    average_harvest_cost=numpy.zeros((len(nodes_used),1))
    storage_mass=numpy.zeros((len(nodes_used),1))
    for i in range(len(nodes_used)):
        node=nodes_used[i]
        average_L1_distance[i,:]=Mass_L1_distance[node,:]/node_mass[node]
        average_harvest_cost[i]=harvest_cost[node]/node_mass[node]    
        storage_mass[i]=node_mass[node]    
        
   
    numpy.save('L1_distances_'+str(storage_nodes.keys()[plant_location]),average_L1_distance)
    numpy.save('supply_mass_'+str(storage_nodes.keys()[plant_location]),storage_mass)
    numpy.save('harvest_cost_'+str(storage_nodes.keys()[plant_location]),average_harvest_cost)
    numpy.save('highway_distances_'+ str(storage_nodes.keys()[plant_location]),highway_distances) 
    numpy.save('source_nodes_'+ str(storage_nodes.keys()[plant_location]),[storage_nodes.keys()[i] for i in nodes_used])          
    numpy.save('sink_nodes_'+ str(storage_nodes.keys()[plant_location]),[i for i in storage_nodes])
    fp=open('results/best_node_assignment_'+str(storage_nodes.keys()[plant_location])+'.pkl','wb')
    cPickle.dump(best_node_assignment,fp)
    fp.close()
    num_done+=1
    print num_done,'plants done'

    
            
        

