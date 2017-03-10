import math
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.affinity import rotate
from shapely.geometry import *


def get_eclipse(a, b, center=(0, 0), rotation=0, use_radians=False, resolution=16):
    # equation: (x-x0)**2/a + (y-y0)**2/b = 1
    if isinstance(center, Point):
        x0 = center.x
        y0 = center.y
    else:
        x0 = center[0]
        y0 = center[1]
    theta = 0
    theta_end = math.pi * 2
    point_list = []
    for i in range(resolution * 4 + 1):
        x = math.cos(theta) * a + x0
        y = math.sin(theta) * b + y0
        point_list.append((x, y))
        theta += theta_end / resolution / 4
    Polygon = LineString(point_list)
    return rotate(Polygon, rotation, use_radians=use_radians)


def get_curve(line_string):
    coords = line_string.coords
    pointa = coords[0]
    pointb = coords[1]
    pointc = coords[2]
    line_ac = LineString([pointa, pointc])
    rotate_angle = math.atan2(pointc[1] - pointa[1], pointc[0] - pointa[0])
    centroid_b = line_ac.centroid
    a = line_ac.length / 2
    b = line_ac.distance(Point(pointb))
    print(line_string.project(line_ac), Point(pointb).distance(line_ac))
    gpd.GeoSeries([line_string, line_ac, centroid_b]).plot()
    plt.show()
    return None


def basic_curve(pointA, pointB, pointC):
    if isinstance(pointA, Point):
        ax = pointA.x
        ay = pointA.y
    else:
        ax = pointA[0]
        ay = pointA[1]
    if isinstance(pointB, Point):
        bx = pointB.x
        by = pointB.y
    else:
        bx = pointB[0]
        by = pointB[1]
    if isinstance(pointC, Point):
        cx = pointC.x
        cy = pointC.y
    else:
        cx = pointC[0]
        cy = pointC[1]

    def bc(a, b, c, t):
        return (1 - t) ** 2 * a + 2 * t * (1 - t) * b + t ** 2 * c

    point_list = []
    for i in range(100):
        t = i / 100
        x = bc(ax, bx, cx, t)
        y = bc(ay, by, cy, t)
        point_list.append((x, y))
    return point_list


def mod(i, module):
    return i % module


def smooth_polygon(polygon, min_length=10, multiple_start=True):
    coords = polygon.boundary.coords
    if multiple_start:
        coords = coords[:-1]
    tuple_list = []
    n = len(coords)
    for i in range(n):
        last_coord = coords[mod(n+i-1, n)]
        this_coord = coords[i]
        next_coord = coords[mod(n+i+1, n)]
        min_side_length = min(Point(next_coord).distance(Point(this_coord)), Point(last_coord).distance(Point(this_coord)))
        rate = min(0.5, min_length / min_side_length)
        s_point = (rate*last_coord[0]+(1-rate)*this_coord[0], rate*last_coord[1]+(1-rate)*this_coord[1])
        e_point = (rate*next_coord[0]+(1-rate)*this_coord[0], rate*next_coord[1]+(1-rate)*this_coord[1])
        curve = basic_curve(s_point, this_coord, e_point)
        tuple_list.extend(curve)
    return Polygon(tuple_list)


polygon = Polygon([(432.745700526681, 297.1757548825801),
                   (525.9844431099502, 282.9700939815971),
                   (511.2150655059379, 180.1481674567808),
                   (432.745700526681, 297.1757548825801)])
# get_curve(line)
poly = smooth_polygon(polygon)
gpd.GeoSeries([polygon, poly]).plot()
plt.show()
sys.exit()


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
