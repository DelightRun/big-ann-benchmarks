from __future__ import absolute_import
import numpy as np
from benchmark.plotting.eval_range_search import compute_AP


def get_recall_values(true_nn, run_nn, count):
    true_nn, _ = true_nn
    true_nn = true_nn[:, :count]
    assert true_nn.shape == run_nn.shape
    recalls = np.zeros(len(run_nn))
    # TODO probably not very efficient
    for i in range(len(run_nn)):
        recalls[i] = len(set(true_nn[i]) & set(run_nn[i]))
    return (np.mean(recalls) / float(count),
            np.std(recalls) / float(count),
            recalls)

def knn(true_nn, run_nn, count, metrics):
    if 'knn' not in metrics:
        print('Computing knn metrics')
        knn_metrics = metrics.create_group('knn')
        mean, std, recalls = get_recall_values(true_nn, run_nn, count)
        knn_metrics.attrs['mean'] = mean
        knn_metrics.attrs['std'] = std
        knn_metrics['recalls'] = recalls
    else:
        print("Found cached result")
    return metrics['knn']

def ap(true_nn, run_nn):
    gt_nres, gt_I, gt_D = true_nn
    nq = gt_nres.shape[0]
    gt_lims = np.zeros(nq + 1, dtype=int)
    gt_lims[1:] = np.cumsum(gt_nres)
    return compute_AP((gt_lims, gt_I, gt_D), run_nn)

def queries_per_second(nq, attrs):
    return nq / attrs["best_search_time"]


def index_size(attrs):
    return attrs.get("index_size", 0)


def build_time(attrs):
    return attrs.get("build_time", 1e6)


def dist_computations(nq, attrs):
    return attrs.get("dist_comps", 0) / (attrs['run_count'] * nq)


all_metrics = {
    "k-nn": {
        "description": "Recall",
        "function": lambda true_nn, run_nn, metrics, run_attrs: knn(true_nn, run_nn, run_attrs["count"], metrics).attrs['mean'],  # noqa
        "worst": float("-inf"),
        "lim": [0.0, 1.03],
    },
    "ap": {
        "description": "Average Precision",
        "function": lambda true_nn, run_nn, metrics, run_attrs: ap(true_nn, run_nn),  # noqa
        "worst": float("-inf"),
        "lim": [0.0, 1.03],
        "search_type" : "range",
    },
    "qps": {
        "description": "Queries per second (1/s)",
        "function": lambda true_nn, run_nn, metrics, run_attrs: queries_per_second(len(true_nn[0]), run_attrs),  # noqa
        "worst": float("-inf")
    },
    "distcomps": {
        "description": "Distance computations",
        "function": lambda true_nn, run_nn,  metrics, run_attrs: dist_computations(len(true_nn[0]), run_attrs), # noqa
        "worst": float("inf")
    },
    "build": {
        "description": "Build time (s)",
        "function": lambda true_nn, run_nn, metrics, run_attrs: build_time(run_attrs), # noqa
        "worst": float("inf")
    },
    "indexsize": {
        "description": "Index size (kB)",
        "function": lambda true_nn, run_nn, metrics, run_attrs: index_size(run_attrs),  # noqa
        "worst": float("inf")
    },
    "queriessize": {
        "description": "Index size (kB)/Queries per second (s)",
        "function": lambda true_nn, run_nn, metrics, run_attrs: index_size(run_attrs) / queries_per_second(len(true_nn[0]), run_attrs), # noqa
        "worst": float("inf")
    }
}
