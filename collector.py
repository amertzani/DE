from mesa.datacollection import DataCollector   
#gini index of evaluations
def compute_gini(model):
    agent_evaluation = [agent.evaluation for agent in model.schedule.agents]
    x = sorted(agent_evaluation)
    N = model.nofactive
    if sum(x)==0:
      B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*1)
    else: 
      B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

def avg_resources(model):
  agent_resources = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.resources
  avg = sum/max(1,N)
  return avg

def avg_salary(model):
  agent_salary = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.salary
  avg = sum/max(1,N)
  return avg

def avg_cost(model):
  agent_salary = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.cost
  avg = sum/max(1,N)
  return avg

def avg_own_evaluation(model):
  agent_salary = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.my_evaluation
  avg = sum/max(1,N)
  return avg

def avg_network_evaluation(model):
  agent_salary = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.network_evaluation
  avg = sum/max(1,N)
  return avg

def avg_evaluation(model):
  agent_salary = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.evaluation
  avg = sum/max(1,N)
  return avg

def avg_shared_salaries(model):
  agent_salary = []
  N = 0
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and agent.salary!=0):
      sum += agent.salary
      N += 1
  avg = sum/max(1,N)
  return avg

def avg_distance(model):
  agent_distance = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.norm_distance
  avg = sum/max(1,N)
  return avg

def avg_satisfaction(model):
  agent_distance = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.satisfaction
  avg = sum/max(1,N)
  return avg

def avg_avg_satisfaction(model):
  agent_distance = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.avg_satisfaction
  avg = sum/max(1,N)
  return avg

def avg_demands(model):
  agent_distance = []
  N = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += agent.demands
  avg = sum/max(1,N)
  return avg

def avg_times_asked(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += model.all_times_asked.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_times_ruled(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      sum += model.all_times_rule.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_times_asked_suggested(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.suggested_node_opinion)):
      sum += model.all_times_asked.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_times_ruled_suggested(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.suggested_node_rule)):
      sum += model.all_times_rule.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_times_asked_notsuggested(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id not in model.suggested_node_opinion)):
      sum += model.all_times_asked.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_times_ruled_notsuggested(model):
  agent_distance = []
  n = model.nofactive
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id not in model.suggested_node_rule)):
      sum += model.all_times_rule.get(agent.unique_id,0)
  avg = sum/max(1,n)
  return avg

def avg_age_opinion(model):
  agent_distance = []
  N = 0
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.sources_of_opinion)):
      sum += agent.age
      N += 1
  avg = sum/max(1,N)
  return avg

def avg_age_knowledge(model):
  agent_distance = []
  N = 0
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.sources_of_knowledge)):
      sum += agent.age
      N += 1
  avg = sum/max(1,N)
  return avg

def avg_degree_opinion(model):
  agent_distance = []
  N = 0
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.sources_of_opinion)):
      sum += agent.degree
      N += 1
  avg = sum/max(1,N)
  return avg

def avg_degree_knowledge(model):
  agent_distance = []
  N = 0
  sum = 0
  for agent in model.schedule.agents:
    if ((agent.unique_id in model.activity_list) and (agent.unique_id in model.sources_of_knowledge)):
      sum += agent.degree
      N += 1
  avg = sum/max(1,N)
  return avg

  
