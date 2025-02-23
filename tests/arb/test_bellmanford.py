import numpy as np
import pytest
from scipy.sparse import csr_array

from arb.bellmanford import BellmanFord

def test_original():
    data = [10, 8, 2, 1, -2, -4, -1, 1] # az élek értéke / költsége
    row =  [ 0, 0, 1, 2,  3,  4,  4, 5] # induló csomópont
    col =  [ 1, 5, 3, 1,  2,  1,  3, 4] # érkező csomópont
    mat = csr_array((data, (row, col)))

    dist, arbitrage, prev = BellmanFord(mat)

    np.testing.assert_array_equal(dist, [[0, 5, 5, 7, 9, 8], 
                    [np.inf, 0, 0, 2, np.inf, np.inf], 
                    [np.inf, 1, 0, 3, np.inf, np.inf], 
                    [np.inf, -1, -2, 0, np.inf, np.inf],
                    [np.inf, -4, -4, -2, 0, np.inf],
                    [np.inf, -3, -3, -1, 1, 0]])
    np.testing.assert_array_equal(arbitrage, [False] * 6)

def test_trio():
    # 0 -> 1 : 10
    # 1 -> 0 : 10
    # 1 -> 2 : 10
    # 2 -> 1 : 10
    # 0 -> 2 : 10
    # 2 -> 0 : -15
    data = [10, 10, 10, 10, 10, -15] # az élek értéke / költsége
    row =  [ 0,  1,  1,  2,  0,   2] # induló csomópont
    col =  [ 1,  0,  2,  1,  2,   0] # érkező csomópont
    mat = csr_array((data, (row, col)))

    dist, arbitrage, prev = BellmanFord(mat)
    np.testing.assert_array_equal(dist, 
                        [[-5, 10, 10],
                        [-10, 0, 0],
                        [-15, -5, -5]])
    np.testing.assert_array_equal(arbitrage, [True, False, True])
    np.testing.assert_array_equal(prev, 
                                [[2, 0, 0],
                                [2, -1, 0],
                                [2, 0, 0]])
