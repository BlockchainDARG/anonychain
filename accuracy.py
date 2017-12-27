"""
__author__ = Yash Patel
__name__   = accuracy.py
__description__ = Runs tests on the spectral clustering deanonymization scripts
to see performance in hierarchical clustering vs. k-means. Does tests over
various values of p, q, and cluster sizes
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from setup.sbm import create_sbm, create_clusters
from analysis.deanonymize import calc_accuracy, deanonymize

def conduct_tests(ps, qs, css):
    """Given lists of p probabilities, q probabilities, and lists of cluster sizes,
    runs tests on clustering accuracies (both hierarchical and k-means)

    Returns void
    """
    trials = 5
    
    for cs in css:
        clusters = create_clusters(cs)

        for p in ps:
            hier_accuracies, kmeans_accuracies = [], []
            for i, q in enumerate(qs):
                if q > p: break
                
                hier_trials, kmeans_trials = [], []
                for _ in range(trials):
                    sbm = create_sbm(clusters, p, q)
                    hier_partitions, kmeans_partitions = deanonymize(sbm, k=len(clusters))
                    hier_accuracy   = calc_accuracy(clusters, hier_partitions)
                    kmeans_accuracy = calc_accuracy(clusters, kmeans_partitions)

                    hier_trials.append(hier_accuracy)
                    kmeans_trials.append(kmeans_accuracy)

                hier_accuracies.append(np.mean(hier_trials))
                kmeans_accuracies.append(np.mean(kmeans_trials))

            print("Completed accuracy for: p={}, cs={}".format(p, cs))
            for accuracies, label in zip([hier_accuracies, kmeans_accuracies],
                ["hierarchical", "kmeans"]):

                fig = plt.figure()
                plt.scatter(qs[:i], accuracies)
                
                plt.title("{} vs. q (p={}_cs={})".format(label, p,cs))
                plt.xlabel("q")
                plt.ylabel("accuracy (%_correct)")

                plt.savefig("output/accuracy/p={}_cs={}_{}.png".format(p, cs, label))
                plt.close()

def main():
    ps  = [i / 10 for i in range(10)]
    qs  = [i / 10 for i in range(10)]

    css = [
        [5,4,3,2]
    ]

    conduct_tests(ps, qs, css)
    
if __name__ == "__main__":
    main()