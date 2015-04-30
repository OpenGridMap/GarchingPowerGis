import psycopg2
import os
conn = psycopg2.connect("dbname=gis user=schreiber")
conn2 = psycopg2.connect("dbname=pgrouting user=schreiber")

def generate_powerlines( conn, conn2 ):
    # generate powerlines
    cur = conn.cursor()
    cur.execute("Truncate only dijkstra_powerlines;")
    conn.commit()
    print "Table truncated"
    cur.execute("SELECT transformer_id, way FROM transformer_voronoi "
                 "where transformer_id IS NOT NULL Limit 1;")
    for row in cur:
        print row
        cur2 = conn.cursor()

        cur2.execute("SELECT ST_Transform(way, 4326) from planet_osm_point WHERE osm_id = %s LIMIT 1;", [row[0]])
        transformer = cur2.fetchone()

        cur2.execute("Select ST_Transform(ST_Centroid(way), 4326) as cent_way from planet_osm_polygon where not "
                      "building = '' and ST_Within(ST_Centroid(way), %s);", [row[1]])
        cur3 = conn2.cursor()
        cur4 = conn.cursor()
        for row2 in cur2:
            cur3.execute("SELECT ST_Transform( (SELECT ST_MakeLine(route.geom) FROM ( SELECT geom FROM pgr_fromAtoB("
                         "'ways', ST_X(%s),ST_Y(%s),ST_X(%s),ST_Y(%s) ) ORDER BY seq) AS route), 900913);",
                         [transformer, transformer, row2[0], row2[0]])

            route = cur3.fetchone()
            print route
            cur4.execute("INSERT INTO dijkstra_powerlines (osm_id,power,way) VALUES (%s, 'line', %s);", [row[0], route[0]])

    conn.commit()

    cur4.close()
    cur3.close()
    cur2.close()
    cur.close()
    return


generate_powerlines(conn, conn2)