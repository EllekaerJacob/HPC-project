from os.path import join
import sys
import time

import cupy as cp
import numpy as np


@cp.fuse()
def fused_jacobi_update(left, right, up, down, center, mask):
    return cp.where(mask, 0.25 * (left + right + up + down), center)


def load_building_ids(load_dir):
    with open(join(load_dir, 'building_ids.txt'), 'r') as f:
        return f.read().splitlines()


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi_cupy(u, interior_mask, max_iter):
    current = cp.asarray(u, dtype=cp.float64)
    next_grid = cp.array(current, copy=True)
    mask = cp.asarray(interior_mask, dtype=cp.bool_)

    for i in range(max_iter):
        next_grid[:, 1:-1, 1:-1] = fused_jacobi_update(
            current[:, 1:-1, :-2],
            current[:, 1:-1, 2:],
            current[:, :-2, 1:-1],
            current[:, 2:, 1:-1],
            current[:, 1:-1, 1:-1],
            mask,
        )
        current, next_grid = next_grid, current

    cp.cuda.Stream.null.synchronize()
    return cp.asnumpy(current)


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])

    building_ids = load_building_ids(LOAD_DIR)[:N]

    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    MAX_ITER = 20_000

    jacobi_cupy(all_u0[:1], all_interior_mask[:1], 10)

    start = time.perf_counter()
    all_u = jacobi_cupy(all_u0, all_interior_mask, MAX_ITER)
    end = time.perf_counter()

    total_time = end - start
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Time per building: {total_time / N:.2f} seconds")
    print(f"Estimated time for all 4571 buildings: {total_time / N * 4571 / 60:.2f} minutes")

    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
