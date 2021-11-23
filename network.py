# -*- coding: utf-8 -*-
import networkx as nx

import sys
from math import log
import random 

#init network
def klemm_eguilez_network(N,m,miu):
  G = nx.Graph()
  central = []
  notcentral = []
  #create fully connected netwrok of m nodes
  for i in range(m):
    G.add_node(i)
    central.append(i) #add node in list of active
    for j in G:
      if i!=j:
        G.add_edge(i, j)
  G.add_nodes_from(range(m, N)) # N-m nodes in the list
  for i in range(m,N):
    for j in central: #m edges to other nodes
      chance = random.uniform(0, 1)
      if (miu>chance) or (notcentral == []):
        G.add_edge(j, i)
      else:
        connected = 0
        while (connected==0):
          node2connect = random.choice(notcentral)
          chance2 = random.uniform(0, 1)
          E = 0
          k_j = G.degree[node2connect]
          for k in notcentral:
            E = E + G.degree[k]
          if (k_j/E)>chance2: #more likely to choose high degrees from inactive (attach to high degrees)
            G.add_edge(node2connect,i)
            connected = 1
    central.append(i)
    #remove central
    j_found = 0
    while (j_found == 0):
        j = random.choice(central)
        k_j = G.degree[j]
        E = 0
        for k in central:
          E = E + 1/G.degree[k]
        p_d = (1/k_j) / E #more likely to choose low degrees from active (remain active if high degree)
        chance3 = random.uniform(0, 1)
        if (p_d > chance3): 
          j_found = 1
          central.remove(j)
          notcentral.append(j)
  return (G,central,notcentral)

  
#generate list of neighbors
def find_neighbors_light(self):          
  agent = self.unique_id
  neighbors = [n for n in self.model.G.neighbors(agent)]
  nei2 = []
  #second
  for sec_nei in neighbors:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei2 = nei2 + neighbors_of_nei
  nei2 = list(dict.fromkeys(nei2)) #remove duplicates
  for i in nei2:
    if (i in neighbors):
      nei2.remove(i)
  #third
  nei3 = []
  for sec_nei in nei2:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei3 = nei3 + neighbors_of_nei
  nei3 = list(dict.fromkeys(nei3)) #remove duplicates
  for i in nei3:
    if (i in neighbors or i in nei2):
      nei3.remove(i)
  nei4 = []
  for sec_nei in nei3:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei4 = nei4 + neighbors_of_nei
  nei4 = list(dict.fromkeys(nei4)) #remove duplicates
  for i in nei4:
    if (i in neighbors or i in nei2 or i in nei3):
      nei4.remove(i)
  nei5 = []
  for sec_nei in nei4:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei5 = nei5 + neighbors_of_nei
  nei5 = list(dict.fromkeys(nei5)) #remove duplicates
  for i in nei5:
    if (i in neighbors or i in nei2 or i in nei3 or i in nei4):
      nei5.remove(i)
  nei6 = []
  for sec_nei in nei5:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei6 = nei6 + neighbors_of_nei
  nei6 = list(dict.fromkeys(nei6)) #remove duplicates
  for i in nei6:
    if (i in neighbors or i in nei2 or i in nei3 or i in nei4 or i in nei5):
      nei6.remove(i)
  hopp6_neighbors = neighbors + nei2  + nei3 + nei4 + nei5 + nei6
  #remove duplicates
  hopp6_neighbors = list(dict.fromkeys(hopp6_neighbors))
  # print(self.unique_id, active_nei)
  return hopp6_neighbors

#generate list of neighbors
def find_close_neighbors(self):          
  agent = self.unique_id
  neighbors = [n for n in self.model.G.neighbors(agent)]
  nei2 = []
  #second
  for sec_nei in neighbors:
    neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
    nei2 = nei2 + neighbors_of_nei
  nei2 = list(dict.fromkeys(nei2)) #remove duplicates
  for i in nei2:
    if (i in neighbors):
      nei2.remove(i)
  #third
  # nei3 = []
  # for sec_nei in nei2:
  #   neighbors_of_nei = [n for n in self.model.G.neighbors(sec_nei)] 
  #   nei3 = nei3 + neighbors_of_nei
  # nei3 = list(dict.fromkeys(nei3)) #remove duplicates
  # for i in nei3:
  #   if (i in neighbors or i in nei2):
  #     nei3.remove(i)
  hopp2_neighbors = neighbors + nei2  
  #remove duplicates
  hopp2_neighbors = list(dict.fromkeys(hopp2_neighbors))
  # print(self.unique_id, active_nei)
  return hopp2_neighbors

def compute_active_neighbors(self): 
  active = []
  for i in self.neighbors:
    if (i in self.model.activity_list):
      active.append(i)
  self.active_neighbors = active

def compute_active_close_neighbors(self): 
  active = []
  for i in self.close_neighbors:
    if (i in self.model.activity_list):
      active.append(i)
  self.active_close_neighbors = active
