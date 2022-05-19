from collections import Counter
from statistics import mean,variance

from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

import networkx as nx
import networkx.algorithms.community as nx_comm

client = MongoClient('127.0.0.1:28847',
                     username='SNA_APP',
                     password='n2zkEtKJ2YHpQe9c',
                     authSource='admin')

db = client["dblp"]
collection = db["publications2"]
center_author = "Philip S. Yu"
center_author_nospace = "".join(center_author.split(" "))

query = {"$and":[{"author":center_author},{"author.1" : {"$exists" : True }}]}

docs = list(collection.find(query))

coauthor_counter = {}

for doc in docs:
    for first_author in doc['author']:
        current_counter = coauthor_counter.get(first_author,Counter())
        for second_author in doc['author']:
            if second_author != first_author:
                current_counter[second_author] += 1
        coauthor_counter[first_author] = current_counter

# Calculate total number of coauthorship and average number of coauthorship per publication
center_counter = coauthor_counter[center_author]
coauthor_total = sum(center_counter.values())
coauthor_unique = len(center_counter.values())

print("{} has had {} co-authors over {} publications.Unique coauthors = {}".format(center_author,coauthor_total,len(docs),coauthor_unique))

# Remove coauthorships for cases lower than 2
for author in list(coauthor_counter):
    new_ctr = Counter({k: c for k, c in coauthor_counter[author].items() if c >= 2})
    if len(new_ctr) == 0:
        del coauthor_counter[author]
    else:
        coauthor_counter[author] = new_ctr

# Create graph and add authors as nodes
G = nx.Graph()
G.add_nodes_from(list(coauthor_counter))

# Iterate over counters and add edges 
for first_author in list(coauthor_counter):
    for second_author in coauthor_counter[first_author]:
        G.add_edge(first_author,second_author)

#Community detection
louvain_communities = nx_comm.louvain_communities(G)
for label,nodes in enumerate(louvain_communities):
    for node in nodes:
        G.nodes[node]["louvain_label"] = label

lpa_communities = nx_comm.asyn_lpa_communities(G)
for label,nodes in enumerate(lpa_communities):
    for node in nodes:
        G.nodes[node]["lpa_label"] = label

nx.write_graphml(G,center_author_nospace+'.graphml')

# Extract network stats
print("# of nodes: {}. # of edges: {}.".format(len(G.nodes),len(G.edges)))

avg_cc = nx.average_clustering(G)
global_cc = nx.transitivity(G)
print("Average local clustering coefficient is {}".format(avg_cc))
print("Global clustering coefficient(transitivity) is {}".format(global_cc))

deg_cnt = nx.degree_centrality(G)
print("Average degree centrality is {} with variance of {}".format(mean(deg_cnt.values()),variance(deg_cnt.values())))

close_cnt = nx.closeness_centrality(G)
print("Average closeness centrality is {} with variance of {}".format(mean(close_cnt.values()),variance(close_cnt.values())))

between_cnt = nx.betweenness_centrality(G)
print("Average betweenness centrality is {} with variance of {}".format(mean(between_cnt.values()),variance(between_cnt.values())))

print("Diameter of graph is {}".format(nx.diameter(G)))

print("Is graph connected? {}".format(nx.is_connected(G)))


# Test power of law for degree centrality
deg_cnt = nx.degree_centrality(G)
deg_counter = Counter(deg_cnt.values())
x = []
y = []
for p,deg in deg_counter.most_common():
    x.append(deg)
    y.append(p)

x = np.log(np.array(x))
y = np.log(np.array(y))

reshaped_x = x.reshape(-1,1)
reg = LinearRegression().fit(reshaped_x, y)
print("Prediction score is {}".format(reg.score(reshaped_x,y)))

pred_x = np.linspace(min(x),max(x),50).reshape(-1,1)
pred_y = reg.predict(pred_x)

plt.scatter(x,y)
plt.plot(pred_x,pred_y,color="red")
plt.xlabel("log(degree centrality)")
plt.ylabel("log(p)")
plt.title("Degree centrality distribution for "+center_author+"'s network")

plt.savefig(center_author_nospace+"_log_deg.jpg")

# Erdos Random Graph Construction
global_cc_error = []
erdos_graphs = []
p_list = np.arange(0.01,0.11,0.01)
for p in p_list:
    erdos_graph = nx.erdos_renyi_graph(len(G.nodes),p)
    global_cc_error.append(abs(nx.transitivity(erdos_graph)-global_cc))
    erdos_graphs.append(erdos_graph)

global_cc_error = np.array(global_cc_error)
best_p = p_list[np.argmin(global_cc_error)]
best_erdos = erdos_graphs[np.argmin(global_cc_error)]

erdos_diam = 0
try:
    erdos_diam = nx.diameter(best_erdos)
except:
    largest_cc = best_erdos.subgraph(max(nx.connected_components(best_erdos), key=len))
    erdos_diam = nx.diameter(largest_cc)

print("Best Erdos random graph is G({},{}) with global clustering coefficient of {} and diameter of {}.".format(len(G.nodes),best_p,nx.transitivity(best_erdos),erdos_diam))
nx.write_graphml(best_erdos,center_author_nospace+'_erdos.graphml')




