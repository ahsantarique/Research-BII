# -*- coding: utf-8 -*-
"""Antivaccine_sentiment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jL_vl5_nxVcHoONrh46gKA6yFamBWlTz
"""

import networkx as nx
from enum import Enum
import numpy as np
import copy
import random
import matplotlib.pyplot as plt
import pandas as pd
import pickle

############## params of graph ############################
# N = 1000
# M = 20
# PROB_TRIANGLE = 0.8
###########################################################

# g = nx.newman_watts_strogatz_graph(N, M, PROB_TRIANGLE, seed=42) ########### toy data #######

# len(nx.triangles(g))
# print(g.number_of_edges())

from google.colab import drive
drive.mount('/content/gdrive')

import os
os.chdir('/content/gdrive/My Drive/antivax_data/')

# g = nx.read_edgelist("twitter_combined.txt", create_using = nx.Graph(), nodetype=int) ########### snap twitter data #############
 
g = nx.read_edgelist("facebook_combined.txt", create_using = nx.Graph(), nodetype=int) ########### snap facebook data #############

# d = 5
# g = nx.random_regular_graph(d=d, n = N, seed = 42)

# nx.draw(g)

def plot(x, y, label, title, xlabel, ylabel, showplot = True):
    # plot
    plt.plot(x, y, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if(showplot):
      plt.show()

def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

"""Start simulation"""

##############  first define the utility function #################

def get_util(graph, i, x, state, alpha, beta, C, gamma, delta):
  util = 0

  for v in graph.neighbors(i):
    if x[v] == state:
      # print(v, " same as ", i)
      util += alpha
    else:
      # print(v, " different from ", i)
      util -= beta

  if(sum(x.values()) < (1-gamma)*graph.number_of_nodes()):
    util += delta

  elif state == 0:
    util += C
  
  return util

def simulate_one_parallel_epoch(graph, x, alpha, beta, gamma, C, delta, ):
  new_x = copy.deepcopy(x)
  for i in graph.nodes:
    if(get_util(graph=graph, i=i, x=x, state = x[i], alpha = alpha, beta = beta, C = C, gamma = gamma, delta = delta) 
    < get_util(graph = graph, i = i, x = x, state= 1-x[i], alpha = alpha, beta = beta, gamma = gamma, C = C, delta = delta)): 
      # new_x[i] = (x[i] == SENTIMENT.PRO.value) and SENTIMENT.ANTI.value or SENTIMENT.PRO.value
      new_x[i] = 1-x[i]

  return new_x

def simulate_parallel(graph, strategy, alpha, beta, gamma, C, delta, verbose, TMAX =50):
  t = 0
  print("antivax at time ", t, ": ", sum(strategy.values())," Probability: ", sum(strategy.values()) / len(g.nodes) )
  
  new_strategy = simulate_one_parallel_epoch(graph = graph, x = strategy, alpha = alpha, beta = beta, gamma=gamma, C = C, delta = delta)

  antivax_history = [sum(strategy.values())]

  while(new_strategy != strategy and t < TMAX):
    t += 1
    strategy = copy.deepcopy(new_strategy)
    
    antivax_history.append(sum(strategy.values()))

    if (random.random() < verbose):
      print("antivax at time ", t, ": ", sum(strategy.values())," Probability: ", sum(strategy.values()) / len(g.nodes) )
    new_strategy = simulate_one_parallel_epoch(graph = graph, x = strategy, alpha = alpha, beta = beta, gamma=gamma, C = C, delta = delta)

  return antivax_history, t, strategy

def get_init_sentiments(nnodes, PROB_PRO, PROB_ANTI, PROB_NEUTRAL):
  random.seed(42)
  initial_sentiments = np.random.choice(3, nnodes, p=[PROB_PRO, PROB_ANTI, PROB_NEUTRAL])

  init_sentiments_dict = {i: initial_sentiments[i] for i in range(len(initial_sentiments))}
  # print(init_sentiments_dict)

  return init_sentiments_dict

#### Experiment 1
#### this script plots histogram of number of epochs for NE
## varying the init strategy vector with fixed probabilities

RUN_THIS = False


alpha = 0
beta = 1

C_list = [70]
gamma_list = [0.9]
delta_list = [35]

PROB_PRO = 0.7
PROB_NEUTRAL = 0.0
PROB_ANTI = 0.3

NUMBER_OF_INIT_STRATEGY = 100

if RUN_THIS and __name__ == "__main__":

  epoch_list = []
  
  for gamma in gamma_list:
    for delta in delta_list:
      for C in C_list:
        for e in range(NUMBER_OF_INIT_STRATEGY):

          init_sentiments_dict = get_init_sentiments(g.number_of_nodes(), PROB_PRO=PROB_PRO, PROB_ANTI=PROB_ANTI, PROB_NEUTRAL = PROB_NEUTRAL)

          antivax_history, t, strategyNE = simulate_parallel(verbose = 0, graph=g, strategy= init_sentiments_dict, alpha = alpha, beta=beta, gamma=gamma, C = C, delta = delta) 
          epoch_list.append(t)
          # plot(x = range(len(antivax_history)), y = antivax_history, title = "gamma = {}, delta = {}, C = {}".format(gamma, delta, C), xlabel="# Epochs", ylabel="# Antivaccine nodes")


  plt.hist(epoch_list, bins = 'auto')

##### Experiment 2
##### plot # antivax per epoch

RUN_THIS = False

alpha = 5
beta = 1
# gamma = 0.9
# C = 70
# delta = 35 ## herd immunity does not guarantee total immunity
C_list = [0, 1, 8, 16, 32, 70]
gamma_list = [0.9]
delta_list = [35]

PROB_PRO = 0.7
PROB_NEUTRAL = 0.0
PROB_ANTI = 0.3

init_sentiments_dict = get_init_sentiments(g.number_of_nodes(), PROB_PRO=PROB_PRO, PROB_ANTI=PROB_ANTI, PROB_NEUTRAL = PROB_NEUTRAL)

if RUN_THIS and __name__ == "__main__":
  for gamma in gamma_list:
    for delta in delta_list:
      for C in C_list:
        antivax_history, t, strategyNE = simulate_parallel(verbose = 1, graph=g, strategy= init_sentiments_dict, alpha = alpha, beta=beta, gamma=gamma, C = C, delta = delta) 
        plot(showplot=False, x = range(len(antivax_history)), y = antivax_history, title="", label = "gamma = {}, delta = {}, C = {}".format(gamma, delta, C), xlabel="# Epochs", ylabel="# Antivaccine nodes")
        plt.legend()
        # plt.show()
        print("Time to converge:", t)

def get_antivax(strategyNE):
  s = []
  for i in range(len(strategyNE)):
    if (strategyNE[i] == 1):
      # print(i)
      s.append(i)
  
  return s

### Experiment 3
### let's understand the antivax nodes in NE
#############################################

RUN_THIS = True

alpha = 1
beta = 1

C_list = [2]
gamma_list = [0.9]
delta_list = [1]

PROB_PRO = 0.6
PROB_NEUTRAL = 0.0
PROB_ANTI = 0.4


NUM_ITERATION = 100

anti_degree_global_count = {} # dictionary of lists

if RUN_THIS and __name__ == "__main__":

  anti_degree_list = []
  anti_cluster_coef_list = []
  for gamma in gamma_list:
    for delta in delta_list:
      for C in C_list:
        anti_degree_local_count = {} # dictionary of ints

        for t in range(NUM_ITERATION):

          init_sentiments_dict = get_init_sentiments(g.number_of_nodes(), PROB_PRO=PROB_PRO, PROB_ANTI=PROB_ANTI, PROB_NEUTRAL = PROB_NEUTRAL)
          
          antivax_history, t, strategyNE = simulate_parallel(TMAX= 20,verbose = 0.01, graph=g, strategy= init_sentiments_dict, alpha = alpha, beta=beta, gamma=gamma, C = C, delta = delta) 
          # plot(x = range(len(antivax_history)), y = antivax_history, title = "gamma = {}, delta = {}, C = {}".format(gamma, delta, C), xlabel="# Epochs", ylabel="# Antivaccine nodes")
          antivaxNE = get_antivax(strategyNE)

          for i in antivaxNE:
            if not g.degree[i] in anti_degree_local_count.keys():
              anti_degree_local_count[g.degree[i]] = 0
            
            anti_degree_local_count[g.degree[i]] += 1
            anti_degree_list.append(g.degree[i])
            anti_cluster_coef_list.append(nx.clustering(g,i))
          
          # print(anti_degree_local_count)

          for deg, count in anti_degree_local_count.items():

            if not deg in anti_degree_global_count.keys():
              anti_degree_global_count[deg]=[]

            anti_degree_global_count[deg].append(count)


    save_obj(anti_degree_global_count, 'anti_degree_global_count')
    # plt.hist(anti_degree_list, bins = 'auto')
    # plt.hist(anti_cluster_coef_list, bins='auto')

def

# plt.hist(anti_degree_list, bins = 'auto', label="Histogram of degree of Antivaccine nodes in NE")
# plt.hist(anti_cluster_coef_list, bins='auto')

def boxplot_dictionary_in_chunks(dict1, split):
  # labels, data = [*zip(*dict1.items())]  # 'transpose' items to parallel key, value lists

  # or backwards compatable    
  labels = [key for key in sorted(dict1.keys())]
  data =  [dict1[key] for key in sorted(dict1.keys())]

  chunk = len(data)//split

  for i in range(split):
    plt.boxplot(data[i* chunk : (i+1)*chunk])
    plt.xticks(range(1 , chunk+1), labels[i* chunk: (i+1)*chunk])
    plt.xlabel("Degree of nodes in NE")
    plt.ylabel("Number of nodes")
    plt.show()

    # fig = plt.gcf()
    # fig.set_size_inches(40, 5)
    # fig.savefig('boxplot.png', dpi=200)


  plt.boxplot(data[split* chunk : -1])
  plt.xticks(range(len(labels[split* chunk : -1])), labels[split* chunk : -1])
  plt.xlabel("Degree of nodes in NE")
  plt.ylabel("Number of nodes")
  plt.show()


RUN_THIS = False

if RUN_THIS:
  boxplot_dictionary_in_chunks(anti_degree_global_count, split=6)

def make_antivax(strategy, s):
  for i in s:
    strategy[i] = 1

  return strategy


def make_provax(strategy, s):
  for i in s:
    strategy[i] = 0

  return strategy

def is_subset(lst1, lst2):

  for i in lst1:
    if( i not in lst2):
      # print(i)
      return False

  return True

### connect subgraph and make them antivax
#########################################

RUN_THIS = False


k = 100
S = random.sample(range(g.number_of_nodes()), k)

for i in S:
  for j in S:
    if not g.has_edge(i,j):
      g.add_edge(i,j)


#### this script plots histogram of number of epochs for NE
## varying the init strategy vector with fixed probabilities

alpha = 0
beta = 1
# gamma = 0.9
# C = 70
# delta = 35 ## herd immunity does not guarantee total immunity
C_list = [0]
gamma_list = [0.9]
delta_list = [35]

PROB_PRO = 0.7
PROB_NEUTRAL = 0.0
PROB_ANTI = 0.3

if RUN_THIS and __name__ == "__main__":

  epoch_list = []
  
  for gamma in gamma_list:
    for delta in delta_list:
      for C in C_list:


        init_sentiments_dict = get_init_sentiments(g.number_of_nodes(), PROB_PRO=PROB_PRO, PROB_ANTI=PROB_ANTI, PROB_NEUTRAL = PROB_NEUTRAL)

        make_antivax(init_sentiments_dict, S)

        antivax_history, t, strategyNE = simulate_parallel(verbose = 1, graph=g, strategy= init_sentiments_dict, alpha = alpha, beta=beta, gamma=gamma, C = C, delta = delta) 

        plot(x = range(len(antivax_history)), y = antivax_history, title = "gamma = {}, delta = {}, C = {}".format(gamma, delta, C), xlabel="# Epochs", ylabel="# Antivaccine nodes")


  print( is_subset( S, get_antivax(strategyNE=strategyNE) ) )
  print(S)
  print(get_antivax( strategyNE= strategyNE))

## Experiment 4
### stubborn nodes
### do it randomly
#########################################

RUN_THIS = True


k = 100
S = random.sample(range(g.number_of_nodes()), k)