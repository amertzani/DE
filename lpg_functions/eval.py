# functions for evaluation of model 
from lpg_functions import res_col_distr as lpg_rcd
from lpg_functions import ag_funct as lpg_aupd
import network as nt
import eeverything as ee
import random 
import helpers as hp 

def run_agents_evaluation2(self): #self is model
  for agent in self.schedule.agents:
    self.own_or_network[agent.unique_id] = 0 #make it 0 if not active
    if (agent.unique_id in self.activity_list):
      lpg_rcd.get_resource_distribution(agent)
      #resource_distribution_updates(agent)
      nt.compute_active_neighbors(agent) #compute which are active
      nt.compute_active_close_neighbors(agent)
      agent.degree = len(agent.active_neighbors)
      self.all_degree[agent.unique_id] = agent.degree
      lpg_aupd.trust_to_new(agent)
      #EVALUATE INSTITUTION 
      agent.my_evaluation , agent.use_my_evaluation = compute_evaluation_new(agent) 
      self.all_first_evaluation[agent.unique_id] = agent.my_evaluation
  self.nof_asked = 0
  self.nof_done = 0
  for agent in self.schedule.agents:
    self.finally_asked_this_round[agent.unique_id]=0
    self.freq_finally_asked_this_round[agent.unique_id] =0
    if (agent.unique_id in self.activity_list):
      if (self.framework == 'RTSI_rules_oracle'):       
        agent.network_evaluation , agent.update_trust, use_network = ask_social_net_oracle_N(agent) #ask_social_net_2(self)
      else: #in both cases you ask network
        agent.network_evaluation , agent.update_trust, use_network = ask_social_net_N(agent)
      agent.last_trust, agent.evaluation = choose_evaluation_update_resources_and_participation_new(agent, agent.my_evaluation, agent.network_evaluation, agent.use_my_evaluation, use_network)
      if (self.own_or_network.get(agent.unique_id,0) == 1): # if agent asked network
        ask_soc_net_light(agent)
        self.nof_asked += 1
        key = self.person_asked.get(agent.unique_id,0)
        self.finally_asked_this_round[key] = self.finally_asked_this_round.get(key,0) + 1
      else: 
        self.nof_done += 1
  self.sum_all_asked += self.nof_asked
  self.sum_all_done += self.nof_done
  self.avg_all_asked = self.sum_all_asked/max(1,self.rounds)
  self.avg_all_done = self.sum_all_done/max(1,self.rounds)


#find evaluation of institution based on difference between its calculation and your calculation
def compute_evaluation_new(self): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!might too strict
  if (self.myrules == []): #if you have no rules/just random
    my_evaluation = random.randint(0,1)
    use_my_eval = 0
  else:
    self.my_borda_score, self.my_borda_sorting = lpg_rcd.borda_score(self, 'agent', self.myrules, self.rule_weights) 
    norm_distance = 0
    if (self.model.eval_method == 'order'):
      dist = hp.pairwise_comparison(self.my_borda_sorting, self.model.borda_sorting) #distance(self.my_borda_sorting, self.model.borda_sorting)
      norm_distance = dist #/(10*self.model.num_agents^2)
    else:  
      mypayments= lpg_rcd.share_resources_lc_agents(self.my_borda_score, self.model,self.model.start_coins)
      dist = hp.distance3(mypayments, self.model.payments)
      norm_distance = dist#/(self.model.nofactive)
    self.norm_distance = norm_distance
    if (dist>(1-self.model.eval_agent_threshold)): #if (norm_distance > (1-self.model.eval_agent_threshold)):
      my_evaluation = 0 #unfair
    else: 
      my_evaluation = 1 #fair
    use_my_eval = 1
  return my_evaluation,use_my_eval

