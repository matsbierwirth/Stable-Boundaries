import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt



from matplotlib.collections import LineCollection
import math
import re
import random

import sys
import os

import matplotlib as mpl
mpl.rcParams.update({
    "font.size": 28,      # base font size
    "axes.titlesize": 30, # title
    "axes.labelsize": 28, # x and y labels
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "legend.fontsize": 24
})


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
    colorless =int(first_line[6])
    
    #print(tau, alpha, seed, iter)

    # Read vertex data
    vertices = []
    for i in range(1, num_vertices + 1):
        vertex_data = lines[i].strip().split()
        vertex_index = int(vertex_data[0])
        pos = (float(vertex_data[1])*100, float(vertex_data[2])*100)
        weight = float(vertex_data[3])
        color = int(vertex_data[4])
        neighbour_color = int(vertex_data[5])
        degree = int(vertex_data[6])
        vertices.append({
            "index": vertex_index,
            "pos": pos,
            "weight": weight,
            "color": color,
            "neighbour_col": neighbour_color,
            "degree": degree
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
        "colorless": colorless,
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

    colorless = graph_data["colorless"]
    
    # Clear the current figure
    plt.clf()
    plt.figure(figsize=(6.4, 6.4))
    # Prepare data for plotting
    positions = {v["index"]: v["pos"] for v in vertices}
    
    print(colorless)
    col= []
    landmark=219
    for vertex in vertices:
        if vertex["degree"] == 0:
            red =(vertex["color"])%2
            blue =(vertex["color"]+1)%2
        else:
            red = max(0, min(1, (1*((vertex["color"])%2) +0*(vertex["degree"]+vertex["neighbour_col"])/(2*vertex["degree"]))))
            blue =max(0, min(1, (1*((vertex["color"]+1)%2)+ +0*(vertex["degree"]-vertex["neighbour_col"])/(2*vertex["degree"]))))
        col.append((red, 0, blue))
        
    # Plot edges
    edge_segments = []
    edge_colors = []
    random.seed(42)
    for src, dest in edges:
        
        x1, y1 = positions[src]
        x2, y2 = positions[dest]
        if(random.random()<0.9):
            continue
        wrapped_x = False
        wrapped_y = False
        
        # Handle toroidal wrapping for edges
        if abs(x1 - x2) > 50:
            if x1 < x2:
                x1 += 100.0
            else:
                x1 -= 100.0
            wrapped_x = True
        if abs(y1 - y2) > 50:
            if y1 < y2:
                y1 += 100.0
            else:
                y1 -= 100.0
            wrapped_y = True
        
        # Add the main edge
        edge_segments.append([(x1, y1), (x2, y2)])
        
        # Determine edge color
        red = max(0, min(1, (col[src][0]+col[dest][0])/2))
        blue = max(0, min(1, (col[src][2]+col[dest][2])/2))
        # if(red>0 and blue>0):
        #     red=0
        #     blue=0
        
        edge_colors.append((0, 0, 0, 0.9))
        
        # Add wrapped edge if necessary
        if wrapped_x or wrapped_y:
            if wrapped_x:
                if x1<x2:
                    x1+=100.0
                    x2+=100.0
                else:
                    x1 -= 100.0
                    x2 -=100.0
            if wrapped_y:
                if y1<y2:
                    y1+=100.0
                    y2+=100.0
                else:
                    y1 -= 100.0
                    y2 -= 100.0
                
            edge_segments.append([(x1, y1), (x2, y2)])
            edge_colors.append(edge_colors[-1])
    #print(edge_colors)
    # Use LineCollection to draw edges
    lc = LineCollection(edge_segments, colors=edge_colors, linewidths=0.13, linestyles='-')
    plt.gca().add_collection(lc)
    
    # Prepare data for scatter plot
    x_coords = [vertex["pos"][0] for vertex in vertices]
    y_coords = [vertex["pos"][1] for vertex in vertices]
    sizes = [max(1,5*math.log(vertex["weight"])**2) for vertex in vertices]
    #print(min(sizes), max(sizes))

    

    #print(colors)
    # Use scatter to plot vertices
    plt.scatter(x_coords, y_coords, s=sizes, c=col, marker=".", linewidths=0.5, zorder=2)
    
    # Adjust axes for the torus
    plt.xlim(0.0, 100.0)
    plt.ylim(0.0, 100.0)
    
    plt.gca().set_aspect('equal', adjustable='box')
    # Save the plot to a file
    #print(split_path)
    filename = split_path[-1].replace(".txt", ".png")
    file_path = f"graph_figures/{split_path[1]}/{split_path[2]}/{split_path[3]}/{split_path[4]}/{filename}"

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    #print(file_path)
    plt.savefig(file_path, dpi=250)

    print(f"File: {file_path} saved")
    print()


def draw_graph_undecided(graph_data, split_path):
    vertices = graph_data["vertices"]
    edges = graph_data["edges"]
    tau = graph_data["tau"]
    vertices_undecided = {}
    for vertex in vertices:
        if (vertex["color"]==0 and vertex["neighbour_col"]>=1):
            vertices_undecided[vertex["index"]] = vertex
    
    plt.clf()
    plt.figure(figsize=(6.4, 6.4))
    # Prepare data for plotting

    print(len(vertices_undecided))
    col= []
    for vertex in vertices_undecided:
        c = (0, 0, 1)
        if abs(vertices_undecided[vertex]["neighbour_col"])>=1:
            c = (1, 0, 0)
        col.append(c)


    edge_segments = []
    edge_colors = []
    for src, dest in edges:
        if src not in vertices_undecided or dest not in vertices_undecided:
            continue
        x1, y1 = vertices_undecided[src]["pos"]
        x2, y2 = vertices_undecided[dest]["pos"]
        
        wrapped_x = False
        wrapped_y = False
        
        # Handle toroidal wrapping for edges
        if abs(x1 - x2) > 0.5:
            if x1 < x2:
                x1 += 1.0
            else:
                x1 -= 1.0
            wrapped_x = True
        if abs(y1 - y2) > 0.5:
            if y1 < y2:
                y1 += 1.0
            else:
                y1 -= 1.0
            wrapped_y = True
        
        # Add the main edge
        edge_segments.append([(x1, y1), (x2, y2)])
        
        # Determine edge color
        edge_colors.append((0, 0, 1))
        
        # Add wrapped edge if necessary
        if wrapped_x or wrapped_y:
            if wrapped_x:
                if x1<x2:
                    x1+=1.0
                    x2+=1.0
                else:
                    x1 -= 1.0
                    x2 -=1.0
            if wrapped_y:
                if y1<y2:
                    y1+=1.0
                    y2+=1.0
                else:
                    y1 -= 1.0
                    y2 -= 1.0
            edge_segments.append([(x1, y1), (x2, y2)])
            edge_colors.append(edge_colors[-1])  # Same color as the original edge
    #print(edge_colors)
    # Use LineCollection to draw edges
    lc = LineCollection(edge_segments, colors=edge_colors, linewidths=0.05, linestyles='-')
    plt.gca().add_collection(lc)
    
    # Prepare data for scatter plot
    x_coords = [vertices_undecided[vertex]["pos"][0] for vertex in vertices_undecided]
    y_coords = [vertices_undecided[vertex]["pos"][1] for vertex in vertices_undecided]
    sizes = [max(0.2,math.log(vertices_undecided[vertex]["weight"])**2) for vertex in vertices_undecided]
    #print(min(sizes), max(sizes))

    

    #print(colors)
    # Use scatter to plot vertices
    plt.scatter(x_coords, y_coords, s=sizes, c=col, marker=".", linewidths=0.5, zorder=2)
    
    # Adjust axes for the torus
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    
    plt.gca().set_aspect('equal', adjustable='box')
    # Save the plot to a file
    #print(split_path)
    filename = split_path[-1].replace(".txt", "_undecided.png")
    file_path = f"graph_figures/{split_path[1]}/{split_path[2]}/{split_path[3]}/{split_path[4]}/{filename}"

    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    #print(file_path)
    plt.savefig(file_path, dpi=300)

    print(f"File: {file_path} saved")
    print()


def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python graphDrawing.py <filename>")
    #     return

    filepath = "graph_data/n=10000_tau=2.500000/a=1000000.000000/col=rand/seed=1046534442/iteration=6777.txt" 
    #filepath =sys.argv[1]
    print(f"Processing file: {filepath}")
    # Add your graph drawing logic here
    #print(filepath)


    split_path = filepath.split("/")
    #print(split_path)
    graph =read_graph_from_file(filepath)

    draw_graph(graph, split_path)

    #draw_graph_undecided(graph, split_path)
    
if __name__ == "__main__":
    main()