import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import KDTree
rng = np.random.default_rng()
points = rng.random((20, 2))
print(points)
plt.figure(figsize=(6, 6))
plt.plot(points[:, 0], points[:, 1], "xk", markersize=14)
kd_tree = KDTree(points)
pairs = kd_tree.query_pairs(r=0.2)
for (i, j) in pairs:
    plt.plot([points[i, 0], points[j, 0]],
            [points[i, 1], points[j, 1]], "-r")
    print(i, j)
plt.show()