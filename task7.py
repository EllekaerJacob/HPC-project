from os.path import join
import sys

import numpy as np

import matplotlib.pyplot as plt

import multiprocessing

import time 

from numba import jit



n_workers=int(sys.argv[2])

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u


@jit(nopython=True)
def single_jaciter_jit(u):
    rows,cols=np.shape(u)
    u_new=np.zeros((rows-2,cols-2))
    for i in range(1,rows-1):
        for j in range(1,cols-1):
            u_new[i-1,j-1]=0.25*(u[i-1,j]+u[i+1,j]+u[i,j-1]+u[i,j+1])
    return u_new


def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
        u_new=single_jaciter_jit(u)
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

@jit(nopython=True)
def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u=np.copy(u)
    rows,cols=np.shape(u)
    for it in range(max_iter):
        delta=0.0
        u_new=np.zeros((rows-2,cols-2))
        for i in range(1,rows-1):
            for j in range(1,cols-1):
                u_new[i-1,j-1]=0.25*(u[i-1,j]+u[i+1,j]+u[i,j-1]+u[i,j+1])
        for i in range(1,rows-1):
            for j in range(1,cols-1):
                if interior_mask[i-1,j-1]:
                    diff =abs(u[i,j]-u_new[i-1,j-1])
                    u[i,j]=u_new[i-1,j-1]
                    if diff > delta:
                        delta=diff
        if delta < atol:
            break
                    
    return u





def jacobi_multiple(multiple_u,multiple_mask,max_iter,tol=1e-6):
    return np.array([jacobi(u_single,mask_single,max_iter,tol) for (u_single,mask_single) in zip(multiple_u,multiple_mask)])




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

    warmup=np.ones((10,10))
    single_jaciter_jit(warmup)
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    def worker(args):
        u, mask = args
        return jacobi_jit(u, mask, MAX_ITER, ABS_TOL)
    T0=time.perf_counter()
    with multiprocessing.Pool(n_workers) as pool:
        all_u=np.array(list(pool.imap(worker,zip(all_u0,all_interior_mask),chunksize=1)))
    print(f"Total time: {time.perf_counter()-T0}")
    print(np.shape(all_u))
    
    


    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
    plt.imshow(all_u[0],cmap="plasma")
    plt.colorbar()
    plt.title(f"results for building {building_ids[0]}")
    plt.savefig(f"results_{building_ids[0]}.png")