#ask network without oracle
def ask_social_net_N(self):
  rand = random.randint(0,1)
  if (self.active_neighbors == []):
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked)
    if (network_evaluation is None):
      network_evaluation = rand
    update_trust = 0
    use_network = 0
    return network_evaluation, update_trust, use_network
  else: 
    #sort trust to others
    self.trust =  {k: v for k, v in sorted(self.trust.items(), key=lambda item: item[1], reverse=True)}
    trust_internal = self.trust.copy()
    max_value = max(self.trust.values())
    max_keys = [k for k, v in self.trust.items() if v == max_value] # getting all keys containing the `maximum`
    if (type(max_keys) == list):
      l = len(max_keys)
      for i in range(0,l):
        key = random.choice(max_keys)
        max_keys.remove(key)
        trust_internal.pop(key)
        p = random.uniform(0, 1)
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked)
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust, use_network
      #you did not find it in max -> look for it in the rest
      for key, value in trust_internal.items():
        p = random.uniform(0, 1)
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked)
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust, use_network
    #iterate over agents and randomly select whom to ask in the order of trust
    else:
      for key, value in self.trust.items():
        p = random.uniform(0, 1)
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust, use_network
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked)
    if (network_evaluation is None):
      network_evaluation = rand
      use_network = 0
    else:
      use_network = 1
    update_trust = 0
    return network_evaluation, update_trust, use_network

def ask_social_net_oracle_N(self):
  rand = random.randint(0,1)
  if (self.active_neighbors == []):
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
    if (network_evaluation is None):
      network_evaluation = rand
    use_network = 0
    update_trust = 0
    return network_evaluation, update_trust, use_network
  else:
    if (self.model.knowledge_codification == 'advice'):
      #it replies with an advice, a list of nodes --> we care about nodes_opinion, nodes_rule 
      self.model.suggested_node_opinion,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
      trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoE', 0, self.model, self.model.suggested_node_opinion,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
      if (nodes_opinion != []):
        for key in nodes_opinion:
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust, use_network
    else: #(self.model.knowledge_codification == 'bit')
      #sort trust to others
      self.trust =  {k: v for k, v in sorted(self.trust.items(), key=lambda item: item[1], reverse=True)}
      #iterate over agents and randomly select whom to ask in the order of trust
      for key, value in self.trust.items():
        #ask_if_trusted
        self.model.suggested_node_opinion,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
        trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoE', 0, self.model, self.model.suggested_node_opinion,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
        if (trusted):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust,use_network       
    #just to avoid failure
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
    if (network_evaluation is None):
      network_evaluation = rand
      use_network = 0
    else:
      use_network = 1
    update_trust = 0
    return network_evaluation, update_trust,use_network

    
def ask_soc_net_light(self):
  my_dict = {}
  my_trust = {}
  for key,value in self.model.own_or_network.items():
    if (key in self.model.activity_list and self.model.own_or_network.get(key,0) == 0):
      my_dict[key] = value
      my_trust[key] = self.trust.get(key,0)
  my_trust =  {k: v for k, v in sorted(my_trust.items(), key=lambda item: item[1], reverse=True)}
  selected = 0
  for key, value in my_trust.items():
    p = random.uniform(0, 1)
    if (p > 0.5):
      if (key in self.model.G.neighbors(self.unique_id)):
        self.last_asked = key
        selected = 1
  if (selected == 0):
    if (my_dict != {}):
      self.last_asked =  random.choice(list(my_dict.keys())) #randomly one not in neighbors
  self.model.person_asked[self.unique_id] = self.last_asked
  return


