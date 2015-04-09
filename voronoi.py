import math
def check_vertex_in_supervertex(triangle, supertriangle):
    for vertex in triangle:
            for supervertex in supertriangle:
                if vertex == supervertex:
                    print "check_vertex_in_supervertex(" + str(triangle) + ", " + str(supertriangle) + ") = True"
                    return True
    print "check_vertex_in_supervertex(" + str(triangle) + ", " + str(supertriangle) + ") = False"
    return False

def calculate_center_of_trianglecircle((a, b, c)):
    print "calculate_center_of_trianglecircle((" + str(a) + ", " + str(b) + ", " + str(c) + "))"
    m1 = (b[1] - a[1], a[0] - b[0])
    middle_ab = ((a[0] + b[0])/2, (a[1] + b[1])/2)
    m2 = (c[1] - b[1], b[0] - c[0])
    middle_bc = ((b[0] + c[0])/2, (b[1] + c[1])/2)
    if (m1[0] - (m2[0] / m2[1]) * m1[1]) == 0:
        print "Fehler " + str(m1) + " " + str(m2) + " " + str(middle_ab) + " " + str(middle_bc) + " " + str(a) + " " + str(b) + " " + str(c)
    if m2[1] != 0:
        s1 = (middle_bc[0] - middle_ab[0] + (middle_ab[1] - middle_bc[1]) * (m2[0] / m2[1])) / (m1[0] - (m2[0] / m2[1]) * m1[1])
    else:
        s1 = (middle_bc[1] - middle_ab[1] + (middle_ab[0] - middle_bc[0]) * (m2[1] / m2[0])) / (m1[1] - (m2[1] / m2[0]) * m1[0])

    g1x = middle_ab[0] + s1 * m1[0]
    g1y = middle_ab[1] + s1 * m1[1]

    return (g1x, g1y)


def triangulate(points):
    min_x, y1 = min(points, key=lambda (x, y): x)
    x1, min_y = min(points, key=lambda (x, y): y)
    max_x, y2 = max(points, key=lambda (x, y): x)
    x2, max_y = max(points, key=lambda (x, y): y)
    min_x -= 1
    min_y -= 1
    max_x += 1
    max_y += 1

    #  rectangle = ((min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y))  # rectangle around points
    distance_min_max_x = max_x - min_x
    distance_min_max_y = max_y - min_y
    supertriangle = ((min_x, min_y), (min_x, max_y + distance_min_max_y), (max_x + distance_min_max_x, min_y))  #  triangle around rectangle


    triangulation = [supertriangle]

    for point in points:
        print "Triangulation 1: " + str(point) + "\n" + str(triangulation)
        bad_triangles = []
        #bad_triangle_edges = []
        for triangle in triangulation:
            hypotenuse = math.sqrt(pow(distance_min_max_x * 2, 2) + pow(distance_min_max_y * 2, 2))
            # center_of_trianglecircle = ((min_x + max_x) / 2, (min_y + max_y / 2))
            center_of_trianglecircle = calculate_center_of_trianglecircle(triangle)
            radiussquare = pow(triangle[0][0] - center_of_trianglecircle[0], 2) + pow(triangle[0][1] - center_of_trianglecircle[1], 2)
            point_length_square = pow(point[0] - center_of_trianglecircle[0], 2) + pow(point[1] - center_of_trianglecircle[1], 2)
            if point_length_square < radiussquare: # if point in circle
                print "center_of_triangleciecle: " + str(center_of_trianglecircle)
                print "radiussquare: " + str(radiussquare)
                print "point_length_square: " + str(point_length_square)
                bad_triangles.append(triangle)
                #bad_triangle_edges.append((triangle[0], triangle[1]))
                #bad_triangle_edges.append((triangle[1], triangle[2]))
                #bad_triangle_edges.append((triangle[2], triangle[0]))
        polygon = []
        print "bad-triangles" + str(bad_triangles)
        edges = []
        for triangle in bad_triangles:
            if triangle[0] < triangle[1]:
                edges.append((triangle[0], triangle[1]))
            else:
                edges.append((triangle[1], triangle[0]))
            if triangle[1] < triangle[2]:
                edges.append((triangle[1], triangle[2]))
            else:
                edges.append((triangle[2], triangle[1]))
            if triangle[2] < triangle[0]:
                edges.append((triangle[2], triangle[0]))
            else:
                edges.append((triangle[0], triangle[2]))
            triangulation.remove(triangle)
        print "edges: " + str(edges)
        for edge in edges: # triangle ist ein Tupel, daher fraglich ob das geht
            print str(edge) + " Anzahl: " + str(edges.count(edge))
            # if bad_triangle_edges.count(edge) < 2:
            if edges.count(edge) < 2:
                polygon.append(edge)
        print "Triangulation remove: " + str(triangulation)
        print "polygon: " + str(polygon)
        for edge in polygon:
            new_triangle = (edge[0], edge[1], point)
            triangulation.append(new_triangle)
            print "Append triangle: " + str(new_triangle)
    result = []
    for triangle in triangulation:
        if not check_vertex_in_supervertex(triangle, supertriangle):
            result.append(triangle)
    print "Triangulation finished: " + str(triangulation)
    print "triangulation without supertriangle" + str(result)

    return result

def is_neighbour(triangle1, triangle2):
    count = 0
    points = []
    for point1 in triangle1:
        for point2 in triangle2:
            if point1 == point2:
                count += 1
                points.append(point1)
    if count == 2:
        points.sort()
        return points
    else:
        return None


def fun1(triangulation):
    result = []
    result2 = {}
    for triangle1 in triangulation:
        for triangle2 in triangulation:
            if triangle1 == triangle2:
                continue
            neighbours = is_neighbour(triangle1, triangle2)
            if neighbours:
                center_triangle1 = calculate_center_of_trianglecircle(triangle1)
                center_triangle2 = calculate_center_of_trianglecircle(triangle2)
                if not neighbours[0] in result2:
                    result2[neighbours[0]] = []
                if not neighbours[1] in result2:
                    result2[neighbours[1]] = []
                if center_triangle1 < center_triangle2:
                    result.append((center_triangle1, center_triangle2, neighbours))
                    result2[neighbours[0]].append((center_triangle1, center_triangle2))
                    result2[neighbours[1]].append((center_triangle1, center_triangle2))
                else:
                    result.append((center_triangle2, center_triangle1, neighbours))
                    result2[neighbours[0]].append((center_triangle2, center_triangle1))
                    result2[neighbours[1]].append((center_triangle2, center_triangle1))
    #return set(result)
    return result, result2