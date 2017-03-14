import datetime
import math

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import *
from shapely.ops import cascaded_union

from mock_bases import get_mock_base
from util import get_entrances, generate_collection, get_roads_v2, smooth_polygon, get_buffered_sections, generate_plan


def generate_division(base, min_r=60, max_r=80):
    distance = math.sqrt(base.area) / 2
    entrances = get_entrances(base, distance=distance)
    collection = generate_collection(base, min_r, max_r, resolution=8, density=20, entrace_collection=entrances)
    coverage = sum([geom.intersection(base).area for geom in collection]) / base.area

    display = []
    display.extend(collection)
    display.append(base)
    roads = get_roads_v2(collection, base, 2 * max_r)
    display.extend(roads)

    cascaded_entrances = cascaded_union(entrances)
    cascaded_roads = cascaded_union([road.buffer(4) for road in roads])
    cascaded_roads = cascaded_union([cascaded_roads, cascaded_entrances])
    place_to_build = base.difference(cascaded_roads)
    new_collection = []
    if isinstance(place_to_build, Polygon):
        new_collection = [place_to_build]
    else:
        for geom in place_to_build:
            new_collection.append(geom)
    new_collection = sorted(new_collection, key=lambda geom: geom.area)
    new_collection = [smooth_polygon(geom) for geom in new_collection]

    return new_collection, cascaded_roads


def check_roads_conected(cascaded_roads):
    return isinstance(cascaded_roads, Polygon)


def get_best_divisions(base):
    def get_max_attemps(base):
        area = base.area
        if area < 10000:
            return 5
        elif area < 50000:
            return 10
        elif area < 100000:
            return 15
        else:
            return 25

    divisions = None
    cascaded_roads = None
    timeout = 0
    area_rate = 9999
    while timeout < get_max_attemps(base):
        timeout += 1
        my_divisions, my_cascaded_roads = generate_division(base)
        areas = [geom.area for geom in my_divisions]
        my_area_rate = max(areas) / min(areas)
        if check_roads_conected(my_cascaded_roads) and my_area_rate < area_rate:
            divisions = my_divisions
            cascaded_roads = my_cascaded_roads
            area_rate = my_area_rate
    return divisions, cascaded_roads


def generate_plans_by_division(divisions, cascaded_roads, plan_number=10,
                               building_length=32, building_width=16, fix_angle=None, shadow_h=80):
    plan_list = []
    for i in range(plan_number):
        overall_buildings = None
        overall_shadows = cascaded_union([base.symmetric_difference(base.envelope.buffer(1)), cascaded_roads])
        # use base.envelope.buffer in case the envelope is exactly the base
        list_to_display = []
        building_lines = []
        for buffer in range(-10, -30, -10):
            new_collection_buffered = get_buffered_sections(divisions, buffer)
            overall_buildings, overall_shadows = generate_plan(new_collection_buffered, overall_shadows,
                                                               overall_buildings, building_length=building_length,
                                                               building_width=building_width, shadow_h=shadow_h,
                                                               fix_angle=fix_angle)

        list_to_display.extend(overall_buildings)
        list_to_display.extend(divisions)
        list_to_display.append(base)
        # list_to_display.append(cascaded_roads)
        # list_to_display.extend(building_lines)
        gpd.GeoSeries(list_to_display).plot()
        plt.savefig("{}.png".format(i))
        print(len(overall_buildings))
        plan_list.append(overall_buildings)
    return plan_list


if __name__ == "__main__":
    base = get_mock_base(4)
    d1 = datetime.datetime.now()
    divisions, cascaded_roads = get_best_divisions(base)
    gpd.GeoSeries(divisions).plot()
    plans = generate_plans_by_division(divisions, cascaded_roads, plan_number=10)
    print(datetime.datetime.now() - d1)
    # plt.show()