def choose_evaluation_update_resources_and_participation_new(self, my_evaluation, network_evaluation, use_my_evaluation, use_network):
  cost_of_calculation = len(self.myrules)/len(self.model.agent_pool_rules)#*self.c #To be adapted to the common pool
  self.cost = cost_of_calculation
  participation_rate = self.participation/self.modelrounds
  trust = self.trust.get(self.last_asked)
  if (self.model.agent_mindset == 'selfish'):
    if (self.satisfaction > 0.5):
      evaluation = 1
    else:
      evaluation = 0
    self.participation = self.participation + 1
    self.model.times_do_the_task = self.model.times_do_the_task + 1
    self.model.own_or_network[self.unique_id] = 0
  elif (self.model.agent_mindset == 'peer_altruistic'):
      if  (self.active_close_neighbors != []):
        nof_satisfied = 0
        if (self.satisfaction > 0.5):
          nof_satisfied +=1
        for agent in self.model.schedule.agents:
          if (agent.unique_id in self.active_close_neighbors):
            if (agent.satisfaction > 0.5):
              nof_satisfied +=1
        if (nof_satisfied/(len(self.active_close_neighbors)+1)>=0.7):
          evaluation = 1
        else:
          evaluation = 0
        self.participation = self.participation + 1
        self.model.times_do_the_task = self.model.times_do_the_task + 1
      else:
        evaluation = 0
        if (self.satisfaction > 0.5):
          evaluation = 1
        self.participation = self.participation + 1
        self.model.times_do_the_task = self.model.times_do_the_task + 1
      self.model.own_or_network[self.unique_id] = 0
  else: #altruistic
    if ((use_my_evaluation == 0 and use_network == 0) or (self.model.setting == 'normal_evaluation' and use_network == 0 and self.resources < cost_of_calculation)):
      p = random.randint(0,1)
      trust = self.trust.get(self.last_asked)
      self.model.times_assign_task = self.model.times_assign_task + 1
      self.model.own_or_network[self.unique_id] = 1
      if (p == 1):
        evaluation = my_evaluation
      else:
        evaluation = network_evaluation
    elif (use_network !=0 and use_my_evaluation == 0):
      evaluation = network_evaluation
      self.model.times_assign_task = self.model.times_assign_task + 1   
      self.model.own_or_network[self.unique_id] = 1
    elif (use_my_evaluation !=0 and use_network == 0):
      evaluation = my_evaluation
      self.resources = self.resources - cost_of_calculation
      self.participation = self.participation + 1
      self.model.times_do_the_task = self.model.times_do_the_task + 1 
      self.model.own_or_network[self.unique_id] = 0         
    else:
      if (self.model.setting == 'simple_evaluation'): #no cost of calculation
        if (trust < self.confidence):
          evaluation = my_evaluation
          self.resources = self.resources - cost_of_calculation
          self.participation = self.participation + 1
          self.model.times_do_the_task = self.model.times_do_the_task + 1
          self.model.own_or_network[self.unique_id] = 0
        else:
          evaluation = network_evaluation
          self.model.times_assign_task = self.model.times_assign_task + 1
          self.model.own_or_network[self.unique_id] = 1
      else:
        if (self.resources < cost_of_calculation):
          evaluation = network_evaluation
          self.model.times_assign_task = self.model.times_assign_task + 1
          self.model.own_or_network[self.unique_id] = 1
        elif (participation_rate + trust + cost_of_calculation < (len(self.model.agent_pool_rules)+2)*self.confidence): #NORMALISe 1st TO ONE!!!!
          evaluation = my_evaluation
          self.resources = self.resources - cost_of_calculation
          self.participation = self.participation + 1
          self.model.times_do_the_task = self.model.times_do_the_task + 1
          self.model.own_or_network[self.unique_id] = 0
        else:
          evaluation = network_evaluation
          self.model.times_assign_task = self.model.times_assign_task + 1
          self.model.own_or_network[self.unique_id] = 1
  self.model.all_evaluations[self.unique_id] = evaluation #gather evaluations
  return trust, evaluation

def ask_social_net_oracle_FINAL(self):
  rand = random.randint(0,1)
  if (self.active_neighbors == []):
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
    if (network_evaluation is None):
      network_evaluation = rand
    use_network = 0
    update_trust = 0
    return network_evaluation, update_trust, use_network
  else:
    if (self.model.knowledge_codification == 'advice'):
      #it replies with an advice, a list of nodes --> we care about nodes_opinion, nodes_rule 
      self.model.suggested_node_opinion,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
      trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoE', 0, self.model, self.model.suggested_node_opinion,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
      if (nodes_opinion != []):
        l = len(nodes_opinion)
        for i in range(0,l):
          key = random.choice(nodes_opinion)
          nodes_opinion.remove(key)
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust, use_network
      #node is not found
      network_evaluation, update_trust, use_network = ask_social_net_N(self)
      return network_evaluation, update_trust,use_network
    else: #(self.model.knowledge_codification == 'bit')
      #sort trust to others
      self.trust =  {k: v for k, v in sorted(self.trust.items(), key=lambda item: item[1], reverse=True)}
      #iterate over agents and randomly select whom to ask in the order of trust
      for key, value in self.trust.items():
        #ask_if_trusted
        self.model.suggested_node_opinion,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
        trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoE', 0, self.model, self.model.suggested_node_opinion,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
        if (trusted):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_asked = key
            #increase times asked
            if (self.model.all_times_asked.get(key) is None):
              self.model.all_times_asked[key] = 1
            else:
              current = self.model.all_times_asked.get(key)
              self.model.all_times_asked[key] = current + 1
            network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
            #if not evaluated yet
            if (network_evaluation is None):
              network_evaluation = rand
              use_network = 0
            else:
              use_network = 1
            update_trust = 1
            return network_evaluation, update_trust,use_network
            network_evaluation, update_trust, use_network = ask_social_net_N(self)
      network_evaluation, update_trust, use_network = ask_social_net_N(self)
      return network_evaluation, update_trust,use_network         
    #just to avoid failure
    self.last_asked =  random.choice(self.model.activity_list) #randomly one not in neighbors
    network_evaluation = self.model.all_first_evaluation.get(self.last_asked) 
    if (network_evaluation is None):
      network_evaluation = rand
      use_network = 0
    else:
      use_network = 1
    update_trust = 0
    return network_evaluation, update_trust,use_network

