# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 12:51:02 2019

@author: hp
"""

# -*- coding: utf-8 -*-
"""
Created on Sun May 26 01:23:33 2019

@author: Braneci Sofiane
"""

N_FIG = 600
import pandas as pd
import networkx as nx
import numpy as np
from matplotlib.figure import Figure
from collections import deque
from sklearn.cluster import KMeans
import re
SEQUENCE = []
N_NODES  = []
All = None

# load data    
data = pd.read_csv('qos_data.csv', sep=';')
# drop unwanted columns
data.drop('Unnamed: 0', axis=1, inplace=True)
def get_header():
    return list(data.columns)
def get_random_data(n_main_nodes, n_nodes_per_main_node):
    global data
    nodes = []
    indexs = []
    for _ in range(n_main_nodes):
        index = []
        node = []
        for j in range(n_nodes_per_main_node):
            index.append(np.random.randint(0, 2507))
            node.append(data['Service Name'][index[j]])
        indexs.append(index)
        nodes.append(node)
    return nodes


  
def construct_discovery_graph(U, n_nodes_per_main_node):
    U_copy = U.copy()
    main_nodes = list(U.nodes)
    n_nodes = len(main_nodes)
    nodes = get_random_data(n_nodes, n_nodes_per_main_node)
    for mn in range(len(main_nodes)):
        for i in range(len(nodes[mn])):
            U_copy.add_edge(main_nodes[mn], nodes[mn][i])
        continue
#    draw(U)
    return U_copy

def get_services_data(G):
    '''returning the selected services data
       -------
       params:
           G: networkX Graph
    '''
    temp = ' '.join(list(G.nodes))
    main_nodes = re.findall(r'AS.\d+', temp)
    global data
    X = []
    for main_node in main_nodes:
        l = []
        for service in list(G[main_node]):
            if service not in main_nodes:
                l.append(data[data['Service Name'] == service].min())
        X.append(np.array(l))
    for l in X:
         
        l[:, :-1] = list(map(np.float32, l[:, :-1]))
            
    return np.array(X)

def get_data(G):
    '''returning the selected services data
       -------
       params:
           G: networkX Graph
    '''
    temp = ' '.join(list(G.nodes))
    main_nodes = re.findall(r'AS.\d+', temp)
    global data
    X = []
    for main_node in main_nodes:
        l = []
        for service in list(G[main_node]):
            if service not in main_nodes:
                l.append(data[data['Service Name'] == service].min())
        X.append(np.array(l))
    for i in  range(len( X)):

            X[i][:,:-1] = np.array(list(map(np.float32,X[i][:,:-1] )))
    return np.array(X)
        

def gsd(G):
    X = []
    for node in list(G.nodes):
        print(node)
        X.append(data[data['Service Name'] == node].min())
    return np.array(X)
    
def get_max_centroid_index(centers):
    m = centers[0]
    index = 0
    for i in range(1,len(centers)):
        if np.sum(centers[i], axis=0) >= np.sum(m, axis=0):
            index = i
            m = centers[i]
    return index, m

def compute_score(services, weights, classes):
    x = (np.dot(services[:, :-1],weights.reshape((-1, 1)))) / len(services)
    classes = classes + 1 
    return x * classes.reshape((-1,1))

def select(U, w, G):
    w = np.array(list(map(np.float32, w)))
    
    X = get_services_data(U)
    services = []
    for AS in X:
        classes, centers = classify(AS)
        index, m = get_max_centroid_index(centers)
        temp = np.concatenate((AS, classes.reshape((-1,1))), axis=1)
        scores = compute_score(AS, w, classes)
        scores = np.concatenate((scores, classes.reshape((-1,1))), axis=1)
        scores_woc = scores[scores[:,-1] == index][:,:-1]
        serices_woc = temp[temp[:,-1] == index][:,:-1]
        s = []
        for i in range(len(serices_woc)):
            if np.all(serices_woc[i][:-1] >=  (0.001 * np.mean(serices_woc[:,:-1], axis=0))) and np.all((0.01 * (np.mean(scores_woc, axis=0)) <= scores_woc[i])):
                s.append(serices_woc[i])
        services.append(s)  
    services_names = []
    for i in range(len(services)):
        if len(services[i]) == 1:
            services_names.append(services[i][0][-1])
        else:
            
            index = np.random.randint(0, len(services[i]))
            name = services[i][index][-1]
            services_names.append(name)
    C = G.copy()
    mapping = {k:v for k, v in zip(list(G.nodes), services_names)}
    C = nx.relabel_nodes(C, mapping) 
    global All
    All = services
    return C
#
#def get_best_composition(G, max_iter):
#    G_copy = G.copy()
#    new = None
#    used = list(G.nodes)
#    old = evaluate_compositionv2(G)[-1]
#    if max_iter > len(All):
#        max_iter = len(All)
#    for j in range(max_iter):
#        names = []
#        for i in range(len(G.nodes)):
#            if len(All[i]) == 1:
#                names.append(All[i][0][-1])
#            else:
#                for j in range(len(All[i])):
#                    index = np.random.randint(0, len(All[i]))
#                    if All[i][index][-1] not in list(G_copy.nodes) and All[i][index][-1] in used:
#                        names.append(All[i][index][-1])
#                        used.append(All[i][index][-1])
#            G_copy = nx.relabel_nodes(G_copy, {k:v for k,v in zip(G_copy.nodes, names)})
#            new = evaluate_compositionv2(G_copy)[-1]
#            if np.all(new >= old):
#                old = new
#    return G_copy
    
def find_optimal_clf(clf, X):
    if len(X) >100:
        _n_clusters = [ 2, 3, 4, 5, 6, 7, 8, 9,10]
    elif len(X) == 1:
        return clf
    else:
        _n_clusters = list(filter(lambda x: x < len(X),[ 2, 3, 4, 5, 6, 7]))
    
    wcss = []
    for n in _n_clusters:
        clf = KMeans(n)
        _ = clf.fit_predict(X[:, :-1])
        wcss.append(clf.inertia_)
    index = list(wcss <= np.mean(wcss)).index(True)
    return KMeans(_n_clusters[index])

def classify(X):
    clf = KMeans(1)
    clf = find_optimal_clf(clf, X)
    return clf.fit_predict(X[:, :-1]), clf.cluster_centers_

def draw_definition_graph(U):
    fig = Figure(figsize=(9, 5.5))
    ax = fig.add_subplot(111)
    ax.axis('off')
    pos = nx.spring_layout(U)
    nx.draw_networkx_nodes(U, pos, node_color='green',ax=ax, node_size=950)
    nx.draw_networkx_edges(U,pos,ax=ax, width=2, arrowsize=30)
    nx.draw_networkx_labels(U, pos,ax=ax)
    return fig

def draw_discovery_graph(U):
    main_nodes = re.findall(r'AS.\d+', ' '.join(list(U.nodes)))
    fig = Figure(figsize=(9,5.5))
    ax = fig.add_subplot(111)
    ax.axis('off')
    #G = nx.relabel_nodes(G, {k:v for k,v in zip(["AS "+str(i) for i in range(1,4)], range(0,4))})
    nodes = []
    for node in list(U.nodes):
        if node not in main_nodes:
            nodes.append(node)
    pos = nx.spring_layout(U)
    nx.draw_networkx_nodes(U, pos, nodelist=main_nodes, node_color='green',ax=ax, node_size=700)
    nx.draw_networkx_nodes(U, pos, nodelist=nodes, node_color='blue',ax=ax, node_size=500)
    nx.draw_networkx_edges(U,pos,ax=ax, width=2, arrowsize=15)
    nx.draw_networkx_labels(U, pos,ax=ax)
#    nx.draw_networkx(U)
    return fig
  

def construct_cs_graph(G, n_node_per_as):
    main_nodes = list(G.nodes)
    G_copy = G.copy()
    n = 1
    for i in range(len(main_nodes)):
        for j in range(n_node_per_as):
            G_copy.add_edge(main_nodes[i], 'CS '+str(n))
            n += 1
    return G_copy


def get_n_cs(U,G):
    main_node = list(G.nodes)[0]
    main_nodes = list(G.nodes)
    n = 0
    for node in list(U[main_node]):
        if node not in main_nodes:
            n +=1
    return n

def get_item_data(item):
    return data[data['Service Name'] == item].min()


                    
def cgv5(times):
    global SEQUENCE, N_NODES 
    SEQUENCE  = []
    N_NODES = []
    seq = np.random.choice(['seq', 'bou'])
    q = deque(['AS 1'])
    G = nx.MultiDiGraph()
    SEQUENCE.append(seq)
    last_seq = seq
    last_node = q[0]
    n = 0
    if seq == 'bou':
        G.add_edge(last_node, last_node)
        N_NODES.append(1)
        n += 1
    else:
        N_NODES.append(1)
        n = 1
    for t in range(times):
        last_node = q.popleft()
        seq = np.random.choice(['seq', 'par', 'bou'])
        SEQUENCE.append(seq)
        if seq == 'seq':
            if last_seq == 'par':
                n += 1
                new_node = "AS " +str(n)
                N_NODES.append(1)
                q.append(new_node)
                index = list(G.nodes).index(last_node)
                nodes = list(G.nodes)[index+1:]
                for node in nodes:
                    G.add_edge(node, new_node)
                if times - 1 < n:
                    break
            elif last_seq == 'bou':
                n += 1
                new_node = "AS "+str(n)
                q.append(new_node)
                N_NODES.append(1)
                G.add_edge(last_node, new_node)
                if times-1 < n:
                    break
            else:
                n += 1
                new_node = "AS " +str(n)
                q.append(new_node)
                N_NODES.append(1)
#                print(N_NODES)
                G.add_edge(last_node, new_node)
                if times-1< n:
                    break
##############################################        
        elif seq == 'par':
            s = 0
            for _ in range(n+1, n+3):
                s +=1
                n +=1
                
                new_node = 'AS '+str(n)
                q.append(new_node)
                G.add_edge(last_node, new_node)
                            
                if times <= n:
                    N_NODES.append(s)
                    break
            N_NODES.append(s)
            if times - 1 < n:
                    break
##############################################
        else:
            n += 1
            new_node = "AS " +str(n)
            q.append(new_node)
            N_NODES.append(1)
            G.add_edge(new_node, new_node)
            G.add_edge(last_node, new_node)
            if times - 1 < n:
                break
        last_seq = seq

    empty_nodes = []
    for node in list(G.nodes)[1:]:
        if list(G[node]) == [] or node in list(G[node]):
            empty_nodes.append(node)  
    l = list(G.nodes)[-1]
    for node in empty_nodes[:-1]:
        if (node, l) not in list(G.edges):
                G.add_edge(node, l)
    return G
    
def evaluate_compositionv2(G):
    X = gsd(G)
    temp = X[:,:-1]
    temp = np.array(list(map(np.float32,temp)))

    seq = []
    par = []
    boucle = []
    xseq = []
    for i in range(len(SEQUENCE)):
        if SEQUENCE[i] == 'par':
            for j in range(N_NODES[i]):
                xseq.append(SEQUENCE[i])
        else:
            xseq.append(SEQUENCE[i])
    if len(temp) == (len(xseq) -1):
        xseq.pop(-1)
    for i in range(len(temp)):
        if xseq[i] == 'seq':
            seq.append(temp[i])
        elif xseq[i] == 'par':
            par.append(temp[i])
        else:
            boucle.append(temp[i])
    #print((("seq", seq), ("par", par), ("bou", boucle)))
    return  agregate_composition_service(seq, par, boucle)

   
def evaluate_compositionv3(G):
    X = gsd(G)
    #print(X)
    temp = X[:,:-1]
    temp = np.array(list(map(np.float32,temp)))

    seq = []
    par = []
    boucle = []
    xseq = []
    for i in range(len(SEQUENCE)):
        if SEQUENCE[i] == 'par':
            for j in range(N_NODES[i]):
                xseq.append(SEQUENCE[i])
        else:
            xseq.append(SEQUENCE[i])
    if len(temp) == (len(xseq) -1):
        xseq.pop(-1)
    for i in range(len(temp)):
        if xseq[i] == 'seq':
            seq.append(temp[i])
        elif xseq[i] == 'par':
            par.append(temp[i])
        else:
            boucle.append(temp[i])
    #print((("seq", seq), ("par", par), ("bou", boucle)))
    #print(evaluate_seq(seq), evaluate_par(par), evaluate_boucle(boucle))
    print(np.sum([evaluate_seq(seq), evaluate_par(par), evaluate_boucle(boucle)], axis=0))
    return  np.sum([evaluate_seq(seq), evaluate_par(par), evaluate_boucle(boucle)], axis=0) ##agregate_composition_service(seq, par, boucle)


def evaluate_seq(seq):
    """    
    RT ---- > SUM
    AV ---- > MAX
    TH ---- > MAX
    SU ---- > MIN
    RE ---- > Min
    CO ---- > MAX
    BP ---- > MAX
    DOC---- > MAX
    LT ---- > MIN"""    
    if seq != []:
        seq = np.array(seq)
        #print(seq)
        funcs = [np.sum, np.max, np.product]
        qos_seq = []
        for i in range(len(funcs)):
            qos_seq.append(funcs[i](seq[:, i], axis=0))
        return qos_seq     
    return np.zeros(3)

def evaluate_par(par):
    """
    
    RT ---- > Min
    AV ---- > MAX
    TH ---- > MAX
    SU ---- > MIN
    RE ---- > Min
    CO ---- > MAX
    BP ---- > MAX
    DOC---- > MAX
    LT ---- > MIN
    """
    if par != []:
        qos_par = []
        par = np.array(par)
        #print(par)
        funcs = [np.min, np.max, np.min]
        for i in range(len(funcs)):
            qos_par.append(funcs[i](par[:,i], axis=0))
        
        return qos_par
    else: return np.zeros(3)
    

def evaluate_boucle(seq):
    """ 
    RT ---- > Sum(RT) * k
    AV ---- > MAX
    TH ---- > MAX
    SU ---- > MIN
    RE ---- > min(RE) ** k
    CO ---- > MAX
    BP ---- > MAX
    DOC---- > MAX
    LT ---- > MIN
    """
    
    if seq != []:
        k = 3
        seq = np.array(seq)
        #print(seq)
        funcs = [np.sum, np.max, np.max]
        qos_bou = []
        for i in range(len(funcs)):
            if i == 0:
                qos_bou.append(((seq[:,i]) * k)[0])
            elif i == 2:
                 qos_bou.append(np.power(seq[:,i], k)[0])
            else:
                 qos_bou.append(funcs[i](seq[:,i], axis=0))
        print(qos_bou)
        return np.sum(qos_bou, axis=0)
    else:
        return np.zeros(3)
        
def agregate_composition_service(seq, par, bou):
    """ 
    RT ---- > SUM
    AV ---- > MAX
    TH ---- > MAX

    """

    if any([seq == [], par == [], bou == []]):
        filtred = tuple(filter(lambda x: x != [], [seq, par, bou]))
        data = np.concatenate(filtred, axis=0)
    else:
        data = np.concatenate((np.array(seq), np.array(par), np.array(bou)),axis=0)
    funcs = [np.sum, np.max, np.max]
    qos = []
    for i in range(len( funcs)):
        qos.append(funcs[i](data[:,i]))
    return qos
    
    

if __name__ == '__main__':
   G = cgv5(3)
   U = construct_discovery_graph(G, 4)
   w = np.random.random(3)
   C = select(U, w, G)
   evaluate_compositionv3(C)

    
    
    
    
    