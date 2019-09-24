import math

from radian import radian


def coordinate_after_rotation(c, degree, offsets):
    return (
        c[0] + math.cos(radian(degree)) * offsets[0],
        c[1] + math.sin(radian(degree)) * offsets[1]
    )