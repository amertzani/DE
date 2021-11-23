import random
import collections

def generate_rule_pool(number_of_claims = 8, starting_rule = 0):
  # lc1 : number of rounds agent has participated - effort
  # lc2 : number of rounds agent has been allocated ri > 0:0 - equals
  # lc3 : average amount agent has provisioned - contribution
  # lc4 : average amount agent has demanded - needs
  # lc5 : average amount agent has been allocated - equals
  # lc6 : normative satisfaction, satisfaction that this agent should have - equals 
  # lc7 : number of rounds agent has been asked for evaluation - social utility
  # lc8 : number of rounds agent has been asked for rule - social utility
  pool = ['lc1', 'lc2', 'lc3', 'lc4', 'lc5', 'lc6', 'lc7', 'lc8']
  remaining_pool = []
  #if wrong init, return list with all the rules
  if starting_rule > len(pool):
    return pool
  if starting_rule+number_of_claims > len(pool):
    return pool
  #do the job
  for i in range(starting_rule,starting_rule + number_of_claims):
    choice = pool[i]
    remaining_pool.append(choice)
  legitimate_claims = []
  for i in range(number_of_claims):
    selected_claim = random.choice(remaining_pool)
    legitimate_claims.append(selected_claim)
    remaining_pool.remove(selected_claim)
  return legitimate_claims

def generate_rule_weights_equal(institutional_pool_rules):
  inst_weights = {}
  inst_nof_rules = len(institutional_pool_rules)
  for lci in institutional_pool_rules:
    inst_weights[lci]=1/inst_nof_rules 
  return inst_weights

def generate_rule_weights_random(institutional_pool_rules):
  inst_weights = {}
  inst_nof_rules = len(institutional_pool_rules)
  for lci in institutional_pool_rules:
    inst_weights[lci]= random.uniform(0,1)
  total = sum(inst_weights.values())
  for lci in institutional_pool_rules:
    inst_weights[lci]= inst_weights.get(lci,0)/total 
  return inst_weights

#init agents rules
def pick_your_rules(pool):
  number_of_rules = random.randint(0, len(pool)) 
  # if (number_of_rules == 0):
  #   number_of_rules = random.randint(0, 1) 
  my_rules = []
  remaining_pool = pool.copy()
  for i in range(number_of_rules):
    selected_rule = random.choice(remaining_pool)
    my_rules.append(selected_rule)
    remaining_pool.remove(selected_rule)
  return my_rules

#initialise trust with 4 modes
def initialise_trust(node_list, trust_mode):
  init_trust = {}
  if (trust_mode == 'random'):
    for i in node_list:
      init_trust[i] = random.uniform(0,1)
  elif (trust_mode == 'average'):
    for i in node_list:
      init_trust[i] = 0.5    
  elif (trust_mode == 'zero'):
    for i in node_list:
      init_trust[i] = 0 
  elif (trust_mode == 'one'):
    for i in node_list:
      init_trust[i] = 1
  return init_trust

def init_agent_rule_weights_equal(rule_list):
  agent_lc_weights = {}
  agent_nof_rules = len(rule_list)
  for lci in rule_list:
    agent_lc_weights[lci]=1/agent_nof_rules
  agent_lc_weights_sorted = collections.OrderedDict(sorted(agent_lc_weights.items()))
  return agent_lc_weights_sorted

def init_agent_rule_weights_random(rule_list):
  agent_lc_weights = {}
  agent_nof_rules = len(rule_list)
  for lci in rule_list:
    agent_lc_weights[lci]=random.uniform(0,1)
  total = sum(agent_lc_weights.values())
  for lci in rule_list:
    agent_lc_weights[lci] = agent_lc_weights.get(lci)/total
  agent_lc_weights_sorted = collections.OrderedDict(sorted(agent_lc_weights.items()))
  return agent_lc_weights_sorted

