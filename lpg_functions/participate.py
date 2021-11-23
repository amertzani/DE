# functions for participation of model 
import random 
import eeverything as ee 
import networkx as nx

#choose births randomly
def choose_births(self,n_births):
    births = []
    max_existing = max(list(self.G)) #add always after
    for i in range(n_births):
      births.append(max_existing+i+1)
      my_neighbor = random.choice(list(self.G))
      self.G.add_edge(births[i],my_neighbor)
      self.notcentral.append(births[i])
    for i in births:
      a = ee.Agent(i, self)
      #add new agent to neighbors of neighbor
      a.neighbors.append(i)
      self.schedule.add(a)
    self.births = births
    self.num_agents = self.num_agents + n_births

#chouse births based on degree
def choose_births_degree(self,n_births,sorted_degree):
    births = []
    max_existing = max(list(self.G)) #add always after
    dict_keys = sorted_degree.keys()
    attach_new = list(dict_keys)[:n_births] #attach new to agents with more neighbors
    for i in range(n_births):
      births.append(max_existing+i+1)
      if (attach_new != []):
        my_neighbor = random.choice(attach_new)
        attach_new.remove(my_neighbor)
      else: 
        my_neighbor = random.choice(list(self.G))
      self.G.add_edge(births[i],my_neighbor)
      self.notcentral.append(births[i])
    for i in births:
      a = ee.Agent(i, self)
      #add new agent to neighbors of neighbor
      a.neighbors.append(i)
      self.schedule.add(a)
    self.births = births
    self.num_agents = self.num_agents + n_births

def choose_dead(self,n_deaths):
    #choose all the nodes that have to be killed 
    #remove them from the network
    #update central, notcentral
    #remove them from the schedule
    deads = []
    for i in range(n_deaths):
      dead = random.choice(list(self.G))
      Gtest = self.G.copy()
      Gtest.remove_node(dead)
      while (nx.is_connected(Gtest) == 0):
        Gtest = self.G.copy()
        dead = random.choice(list(self.G))
        Gtest.remove_node(dead)
      #you found it!
      self.G = Gtest
      deads.append(dead)
      if dead in self.notcentral:
        self.notcentral.remove(dead)
      else:
        self.central.remove(dead)
    #remove from schedule
    for i in deads:
      a = ee.Agent(i, self)
      neighbors = a.neighbors #find its neighbors and remove this one from them
      for j in neighbors:
        j.neighbors.remove(i)
      self.schedule.remove(a)
    self.deaths = deads
    self.num_agents = self.num_agents - n_deaths

  #get activity list from model and define if you are active in this round
def change_state(self):        
  if (self.unique_id in self.model.activity_list):
    self.state = 1 
  else:
    self.state = 0          
  self.modelrounds = self.model.rounds + 1
  self.activerounds = self.activerounds + self.state
  self.activitylevel = self.activerounds/self.modelrounds
