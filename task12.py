from os.path import join
import os
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from task9_fast import jacobi_cupy, load_building_ids, load_data, summary_stats


LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
OUT_DIR = 'task12_results'


def solve_buildings(building_ids, max_iter):
    n_buildings = len(building_ids)
    all_u0 = np.empty((n_buildings, 514, 514))
    all_interior_mask = np.empty((n_buildings, 512, 512), dtype='bool')

    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    all_u = jacobi_cupy(all_u0, all_interior_mask, max_iter)

    results = []
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        results.append({'building_id': bid, **stats})

    return results

#histogram lavet af chatten lol
def save_histograms(df):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    columns = [
        'mean_temp',
        'std_temp',
        'pct_above_18',
        'pct_below_15',
    ]
    titles = [
        'Mean temperatures',
        'Temperature standard deviations',
        'Area above 18 C',
        'Area below 15 C',
    ]

    for ax, column, title in zip(axes.ravel(), columns, titles):
        ax.hist(df[column], bins=40, color='steelblue', edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel(column)
        ax.set_ylabel('Number of buildings')

    fig.tight_layout()
    fig.savefig(join(OUT_DIR, 'histograms.png'), dpi=200)
    plt.close(fig)


def print_answers(df, total_time):
    avg_mean_temp = df['mean_temp'].mean()
    avg_std_temp = df['std_temp'].mean()
    n_above_18 = (df['pct_above_18'] >= 50).sum()
    n_below_15 = (df['pct_below_15'] >= 50).sum()

    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Number of buildings: {len(df)}")
    print(f"Average mean temperature: {avg_mean_temp:.4f}")
    print(f"Average temperature standard deviation: {avg_std_temp:.4f}")
    print(f"Buildings with at least 50% area above 18 C: {n_above_18}")
    print(f"Buildings with at least 50% area below 15 C: {n_below_15}")
    print(f"Results CSV: {join(OUT_DIR, 'results.csv')}")
    print(f"Histograms: {join(OUT_DIR, 'histograms.png')}")


if __name__ == '__main__':
    max_iter = 20_000
    all_building_ids = load_building_ids(LOAD_DIR)

    os.makedirs(OUT_DIR, exist_ok=True)

    warmup_u0, warmup_mask = load_data(LOAD_DIR, all_building_ids[0])
    jacobi_cupy(warmup_u0[None, :, :], warmup_mask[None, :, :], 10)

    start = time.perf_counter()
    all_results = solve_buildings(all_building_ids, max_iter)
    total_time = time.perf_counter() - start

    df = pd.DataFrame(all_results)
    df.to_csv(join(OUT_DIR, 'results.csv'), index=False)
    save_histograms(df)
    print_answers(df, total_time)
