# import pandas as pd
# import networkx as nx
# import opendssdirect as dss
# from util.NetworkFunctions import getElevationByCoords, fixBusName,findNodeNum, getLandCover,findAvgLineVegetation
# from util.ComponentClasses import Bus, Line, Load, Node, Edge, Transformer
# import warnings
# warnings.filterwarnings("ignore")



# dss.Command('Redirect P3R/DSS/Master.dss')

# # Acquire a list of buses, lines, elements, transformers, and loads
# buses = dss.Circuit.AllBusNames()
# lines = dss.Lines.AllNames()
# elements = dss.Circuit.AllElementNames()
# transformers  = [item for item in elements if 'Transformer' in item]
# loads = [item for item in elements if 'Load' in item] 

# # Initialize empty list for circuit and graph components
# BUSES=[]
# LINES = []
# TRANSFORMERS = []
# LOADS = []
# NODES = []
# EDGES = []

# print("Here")
# # Loop through buses, and append bus data to bus list
# for bus in buses:
#     dss.Circuit.SetActiveBus(bus)
#     # Append [Name, (X,Y), Base kV] to bus object and store in list
#     BUSES.append(Bus(dss.Bus.Name(),(dss.Bus.X(),dss.Bus.Y()),dss.Bus.kVBase()))

# # Loop through lines, and append line data to line list
# for line in lines:
#     # Set the current line
#     dss.Lines.Name(line)
#     # Set the current line (element form to get enabled)
#     dss.Circuit.SetActiveElement(line)
#     # Append [Name, Length, Bus1, Bus2, Enabled] to line object and store list
#     LINES.append(Line(dss.Lines.Name(),dss.Lines.Length(),dss.Lines.Bus1(),dss.Lines.Bus2(),dss.CktElement.Enabled()))

# # Loop through transformers
# for transformer in transformers:
#     # Set the current transformer
#     dss.Circuit.SetActiveElement(transformer)
#     # Get the buses attached to transformers
#     busesT = dss.CktElement.BusNames()
#     # Remove the node number from bus name for simplification
#     newBusT = fixBusName(busesT)
#     # Append [Name, Bus1 Bus2 WdgVoltages and WdgCurrents] to Transformer object and store in list
#     TRANSFORMERS.append(Transformer(dss.Element.Name(),newBusT[0],newBusT[1],dss.Transformers.WdgVoltages(),dss.Transformers.WdgCurrents()))

# # Loop through loads
# for load in loads:
#     # Set the current load element
#     dss.Circuit.SetActiveElement(load)
#     # Get the bus attached to the load
#     lBus = dss.CktElement.BusNames()
#     # Fix the bus name for simplicity
#     newBusL = fixBusName(lBus)
#     # Append [Name, Bus, kV, kvar, Vminpu, Vmaxpu, Phases] to Load object and store in list
#     LOADS.append(Load(dss.Loads.Name(), newBusL[0], dss.Loads.kV(), dss.Loads.kW(), dss.Loads.kvar(), dss.Loads.Vminpu(), dss.Loads.Vmaxpu(), dss.Loads.Phases()))

# # Loop through bus list
# for i, bus in enumerate(BUSES):
#     # Append [Name, Num, Coord, Elevation, Vegetation] to node object and store in node list
#     NODES.append(Node(bus.name,i,bus.coordinates,elevation=getElevationByCoords(bus.coordinates), vegetation=None))

# # Loop through lines
# for line in LINES:
#     # Append [Name, Length, Node1, Node2, Enabled] to Edge object and store in list
#     EDGES.append(Edge(line.name,line.length,findNodeNum(line.bus1, NODES),findNodeNum(line.bus2, NODES),line.enabled))

# # Loop through transformers
# for tf in TRANSFORMERS:
#     # Append [Name, 0, Node1, Node2, 1] to Edge object and store in list
#     EDGES.append(Edge(tf.name,0, findNodeNum(tf.bus1, NODES),findNodeNum(tf.bus2, NODES),1))

# # Create a new graph. # Need to use a graph class that includes Multi (MultiGraph, MultiDiGraph, etc.)
# G = nx.MultiDiGraph()

# # Initialize a node dictionary to convert to csv
# nodeDict = []

# # Loop through node list
# for node in NODES:
#     # Add the Node to Graph G
#     G.add_node(node.num, name = node.name, coords = node.coords)
#     # Add Node Data to dictionary entry and store in list
#     nodeDict.append({
#         'name':node.name,
#         'coords':node.coords,
#         'elevation':node.elevation,
#         'vegetation':node.vegetation
#         })

# # Loop through edges
# for i, edge in enumerate(EDGES):
#     # Check if the edge is enabled
#     if edge.enabled ==1:
#         # Print the edge number for progress update
#         print('Edge ' + str(i))
#         # Add the Edge to Graph G and assign edge data to corresponding attributes
#         # G.add_edge(edge.bus1, edge.bus2,name = edge.name, length = edge.length, vegetation = findAvgLineVegetation(edge.bus1, edge.bus2, NODES,10))
#         G.add_edge(edge.bus1, edge.bus2,name = edge.name, length = edge.length, vegetation = None)


# # Convert Edge List and Node List to Panda Dataframes
# el = nx.to_pandas_edgelist(G).to_dict()
# nl = pd.DataFrame(nodeDict).to_dict()

# response = {
#     "node": nl,
#     "edge": el 
# }

import click

@click.group(
    name="import-dss"
)
def IMPORT_DSS():
    pass

@IMPORT_DSS.command()
def import_dss():
    """Testing"""
    click.echo("It is working")