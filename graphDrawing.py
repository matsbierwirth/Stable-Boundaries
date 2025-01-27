import matplotlib.pyplot as plt

from matplotlib.collections import LineCollection
import math
import re

import sys
import os

def read_graph_from_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file {filepath} does not exist.")

    with open(filepath, 'r') as file:
        lines = file.readlines()



    # Read the first line for the metadata
    first_line = lines[0].strip().split()
    num_vertices = int(first_line[0])
    num_edges = int(first_line[1])
    tau = float(first_line[2])
    alpha =first_line[3]
    seed = int(first_line[4])
    iter = int(first_line[5])
    
    #print(tau, alpha, seed, iter)

    # Read vertex data
    vertices = []
    for i in range(1, num_vertices + 1):
        vertex_data = lines[i].strip().split()
        vertex_index = int(vertex_data[0])
        pos = (float(vertex_data[1]), float(vertex_data[2]))
        weight = float(vertex_data[3])
        color = int(vertex_data[4])
        vertices.append({
            "index": vertex_index,
            "pos": pos,
            "weight": weight,
            "color": color
        })

    # Read edge data
    edges = []
    for i in range(num_vertices + 1, num_vertices + 1 + num_edges):
        edge_data = lines[i].strip().split()
        src = int(edge_data[0])
        dest = int(edge_data[1])
        edges.append((src, dest))

    return {
        "num_vertices": num_vertices,
        "num_edges": num_edges,
        "tau": tau,
        "alpha": alpha,
        "iter": iter,
        "seed": seed,
        "vertices": vertices,
        "edges": edges
    }

def draw_graph(graph_data, split_path):
    """
    Draws a graph based on parsed data from `read_graph_from_file` and saves the plot to a file.
    
    Args:
        graph_data: Dictionary returned by `read_graph_from_file`.
        filename: The name of the file to save the plot to.
    """
    # Extract data
    vertices = graph_data["vertices"]
    edges = graph_data["edges"]

    tau = graph_data["tau"]
    
    # Clear the current figure
    plt.clf()
    plt.figure(figsize=(6.4, 6.4))
    # Prepare data for plotting
    positions = {v["index"]: v["pos"] for v in vertices}
    weights = {v["index"]: v["weight"] for v in vertices}
    colors = {v["index"]: v["color"] for v in vertices}
    
    # Plot edges
    edge_segments = []
    edge_colors = []
    for src, dest in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[dest]
        
        wrapped_x = False
        wrapped_y = False
        
        # Handle toroidal wrapping for edges
        if abs(x1 - x2) > 0.5:
            if x1 < x2:
                x1 += 1.0
            else:
                x2 += 1.0
            wrapped_x = True
        if abs(y1 - y2) > 0.5:
            if y1 < y2:
                y1 += 1.0
            else:
                y2 += 1.0
            wrapped_y = True
        
        # Add the main edge
        edge_segments.append([(x1, y1), (x2, y2)])
        
        # Determine edge color
        if colors[src] == 0 and colors[dest] == 0:
            edge_colors.append("red")
        elif colors[src] == 1 and colors[dest] == 1:
            edge_colors.append("blue")
        else:
            edge_colors.append("black")
        
        # Add wrapped edge if necessary
        if wrapped_x or wrapped_y:
            if wrapped_x:
                x1 -= 1.0
                x2 -= 1.0
            if wrapped_y:
                y1 -= 1.0
                y2 -= 1.0
            edge_segments.append([(x1, y1), (x2, y2)])
            edge_colors.append(edge_colors[-1])  # Same color as the original edge

    # Use LineCollection to draw edges
    lc = LineCollection(edge_segments, colors=edge_colors, linewidths=0.05, linestyles='-')
    plt.gca().add_collection(lc)
    
    # Prepare data for scatter plot
    x_coords = [vertex["pos"][0] for vertex in vertices]
    y_coords = [vertex["pos"][1] for vertex in vertices]
    sizes = [max(0.2,math.log(vertex["weight"])**tau) for vertex in vertices]
    #print(min(sizes), max(sizes))
    colors = ["red" if vertex["color"] == 0 else "blue" for vertex in vertices]

    # Use scatter to plot vertices
    plt.scatter(x_coords, y_coords, s=sizes, c=colors, marker=".", linewidths=0.5, zorder=2)
    
    # Adjust axes for the torus
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    
    plt.gca().set_aspect('equal', adjustable='box')
    # Save the plot to a file
    #print(split_path)
    filename = split_path[3].replace(".txt", ".png")
    file_path = f"graph_figures/{split_path[1]}/{split_path[2]}/{filename}"

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    #print(file_path)
    plt.savefig(file_path, dpi=600)

    print(f"File: {file_path} saved")
    print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python graphDrawing.py <filename>")
        return

    filepath = sys.argv[1]
    print(f"Processing file: {filepath}")
    # Add your graph drawing logic here
    #print(filepath)


    split_path = filepath.split("/")
    #print(split_path)
    graph =read_graph_from_file(filepath)

    draw_graph(graph, split_path)
    
if __name__ == "__main__":
    main()