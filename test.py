import psycopg2
import voronoi

conn = psycopg2.connect("dbname=gis user=schreiber")

def flachmach(liste):
    result = []
    for (x, y) in liste:
        result.append(x)
        result.append(y)
    return result

def generate_transformer_voronoi(conn):
    cur = conn.cursor()
    cur.execute("Truncate only transformer_voronoi;")
    conn.commit()
    cur.execute("Create Temporary Table transformer AS (Select osm_id, way from planet_osm_point where power = 'transformer' and \"addr:postcode\" = '85748');")
    cur.execute("Select ST_X(way), ST_Y(way) from transformer;")
    points = []
    for row in cur:
        points.append((row[0], row[1]))

    ##points = [#(1296482.4329096, 6147582.8633626),
    #(1292638.8550264, 6148130.4997612),
    #(1296801.4064993, 6149102.0355884),
    #(1296598.9678072, 6148730.0022398),
    ##(1297129.5126022, 6149248.8896349),
    ##(1297810.8770496, 6147660.4326411),
    ##(1297269.5832974, 6147182.7495815),
    ##(1297502.7402794, 6149100.1957284),
    ##(1297252.8626975, 6147494.4693375)] #,
    #(1295880.2449214, 6149826.347497)]

    #points = [(1.25, 9.25), (8.125, 7.6), (2.6, 7.125), (5.0, 9.125), (2.5, 7.4)]


    #print points
    triangulation = voronoi.triangulate(points)
    voronoidiagram, result2 = voronoi.fun1(triangulation)
    print "Voronoi: " + str(voronoidiagram)
    #print(voronoidiagram)
    for (trafo, lines) in result2.iteritems():
        lines2 = lines
        liste = [lines2[0][0], lines2[0][1]]
        lines2.remove(lines2[0])
        while True:
            current = liste[-1]
            nextline = None
            for line in lines2:
                if line[0] == current or line[1] == current:
                    nextline = line
                    break;
            if nextline == None:
                break;
            if nextline[0] == current:
                liste.append(nextline[1])
            else:
                liste.append(nextline[0])
            lines2.remove(nextline)
            if len(lines2) == 0:
                break
        liste.append(liste[0]) # um auch in Randfaellen ein gueltiges Polygon zu bekommen
        count = len(liste)

        cur.execute("Insert into transformer_voronoi (way) VALUES (ST_GeomFromEWKT('SRID=900913;POLYGON((" + ((count - 1) * "%s %s,") + "%s %s))'))", flachmach(liste))
    #cur.execute("Insert into transformer_voronoi (osm_id, way) select osm_id, way from voronoi('transformer', 'way') as (osm_id integer, way geometry);")


    # SRID=900913;POLYGON((1296814.18069 6147382.95517,1296639.81155 6147404.40832,1296616.15344 6147821.31429,1297085.62181 6147961.20919,1297104.37966 6147955.32306,1297010.47622 6147529.0615,1296814.18069 6147382.95517))


    conn.commit()
    cur.close()
    print "Temporary table of \"Transformer\" created"
    print "Voronoi diagramm created"
    return

def connect_transformer_voronoi(conn):
    # add osm_id of transformator to matching voronoi diagram
    cur = conn.cursor()
    cur.execute("SELECT osm_id, way FROM planet_osm_point where power = 'transformer' and \"addr:postcode\" = '85748';")
    for row in cur:
        print row
        cur2 = conn.cursor()
        # in row[0] there is osm_id, in row[1] there is way
        cur2.execute("UPDATE transformer_voronoi SET transformer_id = %s WHERE ST_Within(%s, way);", [row[0], row[1]])

    conn.commit()

    cur2.close()
    cur.close()
    return

def generate_powerlines(conn):
    # generate powerlines
    cur = conn.cursor()
    cur.execute("SELECT transformer_id, way FROM transformer_voronoi where transformer_id IS NOT NULL;")
    for row in cur:
        print row
        cur2 = conn.cursor()
        cur2.execute("Select ST_Centroid(way) as cent_way from planet_osm_polygon where not building = '' and ST_Within(ST_Centroid(way), %s);", [row[1]])
        cur3 = conn.cursor()
        for row2 in cur2:
            cur3.execute("INSERT INTO powerlines (osm_id,power,way) VALUES (%s, 'line', ST_MakeLine((SELECT way from planet_osm_point WHERE osm_id = %s LIMIT 1), %s));", [row[0], row[0], row2[0]])
            print row2[0]

    conn.commit()

    cur3.close()
    cur2.close()
    cur.close()
    return

def generate_colors(conn):
    # generate colora
    colors = ('#F2F5A9', '#FE642E', '#084B8A', '#8A0886', '#FFFF00', '#CED8F6', '#088A29', '#B40404', '#00CCFF', '#110022', '#118800', '#2211AA', '#225500', '#AAa2200', '#CCAA00', '#FFAAAA')
    i = 0
    cur = conn.cursor()
    cur.execute("SELECT osm_id FROM transformer_voronoi;")
    for row in cur:
        if i < 15:
            i = i + 1
        else:
            i = 0
        cur2 = conn.cursor()
        cur2.execute("UPDATE transformer_voronoi SET color = %s WHERE osm_id = %s;", [colors[i], row[0]])

    conn.commit()

    cur2.close()
    cur.close()
    return


generate_transformer_voronoi(conn)
#connect_transformer_voronoi(conn)
#generate_powerlines(conn)
#generate_colors(conn)