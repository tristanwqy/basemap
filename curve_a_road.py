from shapely.geometry import *
import geopandas as gpd
import matplotlib.pyplot as plt

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
        return (1-t)**2*a+2*t*(1-t)*b+t**2*c + 4*(1/4-(t-1/2)**2)*(-1/4*a+b/2-1/4*c)

    point_list = []
    for i in range(101):
        t = i / 100
        x = bc(ax, bx, cx, t)
        y = bc(ay, by, cy, t)
        point_list.append((x, y))

    return LineString(point_list)

pointA = Point((-1, 6))
pointB = Point((0, 2))
pointC = Point((1, 2.5))
gpd.GeoSeries([get_curve(pointA, pointB, pointC), pointA, pointB, pointC]).plot()
plt.show()
