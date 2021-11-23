# functions for resource collection distribution of model 
import random 
import network as nt
import eeverything as ee
from lpg_functions import participate as lpg_part
#calculate legitimate claims of each agent and compute borda
def updates_lcs_and_Borda(self):
  for agent in self.schedule.agents:
    if (agent.unique_id in self.activity_list):
      self.lc1[agent.unique_id] =  round(agent.activitylevel,2)
      self.lc2[agent.unique_id] =  round(agent.allocationfreq,2)
      self.lc3[agent.unique_id] =  round(agent.provisionlevel,2)
      self.lc4[agent.unique_id] =  round(agent.requiredlevel,2)
      self.lc5[agent.unique_id] =  round(agent.allocationlevel,2)
      self.lc6[agent.unique_id] =  round(agent.normative_satisfaction,2)
      if (self.all_times_asked.get(agent.unique_id) is None):
        self.lc7[agent.unique_id] = 0
      else:   
        self.lc7[agent.unique_id] =  self.all_times_asked.get(agent.unique_id)
      if (self.all_times_rule.get(agent.unique_id) is None):
        self.lc8[agent.unique_id] = 0
      else:   
        self.lc8[agent.unique_id] =  self.all_times_rule.get(agent.unique_id)
  self.lc1_Borda = borda_points(self, self.lc1,'keep') #some lcs work the other way round
  self.lc2_Borda = borda_points(self, self.lc2,'reverse') 
  self.lc3_Borda = borda_points(self, self.lc3,'keep')
  self.lc4_Borda = borda_points(self, self.lc4,'reverse')
  self.lc5_Borda = borda_points(self, self.lc5,'reverse')
  self.lc6_Borda = borda_points(self, self.lc6,'reverse')
  self.lc7_Borda = borda_points(self, self.lc7,'keep')
  self.lc8_Borda = borda_points(self, self.lc8,'keep')
  self.Borda_score, self.borda_sorting = borda_score(self, 'model', self.institutional_pool_rules, self.ilc_weights)


#inistitution shares resources
def share_resources_lc(borda_ordered_dict, model):
  borda_ordered_dict  =  {k: v for k, v in sorted(borda_ordered_dict.items(), key=lambda item: item[1], reverse=True)} #just in case
  salary = {}
  init_coins = model.coins + model.generated_resources
  remaining_coins = model.coins + model.generated_resources
  # print('NEW ROUND')
  count = 0
  for key in borda_ordered_dict.keys():
    agent = key
    next_salary = model.all_required_resources.get(agent) #To be tested
    if (next_salary is not None):
      if (remaining_coins) >= next_salary:
        agent_salary = next_salary
        salary[agent] = agent_salary
        remaining_coins = remaining_coins - agent_salary
        count +=1
      else:
        salary[agent] = 0
  #print('out',count,'total',nofactive)
  return salary, remaining_coins, init_coins, count

def share_resources_lc_agents(borda_ordered_dict,model,start_coins):
  borda_ordered_dict  =  {k: v for k, v in sorted(borda_ordered_dict.items(), key=lambda item: item[1], reverse=True)} #just in case
  salary = {}
  init_coins = start_coins
  remaining_coins = start_coins
  # print('NEW ROUND')
  for key in borda_ordered_dict.keys():
    agent = key
    next_salary = model.all_required_resources.get(agent) #To be tested
    if (next_salary is not None):
      if (remaining_coins) >= next_salary:
        agent_salary = next_salary
        salary[agent] = agent_salary
        remaining_coins = remaining_coins - agent_salary
      else:
        salary[agent] = 0
  return salary

def run_agents_resource_updates_new(self):
  for agent in self.schedule.agents:
    agent.age += 1 
    self.all_ages[agent.unique_id] = agent.age 
    if (agent.age == 1):
      agent.neighbors = nt.find_neighbors_light(agent) #recompute neighbors at each step (useful if network N increases)
      agent.close_neighbors = nt.find_close_neighbors(agent)
      lpg_part.change_state(agent) #activity in this round
    if (agent.unique_id in self.activity_list):
      agent.generated = random.uniform(0, 1)
      agent.required =  random.uniform(agent.generated, 1)
      agent.provision = random.uniform(0, agent.generated) #agent's contribution
      agent.demands = agent.required #random.uniform(0, self.required)
      agent.provisionlevel =  agent.provisionlevel + agent.provision/max(agent.activerounds,1)
      agent.requiredlevel =  agent.requiredlevel + agent.required/max(agent.activerounds,1)
      self.coins = agent.model.coins + agent.provision #provision to pool
      self.all_required_resources[agent.unique_id] = agent.demands
      agent.resources = agent.generated - agent.provision

