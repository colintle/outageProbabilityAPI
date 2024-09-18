import click
import os
import pandas as pd
import networkx as nx
import opendssdirect as dss
from .util.NetworkFunctions import getElevationByCoords, fixBusName, findNodeNum, getLandCover, findAvgLineVegetation
from .util.ComponentClasses import Bus, Line, Load, Node, Edge, Transformer
import warnings


OFFSET = 0.000001

warnings.filterwarnings("ignore")

@click.group(
    name="import-dss"
)
def IMPORT_DSS():
    pass

@IMPORT_DSS.command()
@click.option('--input-path', type=click.Path(exists=True), required=True,
              help="Relative path to the input directory containing the DSS files.")
@click.option('--output-path', type=click.Path(), required=True,
              help="Directory where the nodeList & edgeList CSV files will be saved.")
def import_dss(input_path, output_path):
    """Process DSS files and save nodeList and edgeList as CSV files."""
    
    # Redirect to the DSS file
    dss.Command(f'Redirect {input_path}/Master.dss')

    # Acquire a list of buses, lines, elements, transformers, and loads
    buses = dss.Circuit.AllBusNames()
    lines = dss.Lines.AllNames()
    elements = dss.Circuit.AllElementNames()
    transformers  = [item for item in elements if 'Transformer' in item]
    loads = [item for item in elements if 'Load' in item]
    used_coords = set()

    # Initialize empty list for circuit and graph components
    BUSES = []
    LINES = []
    TRANSFORMERS = []
    LOADS = []
    NODES = []
    EDGES = []

    # Loop through buses, and append bus data to bus list
    for bus in buses:
        dss.Circuit.SetActiveBus(bus)
        BUSES.append(Bus(dss.Bus.Name(), (dss.Bus.X(), dss.Bus.Y()), dss.Bus.kVBase()))

    # Loop through lines, and append line data to line list
    for line in lines:
        dss.Lines.Name(line)
        dss.Circuit.SetActiveElement(line)
        LINES.append(Line(dss.Lines.Name(), dss.Lines.Length(), dss.Lines.Bus1(), dss.Lines.Bus2(), dss.CktElement.Enabled()))

    # Loop through transformers
    for transformer in transformers:
        dss.Circuit.SetActiveElement(transformer)
        busesT = dss.CktElement.BusNames()
        newBusT = fixBusName(busesT)
        TRANSFORMERS.append(Transformer(dss.Element.Name(), newBusT[0], newBusT[1], dss.Transformers.WdgVoltages(), dss.Transformers.WdgCurrents()))

    # Loop through loads
    for load in loads:
        dss.Circuit.SetActiveElement(load)
        lBus = dss.CktElement.BusNames()
        newBusL = fixBusName(lBus)
        LOADS.append(Load(dss.Loads.Name(), newBusL[0], dss.Loads.kV(), dss.Loads.kW(), dss.Loads.kvar(), dss.Loads.Vminpu(), dss.Loads.Vmaxpu(), dss.Loads.Phases()))

    # Loop through bus list
    for i, bus in enumerate(BUSES):
        lon, lat = bus.coordinates  # Extract coordinates

        # Check if the coordinates already exist in the set
        while (lon, lat) in used_coords:
            lon += OFFSET  # Offset the longitude
            lat += OFFSET  # Offset the latitude

        # Add the new coordinates to the set
        used_coords.add((lon, lat))

        # Append the node with adjusted coordinates
        NODES.append(Node(bus.name, i, (lon, lat), 
                        elevation=getElevationByCoords((lon, lat)), 
                        vegetation=getLandCover((lon, lat))))


    # Loop through lines
    for line in LINES:
        EDGES.append(Edge(line.name, line.length, findNodeNum(line.bus1, NODES), findNodeNum(line.bus2, NODES), line.enabled))

    # Loop through transformers
    for tf in TRANSFORMERS:
        EDGES.append(Edge(tf.name, 0, findNodeNum(tf.bus1, NODES), findNodeNum(tf.bus2, NODES), 1))

    # Create a new graph
    G = nx.MultiDiGraph()

    # Initialize a node dictionary to convert to csv
    nodeDict = []

    # Loop through node list
    for node in NODES:
        G.add_node(node.num, name=node.name, coords=node.coords)
        nodeDict.append({
            'name': node.name,
            'coords': node.coords,
            'elevation': node.elevation,
            'vegetation': node.vegetation
        })

    # Loop through edges
    for i, edge in enumerate(EDGES):
        if edge.enabled == 1:
            G.add_edge(edge.bus1, edge.bus2, name=edge.name, length=edge.length, vegetation=findAvgLineVegetation(edge.bus1, edge.bus2, NODES,10))
            # G.add_edge(edge.bus1, edge.bus2, name=edge.name, length=edge.length)

    # Convert Edge List and Node List to Panda Dataframes
    el = nx.to_pandas_edgelist(G)
    nl = pd.DataFrame(nodeDict)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Save the dataframes as CSV files
    pd.DataFrame.to_csv(nl, os.path.join(output_path, 'nodeList.csv'))
    pd.DataFrame.to_csv(el, os.path.join(output_path, 'edgeList.csv'))

    click.echo(f"nodeList and edgeList saved to {output_path}.")

if __name__ == "__main__":
    IMPORT_DSS()
