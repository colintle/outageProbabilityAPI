import click
import os
import pandas as pd
import networkx as nx
import opendssdirect as dss
from .util.NetworkFunctions import checkFloodZone, generateFloodZoneBox, getElevationByCoords, getTreeCanopy, findSlopeOfElevation, generateDem, getLandCover, convertCoverToSeverity
from .util.ComponentClasses import Node, Edge
import warnings
import numpy as np
import matplotlib.pyplot as plt


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
    
    OFFSET = 0.000001

    dss.Command(f'Redirect {input_path}/Master.dss')
    buses = dss.Circuit.AllBusNames()
    line_catalog = pd.read_csv('outage_map/util/LineGeometryCatalog.csv')
    line_catalog['name']=line_catalog['name'].str.upper()

    # Initialize empty list for circuit and graph components
    HIGH_TENSION_NODES= []
    LOW_TENSION_NODES= []
    HIGH_VOLTAGE_POLES= []
    LOW_VOLTAGE_POLES= []
    LOADS = []

    NODES = []
    EDGES = []

    lons = []
    lats = []

    # coords = np.zeros((2, len(buses)))
    coords = [0] * len(buses)

    for i, bus in enumerate(buses):
        dss.Circuit.SetActiveBus(bus)
        name = dss.Bus.Name()
        lon, lat = float(dss.Bus.X()), float(dss.Bus.Y())

        if 'htnode' in name:
            HIGH_TENSION_NODES.append({'name':name,'num':i,})
        elif 'ltnode' in name:
            LOW_TENSION_NODES.append({'name':name,'num':i,})
        elif 'load' in name:
            LOADS.append({'name':name,'num':i,})
        elif 'secondary' in name:
            LOW_VOLTAGE_POLES.append({'name':name,'num':i,})
        else:
            HIGH_VOLTAGE_POLES.append({'name':name,'num':i,})

        coords[i] = (lon, lat)
        lons.append(lon)
        lats.append(lat)

    elevations = getElevationByCoords(coords)
    covers = getLandCover(coords)
    vegetations = getTreeCanopy(coords)
    dem = generateDem(lat=lats, lon=lons)
    flood_zones = generateFloodZoneBox(coords)

    node_counter = 0
    for i in range(len(HIGH_TENSION_NODES)):
        name_to_match = HIGH_TENSION_NODES[i]['name'].split('_h')[0]
        
        for j in range(len(LOW_TENSION_NODES)):
            if name_to_match in LOW_TENSION_NODES[j]['name']:
                LT_index = j

        NODES.append(Node(
            name ='pole_xfmr_'+str(i),
            num = node_counter,
            original_index = HIGH_TENSION_NODES[i]['num'],
            coords = coords[HIGH_TENSION_NODES[i]['num']],
            original_name = 'pole_xfmr',
            low_tension_bus = LOW_TENSION_NODES[LT_index]['name'],
            high_tension_bus = HIGH_TENSION_NODES[i]['name'],
            flood_zone = checkFloodZone(coords[HIGH_TENSION_NODES[i]['num']], flood_zones),
            material = 'wood',
            node_type = 'pole_xfmr',
            elevation = elevations[HIGH_TENSION_NODES[i]['num']],
            vegetation = vegetations[HIGH_TENSION_NODES[i]['num']],
            cover = convertCoverToSeverity(covers[HIGH_TENSION_NODES[i]['num']]) 
            ))                                        
        
        node_counter = node_counter + 1                                 

    for i in range(len(LOADS)):
        NODES.append(Node(
            name ='load_'+str(i),
            num = node_counter,
            original_index=LOADS[i]['num'],
            coords = coords[LOADS[i]['num']],
            original_name = LOADS[i]['name'],
            low_tension_bus = None,
            high_tension_bus = None,
            flood_zone = checkFloodZone(coords[LOADS[i]['num']], flood_zones),
            material = 'load',
            node_type = 'load',
            elevation = elevations[LOADS[i]['num']],
            vegetation = vegetations[LOADS[i]['num']],
            cover = convertCoverToSeverity(covers[LOADS[i]['num']])
            ))
        
        node_counter = node_counter + 1

    for i in range(len(HIGH_VOLTAGE_POLES)):
        NODES.append(Node(
            name ='pole_hv_'+str(i),
            num = node_counter,
            original_index=HIGH_VOLTAGE_POLES[i]['num'],
            coords = coords[HIGH_VOLTAGE_POLES[i]['num']],
            original_name = HIGH_VOLTAGE_POLES[i]['name'],
            low_tension_bus = None,
            high_tension_bus = None,
            flood_zone = checkFloodZone(coords[HIGH_VOLTAGE_POLES[i]['num']], flood_zones),
            material = 'wood',
            node_type = 'pole',
            elevation = elevations[HIGH_VOLTAGE_POLES[i]['num']],
            vegetation = vegetations[HIGH_VOLTAGE_POLES[i]['num']],
            cover = convertCoverToSeverity(covers[HIGH_VOLTAGE_POLES[i]['num']])))
        
        node_counter = node_counter + 1

    for i in range(len(LOW_VOLTAGE_POLES)):
        NODES.append(Node(
            name ='pole_lv_'+str(i),              
            num = node_counter,
            original_index=LOW_VOLTAGE_POLES[i]['num'],
            coords = coords[LOW_VOLTAGE_POLES[i]['num']],
            original_name = LOW_VOLTAGE_POLES[i]['name'],
            low_tension_bus = None,
            high_tension_bus = None,
            flood_zone = checkFloodZone(coords[LOW_VOLTAGE_POLES[i]['num']], flood_zones),
            material = 'wood',
            node_type = 'pole',
            elevation = elevations[LOW_VOLTAGE_POLES[i]['num']],
            vegetation = vegetations[LOW_VOLTAGE_POLES[i]['num']],
            cover = convertCoverToSeverity(covers[LOW_VOLTAGE_POLES[i]['num']])
            ))
        
        node_counter = node_counter + 1
    
    nodes_data = [{
        'name': node.name,
        'num': node.num,
        'original_index': node.original_index,
        'coords': node.coords,
        'original_name': node.original_name,
        'low_tension_bus': node.low_tension_bus,
        'high_tension_bus': node.high_tension_bus,
        'flood_zone': node.flood_zone,
        'material': node.material,
        'node_type': node.type,
        'elevation': node.elevation,
        'vegetation': node.vegetation
    } for node in NODES]

    df_nodes = pd.DataFrame(nodes_data)

    lineCounter = 0
    edge_set = set()  

    for i, bus in enumerate(buses):
        dss.Circuit.SetActiveBus(bus)
        
        name = dss.Bus.Name()
        
        connected_lines = dss.Bus.LineList()
        
        for j, line in enumerate(connected_lines):
            dss.Lines.Name(line.replace('LINE.', ''))   
            
            bus1Name = dss.Lines.Bus1().split('.')[0]
            
            if 'ht' not in bus1Name and 'lt' not in bus1Name:
                new_bus1Name = df_nodes.loc[df_nodes['original_name'] == bus1Name, 'name'].values[0]
                new_bus1Num = df_nodes.loc[df_nodes['original_name'] == bus1Name, 'num'].values[0]
            elif 'ht' in bus1Name:
                new_bus1Name = df_nodes.loc[df_nodes['high_tension_bus'] == bus1Name, 'name'].values[0]
                new_bus1Num = df_nodes.loc[df_nodes['high_tension_bus'] == bus1Name, 'num'].values[0]
            
            else:
                new_bus1Name = df_nodes.loc[df_nodes['low_tension_bus'] == bus1Name, 'name'].values[0]
                new_bus1Num = df_nodes.loc[df_nodes['low_tension_bus'] == bus1Name, 'num'].values[0]

            bus2Name = dss.Lines.Bus2().split('.')[0]

            if 'ht' not in bus2Name and 'lt' not in bus2Name:
                new_bus2Name = df_nodes.loc[df_nodes['original_name'] == bus2Name, 'name'].values[0]
                new_bus2Num = df_nodes.loc[df_nodes['original_name'] == bus2Name, 'num'].values[0]
            elif 'ht' in bus2Name:
                new_bus2Name = df_nodes.loc[df_nodes['high_tension_bus'] == bus2Name, 'name'].values[0]
                new_bus2Num = df_nodes.loc[df_nodes['high_tension_bus'] == bus2Name, 'num'].values[0]
            else:
                new_bus2Name = df_nodes.loc[df_nodes['low_tension_bus'] == bus2Name, 'name'].values[0]
                new_bus2Num = df_nodes.loc[df_nodes['low_tension_bus'] == bus2Name, 'num'].values[0]
            
            edge_name = new_bus1Name + str('__') + new_bus2Name
            
            if edge_name in edge_set:
                continue
            
            edge_set.add(edge_name)  
            dss.LineGeometries.Name(dss.Lines.Geometry())
            line_conductor = dss.LineGeometries.Conductors()[0]
            line_conductor=line_conductor.upper()
            line_location = line_catalog.loc[line_catalog['name'] == line_conductor, 'type'].values[0]
            line_material = line_catalog.loc[line_catalog['name'] == line_conductor, 'material'].values[0]

            coords1 = coords[new_bus1Num]
            coords2 = coords[new_bus2Num]
            avg_veg = (vegetations[new_bus1Num] +  vegetations[new_bus2Num]) / 2
            
            if 'hv' in new_bus1Name:
                EDGES.append(Edge(
                    name = edge_name,
                    num = lineCounter,
                    source = new_bus1Num,
                    target = new_bus2Num,
                    conductor = line_material,
                    original_name = line,
                    location = line_location,
                    voltage =  11, 
                    length = dss.Lines.Length(),
                    vegetation = avg_veg,
                    slope=findSlopeOfElevation(coords1=coords1, coords2=coords2, dem=dem)
                ))
            else:
                EDGES.append(Edge(
                    name = edge_name,
                    num = lineCounter,
                    source = new_bus1Num,
                    target = new_bus2Num,
                    conductor = line_material,
                    original_name = line,
                    location = line_location,
                    voltage =  11, 
                    length = dss.Lines.Length(),
                    vegetation = avg_veg,
                    slope=findSlopeOfElevation(coords1=coords1, coords2=coords2, dem=dem)
                ))

            lineCounter += 1

    edges_data = [{
        'name': edge.name,
        'num': edge.num,
        'source':edge.source,
        'target':edge.target,
        'original_name': edge.original_name,
        'material': edge.material,
        'voltage': edge.voltage,
        'location': edge.location,
        'length': edge.length,
        'vegetation': edge.vegetation,
        'slope': edge.slope
    } for edge in EDGES]

    G = nx.MultiGraph()

    for node in NODES:
        G.add_node(
            node.num,
            name=node.name,
            original_index=node.original_index,
            coords=node.coords,
            original_name=node.original_name,
            low_tension_bus=node.low_tension_bus,
            high_tension_bus=node.high_tension_bus,
            flood_zone=node.flood_zone,
            material=node.material,
            node_type=node.type,
            elevation=node.elevation,
            vegetation=node.vegetation
        )
    
    for edge in EDGES:
        G.add_edge(edge.source, edge.target, 
                            name=edge.name,
                            source=edge.source,
                            target=edge.target,
                            original_name=edge.original_name,
                            material=edge.material,
                            voltage=edge.voltage,
                            location=edge.location,
                            length=edge.length,
                            vegetation=edge.vegetation
                   )

    df_edges = pd.DataFrame(edges_data)

    grouped_nodes = df_nodes.groupby('coords').filter(lambda x: len(x) > 1)
    matching_nodes = grouped_nodes.groupby('coords')['name'].apply(lambda x: ', '.join(x)).reset_index()

    matching_nodes_expanded = matching_nodes['name'].str.split(', ', expand=True).rename(columns={0: 'Node 1', 1: 'Node 2'})

    matching_nodes_final = pd.concat([matching_nodes['coords'], matching_nodes_expanded], axis=1)

    for i in range(len(matching_nodes_final)):
        match1 = matching_nodes_final.loc[i, 'Node 1']
        match2 = matching_nodes_final.loc[i, 'Node 2']
        
        if 'pole_lv' in match1:
            nodeToChange = match1
        else:
            nodeToChange = match2

        num = df_nodes.loc[df_nodes['name'] == nodeToChange, 'num'].values[0]
        
        original_value = df_nodes.loc[num, 'coords']
        
        new_x = original_value[0] + OFFSET
        new_y = original_value[1] + OFFSET
        
        df_nodes.at[num, 'coords'] = (new_x, new_y)

    pos = {row['num']: row['coords'] for idx, row in df_nodes.iterrows() if row['coords'] is not None}

    pos = {k: tuple(map(float, v)) for k, v in pos.items()}

    plt.figure(constrained_layout=True)
    G = nx.from_pandas_edgelist(df_edges,edge_attr=True)
    T = nx.dfs_tree(G, 0)
    pos = {row['num']: row['coords'] for idx, row in df_nodes.iterrows() if row['coords'] is not None}
    color_map_nodes = []
    color_map_edges = []
    size_map = []
    for node in T.nodes:
        if node== 0:
            color_map_nodes.append('orange')
            size_map.append(40)
        elif df_nodes.loc[df_nodes['num'] == node, 'node_type'].values[0] == 'pole_xfmr':
            color_map_nodes.append('red')
            size_map.append(30)        
        elif df_nodes.loc[df_nodes['num'] == node, 'node_type'].values[0] == 'load':
            color_map_nodes.append('green')
            size_map.append(30)
        else: 
            color_map_nodes.append('black')
            size_map.append(15)

    for u, v in T.edges:
        edge_attr = G.edges[u, v]
        if edge_attr['location'] == 'OH':
            color_map_edges.append('brown')
        else:
            color_map_edges.append('grey')        
    i = i+1


    el = nx.to_pandas_edgelist(G)
    el1 = nx.to_pandas_edgelist(T)

    for i in range(len(el1)):
        source, target = el1.iloc[i]["source"], el1.iloc[i]["target"]
        for j in range(len(el)):
            original_source, original_target = el.iloc[j]["source"], el.iloc[j]["target"]

            if (source == original_source and target == original_target) or (source == original_target and target == original_source):
                for column in el.columns:
                    if column not in ["source", "target"]:
                        if source == original_target and target == original_source and column == "slope":
                            el1.at[i, column] = -el.iloc[j][column]
                        else:
                            el1.at[i, column] = el.iloc[j][column]

    nx.draw_networkx(T, pos=pos,with_labels=False, node_color=color_map_nodes,edge_color=color_map_edges,node_size=size_map, font_size=6,arrows=True)
    plt.show()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    df_nodes.to_csv(os.path.join(output_path, 'nodeList.csv'), index=False)
    pd.DataFrame.to_csv(el1, os.path.join(output_path, 'edgeList.csv'))
    click.echo(f"nodeList and edgeList saved to {output_path}.")

    print("Tree T node and edge lists saved to CSV.")
