import psycopg2
import os
import networkx as nx
conn = psycopg2.connect("dbname=gis user=schreiber")


cur = conn.cursor()
cur.execute("Truncate only networkx_test;")
print "Table truncated"
conn.commit()
#cur.execute("SELECT transformer_id, way FROM transformer_voronoi where transformer_id IS NOT NULL and NOT transformer_id = '999999999990031' AND NOT transformer_id = '999999999990082' AND NOT transformer_id = '999999999990093' ORDER BY transformer_id;")
cur.execute("SELECT transformer_id, way FROM transformer_voronoi where transformer_id IS NOT NULL ORDER BY transformer_id;")
i = 1
for row in cur:
    cur2 = conn.cursor()
    # I took the middle of house to not have a 0.0 distance between two direct neighboor houses (Reihenhaeuser)
    cur2.execute("Select t1.osm_id, t2.osm_id, ST_Distance(ST_Centroid(t1.way), ST_Centroid(t2.way)) from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id;", [row[1], row[1]])
    # cur2.execute("Select t1.osm_id, t2.osm_id, ST_Distance(ST_Centroid(t1.way), ST_Centroid(t2.way)) as dist from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id order by dist DESC;", [row[1], row[1]])
    #cur2.execute("Select t1.osm_id, t2.osm_id, ST_Distance(t1.way, t2.way) as dist from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id order by dist DESC;", [row[1], row[1]])
    graph = []
    for row2 in cur2:
        # generates connections between the houses
        graph.append(str(row2[0]) + " " + str(row2[1]) + " {'weight':" + str(row2[2]) + "}")
        #print row2[0], "\t", row2[1], "\t", row2[2]
    cur3 = conn.cursor()
    cur3.execute("Select t1.osm_id, t2.osm_id, ST_Distance(ST_Centroid(t1.way), t2.way) from planet_osm_polygon as t1, planet_osm_point as t2 where not t1.building = '' and t2.osm_id = %s and t2.power = 'transformer' and ST_Within(ST_Centroid(t1.way), %s);", [row[0], row[1]])
    for row3 in cur3:
        # generate connections between transformer and every house
        graph.append(str(row3[0]) + " " + str(row3[1]) + " {'weight':" + str(row3[2]) + "}")
    G = nx.parse_edgelist(graph, nodetype = int)

    T = nx.minimum_spanning_edges(G, data=False)
    minspantree = list(T)
    for edge in minspantree:
        (startnode, endnode) = edge
        cur4 = conn.cursor()
        cur4.execute("Insert into networkx_test (power, way, startosm_id, endosm_id) VALUES ('line', ST_MakeLine((SELECT ST_Centroid(way) as way from planet_osm_polygon WHERE osm_id = %s UNION Select way from planet_osm_point WHERE osm_id = %s), (SELECT ST_Centroid(way) as way from planet_osm_polygon WHERE osm_id = %s UNION Select way from planet_osm_point WHERE osm_id = %s)), %s, %s);", [startnode, startnode, endnode, endnode, startnode, endnode])

    conn.commit()
    print "line " + str(i) + " (transformer_id: " + str(row[0]) + ") added"
    i = i + 1

conn.commit()

cur4.close()
cur3.close()
cur2.close()
cur.close()

os.system("sudo rm -rf /var/lib/mod_tile/networkx_test")
print "powerlines cleared"
os.system("sudo service renderd restart")