import copy
import math
import random

from shapely.geometry import *
from shapely.ops import cascaded_union


def get_corners(length, width, rotate_angle, center):
    if isinstance(center, Point):
        x = center.coords[0][0]
        y = center.coords[0][1]
    else:
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
    corners = [(r * math.cos(pointA_angle) + x, r * math.sin(pointA_angle) + y),
               (r * math.cos(pointB_angle) + x, r * math.sin(pointB_angle) + y),
               (r * math.cos(pointC_angle) + x, r * math.sin(pointC_angle) + y),
               (r * math.cos(pointD_angle) + x, r * math.sin(pointD_angle) + y)]
    return corners


def get_building(length, width, rotate_angle, center=(0, 0)):
    corners = get_corners(length, width, rotate_angle, center)
    return Polygon(corners)


def get_building_shadow(length, width, rotation_angle, center=(0, 0), h=80):
    shadow_list = []
    shadow_long = get_building(length=length + 2 * 13, width=width, rotate_angle=rotation_angle, center=center)
    shadow_height = get_building(length=length, width=2 * h, rotate_angle=rotation_angle, center=center)
    shadow_list.append(shadow_long)
    shadow_list.append(shadow_height)
    corners = get_corners(length, width, rotation_angle, center)
    for corner in corners:
        shadow_list.append(Point(corner).buffer(6))
    shadow = cascaded_union(shadow_list)
    return shadow


def get_curve(pointA, pointB, pointC):
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
    return LineString(point_list)


def get_roads_v2(collection, base, max_distance):
    roads = []
    outside = base.symmetric_difference(base.envelope).buffer(-5)
    for i in range(len(collection) - 1):
        for j in range(i + 1, len(collection)):
            element1 = collection[i]
            element2 = collection[j]
            if element1.centroid.distance(element2.centroid) < max_distance:
                line = LineString([element1.centroid, element2.centroid])
                if not line.intersects(outside):
                    roads.append(line)
    return roads


def get_entrances(base, entrances_count=2, distance=100):
    coords = base.boundary.coords
    lines = []
    for i in range(len(coords)):
        line = LineString([coords[i % len(coords)], coords[(i + 1) % len(coords)]])
        lines.append(line)
    lines = sorted(lines, key=lambda line: line.length, reverse=True)
    entrances = [lines[0].centroid]
    for i in range(1, len(lines)):
        entrance = lines[i].centroid
        acceptable = True
        for other_entrance in entrances:
            if entrance.distance(other_entrance) < distance:
                acceptable = False
                break
        if acceptable:
            entrances.append(entrance)
        if len(entrances) >= entrances_count:
            break
    return [entrance.buffer(25) for entrance in entrances]


def get_buffered_sections(collection, buffer):
    new_collection_buffered = []
    for our_base in collection:
        buffered = our_base.buffer(buffer)
        if buffered.is_empty:
            continue
        elif isinstance(buffered, MultiPolygon):
            for geom in buffered:
                new_collection_buffered.append(geom)
        else:
            new_collection_buffered.append(buffered)
    return new_collection_buffered


def generate_plan(collection_buffered, overall_shadows, overall_buildings,
                  building_length=32, building_width=16, shadow_h=80, fix_angle=None):
    random.shuffle(collection_buffered)
    for our_base in collection_buffered:
        building_line = our_base
        if building_line.is_empty:
            continue
        building_line = building_line.boundary
        building_coords = building_line.coords
        k = random.choice(range(len(building_coords)))

        for i in range(k, k + len(building_coords) - 1):
            start_point = building_coords[i % len(building_coords)]
            end_point = building_coords[(i + 1) % len(building_coords)]
            startx = start_point[0]
            starty = start_point[1]
            endx = end_point[0]
            endy = end_point[1]
            line = LineString([start_point, end_point])
            if not fix_angle:
                angle = math.degrees(math.atan2(endy - starty, endx - startx))
            else:
                angle = fix_angle
            n = int(line.length / 3)
            for j in range(n):
                k = random.randint(0, n - 1)
                center = (
                    startx + ((j + k) % n) * (endx - startx) / n, starty + ((j + k) % n) * (endy - starty) / n)
                building = get_building(building_length, building_width, angle, center=center)
                shadow = get_building_shadow(building_length, building_width, angle, center=center, h=shadow_h)
                if not overall_buildings:
                    if overall_shadows.intersects(building):
                        continue
                    else:
                        overall_buildings = building
                        overall_shadows = overall_shadows.union(shadow)
                elif overall_shadows.intersects(building) or overall_buildings.intersects(shadow):
                    continue
                else:
                    overall_shadows = overall_shadows.union(shadow)
                    overall_buildings = overall_buildings.union(building)
    return overall_buildings, overall_shadows


def generate_collection(base, min_r, max_r, density=20, resolution=4, entrace_collection=[]):
    envelope = base.envelope
    minx, miny, maxx, maxy = envelope.bounds
    x_diff = maxx - minx
    y_diff = maxy - miny
    point_list = []
    for j in range(density):
        for i in range(density):
            point = Point(minx + x_diff / density * i, miny + y_diff / density * j)
            if base.buffer(-15).contains(point):
                point_list.append(point)

    collection = copy.deepcopy(entrace_collection)
    max_iteration = 200
    iter = 0
    while len(point_list) > 0 and iter < max_iteration:
        iter += 1
        first_point = random.choice(point_list)
        if len(collection) == 0:
            r = random.randint(min_r, max_r)
            circle = first_point.buffer(r, resolution)
            collection.append(circle)
            point_list.remove(first_point)
        else:
            distances = [first_point.distance(circle) for circle in collection]
            min_distance = min(distances)
            if min_distance < min_r:
                point_list.remove(first_point)
            elif min_distance > max_r:
                continue
            else:
                circle = first_point.buffer(min_distance + 1, resolution)
                collection.append(circle)
                point_list.remove(first_point)
    return collection


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
    for i in range(8):
        t = i / 8
        x = bc(ax, bx, cx, t)
        y = bc(ay, by, cy, t)
        point_list.append((x, y))
    return point_list


def mod(i, module):
    return i % module


def smooth_polygon(polygon, min_length=20, multiple_start=True):
    if not isinstance(polygon, Polygon):
        return polygon
    coords = polygon.boundary.coords
    if multiple_start:
        coords = coords[:-1]
    tuple_list = []
    n = len(coords)
    for i in range(n):
        last_coord = coords[mod(n + i - 1, n)]
        this_coord = coords[i]
        next_coord = coords[mod(n + i + 1, n)]
        min_side_length = min(Point(next_coord).distance(Point(this_coord)),
                              Point(last_coord).distance(Point(this_coord)))
        rate = min(0.5, min_length / min_side_length)
        s_point = (rate * last_coord[0] + (1 - rate) * this_coord[0], rate * last_coord[1] + (1 - rate) * this_coord[1])
        e_point = (rate * next_coord[0] + (1 - rate) * this_coord[0], rate * next_coord[1] + (1 - rate) * this_coord[1])
        curve = basic_curve(s_point, this_coord, e_point)
        tuple_list.extend(curve)
    return Polygon(tuple_list)
