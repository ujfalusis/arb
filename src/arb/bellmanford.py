import numpy as np
from scipy.sparse import csr_array

# https://www.youtube.com/watch?v=obWXjtg0L64
def BellmanFord(graph: csr_array):
    # xx = 0
    n = graph.shape[0]
    dist = np.full((n, n), np.inf)
    prev = np.full((n, n), -1, dtype=np.int16)
    for k in range(n): # calculate shortest path from all nodes (k) to all nodes (j) of the graph
        dist[k, k] = 0
        arbitrageFound = False
        for i in range(n): # iterate n-1 times, plus 1 because of arbitrage 
            changed = False
            for j in list(range(k, n)) + list(range(k)): # 'to all nodes (j)' except k
                # xx += 1
                li, hi = int(graph.indptr[j]), int(graph.indptr[j + 1])
                if li < hi and ~np.isinf(dist[k, j]):
                    # xx += 1
                    # for j:
                    #   all out edges:
                    #       connected node cost: min(current cost, cost to j + edge)
                    s = slice(li, hi)
                    outcosts = graph.data[s] # costs of outgoing edges from j
                    outnodes = graph.indices[s] # connected nodes indexes in csr_array
                    lowersi = np.where(outcosts + dist[k, j] < dist[k, outnodes])[0]
                    nodes = [outnodes[i] for i in lowersi] # lower nodes indecis
                    costs = [outcosts[i] + dist[k, j] for i in lowersi] # lower nodes costs
                    if nodes:
                        changed = True
                    if i == n - 1: # number of 0..n-2 is n-1
                        # if changed: # and newval[k] != dist[k, k]:
                        #     arbitrage[k] = True
                        pass
                    elif nodes:
                        dist[k, nodes] = costs
                        # print(f'j: {j}, idx_cols: {idx_cols}')
                        prev[k, nodes] = j
                        # if k == 4:
                        #     print(f'k: {k}, i: {i}, j: {j}, distk: {dist[k]}, nodes: {nodes}, costs: {costs}, prevk: {prev[k]}')
                        if dist[k, k] < 0:
                            arbitrageFound = True
                            break
                    else:
                        pass # last cycle is only for check arbitrage 
            if arbitrageFound:
                break
            if not changed:
                break
        if arbitrageFound:
            continue
    arbitrage = (dist.diagonal() < 0).tolist()     
    # print(f'xx: {xx}')   
    return dist, arbitrage, prev
