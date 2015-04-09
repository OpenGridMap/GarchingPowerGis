import psycopg2
import os
conn = psycopg2.connect("dbname=gis user=schreiber")

def generate_transformer_voronoi( conn ):
    cur = conn.cursor()
    cur.execute("Truncate only transformer_voronoi;")
    conn.commit()
    cur.execute("Create Temporary Table transformer AS (Select osm_id, way from planet_osm_point where power = 'transformer');")
    cur.execute("Insert into transformer_voronoi (osm_id, way) select osm_id, way from voronoi('transformer', 'way') as (osm_id integer, way geometry);")
    cur.execute("DELETE from transformer_voronoi where ST_Disjoint(way, (select way from planet_osm_polygon where osm_id = -30971));")  # Delete all voronois outside Garchiing
    cur.execute("UPDATE transformer_voronoi SET way = intersection.new_way FROM (select osm_id, ST_Intersection(way, (SELECT way FROM planet_osm_polygon WHERE osm_id = -30971)) AS new_way FROM transformer_voronoi) AS intersection WHERE transformer_voronoi.osm_id = intersection.osm_id;")  # restrict the area to Garching
    conn.commit()
    cur.close()
    print "Temporary table of \"Transformer\" created"
    print "Voronoi diagramm created"
    return

def connect_transformer_voronoi( conn ):
    # add osm_id of transformator to matching voronoi diagram
    cur = conn.cursor()
    #cur.execute("SELECT osm_id, way FROM planet_osm_point where power = 'transformer' and \"addr:postcode\" = '85748';")
    cur.execute("SELECT osm_id, way FROM planet_osm_point where power = 'transformer';")
    for row in cur:
        print row
        cur2 = conn.cursor()
        # in row[0] there is osm_id, in row[1] there is way
        cur2.execute("UPDATE transformer_voronoi SET transformer_id = %s WHERE ST_Within(%s, way);", [row[0], row[1]])

    conn.commit()
    #cur.execute("DELETE FROM transformer_voronoi where transformer_id IS NULL;")
    conn.commit()

    cur2.close()
    cur.close()
    return

def generate_powerlines( conn ):
    # generate powerlines
    cur = conn.cursor()
    cur.execute("Truncate only powerlines;")
    conn.commit()
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

def generate_colors( conn ):
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

def clear_cache():
    os.system("sudo rm -rf /var/lib/mod_tile/voronoi")
    print "voronoi cleared"
    os.system("sudo rm -rf /var/lib/mod_tile/voronoicolored")
    print "voronoicolored cleared"
    os.system("sudo rm -rf /var/lib/mod_tile/powerlines")
    print "powerlines cleared"
    os.system("sudo service renderd restart")
    return


generate_transformer_voronoi(conn)
connect_transformer_voronoi(conn)
generate_powerlines(conn)
generate_colors(conn)
clear_cache()