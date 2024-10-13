import click
from .util.mainHelper import assign_values_to_ranges, createTables, generateProb, probOfNodeAndParent, plotTreeWithProb
import pandas as pd
import numpy as np
from collections import defaultdict
import networkx as nx
import os

@click.group(name="generate-outage-map")
def GENERATE_OUTAGE_MAP():
    """
    CLI tool for generating an outage map based on node and edge features, weather impacts,
    and network structure.
    """
    pass

@GENERATE_OUTAGE_MAP.command()
@click.option(
    '--node-feature',
    type=(str, float, float, float, float),
    multiple=True,
    required=True,
    help='Node feature with mean min, mean max, std min, and std max. Example: --node-feature elevation 0.5 1.0 0.1 0.2'
)
@click.option(
    '--edge-feature',
    type=(str, float, float, float, float),
    multiple=True,
    required=True,
    help='Edge feature with mean min, mean max, std min, and std max. Example: --edge-feature length 0.7 0.9 0.2 0.3'
)
@click.option(
    '--list-folder',
    type=click.Path(exists=True),
    required=True,
    help='Input relative path to the folder containing nodeList.csv and edgeList.csv.'
)
@click.option(
    '--weather-event',
    type=str,
    required=True,
    help='Input weather event that contains the weather impact'
)
@click.option(
    '--wi-folder',
    type=click.Path(exists=True),
    required=True,
    help='Input relative path to the folder containing weather impacts. This folder should contain "edges" and "nodes" folders.'
)
def generate_outage_map(node_feature, edge_feature, list_folder, weather_event, wi_folder):
    """
    Generate an outage map using specified node and edge features, and weather impacts.
    """

    # Separate mean and standard deviation dictionaries for nodes and edges
    meanWI_nodes = {name: [mean_min, mean_max] for name, mean_min, mean_max, std_min, std_max in node_feature}
    stdWI_nodes = {name: [std_min, std_max] for name, mean_min, mean_max, std_min, std_max in node_feature}

    meanWI_edges = {name: [mean_min, mean_max] for name, mean_min, mean_max, std_min, std_max in edge_feature}
    stdWI_edges = {name: [std_min, std_max] for name, mean_min, mean_max, std_min, std_max in edge_feature}

    # List of node and edge features
    nodeFeatures = [name for name, *_ in node_feature]
    edgeFeatures = [name for name, *_ in edge_feature]

    # Number of bins for range assignment
    numOfBins = 10

    # Load node and edge data from CSV files
    nodes = pd.read_csv(os.path.join(list_folder, 'nodeList.csv'))
    edges = pd.read_csv(os.path.join(list_folder, 'edgeList.csv'))

    # Initialize forecasted range dictionaries for nodes and edges
    forecastedRange_nodes = {}
    forecastedRange_edges = {}

    # Calculate forecasted ranges for node features
    for name in nodeFeatures:
        vals = np.round(nodes[name].values, 1)
        if name == "elevation":
            bins = assign_values_to_ranges(vals, numOfBins, inv=True)
        else:
            bins = assign_values_to_ranges(vals, numOfBins, inv=False)
        levels = []
        total = np.array([])
        for index, [ranges, count] in enumerate(bins):
            total = np.concatenate((total, (index + 1) * np.ones((1, count))), axis=1) if len(total) > 0 else (index + 1) * np.ones((1, count))
            levels.append(list(ranges))
        forecastedRange_nodes[name] = levels
    
    # Calculate forecasted ranges for edge features
    for name in edgeFeatures:
        vals = np.round(edges[name].values, 1)
        bins = assign_values_to_ranges(vals, numOfBins)
        levels = []
        total = np.array([])
        for index, [ranges, count] in enumerate(bins):
            total = np.concatenate((total, (index + 1) * np.ones((1, count))), axis=1) if len(total) > 0 else (index + 1) * np.ones((1, count))
            levels.append(list(ranges))
        forecastedRange_edges[name] = levels

    # Create tables for mean and standard deviation ranges for nodes and edges
    meanRange_nodes, stdRange_nodes = createTables(stdWI_nodes, meanWI_nodes, numOfBins + 1)
    meanRange_edges, stdRange_edges = createTables(stdWI_edges, meanWI_edges, numOfBins + 1)

    # Load weather impact data for nodes and edges
    weatherImpactEdges = pd.read_csv(os.path.join(wi_folder, f'edges/{weather_event}.csv'))
    weatherImpactNodes = pd.read_csv(os.path.join(wi_folder, f'nodes/{weather_event}.csv'))

    # Prepare graph structure
    edgeList = []
    graph = defaultdict(list)
    for i in range(len(edges)):
        index = edges.iloc[i]['num']
        edgeList.append((int(edges.iloc[i]["source"]), int(edges.iloc[i]["target"])))
        graph[int(edges.iloc[i]["source"])].append([int(edges.iloc[i]["target"]), index])

    # Initialize directed graph and add nodes and edges
    G = nx.DiGraph()
    G.add_nodes_from(range(len(nodes)))
    G.add_edges_from(sorted(edgeList))

    # Calculate probabilities for nodes based on weather impact
    probNodes = [0] * len(nodes)
    for i in range(len(nodes)):
        currWeatherImpactN = weatherImpactNodes.iloc[[i]]
        index = nodes.iloc[i]["num"]
        currProb = []
        for j in range(2):
            bounds = {}
            for feature in nodeFeatures:
                bounds[feature] = eval(currWeatherImpactN[feature][i])[j]
            currProb.append(generateProb(nodes.iloc[[i]], None, nodeFeatures, edgeFeatures, meanRange_nodes, stdRange_nodes, forecastedRange_nodes, bounds, None, numOfBins))
        probNodes[index] = currProb

    # Calculate probabilities for edges based on weather impact
    probEdges = [0] * len(edges)
    for i in range(len(edges)):
        currWeatherImpactE = weatherImpactEdges.iloc[[i]]
        index = edges.iloc[i]["num"]
        currProb = []
        for j in range(2):
            bounds = {}
            for feature in edgeFeatures:
                bounds[feature] = eval(currWeatherImpactE[feature][i])[j]
            currProb.append(generateProb(None, edges.iloc[[i]], nodeFeatures, edgeFeatures, meanRange_edges, stdRange_edges, forecastedRange_edges, None, bounds, numOfBins))
        probEdges[index] = currProb

    # Calculate combined probabilities for nodes and their parent nodes
    prob = probOfNodeAndParent(probNodes, probEdges, graph)

    # Calculate the mean probability for visualization
    meanProb = [(low + high) / 2 for low, high in prob]

    # Set positions for nodes based on their coordinates
    pos = {nodes.iloc[i]["num"]: eval(nodes.iloc[[i]]["coords"][i]) for i in range(len(nodes))}

    resultProb = []

    for i in range(len(nodes)):
        index = nodes.iloc[i]["num"]
        resultProb.append(meanProb[index])

    nodes["Probability"] = resultProb
    nodes.to_csv(os.path.join(list_folder, 'nodeList.csv'), index=False)

    # Plot the graph with probabilities
    plotTreeWithProb(G, meanProb, "", pos)

if __name__ == "__main__":
    GENERATE_OUTAGE_MAP()
