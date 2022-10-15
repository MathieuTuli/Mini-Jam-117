from typing import Tuple

import numpy as np


# class Coordinates:
#     def __init__(self, x: int, y: int):
#         self.x = x
#         self.y = y
#
#     def tuple(self) -> Tuple[int, int]:
#         return (self.x, self.y)
#
#     def __add__(self, other):
#         if isinstance(other, Coordinates):
#             self.x += other.x
#             self.y += other.y
#         elif isinstance(other, int) or isinstance(other, float):
#             self.x += int(other)
#             self.y += int(other)
#         return Coordinates(self.x, self.y)
#
#     def __sub__(self, other):
#         if isinstance(other, Coordinates):
#             self.x -= other.x
#             self.y -= other.y
#         elif isinstance(other, int) or isinstance(other, float):
#             self.x -= int(other)
#             self.y -= int(other)
#         return Coordinates(self.x, self.y)
#
#     def __truediv__(self, other):
#         if isinstance(other, Coordinates):
#             self.x /= other.x
#             self.y /= other.y
#         elif isinstance(other, int) or isinstance(other, float):
#             self.x /= int(other)
#             self.y /= int(other)
#         return Coordinates(self.x, self.y)
#
#     def __mult__(self, other):
#         if isinstance(other, Coordinates):
#             self.x *= other.x
#             self.y *= other.y
#         elif isinstance(other, int) or isinstance(other, float):
#             self.x *= int(other)
#             self.y *= int(other)
#         return Coordinates(self.x, self.y)


# def get_angle(p1, p2):
#     return np.arctan2(p2[1] - p1[1], p2[0] - p2[1]) * (180 / np.pi)
