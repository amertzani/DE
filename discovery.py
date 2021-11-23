#additions/modifications for discovery setting
import helpers as hp 
import random 

def gen_discotrust(agent):
    gen_trust = random.uniform(0,1) 
    return gen_trust

#initialisers required for discovery
def init_disco_avars(agent):
    agent.gen_trust = gen_discotrust(agent)
    return

def init_disco_mvars(model):
    model.general_population_rules_dict = {'lc1':1}  
    model.optimal_rules_dict = {'lc1':1}  
    model.genpop_inst_EU = 1 #euclidean_distance(model.general_population_rules_dict,model.ilc_weights)
    model.optimal_inst_EU = 1 #euclidean_distance(model.general_population_rules_dict,model.optimal_rules_dict)          
    compute_knowledge_EUdistance(model)

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

def compute_knowledge_EUdistance(model):
  model.genpop_inst_EU = hp.euclidean_distance(model.general_population_rules_dict,model.ilc_weights)
  model.optimal_inst_EU = hp.euclidean_distance(model.general_population_rules_dict,model.optimal_rules_dict)


