"""
__author__ = Yash Patel
__name__   = contract.py
__description__ = Main contractions script
"""

import numpy as np
import networkx as nx
import matplotlib
import random
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from setup.sbm import create_sbm, create_clusters
from analysis.pca import plot_pca
from analysis.deanonymize import draw_partitions, calc_accuracy, deanonymize
from blockchain.read import create_simple_graph

def _contract_edges(G, num_edges):
    identified_nodes = {}
    for _ in range(num_edges):
        edges = list(G.edges)
        random_edge = edges[random.randint(0,len(edges)-1)]
        node_to_contract = random_edge[1]
        identified_nodes[node_to_contract] = random_edge[0] # right gets contracted into left
        G = nx.contracted_edge(G, random_edge)
    return G, identified_nodes

def _reconstruct_contracted(identified_nodes, partitions):
    for contracted in identified_nodes:
        for partition in partitions:
            if identified_nodes[contracted] in partition:
                partition.add(contracted)
                break
    return partitions

def plot_graphs(G, contracted_G):
    print("Plotting contracted graph...")
    contracted_pos = nx.spring_layout(contracted_G)
    nx.draw(contracted_G, contracted_pos)
    plt.axis('off')
    plt.savefig("output/contraction/graph.png")
    plt.close()

    spring_pos = nx.spring_layout(G)
    draw_partitions(G, spring_pos, clusters, 
        "contraction/truth.png", weigh_edges=False)
    draw_partitions(G, spring_pos, hier_partitions, 
        "contraction/eigen_guess.png", weigh_edges=False)
    draw_partitions(G, spring_pos, kmeans_partitions, 
        "contraction/kmeans_guess.png", weigh_edges=False)

def contract_deanonymize(G, k, to_contract, to_plot=False):
    contracted_G, identified_nodes = _contract_edges(G, num_edges=to_contract)

    hier_partitions, kmeans_partitions = deanonymize(contracted_G, k=k)
    hier_partitions   = _reconstruct_contracted(identified_nodes, hier_partitions)
    kmeans_partitions = _reconstruct_contracted(identified_nodes, kmeans_partitions)

    if to_plot:
        plot_graphs(G, contracted_G)
    return hier_partitions, kmeans_partitions

def single_contract_test(params):
    cluster_size = 8
    num_clusters = 5
    cluster_sizes = [cluster_size] * num_clusters
    clusters = create_clusters(cluster_sizes)

    G = create_sbm(clusters, params["p"], params["q"], False)
    to_contract = int(len(G.edges) * params["percent_edges"])

    num_clusters = len(clusters)
    hier_partitions, kmeans_partitions = contract_deanonymize(G, 
        k=num_clusters, to_contract=to_contract)
    
    hier_accuracy   = calc_accuracy(clusters, hier_partitions)
    kmeans_accuracy = calc_accuracy(clusters, kmeans_partitions)

    print("hierarchical accuracy: {}".format(hier_accuracy))
    print("k-means accuracy: {}".format(kmeans_accuracy))
    return hier_accuracy, kmeans_accuracy

def contract_tests():
    edge_percents = np.arange(0, .30, 0.03)
    num_trials    = 10

    for p in np.arange(0, 1.0, 0.1):
        for q in np.arange(0, p, 0.1):
            hier_accuracies   = []
            kmeans_accuracies = []

            for percent_edges in edge_percents:
                hier_trial   = []
                kmeans_trial = []
                
                for trial in range(num_trials):
                    params = {
                        "p"          : .75,
                        "q"          : 0.15,
                        "percent_edges"  : 0.0,
                    }
                    
                    hier_accuracy, kmeans_accuracy = single_contract_test(params)
                    hier_trial.append(hier_accuracy)
                    kmeans_trial.append(kmeans_accuracy)

                hier_accuracies.append(np.median(hier_trial))
                kmeans_accuracies.append(np.median(kmeans_trial))

            for graph_type, accuracy in \
                zip(["hierarchical","kmeans"], [hier_accuracies,kmeans_accuracies]):

                plt.title("{} {} {}".format(graph_type,p,q))
                plt.plot(edge_percents, accuracy)
                plt.savefig("output/contraction/{}_{}_{}.png".format(graph_type,p,q))
                plt.close()

if __name__ == "__main__":
    contract_tests()