def init_lcs(model):
  model.lc1 = {}
  model.lc1_Borda = {}
  model.lc2 = {}
  model.lc2_Borda = {}
  model.lc3 = {}
  model.lc3_Borda = {}
  model.lc4 = {}
  model.lc4_Borda = {}
  model.lc5 = {}
  model.lc5_Borda = {}
  model.lc6 = {}
  model.lc6_Borda = {}
  model.lc7 = {}
  model.lc7_Borda = {}
  model.lc8 = {}
  model.lc8_Borda = {}
  model.times_assign_task = 0
  model.times_do_the_task = 0
  model.lc1_w = 0 #popular rules
  model.lc2_w = 0
  model.lc3_w = 0
  model.lc4_w = 0
  model.lc5_w = 0
  model.lc6_w = 0
  model.lc7_w = 0
  model.lc8_w = 0
  model.rulerweight_1 = 0 #suggested by oracle
  model.rulerweight_2 = 0
  model.rulerweight_3 = 0
  model.rulerweight_4 = 0
  model.rulerweight_5 = 0
  model.rulerweight_6 = 0
  model.rulerweight_7 = 0
  model.rulerweight_8 = 0
  model.ints_rw_1 = 0 #institutions
  model.ints_rw_2 = 0
  model.ints_rw_3 = 0
  model.ints_rw_4 = 0
  model.ints_rw_5 = 0
  model.ints_rw_6 = 0
  model.ints_rw_7 = 0
  model.ints_rw_8 = 0
  model.exp_rw_1 = 0 #experts
  model.exp_rw_2 = 0
  model.exp_rw_3 = 0
  model.exp_rw_4 = 0
  model.exp_rw_5 = 0
  model.exp_rw_6 = 0
  model.exp_rw_7 = 0
  model.exp_rw_8 = 0

def init_helpers(self):
  self.rounds = 0
  self.generated_resources = 0
  #participation
  self.births = list(self.G) #all agents new
  self.deaths = []
  #resource distribution
  self.payments = {}
  self.Borda_score = {}
  self.borda_sorting = {}
  self.all_required_resources = {}
  self.start_coins = 0
  self.number_of_paid_agents = 0
  #evaluation
  self.avg_evaluation = 0
  self.actual_evaluation = 0
  self.average_satisfaction = 0
  self.all_evaluations = {}
  #oracle_updates
  self.all_times_asked = {}
  self.all_times_rule = {} 
  self.times_assign_task = 0
  self.times_do_the_task = 0
  self.freq_assign_task = 0
  self.freq_do_the_task = 0
  self.avg_over_rounds_assign = 0
  self.avg_over_rounds_do = 0
  self.all_times_do = 0
  self.all_times_assign = 0 
  self.all_trusted_weights = {}
  self.all_avg_satisfaction = {}
  self.all_degree = {}
  self.all_ages = {}
  #institutional updates
  self.increase_factor = 0.1
  self.counter = 0
  self.A = 0.1 #random.uniform(0,1)
  self.B = 0.1 #random.uniform(0,1)
  self.oracletrust = 1
  self.confidence = 0
  #-----------SOURCES------------
  self.sources_of_opinion = []
  self.all_times_source_opinion = {}
  self.opinion_times = []
  self.avg_op_times = 0
  self.sources_of_knowledge = []
  self.all_times_source_knowledge = {}
  self.knowledge_times = []
  self.avg_kn_times = 0
  self.pop_rules = []
  self.exp_rules = []
  self.majority_voted = [] 
  self.expert_rule_weights = {}
  self.popular_order_weights = {}
  self.maj_voted_weights = {}
  self.rules_2_endorse = []    
  self.weights_2_endorse = {}  
  self.nodes_opinion = []
  self.nodes_rule = []
  self.most_asked = 0
  self.most_ruled = 0
  self.suggested_node_opinion = []
  self.suggested_node_rule = []
  self.suggested_rules = []
  self.suggested_ruleweights = {}
  self.avg_degree = 0
  self.avg_age = 0
  init_lcs(self)
  self.popular_age = {}
  all_rules = generate_rule_pool(8,0)
  for lci in all_rules:
    self.popular_age[lci] = 0

def init_PL_helpers(model):
  #power law
  model.person_asked = {} #node that asked - who was asked
  model.own_or_network = {} # node that asked - 0:own 1:net
  model.finally_asked_this_round = {} #all nodes -> incr asked
  model.nof_asked = 0
  model.nof_done = 0
  model.freq_finally_asked_this_round = {} #all nodes ->finally_asked_this_round/total_asked
  model.nof_nodes_summing_50_perc = 0
  model.nof_nodes_replied = 0
  model.sum_all_asked = 0
  model.sum_all_done = 0
  model.sum_all_nof_replied = 0
  model.avg_all_asked = 0
  model.avg_all_done = 0
  model.avg_all_nof_replied = 0

def init_PL_helpers_agent(self):
  self.model.person_asked[self.unique_id] = random.choice(list(self.model.G))
  self.model.own_or_network[self.unique_id] = 0
  self.model.finally_asked_this_round[self.unique_id] = 0 #all nodes -> incr asked
  self.model.freq_finally_asked_this_round[self.unique_id] = 0 #all nodes ->finally_asked_this_round/total_asked