def rule_social_net_6_oracle_FINAL(self):
  if (self.active_neighbors == []): #theoretically can't happen
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust
  else:
    if (self.model.knowledge_codification == 'advice'):
      self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
      trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
      if (nodes_rule !=[]):
        l = len(nodes_rule)
        for i in range(0,l):
          key = random.choice(nodes_rule)
          nodes_rule.remove(key)
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_ruled = key
            #increase times asked
            if (self.model.all_times_rule.get(key) is None):
              self.model.all_times_rule[key] = 1
            else:
              current = self.model.all_times_rule.get(key)
              self.model.all_times_rule[key] = current + 1
            trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
            if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
              max_value = max(trusted_weights.values())  # maximum value
              max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
              update_rule_trust = 1              
              return max_value, max_keys, update_rule_trust
      max_value, max_keys, update_rule_trust = rule_social_net_4_a(self)
      return max_value, max_keys, update_rule_trust
    else:  #(self.model.knowledge_codification == 'bit')      
      #sort trust to others
      self.ruletrust =  {k: v for k, v in sorted(self.ruletrust.items(), key=lambda item: item[1], reverse=True)}
      trust_internal = self.ruletrust.copy()
      max_value = max(self.ruletrust.values())
      max_keys = [k for k, v in self.ruletrust.items() if v == max_value] # getting all keys containing the `maximum`
      if (type(max_keys) == list):
        l = len(max_keys)
        for i in range(0,l):
          key = random.choice(max_keys)
          max_keys.remove(key)
          trust_internal.pop(key)
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust
        for key, value in trust_internal.items():
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust    
      else:
        for key, value in self.ruletrust.items():
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust
      network_evaluation, update_trust, use_network = ask_social_net_N(self)
      return network_evaluation, update_trust,use_network      
    #backup plan
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust


#rule network without oracle
def rule_social_net_4_a(self):
  if (self.active_neighbors == []): #theoretically can't happen
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust
  else: 
    #sort trust to others
    self.ruletrust =  {k: v for k, v in sorted(self.ruletrust.items(), key=lambda item: item[1], reverse=True)}
    trust_internal = self.ruletrust.copy()
    max_value = max(self.ruletrust.values())
    max_keys = [k for k, v in self.ruletrust.items() if v == max_value] # getting all keys containing the `maximum`
    if (type(max_keys) == list):
      l = len(max_keys)
      for i in range(0,l):
        key = random.choice(max_keys)
        max_keys.remove(key)
        trust_internal.pop(key)
        p = random.uniform(0, 1)  
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_ruled = key
            #increase times asked
            if (self.model.all_times_rule.get(key) is None):
              self.model.all_times_rule[key] = 1
            else:
              current = self.model.all_times_rule.get(key)
              self.model.all_times_rule[key] = current + 1
            trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
            if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
              max_value = max(trusted_weights.values())  # maximum value
              max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
              update_rule_trust = 1              
              return max_value, max_keys, update_rule_trust
            else:
              update_rule_trust = 1
            return 0, 0, update_rule_trust 
      for key, value in trust_internal.items():
        p = random.uniform(0, 1)
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_ruled = key
            #increase times asked
            if (self.model.all_times_rule.get(key) is None):
              self.model.all_times_rule[key] = 1
            else:
              current = self.model.all_times_rule.get(key)
              self.model.all_times_rule[key] = current + 1
            trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
            if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
              max_value = max(trusted_weights.values())  # maximum value
              max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
              update_rule_trust = 1              
              return max_value, max_keys, update_rule_trust
            else:
              update_rule_trust = 1
            return 0, 0, update_rule_trust      
    else:
      for key, value in self.ruletrust.items():
        p = random.uniform(0, 1)
        if (p > 0.5):
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_ruled = key
            #increase times asked
            if (self.model.all_times_rule.get(key) is None):
              self.model.all_times_rule[key] = 1
            else:
              current = self.model.all_times_rule.get(key)
              self.model.all_times_rule[key] = current + 1
            trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
            if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
              max_value = max(trusted_weights.values())  # maximum value
              max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
              update_rule_trust = 1              
              return max_value, max_keys, update_rule_trust
            else:
              update_rule_trust = 1
            return 0, 0, update_rule_trust
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust

