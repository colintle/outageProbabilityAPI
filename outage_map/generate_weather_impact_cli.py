import click
import numpy as np
import pandas as pd
import os
from .util.mainHelper import weatherImpact, createLevelsAlt, findWeatherLevel

@click.group(name="generate-weather-impact")
def GENERATE_WEATHER_IMPACT():
    """CLI group for generating weather impact."""
    pass

# Custom validation function for node-feature and edge-feature
def validate_feature_values(ctx, param, value):
    """
    Validates that each feature has the correct number of float values, 
    and that the float values sum to 1.
    """
    try:
        feature_list = ctx.params['feature_list']  # Get the feature list
        num_features = len(feature_list)  # Number of features

        # Parse the feature, ensuring each has the correct number of floats
        parsed_values = []
        for feature in value:
            parts = feature.split(",")
            feature_name = parts[0]  # First part is the feature name
            values = [float(v) for v in parts[1:]]  # The remaining parts are the float values

            if len(values) != num_features:
                raise click.BadParameter(f"Each feature must have exactly {num_features} values.")
            
            if not abs(sum(values) - 1.0) < 1e-6:
                raise click.BadParameter(f"Values for {feature_name} must sum to 1. Provided values sum to {sum(values)}.")
            
            parsed_values.append((feature_name, values))
        return parsed_values

    except ValueError as e:
        raise click.BadParameter(f"Invalid input: {str(e)}")

# CLI command
@GENERATE_WEATHER_IMPACT.command()
@click.option('--feature-list', type=(str, int, int), multiple=True, required=True, help='List of features with min and max values. Example: --feature-list temp 0 100 --feature-list prcp 0 10')
@click.option('--input-path', type=click.Path(exists=True), required=True, help='Input relative path to the folder containing feature folders.')
@click.option('--node-feature', multiple=True, required=True, callback=validate_feature_values, help='Node feature with relative values. Example: --node-feature "elevation 0.5 0.5"')
@click.option('--edge-feature', multiple=True, required=True, callback=validate_feature_values, help='Edge feature with relative values. Example: --edge-feature "elevation 0.7 0.3"')
@click.option('--output-path', type=click.Path(), required=True, help='Output directory to save the results.')
def generate_weather_impact(feature_list, input_path, node_feature, edge_feature, output_path):
    """Generate weather impact based on input features, node and edge data."""
    
    # Check if the output directory exists; if not, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    nodes_output_path = os.path.join(output_path, 'nodes')
    edges_output_path = os.path.join(output_path, 'edges')

    if not os.path.exists(nodes_output_path):
        os.makedirs(nodes_output_path)

    if not os.path.exists(edges_output_path):
        os.makedirs(edges_output_path)

    # Dynamically determine directories and severity levels based on feature list
    node_directories = []
    edge_directories = []
    severity_levels = {}
    for feature, min_val, max_val in feature_list:
        node_directories.append(os.path.join(input_path, f"{feature}/nodes/"))
        edge_directories.append(os.path.join(input_path, f"{feature}/edges/"))
        severity_levels[feature] = createLevelsAlt(min_val, max_val, 10)

    # Process files for nodes
    file_names = [f for f in os.listdir(node_directories[0]) if os.path.isfile(os.path.join(node_directories[0], f))]
    
    for name in file_names:
        # alpha = {feature_name: float(values) for feature_name, values in node_feature}
        alpha = {feature_name: values for feature_name, values in node_feature}


        # Dynamically read data based on the feature
        data_frames = {}
        for i, feature in enumerate(feature_list):
            data_frames[feature[0]] = pd.read_csv(os.path.join(node_directories[i], name))

        # Determine LENGTH as the number of rows (excluding the header) in the first file
        LENGTH = len(data_frames[feature_list[0][0]])

        # Initialize arrays to store scores and vectors
        weather_vector = np.zeros((len(feature_list), LENGTH, 2))
        scores = {feature[0]: np.zeros((2, LENGTH)) for feature in feature_list}

        # Loop through each node to find the normalized weather value
        for i in range(LENGTH):
            for feature in feature_list:
                feature_name = feature[0]
                severity = severity_levels[feature_name]

                min_val = np.array(data_frames[feature_name].min(axis=1))[i]
                max_val = np.array(data_frames[feature_name].max(axis=1))[i]

                scores[feature_name][0, i] = findWeatherLevel(min_val, severity)
                scores[feature_name][1, i] = findWeatherLevel(max_val, severity)

        # Create the normalized weather vector
        for j, feature in enumerate(feature_list):
            feature_name = feature[0]
            weather_vector[j, :] = np.linspace(scores[feature_name][0, :], scores[feature_name][1, :], num=2).T

        # Compute weather impact for both interpolated points
        wi1 = weatherImpact(alpha, weather_vector[:, :, 0])
        wi2 = weatherImpact(alpha, weather_vector[:, :, 1])

        wi = {feature_name: [] for feature_name in alpha}

        for feature in wi:
            for low, high in zip(wi1[feature], wi2[feature]):
                wi[feature].append((np.round(low, 3), np.round(high, 3)))

        events = pd.DataFrame(wi)
        events.to_csv(os.path.join(nodes_output_path, name), index=False)

    # Process files for edges
    edge_file_names = [f for f in os.listdir(edge_directories[0]) if os.path.isfile(os.path.join(edge_directories[0], f))]
    
    for name in edge_file_names:
        # alpha = {feature_name: float(values) for feature_name, values in edge_feature}
        alpha = {feature_name: values for feature_name, values in edge_feature}


        # Dynamically read data based on the feature
        edge_data_frames = {}
        for i, feature in enumerate(feature_list):
            edge_data_frames[feature[0]] = pd.read_csv(os.path.join(edge_directories[i], name))

        # Determine LENGTH as the number of rows (excluding the header) in the first file
        LENGTH = len(edge_data_frames[feature_list[0][0]])

        # Initialize arrays to store scores and vectors for edges
        edge_weather_vector = np.zeros((len(feature_list), LENGTH, 2))
        edge_scores = {feature[0]: np.zeros((2, LENGTH)) for feature in feature_list}

        # Loop through each edge to find the normalized weather value
        for i in range(LENGTH):
            for feature in feature_list:
                feature_name = feature[0]
                severity = severity_levels[feature_name]

                min_val = np.array(edge_data_frames[feature_name].min(axis=1))[i]
                max_val = np.array(edge_data_frames[feature_name].max(axis=1))[i]

                edge_scores[feature_name][0, i] = findWeatherLevel(min_val, severity)
                edge_scores[feature_name][1, i] = findWeatherLevel(max_val, severity)

        # Create the normalized weather vector for edges
        for j, feature in enumerate(feature_list):
            feature_name = feature[0]
            edge_weather_vector[j, :] = np.linspace(edge_scores[feature_name][0, :], edge_scores[feature_name][1, :], num=2).T

        # Compute weather impact for both interpolated points for edges
        edge_wi1 = weatherImpact(alpha, edge_weather_vector[:, :, 0])
        edge_wi2 = weatherImpact(alpha, edge_weather_vector[:, :, 1])

        edge_wi = {feature_name: [] for feature_name in alpha}

        for feature in edge_wi:
            for low, high in zip(edge_wi1[feature], edge_wi2[feature]):
                edge_wi[feature].append((np.round(low, 3), np.round(high, 3)))

        edge_events = pd.DataFrame(edge_wi)
        edge_events.to_csv(os.path.join(edges_output_path, name), index=False)

if __name__ == "__main__":
    GENERATE_WEATHER_IMPACT()
