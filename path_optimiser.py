from itertools import permutations
from typing import List, Tuple

from constants import *


def get_distance(coord1: Tuple, coord2: Tuple) -> float:
    lat_diff = coord1[0] - coord2[0]
    lon_diff = coord1[1] - coord2[1]

    dist = (lat_diff**2 + lon_diff**2) ** (0.5)
    return dist


# def rotate_to_start(start: Tuple, path: Tuple[Tuple]) -> List[Tuple]:
#     path_list = list(path)
#     while True:
#         if path_list[0] != start:
#             path_list = path_list[1:] + path_list[:1]
#         else:
#             break
#     return path_list


async def optimize_path(coords_list: List[Tuple]) -> List[Tuple]:
    opt_path = None
    optt_length = float("inf")
    all_permutations = permutations(coords_list)
    for path in all_permutations:
        print(f"path: {path}")
        total_length = 0
        for i in range(len(path) - 1):
            total_length += get_distance(path[i], path[i + 1])
        print(total_length, optt_length)
        if total_length < optt_length:
            optt_length = total_length
            opt_path = path
    return list(opt_path)
