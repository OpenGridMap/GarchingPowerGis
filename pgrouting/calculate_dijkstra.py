import psycopg2
import os
import sys
conn = psycopg2.connect("dbname=gis user=schreiber")
conn2 = psycopg2.connect("dbname=pgrouting user=schreiber")

def generate_powerlines( conn, conn2 ):
    # generate powerlines
    cur = conn.cursor()
    cur.execute("Truncate only dijkstra_powerlines;")
    conn.commit()
    print "Table truncated"
    # Get the polygon for every transformer
    cur.execute("SELECT voronoi.transformer_id, voronoi.way, ST_Transform(transformer.way, 4326), transformer.way FROM transformer_voronoi as voronoi INNER JOIN planet_osm_point as transformer ON voronoi.transformer_id = transformer.osm_id where voronoi.transformer_id IS NOT NULL;")
    for transformer in cur:
        print "Routing for transformer " + str(transformer[0])
        cur2 = conn.cursor()

        #cur2.execute("SELECT way, ST_Transform(way, 4326) as trans_way from planet_osm_point WHERE osm_id = %s LIMIT 1;", [row[0]])
        #transformer = cur2.fetchone()

        # cent_way = the middle of the houses
        # select all houses in one voronoi polygon
        cur2.execute("Select ST_Centroid(way) as cent_way, ST_Transform(ST_Centroid(way), 4326) from planet_osm_polygon where not building = '' and ST_Within(ST_Centroid(way), %s);", [transformer[1]])
        cur3 = conn2.cursor()
        cur4 = conn.cursor()
        for house in cur2:
            cur3.execute("SELECT ST_Transform( (SELECT ST_MakeLine(route.geom) FROM ( SELECT geom FROM pgr_fromAtoB("
                         "'ways', ST_X(%s),ST_Y(%s),ST_X(%s),ST_Y(%s) ) ORDER BY seq) AS route), 900913);",
                         [transformer[2], transformer[2], house[1], house[1]])

            route = cur3.fetchone()
            #print route
            cur4.execute("INSERT INTO dijkstra_powerlines (osm_id,power,way) VALUES (%s, 'line', ST_AddPoint( ST_AddPoint(%s, %s, 0), %s));", [transformer[0], route[0], transformer[3], house[0]])

            sys.stdout.write('.')
            sys.stdout.flush()
        conn.commit()
        print "" # for adding a new line
    conn.commit()

    cur4.close()
    cur3.close()
    cur2.close()
    cur.close()
    print "Finished routing"
    return


generate_powerlines(conn, conn2)