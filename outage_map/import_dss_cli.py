import click
import os
import pandas as pd
import networkx as nx
import opendssdirect as dss
from .util.NetworkFunctions import getElevationByCoords, fixBusName, findNodeNum, getTreeCanopy, findSlopeOfElevation, generateDem, getLandCover
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
    lats = []
    lons = []

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

    for load in loads:
        dss.Circuit.SetActiveElement(load)
        lBus = dss.CktElement.BusNames()
        newBusL = fixBusName(lBus)
        LOADS.append(Load(dss.Loads.Name(), newBusL[0], dss.Loads.kV(), dss.Loads.kW(), dss.Loads.kvar(), dss.Loads.Vminpu(), dss.Loads.Vmaxpu(), dss.Loads.Phases()))

    for i, bus in enumerate(BUSES):
        lon, lat = bus.coordinates

        while (lon, lat) in used_coords:
            lon += OFFSET
            lat += OFFSET

        used_coords.add((lon, lat))
        lats.append(lat)
        lons.append(lon)

    coords = [(lon, lat) for lon, lat in zip(lons, lats)]
    elevations = getElevationByCoords(coords)
    covers = getLandCover(coords)
    vegetations = getTreeCanopy(coords)

    for i, bus in enumerate(BUSES):
        NODES.append(Node(bus.name, i, coords[i], 
                        elevation=elevations[i],
                        cover=covers[i],
                        vegetation=vegetations[i]))

    for line in LINES:
        EDGES.append(Edge(line.name, line.length, findNodeNum(line.bus1, NODES), findNodeNum(line.bus2, NODES), line.enabled))

    for tf in TRANSFORMERS:
        EDGES.append(Edge(tf.name, 0, findNodeNum(tf.bus1, NODES), findNodeNum(tf.bus2, NODES), 1))

    G = nx.MultiDiGraph()

    nodeDict = []

    for node in NODES:
        G.add_node(node.num, name=node.name, coords=node.coords)
        nodeDict.append({
            'name': node.name,
            'coords': node.coords,
            'elevation': node.elevation,
            'vegetation': node.vegetation,

        })

    dem = generateDem(lat=lats, lon=lons)
    for i, edge in enumerate(EDGES):
        if edge.enabled == 1:
            coords1 = NODES[edge.bus1].coords
            coords2 = NODES[edge.bus2].coords
            avg_veg = (vegetations[edge.bus1] +  vegetations[edge.bus2]) / 2
            G.add_edge(edge.bus1, edge.bus2, name=edge.name, length=edge.length, slope=findSlopeOfElevation(coords1=coords1, coords2=coords2, dem=dem), vegetation=avg_veg)

    el = nx.to_pandas_edgelist(G)
    nl = pd.DataFrame(nodeDict)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    pd.DataFrame.to_csv(nl, os.path.join(output_path, 'nodeList.csv'))
    pd.DataFrame.to_csv(el, os.path.join(output_path, 'edgeList.csv'))

    click.echo(f"nodeList and edgeList saved to {output_path}.")

if __name__ == "__main__":
    IMPORT_DSS()
