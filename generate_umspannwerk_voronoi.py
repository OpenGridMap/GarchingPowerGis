import psycopg2
import os
conn = psycopg2.connect("dbname=gis user=schreiber")


def generate_substation_voronoi( conn ):
    cur = conn.cursor()
    cur.execute("Truncate only umspannwerk_voronoi;")
    conn.commit()
    cur.execute("Create Temporary Table umspannwerke AS (Select osm_id, ST_Centroid(way) as way from planet_osm_polygon where name like 'Umspannwerk%' OR name like 'UW%');")
    cur.execute("Insert into umspannwerk_voronoi (osm_id, way) select osm_id, way from voronoi('umspannwerke', 'way') as (osm_id integer, way geometry);")
    conn.commit()
    cur.close()
    print "Temporary table of \"Umspannwerke\" created"
    print "Voronoi diagramm created"
    return

def generate_colors( conn ):
    # generate colora
    colors = ('#F2F5A9', '#FE642E', '#084B8A', '#8A0886', '#FFFF00', '#CED8F6', '#088A29', '#B40404', '#00CCFF', '#110022', '#118800', '#2211AA', '#225500', '#AAa2200', '#CCAA00', '#FFAAAA')
    i = 0
    cur = conn.cursor()
    cur.execute("SELECT osm_id FROM umspannwerk_voronoi;")
    for row in cur:
        if i < 15:
            i = i + 1
        else:
            i = 0
        cur2 = conn.cursor()
        cur2.execute("UPDATE umspannwerk_voronoi SET color = %s WHERE osm_id = %s;", [colors[i], row[0]])

    conn.commit()

    cur2.close()
    cur.close()
    print "colors added to voronoi diagramm"
    return

def connect_substation_voronoi( conn ):
    # add osm_id of substations to matching voronoi diagram
    cur = conn.cursor()
    cur.execute("Select osm_id, ST_Centroid(way) as way from planet_osm_polygon where name like 'Umspannwerk%' OR name like 'UW%';")
    for row in cur:
        print row
        cur2 = conn.cursor()
        # in row[0] there is osm_id, in row[1] there is way
        cur2.execute("UPDATE umspannwerk_voronoi SET umspannwerk_id = %s WHERE ST_Within(%s, way);", [row[0], row[1]])

    conn.commit()

    cur2.close()
    cur.close()
    print "\"Umspannwerke\" connected with voronoi polygons"
    return

def generate_powerlines( conn ):
    # generate powerlines
    cur = conn.cursor()
    cur.execute("Truncate only umspannwerk_powerlines;")
    conn.commit()
    cur.execute("SELECT umspannwerk_id, way FROM umspannwerk_voronoi where umspannwerk_id IS NOT NULL;")
    for row in cur:
        print row
        cur2 = conn.cursor()
        cur2.execute("Select way from planet_osm_point where power = 'transformer' and ST_Within(ST_Centroid(way), %s);", [row[1]])
        cur3 = conn.cursor()
        for row2 in cur2:
            cur3.execute("INSERT INTO umspannwerk_powerlines (osm_id,power,way) VALUES (%s, 'line', ST_MakeLine((SELECT ST_Centroid(way) from planet_osm_polygon WHERE osm_id = %s LIMIT 1), %s));", [row[0], row[0], row2[0]])
            print row2[0]

    conn.commit()

    cur3.close()
    cur2.close()
    cur.close()
    print "powerlines generated"
    return

def clear_cache():
    os.system("sudo rm -rf /var/lib/mod_tile/umspannwerk_voronoi")
    print "umspannwerk_voronoi cleared"
    os.system("sudo rm -rf /var/lib/mod_tile/umspannwerk_voronoicolored")
    print "umspannwerk_voronoicolored cleared"
    os.system("sudo rm -rf /var/lib/mod_tile/umspannwerk_powerlines")
    print "umspannwerk_powerlines cleared"
    os.system("sudo service renderd restart")
    return

generate_substation_voronoi(conn)
generate_colors(conn)
connect_substation_voronoi(conn)
generate_powerlines(conn)
clear_cache()