def rule_social_net_6_oracle_a(self):
  if (self.active_neighbors == []): #theoretically can't happen
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust
  else:
    if (self.model.knowledge_codification == 'advice'):
      self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
      trusted, nodes_opinion, nodes_rule = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule, self.model.knowledge_codification,[],{})
      if (nodes_rule !=[]):
        for key in nodes_rule: 
          if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
            self.last_ruled = key
            #increase times asked
            if (self.model.all_times_rule.get(key) is None):
              self.model.all_times_rule[key] = 1
            else:
              current = self.model.all_times_rule.get(key)
              self.model.all_times_rule[key] = current + 1
            trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
            if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
              max_value = max(trusted_weights.values())  # maximum value
              max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
              update_rule_trust = 1              
              return max_value, max_keys, update_rule_trust
            else:
              update_rule_trust = 1
            return 0, 0, update_rule_trust
    else:  #(self.model.knowledge_codification == 'bit')      
      #sort trust to others
      self.ruletrust =  {k: v for k, v in sorted(self.ruletrust.items(), key=lambda item: item[1], reverse=True)}
      trust_internal = self.ruletrust.copy()
      max_value = max(self.ruletrust.values())
      max_keys = [k for k, v in self.ruletrust.items() if v == max_value] # getting all keys containing the `maximum`
      if (type(max_keys) == list):
        l = len(max_keys)
        for i in range(0,l):
          key = random.choice(max_keys)
          max_keys.remove(key)
          trust_internal.pop(key)
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust
        for key, value in trust_internal.items():
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust    
      else:
        for key, value in self.ruletrust.items():
          self.model.suggested_node_opinion ,self.model.suggested_node_rule = ee.prepare_nodes_2_endorse(self,self.model.oracle_strategy,'agents')
          trusted,a,b = ee.Oracle6('SoK', 0, self.model, self.model.suggested_node_opinion ,self.model.suggested_node_rule , self.model.knowledge_codification,[],{})
          if (trusted):
            if (key in self.model.G.neighbors(self.unique_id) and key in self.model.activity_list):
              self.last_ruled = key
              #increase times asked
              if (self.model.all_times_rule.get(key) is None):
                self.model.all_times_rule[key] = 1
              else:
                current = self.model.all_times_rule.get(key)
                self.model.all_times_rule[key] = current + 1
              trusted_weights = self.model.all_trusted_weights.get(key) #dictionary {'lc1':0.3} maybe self.key
              if (trusted_weights is not None and trusted_weights != {}): # or self.agent_pool_rules == []):
                max_value = max(trusted_weights.values())  # maximum value
                max_keys = [k for k, v in trusted_weights.items() if v == max_value] # getting all keys containing the `maximum`
                update_rule_trust = 1 
                # print('max:',max_value, max_keys)             
                return max_value, max_keys, update_rule_trust
              else: 
                update_rule_trust = 1
              return 0, 0, update_rule_trust
    #backup plan
    self.last_ruled =  random.choice(self.model.activity_list) #randomly one not in network
    update_rule_trust = 0
    return 0, 0, update_rule_trust
