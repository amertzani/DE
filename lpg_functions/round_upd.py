# functions for round updates of model 

#add institutional rules
def add_rules(self,to_be_added):
  new_list = self.agent_pool_rules.copy()
  new_list.extend(to_be_added)
  self.agent_pool_rules = list(dict.fromkeys(new_list))

#forget existing institutional rules (for restart mode)
def restart_rules(self,to_be_added):
  self.agent_pool_rules = to_be_added

  
def compute_avg_rules_discovery(model):
  for agent in model.schedule.agents: 
    for key, value in agent.rule_weights.items():
      if key in model.general_population_rules_dict.keys():
        model.general_population_rules_dict[key] = model.general_population_rules_dict.get(key,0) + agent.rule_weights.get(key,0)
      else:
        model.general_population_rules_dict[key] = value
  for key, value in model.general_population_rules_dict.items():
    if key not in model.optimal_rules_dict.keys():
      model.optimal_rules_dict[key] = value 
  #normalise general population
  if len(model.general_population_rules_dict) != 0:
    factor=1.0/sum(model.general_population_rules_dict.values())
    for k in model.general_population_rules_dict:
      model.general_population_rules_dict[k] = model.general_population_rules_dict[k]*factor
  #make equal optimal rules
  if (len(model.optimal_rules_dict)!=0):
    factor=1.0/len(model.optimal_rules_dict)
    for k in model.optimal_rules_dict:
      model.optimal_rules_dict[k] = factor