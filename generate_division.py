import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import *
from shapely.ops import cascaded_union

from mock_bases import get_mock_base
from util import get_entrances, generate_collection, get_roads_v2, smooth_polygon


def generate_division(base):
    entrances = get_entrances(base, distance=400)
    collection = generate_collection(base, 60, 80, resolution=8, density=20, entrace_collection=entrances)
    coverage = sum([geom.intersection(base).area for geom in collection]) / base.area

    display = []
    display.extend(collection)
    display.append(base)
    roads = get_roads_v2(collection, base, 160)
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
    new_collection = sorted(new_collection, key=lambda geom: geom.area, reverse=True)
    new_collection = [smooth_polygon(geom) for geom in new_collection]

    return new_collection, cascaded_roads


def check_roads_conected(cascaded_roads):
    return isinstance(cascaded_roads, Polygon)


def get_best_divisions():
    new_collection = None
    cascaded_roads = None
    timeout = 0
    area_rate = 9999
    while timeout < 30:
        timeout += 1
        my_collection, my_cascaded_roads = generate_division(base)
        areas = [geom.area for geom in my_collection]
        my_area_rate = max(areas) / min(areas)
        if check_roads_conected(my_cascaded_roads) and my_area_rate < area_rate:
            new_collection = my_collection
            cascaded_roads = my_cascaded_roads
            area_rate = my_area_rate
    return new_collection, cascaded_roads

if __name__ == "__main__":
    base = get_mock_base(3)

    new_collection = None
    cascaded_roads = None
    timeout = 0
    area_rate = 9999
    while timeout < 30:
        timeout += 1
        my_collection, my_cascaded_roads = generate_division(base)
        areas = [geom.area for geom in my_collection]
        my_area_rate = max(areas)/min(areas)
        if check_roads_conected(my_cascaded_roads) and my_area_rate < area_rate:
            new_collection = my_collection
            cascaded_roads = my_cascaded_roads
            area_rate = my_area_rate

    gpd.GeoSeries(new_collection).plot()
    plt.show()
