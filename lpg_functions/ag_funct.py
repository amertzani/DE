#agent related updates
import helpers as hp
import random

#agents self reflection
def self_reflection(self, update_trust, trust):
  diff1 = abs(self.model.avg_evaluation - self.my_evaluation)
  diff2 = abs(self.model.avg_evaluation - self.network_evaluation)
  if (update_trust == 1 and trust is not None): # if (network_evaluation is not None and trust is not None): # update only if at least one neighbor
    if (diff1 < diff2):
      self.confidence = min(self.confidence + self.a*(1 - self.confidence),1)
      self.trust[self.last_asked] = max(self.trust[self.last_asked] - self.b*self.trust[self.last_asked],0)
    elif (diff1 > diff2):
      self.confidence = max(self.confidence - self.b*self.confidence,0)
      self.trust[self.last_asked] = min(self.trust[self.last_asked] + self.a*(1-self.trust[self.last_asked]),1)
  return diff1


#trust for evaluation and trust for rule to new agents
def trust_to_new(self): 
  for i in list(self.model.G):
    if (i not in self.trust):
      if (self.model.trust_mode == 'random'):
        self.trust[i] = random.uniform(0,1)
      elif (self.model.trust_mode == 'average'):
          self.trust[i] = 0.5    
      elif (self.model.trust_mode == 'zero'):
          self.trust[i] = 0 
      elif (self.model.trust_mode == 'one'):
          self.trust[i] = 1
    if (i not in self.ruletrust):
      if (self.model.ruletrust_mode == 'random'):
        self.ruletrust[i] = random.uniform(0,1)
      elif (self.model.ruletrust_mode == 'average'):
          self.ruletrust[i] = 0.5    
      elif (self.model.ruletrust_mode == 'zero'):
          self.ruletrust[i] = 0 
      elif (self.model.ruletrust_mode == 'one'):
          self.ruletrust[i] = 1

def update_ruletrust(self, pos_rules, maj_voted):
  ruletrust = self.ruletrust.get(self.last_ruled)
  if (maj_voted != [] and ruletrust is not None):
    grade = 0
    if (pos_rules == 0):
      grade = -2
    else:
      for i in pos_rules:
        if (i in maj_voted):
          grade +=1
        else:
          grade -=1
    if (grade > 0): 
      self.ruletrust[self.last_ruled] = min(ruletrust + self.a*grade*(1-ruletrust),1)
    elif (grade < 0):
      self.ruletrust[self.last_ruled] = max(ruletrust + self.b*grade*ruletrust,0) #negative    

  #integrate proposed rules and weights (by oracle or neighbor) to agent or institution

def proposed_rules_popular_majority_expert_MEMORY(self):
  exp_ruleweights = {}
  common_ruleweights = {}
  rule_vote = {}
  for agent in self.schedule.agents:
    if (agent.unique_id in self.activity_list):
      #majority max
      if (self.majority_method == 'max_rules'):
        if (agent.rule_weights != {}):
          max_value = max(agent.rule_weights.values())  # maximum value
          max_keys = [k for k, v in agent.rule_weights.items() if v == max_value] # getting all keys containing the `maximum`
          if (max_keys != 0):
            for i in max_keys:
              rule_vote[i] = rule_vote.get(i,0) + 1
      #common knowledge -> total weights
      for rule, weight in agent.rule_weights.items():
        common_ruleweights[rule] = common_ruleweights.get(rule, 0) + weight            
        if (self.majority_method == 'important_rules'):
        #majority important
          if ( weight> 0.1 ):
            rule_vote[rule] = rule_vote.get(rule,0) + 1
        #expertise
        if (agent.unique_id in self.sources_of_knowledge):
          for rule, weight in agent.rule_weights.items():
            exp_ruleweights[rule] = exp_ruleweights.get(rule,0) + weight
  #compute oldness + normalise
  rule_oldness = {}
  combined_common = {}
  total = sum(common_ruleweights.values())
  for rule,value in self.popular_age.items():
    rule_oldness[rule] = self.popular_age.get(rule,0)/max(1,self.rounds) 
    common_ruleweights[rule] = common_ruleweights.get(rule,0)/total
    combined_common[rule] = self.past_factor*rule_oldness.get(rule,0) + self.present_factor*common_ruleweights.get(rule,0)
  total_combined = sum(combined_common.values())
  for key, value in combined_common.items(): 
    combined_common[key] = combined_common.get(key,0)/max(1,total_combined)
  #expert
  total = sum(exp_ruleweights.values())
  for rule in exp_ruleweights.keys():
    if (exp_ruleweights.get(rule) is not None): #do nothing
      lc_weight = exp_ruleweights.get(rule)
      exp_ruleweights[rule] = lc_weight/total
  #moved here: majority vote
  majority_voted = vote(self,rule_vote)
  if (majority_voted == []):
    max_value = max(rule_vote.values())  # maximum value
    majority_voted = [k for k, v in rule_vote.items() if v == max_value]
  maj_weights = {}
  for lci in majority_voted:
    maj_weights[lci] = 1/max(1,len(majority_voted))
  #moved here: common_rules only important
  pop_rules = []
  new_popular_weights = {}
  for key, value in combined_common.items(): 
    if (value > 1/max(1,len(combined_common))):
      pop_rules.append(key)
      new_popular_weights[key] = value
  total = sum(new_popular_weights.values())
  for key, value in new_popular_weights.items(): 
    new_popular_weights[key] = value/total
    self.popular_age[key] = self.popular_age.get(key,0) + 1 #increase age in popular rules
  #moved here: expert_rules only important  
  exp_rules = []
  exp_weights = {}
  for key, value in exp_ruleweights.items(): 
    if (value > 1/max(1,len(exp_ruleweights))):
      exp_rules.append(key)
      exp_weights[key] = value
  total = sum(exp_weights.values())
  for key, value in exp_weights.items(): 
    exp_weights[key] = value/total
  return pop_rules, new_popular_weights, exp_rules, exp_ruleweights, majority_voted, maj_weights

def vote(self,maj_rule_weights):
  majority_vote = []
  for key, value in maj_rule_weights.items():
    if (value/max(1,self.nofactive) >= 0.5):
      majority_vote.append(key)
  return majority_vote

def self_correction(self, update_trust, trust):
  diff1 = hp.euclidean_distance(self.rule_weights,self.model.ilc_weights)
  diff2 = hp.euclidean_distance(self.rule_weights,self.model.general_population_rules_dict)
  if (update_trust == 1 and trust is not None): # if (network_evaluation is not None and trust is not None): # update only if at least one neighbor
    if (diff1 < diff2):
      self.confidence = min(self.confidence + self.a*(1 - self.confidence),1)
      self.trust[self.last_asked] = max(self.trust[self.last_asked] - self.b*self.trust[self.last_asked],0)
    elif (diff1 > diff2):
      self.confidence = max(self.confidence - self.b*self.confidence,0)
      self.trust[self.last_asked] = min(self.trust[self.last_asked] + self.a*(1-self.trust[self.last_asked]),1)
  return diff1

