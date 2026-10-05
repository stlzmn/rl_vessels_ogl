import numpy as np
np.set_printoptions(suppress=True)
arr = np.array([[ 3787.0364, -2254.5244],
                [ 3788.356 , -2253.8767],
                [ 3788.356 , -2253.8767],
                [ 3792.719 , -2227.8289],
                [ 3797.9612, -2200.4856],
                [ 3819.357 , -2078.2324],
                [ 3819.797 , -2078.2324],
                [ 3849.0715, -1913.3093]])

rows_to_copy = arr[1:-1]

new_arr_size = len(arr) + len(rows_to_copy)
new_arr = np.empty((new_arr_size, arr.shape[1]))

for i in range(len(arr)):
    new_arr[i + (i >= 1)] = arr[i]

for i, row in enumerate(rows_to_copy):
    new_arr[i + 1] = row

print(new_arr)