def init_collectors(self):   
  self.datacollector = DataCollector(
      model_reporters={"Agent_Rules": "agent_pool_rules","Institutional_Rules": "institutional_pool_rules","Weights":"ilc_weights"},
      agent_reporters={"My_Rules":"myrules","My_weights":"rule_weights"})
  self.datacollector_1 = DataCollector(
      model_reporters={"Majority Voted": "majority_voted","Popular":"popular_order_weights"},
      agent_reporters={"Trust":"trust","Ruletrust":"ruletrust"}) 
  self.datacollector_2 = DataCollector(
      model_reporters={"Evaluation": "avg_evaluation"},
      agent_reporters={"neighbors":"neighbors","Active Neighbors":"active_neighbors","Close Network":"close_neighbors","Active Close Network":"active_close_neighbors","Nof active neighbors":"degree","State":"state",})
  self.datacollector_3 = DataCollector(
      model_reporters={"Actual evaluation":"actual_evaluation"},
      agent_reporters={"Last asked":"last_asked","Last ruled":"last_ruled"})
  self.datacollector_4 = DataCollector(
      model_reporters={"Experts":"experts"}) 
  self.datacollector_5 = DataCollector(
       model_reporters={"Average":"average"})   
  self.datacollector_6 = DataCollector(
      model_reporters={"Mediocre":"mediocre"})                  
  self.datacollector_7 = DataCollector(
      model_reporters={"Naive":"silly"})  
  self.datacollector_9 = DataCollector(
      model_reporters={"Know who":"sources_of_opinion","Know how":"sources_of_knowledge","All times asked":"all_times_asked","All times ruled":"all_times_rule"},
      agent_reporters={"Network Eval": "network_evaluation" ,"Own Eval": "my_evaluation", "Eval": "evaluation", "Satisfaction": "satisfaction"})                  
  self.datacollector_10 = DataCollector(
      model_reporters={"Assign Task":"freq_assign_task","Do the task":"freq_do_the_task"},
      agent_reporters={"Salary":"salary" ,}) 
  self.datacollector_11 = DataCollector(
      model_reporters={"Average salary":avg_salary,"Avg demands":avg_demands,"resources":"resources","Average Satisfaction":avg_satisfaction,"Average Cost":avg_cost,"Paid agents":"number_of_paid_agents"},#"Average of Average Satisfaction":avg_avg_satisfaction},
      agent_reporters={"Nof active neighbors":"degree",}) 
  self.datacollector_12 = DataCollector( 
      model_reporters={"Experts":"experts","Average":"average","Naive":"silly"})   
  self.datacollector_13 = DataCollector(
      model_reporters={"Intellectual level":"average_intellectual_level"})  
  self.datacollector_15 = DataCollector(
      model_reporters={"Avg own evaluation": avg_own_evaluation, "Avg network evaluation": avg_network_evaluation, "Avg evaluation": avg_evaluation,},
      agent_reporters={"Nof active neighbors":"degree",})   
  self.d_14 = DataCollector(
      model_reporters={"A LC1":"lc1_w","A LC2":"lc2_w","A LC3":"lc3_w","A LC4":"lc4_w","A LC5":"lc5_w","A LC6":"lc6_w","A LC7":"lc7_w","A LC8":"lc8_w"})
  self.d_15 = DataCollector(
      model_reporters={"I LC1":"ints_rw_1","I LC2":"ints_rw_2","I LC3":"ints_rw_3","I LC4":"ints_rw_4","I LC5":"ints_rw_5","I LC6":"ints_rw_6","I LC7":"ints_rw_7","I LC8":"ints_rw_8"})
  self.d_16 = DataCollector(
      model_reporters={"E LC1":"exp_rw_1","E LC2":"exp_rw_2","E LC3":"exp_rw_3","E LC4":"exp_rw_4","E LC5":"exp_rw_5","E LC6":"exp_rw_6","E LC7":"exp_rw_7","E LC8":"exp_rw_8"})
  self.d_17 = DataCollector(
      model_reporters={"O LC1":"rulerweight_1","O LC2":"rulerweight_2","O LC3":"rulerweight_3","O LC4":"rulerweight_4","O LC5":"rulerweight_5","O LC6":"rulerweight_6","O LC7":"rulerweight_7","O LC8":"rulerweight_8"})
  self.datacollector_17 = DataCollector(
      model_reporters={"Experts Divergence over rounds": "experts_divergence_over_rounds"})
  self.datacollector_18 = DataCollector(
      model_reporters={"EU Ensemble Divergence":"ensemble_divergence","EU Expert Divergence":"experts_divergence"})
  self.datacollector_19 = DataCollector(
      model_reporters={"EU Ensemble from Institution":"ensemble_from_institution_divergence","EU Experts from Institution":"expert_from_institution_divergence"})
  self.datacollector_20 = DataCollector(
      model_reporters={"EU Ensemble from Common":"ensemble_from_common_divergence","EU Experts from Common":"expert_from_common_divergence"}) 
  self.d_18 = DataCollector(
      model_reporters={"KL Ensemble Divergence":"ensemble_divergenceKL","KL Expert Divergence":"experts_divergenceKL"})
  self.d_19 = DataCollector(
      model_reporters={"KL Ensemble from Institution":"ensemble_from_institution_divergenceKL","KL Experts from Common":"expert_from_common_divergenceKL"})
  self.d_20 = DataCollector(
      model_reporters={"KL Ensemble from Common":"ensemble_from_common_divergenceKL","KL Experts from Institution":"expert_from_institution_divergenceKL"})
  self.d_21 = DataCollector(
      model_reporters={"Expertice Divergence asked": "exp_distr_change_from_prev_asked"})
  self.d_22 = DataCollector(
      model_reporters={"Expertice Divergence sources": "exp_distr_change_from_prev_source"})
  self.d_23 = DataCollector(
      model_reporters={"prob_asked": "prob_asked"})
  self.d_24 = DataCollector(
      model_reporters={ "prob_ruled": "prob_ruled"})
  self.d_25 = DataCollector(
      model_reporters={"prob_SoP": "prob_SoP"})
  self.d_26 = DataCollector(
      model_reporters={"prob_SoK": "prob_SoK"})
  self.datacollector_25 = DataCollector(
      model_reporters={"S Lc1 w":"rulerweight_1","S Lc2 w":"rulerweight_2","S Lc3 w":"rulerweight_3","S Lc4 w":"rulerweight_4","S Lc5 w":"rulerweight_5","S Lc6 w":"rulerweight_6","S Lc7 w":"rulerweight_7","S Lc8 w":"rulerweight_8"})
  self.datacollector_26 = DataCollector(
      model_reporters={"I Weight Lc1": "ints_rw_1","A Weight Lc1": "lc1_w", "O Weight Lc1": "rulerweight_1"})
  self.datacollector_27 = DataCollector(
      model_reporters={"I Weight Lc2": "ints_rw_2","A Weight Lc2": "lc2_w", "O Weight Lc2": "rulerweight_2"})
  self.datacollector_28 = DataCollector(
      model_reporters={"I Weight Lc3": "ints_rw_3","A Weight Lc3": "lc3_w", "O Weight Lc3": "rulerweight_3"})
  self.datacollector_29 = DataCollector(
      model_reporters={"I Weight Lc4": "ints_rw_4","A Weight Lc4": "lc4_w", "O Weight Lc4": "rulerweight_4"})
  self.datacollector_30 = DataCollector(
      model_reporters={"I Weight Lc5": "ints_rw_5","A Weight Lc5": "lc5_w", "O Weight Lc5": "rulerweight_5"})
  self.datacollector_31 = DataCollector(
      model_reporters={"I Weight Lc6": "ints_rw_6","A Weight Lc6": "lc6_w", "O Weight Lc6": "rulerweight_6"})
  self.datacollector_32 = DataCollector(
      model_reporters={"I Weight Lc7": "ints_rw_7","A Weight Lc7": "lc7_w", "O Weight Lc7": "rulerweight_7"})
  self.datacollector_33 = DataCollector(
      model_reporters={"I Weight Lc8": "ints_rw_8","A Weight Lc8": "lc8_w", "O Weight Lc8": "rulerweight_8"})
  self.datacollector_34 = DataCollector(
      model_reporters={"All times source opinion": "all_times_source_opinion","All times source knowledge": "all_times_source_knowledge"})
  self.d_35 = DataCollector(
      model_reporters={"times do": "times_do_the_task","times ask": "times_assign_task", "freq do": "freq_do_the_task","freq ask": "freq_assign_task"})
  self.d_36 = DataCollector(
      model_reporters={"nof ag":"num_agents","part":"nofactive", "avg over rounds do": "avg_over_rounds_do","avg over rounds ask": "avg_over_rounds_assign"}) 
  self.dc_1 = DataCollector(
      model_reporters={"nof_asked":"nof_asked","nof_done":"nof_done","nof_nodes_replied":"nof_nodes_replied"})   
  self.dc_2 = DataCollector(
      model_reporters={"avg nof_nodes_replied":"avg_all_nof_replied"}) 
  self.dc_3 = DataCollector(
      model_reporters={"avg kn times":"avg_kn_times","avg op times":"avg_op_times"}) 
  self.dc_4 = DataCollector(
      model_reporters={"avg nof_asked":"avg_all_asked","avg nof_done":"avg_all_done"}) 
  self.satcol_1 = DataCollector(
    model_reporters={"Average Satisfaction":avg_satisfaction})
  self.satcol_3 = DataCollector(
    model_reporters={"Average Average Satisfaction":avg_avg_satisfaction}) 
  if self.framework == 'RTSI_rule_reason':
    self.era_1 = DataCollector(
      model_reporters={"General Population Rules":"general_population_rules_dict", "Optimal Agent's Rules":"optimal_rules_dict"}) 
    self.era_2 = DataCollector(
      model_reporters={"GenPop-Inst EUDistance":"genpop_inst_EU", "OptAgent-Inst EUDistance":"optimal_inst_EU"})
