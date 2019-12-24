import torch


MAX_EXTENT = 1


class ComputeGraph(object):
    def __init__(self, x, edge_index, node_type_index, edge_type_index):
        self.x = x
        self.edge_index = edge_index
        self.node_type_index = node_type_index
        self.edge_type_index = edge_type_index
        self.num_nodes = len(x)
        self.num_edges = len(edge_index[0])
        self.num_node_type = len(node_type_index) - 1
        self.num_edge_type = len(edge_type_index) - 1
        self.in_channel = len(x[0])

    def to(self, device="cpu:0"):
        self.x = self.x.to(device)
        self.edge_index = self.edge_index.to(device)
        self.node_type_index = self.node_type_index.to(device)
        self.edge_type_index = self.edge_type_index.to(device)


def graph_gemm(M, N, K):
    x = torch.FloatTensor(
        [
            [M, 0, 0, 0],  # 0, tensor nodes
            [K, 0, 0, 0],  # 1
            [1, 0, 0, 0],  # 2
            [K, 0, 0, 0],  # 3
            [N, 0, 0, 0],  # 4
            [1, 0, 0, 0],  # 5
            [M, 0, 0, 0],  # 6
            [N, 0, 0, 0],  # 7
            [1, 0, 0, 0],  # 8
            [0, M, 0, 0],  # 9, spatial nodes
            [0, N, 0, 0],  # 10
            [0, 0, K, 0]   # 11, reduce nodes
            # add nodes
        ]
    ) / MAX_EXTENT
    edge_index = torch.LongTensor(
        [
            [0, 0],  # self edge
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 5],
            [6, 6],
            [7, 7],
            [8, 8],
            [9, 9],
            [10, 10],
            [11, 11],
            [0, 1],  # stride edge
            [1, 0],
            [1, 2],
            [2, 1],
            [3, 4],
            [4, 3],
            [4, 5],
            [5, 4],
            [6, 7],
            [7, 6],
            [7, 8],
            [8, 7],
            [0, 9],  # read edge
            [9, 0],
            [1, 10],
            [10, 1],
            [3, 10],
            [10, 3],
            [4, 11],
            [11, 4],
            [6, 9],  # write edge
            [9, 6],
            [7, 11],
            [11, 7],
            # add edge
        ]
    ).t()

    node_type_index = torch.LongTensor([0, 9, 11, 12, 12])
    edge_type_index = torch.LongTensor([0, 12, 24, 32, 36, 36])

    g = ComputeGraph(x, edge_index, node_type_index, edge_type_index)

    return g