import math

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon


def get_eclipse(a, b, center=(0, 0), resolution=16):
    # equation: (x-x0)**2/a + (y-y0)**2/b = 1
    x0 = center[0]
    y0 = center[1]
    theta = 0
    point_list = []
    for i in range(resolution * 4):
        x = math.cos(theta) * math.sqrt(a) + x0
        y = math.sin(theta) * math.sqrt(b) + y0
        point_list.append((x, y))
        theta += 2 * math.pi / resolution / 4
    return Polygon(point_list)


# gpd.GeoSeries([get_eclipse(5, 3, (3, 15))]).plot()
# plt.show()


def get_building(length, width, rotate_angle, center=(0, 0)):
    x = center[0]
    y = center[1]
    diagonal = math.sqrt(length ** 2 + width ** 2)
    r = diagonal / 2
    rotate_angle = math.radians(rotate_angle)
    original_angle = math.atan2(width, length)
    pointA_angle = -original_angle + rotate_angle
    pointB_angle = +original_angle + rotate_angle
    pointC_angle = math.pi - original_angle + rotate_angle
    pointD_angle = math.pi + original_angle + rotate_angle
    new_polygon = Polygon([(r * math.cos(pointA_angle) + x, r * math.sin(pointA_angle) + y),
                           (r * math.cos(pointB_angle) + x, r * math.sin(pointB_angle) + y),
                           (r * math.cos(pointC_angle) + x, r * math.sin(pointC_angle) + y),
                           (r * math.cos(pointD_angle) + x, r * math.sin(pointD_angle) + y)])
    return new_polygon


def get_building_shadow(length, width, rotation_angle, center=(0, 0), h=80):
    shadow_long = get_building(length=length + 26, width=width, rotate_angle=rotation_angle, center=center)
    shadow_height = get_building(length=length, width=2 * h, rotate_angle=rotation_angle, center=center)
    demi_shadow = shadow_long.symmetric_difference(shadow_height)
    return demi_shadow


def create_building_vertical(line, length, width, rotation_angle):
    if line.length < length:
        return None
    line

polygon2 = get_building(48, 16, 30, (0, 0))
polygon4 = get_building_shadow(48, 16, 30, (0, 0))
gdf = gpd.GeoSeries([polygon2, polygon4])
gdf.plot()
plt.show()