#auxiliary function for borda scores
def borda_points(self, lci, order):
  rank = 1
  if (order == 'keep'):
    lci_sorted =  {k: v for k, v in sorted(lci.items(), key=lambda item: item[1])}
  else: #reverse
    lci_sorted =  {k: v for k, v in sorted(lci.items(), key=lambda item: item[1], reverse=True)} #in this case the greater the value the more the least the points you get
  Borda_point = {}
  for i in lci_sorted:
    Borda_point[i] =  rank
    rank = rank + 1
  return Borda_point 

#borda score calculation for institution and agents
def borda_score(self, purpose = 'model', rules = [], weights = {}):
    Borda_score =  {}
    listactive = []
    if (purpose == 'model'):
      # rules = self.institutional_pool_rules
      # weights = self.ilc_weights
      model = self
    elif (purpose == 'agent'):
      # rules = self.myrules
      # weights = self.rule_weights
      model = self.model  
    if (rules != []): 
      for key, value in model.lc1_Borda.items():
        listactive.append(key)
      for i in listactive:
        first = 1 #flag for first rule (to sort a bug)
        if ('lc1' in rules):
          if (first):
            Borda_score[i] = model.lc1_Borda[i]*weights['lc1']
            first = 0
        if ('lc2' in rules): 
          if (first):
            Borda_score[i] = model.lc2_Borda[i]*weights['lc2']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i]+ model.lc2_Borda[i]*weights['lc2']
        if ('lc3' in rules):  
          if (first):
            Borda_score[i] = model.lc3_Borda[i]*weights['lc3']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc3_Borda[i]*weights['lc3']
        if ('lc4' in rules):  
          if (first):
            Borda_score[i] = model.lc4_Borda[i]*weights['lc4']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc4_Borda[i]*weights['lc4']
        if ('lc5' in rules):  
          if (first):
            Borda_score[i] = model.lc5_Borda[i]*weights['lc5']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc5_Borda[i]*weights['lc5']
        if ('lc6' in rules):  
          if (first):
            Borda_score[i] = model.lc6_Borda[i]*weights['lc6']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc6_Borda[i]*weights['lc6']
        if ('lc7' in rules):  
          if (first):
            Borda_score[i] = model.lc7_Borda[i]*weights['lc7']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc7_Borda[i]*weights['lc7']
        if ('lc8' in rules):  
          if (first):
            Borda_score[i] = model.lc8_Borda[i]*weights['lc8']
            first = 0 
          else:
            Borda_score[i] = Borda_score[i] + model.lc8_Borda[i]*weights['lc8']
    else: #if no rules random sorting
      for i in listactive:
        Borda_score[i] = random.randint(0, len(model.activity_list))
    Borda_score =  {k: v for k, v in sorted(Borda_score.items(), key=lambda item: item[1], reverse=True)}
    borda_sort = {}
    for i, key in enumerate(Borda_score.keys()):
      borda_sort[key] = i
    return Borda_score, borda_sort

#for agents

def get_resource_distribution(self): #self is agent
    if (self.unique_id in self.model.activity_list):
      self.salary = self.model.payments.get(self.unique_id,0)
      #self.salary = get_salary(self.model.payments,self.unique_id)
      self.resources = self.resources + self.salary
      if (self.salary!=0):
        self.timesallocated = self.timesallocated + 1
        self.allocationfreq =  self.timesallocated/max(1,self.activerounds)
        self.allocationlevel =  (self.allocationlevel*(self.activerounds-1) + self.salary)/max(self.activerounds,1)
        self.satisfaction = min(self.satisfaction + self.d*(1 - self.satisfaction),1)
        self.avg_satisfaction = self.satisfaction/max(self.activerounds,1)
      else:
        self.allocationfreq =  self.timesallocated/max(1,self.activerounds)
        self.allocationlevel =  (self.allocationlevel*(self.activerounds-1))/ max(self.activerounds,1)
        self.satisfaction = max(self.satisfaction - self.h*self.satisfaction,0)
        self.avg_satisfaction = self.satisfaction/max(self.activerounds,1)
      self.model.all_avg_satisfaction[self.unique_id] = self.avg_satisfaction 
      # if (self.unique_id == 40):
        # print('timas alloc',self.salary)
      if (self.model.average_satisfaction != 0): 
        self.normative_satisfaction = self.salary/max(1,self.model.average_satisfaction)
        # if (self.unique_id == 40):
          # print('normative_satisfaction',self.normative_satisfaction)
          # print('average_satisfaction',self.model.average_satisfaction)
