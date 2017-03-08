##############################################################################################################
#
#	Python implementation of the Delaunay triangulation algorithm 
#	as described in http://paulbourke.net/papers/triangulate/
#
#	developed by PanosRCng, https://github.com/PanosRCng
#
#
#	--> module usage
#		after imported, call the getTriangulation(vertex_list)
#		
#		the vertex_list is a list with instances of the Vertex class (as defined in this file)
#		returns the vertex_list, and a list with instances of the Triangle class (as defined in this file)
#
#	(!) duplicate points will result in undefined behavior
#



def getTriangulation(vertex_list):
    global V

    V = vertex_list

    # initialize the triangle list
    triangle_list = []

    # determine the supertriangle
    superTriangle = getSuperTriangle()

    # add the supertriangle to the triangle list
    triangle_list.append(superTriangle)

    # for each sample point in the vertex list
    for point in V[:-3]:

        # initialize the edge buffer
        edge_buffer = {}

        # for each triangle currently in the triangle list
        for triangle in triangle_list[:]:

            # if the point lies in the triangle circumcircle
            if triangle.isInCircumcircle(point):

                # add the three triangle edges to the edge buffer
                # delete all doubly specified edges from the edge buffer
                # this leaves the edges of the enclosing polygon only

                for edge in triangle.edges:
                    if edge.id in edge_buffer.keys():
                        edge_buffer.pop(edge.id)
                    else:
                        edge_buffer[edge.id] = edge

                # remove the triangle from the triangle list
                triangle_list.remove(triangle)

        # add to the triangle list all triangles formed between the point
        # and the edges of the enclosing polygon
        for edge_id in edge_buffer.keys():
            triangle_list.append(Triangle(point, edge_buffer[edge_id].A, edge_buffer[edge_id].B))

    print
    len(triangle_list)

    # remove any triangles from the triangle list that use the supertriangle vertices
    sv = [superTriangle.A, superTriangle.B, superTriangle.C]

    for triangle in triangle_list[:]:
        if (triangle.A in sv) or (triangle.B in sv) or (triangle.C in sv):
            triangle_list.remove(triangle)

    # remove the supertriangle vertices from the vertex list
    del V[-3:]

    return [V, triangle_list]


def getSuperTriangle():
    # find the maximum and minimum vertex bounds.
    # this is to allow calculation of the bounding triangle

    xmin = V[0].x
    ymin = V[0].y
    xmax = xmin
    ymax = ymin

    for point in V[1:]:
        if point.x < xmin: xmin = point.x
        if point.x > xmax: xmax = point.x
        if point.y < ymin: ymin = point.y
        if point.y > ymax: ymax = point.y

    dx = xmax - xmin;
    dy = ymax - ymin;

    dmax = dx if (dx > dy) else dy
    xmid = (xmax + xmin) / 2.0
    ymid = (ymax + ymin) / 2.0

    # add supertriangle vertices to the end of the vertex list
    V1 = Vertex((xmid - 2.0 * dmax, ymid - dmax))
    V2 = Vertex((xmid, ymid + 2.0 * dmax))
    V3 = Vertex((xmid + 2.0 * dmax, ymid - dmax))

    V.append(V1)
    V.append(V2)
    V.append(V3)

    return Triangle(V1, V2, V3)


#######################################################################################################################################

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y


#######################################################################################################################################

class Edge:
    def __init__(self, A, B):

        if A.x <= B.x:
            self.A = A
            self.B = B
            self.id = (A, B)
        else:
            self.A = B
            self.B = A
            self.id = (B, A)


#######################################################################################################################################

class Triangle:
    EPSILON = 0.0000000001

    def __init__(self, A, B, C):

        self.A = A
        self.B = B
        self.C = C

        self.a = Edge(A, B)
        self.b = Edge(B, C)
        self.c = Edge(C, A)

        self.edges = [self.a, self.b, self.c]

        self.circumcircle_center = Vertex((0, 0))
        self.circumcircle_radius = 0.0
        # self.rsqr = 0.0

        self.Circumcircle()

    def Circumcircle(self):

        if ((abs(self.A.y - self.B.y) < self.EPSILON) and (abs(self.B.y - self.C.y) < self.EPSILON)):
            print("CircumCircle: Points are coincident.")

            return False

        if (abs(self.B.y - self.A.y) < self.EPSILON):
            m2 = - (self.C.x - self.B.x) / float(self.C.y - self.B.y)
            mx2 = (self.B.x + self.C.x) / 2.0
            my2 = (self.B.y + self.C.y) / 2.0
            self.circumcircle_center.x = (self.B.x + self.A.x) / 2.0
            self.circumcircle_center.y = m2 * (self.circumcircle_center.x - mx2) + my2

        elif (abs(self.C.y - self.B.y) < self.EPSILON):
            m1 = - (self.B.x - self.A.x) / float(self.B.y - self.A.y)
            mx1 = (self.A.x + self.B.x) / 2.0
            my1 = (self.A.y + self.B.y) / 2.0
            self.circumcircle_center.x = (self.C.x + self.B.x) / 2.0
            self.circumcircle_center.y = m1 * (self.circumcircle_center.x - mx1) + my1

        else:
            m1 = - (self.B.x - self.A.x) / float(self.B.y - self.A.y)
            m2 = - (self.C.x - self.B.x) / float(self.C.y - self.B.y)
            mx1 = (self.A.x + self.B.x) / 2.0
            mx2 = (self.B.x + self.C.x) / 2.0
            my1 = (self.A.y + self.B.y) / 2.0
            my2 = (self.B.y + self.C.y) / 2.0
            self.circumcircle_center.x = (m1 * mx1 - m2 * mx2 + my2 - my1) / float(m1 - m2)
            self.circumcircle_center.y = m1 * (self.circumcircle_center.x - mx1) + my1

        dx = self.B.x - self.circumcircle_center.x
        dy = self.B.y - self.circumcircle_center.y
        # self.rsqr = dx*dx + dy*dy
        self.circumcircle_radius = dx * dx + dy * dy

    def isInCircumcircle(self, point):

        dx = point.x - self.circumcircle_center.x
        dy = point.y - self.circumcircle_center.y
        drsqr = dx * dx + dy * dy;

        #    return((drsqr - *rsqr) <= EPSILON ? TRUE : FALSE);
        return True if ((drsqr - self.circumcircle_radius) <= self.EPSILON) else False
