import psycopg2
import networkx as nx
conn = psycopg2.connect("dbname=gis user=schreiber")


cur = conn.cursor()
cur.execute("Truncate only minspantree_powerlines;")
print "Table truncated"
conn.commit()
cur.execute("SELECT transformer_id, way FROM transformer_voronoi where transformer_id IS NOT NULL;")
i = 1
for row in cur:
    cur2 = conn.cursor()
    # I took the middle of house to not have a 0.0 distance between two direct neighboor houses (Reihenhaeuser)
    cur2.execute("Select t1.osm_id, t2.osm_id, ST_Centroid(t1.way), ST_Centroid(t2.way), ST_Distance(ST_Centroid(t1.way), ST_Centroid(t2.way)) from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id;", [row[1], row[1]])
    # cur2.execute("Select t1.osm_id, t2.osm_id, ST_Distance(ST_Centroid(t1.way), ST_Centroid(t2.way)) as dist from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id order by dist DESC;", [row[1], row[1]])
    #cur2.execute("Select t1.osm_id, t2.osm_id, ST_Distance(t1.way, t2.way) as dist from planet_osm_polygon as t1, planet_osm_polygon as t2 where not t1.building = '' and not t2.building = '' and ST_Within(ST_Centroid(t1.way), %s) and ST_Within(ST_Centroid(t2.way), %s) and t1.osm_id != t2.osm_id order by dist DESC;", [row[1], row[1]])
    graph = []
    for row2 in cur2:
        # generates connections between the houses
        line = str(row2[2]) + ", " + str(row2[3]);
        graph.append(str(row2[0]) + " " + str(row2[1]) + " {'weight':" + str(row2[4]) + ", 'line':'" + line + "'}")
        #print row2[0], "\t", row2[1], "\t", row2[4]
    cur3 = conn.cursor()
    cur3.execute("Select t1.osm_id, t2.osm_id, ST_Centroid(t1.way), t2.way, ST_Distance(ST_Centroid(t1.way), t2.way) from planet_osm_polygon as t1, planet_osm_point as t2 where not t1.building = '' and t2.osm_id = %s and t2.power = 'transformer' and ST_Within(ST_Centroid(t1.way), %s);", [row[0], row[1]])
    for row3 in cur3:
        # generate connections between transformer and every house
        line2 = str(row3[2]) + ", " + str(row3[3]);
        graph.append(str(row3[0]) + " " + str(row3[1]) + " {'weight':" + str(row3[4]) + ", 'line':'" + line2 + "'}")
    G = nx.parse_edgelist(graph, nodetype = int)
    #print G.edges(data = True)
    T = nx.minimum_spanning_tree(G)
    #print T.edges()
    minspantree = T.edges(data=True)
    for edge in minspantree:
        (startnode, endnode, data) = edge
        print(data);
        cur4 = conn.cursor()
        cur4.execute("Insert into minspantree_powerlines (power, way, startosm_id, endosm_id) VALUES ('line', ST_MakeLine((SELECT ST_Centroid(way) as way from planet_osm_polygon WHERE osm_id = %s UNION Select way from planet_osm_point WHERE osm_id = %s), (SELECT ST_Centroid(way) as way from planet_osm_polygon WHERE osm_id = %s UNION Select way from planet_osm_point WHERE osm_id = %s)), %s, %s);", [startnode, startnode, endnode, endnode, startnode, endnode])

    conn.commit()
    print "minimum spanning tree " + str(i) + " added"
    i = i + 1

conn.commit()

cur4.close()
cur3.close()
cur2.close()
cur.close()