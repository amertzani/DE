# functions for institutional updates
import eeverything as ee

def institution_my_update(self):
  my_prop_rules, my_prop_weights = integrate_maj_rules2(self.majority_voted,self.institutional_pool_rules, self.ilc_weights,self.increase_factor)
  #print('own', my_prop_weights)
  #print('maj',self.majority_voted)
  return my_prop_rules, my_prop_weights

def institution_oracle_update2(self):
  prop_rules = self.institutional_pool_rules
  prop_weights = self.ilc_weights
  self.suggested_rules, self.suggested_ruleweights = ee.prepare_rules_2_endorse(self,self.oracle_strategy,'institution') 
  if (self.knowledge_codification == 'advice'):
    max_weight, max_rules, e = ee.Oracle6('rule', 0, self,self.sources_of_opinion, self.sources_of_knowledge, self.knowledge_codification,self.suggested_rules, self.suggested_ruleweights)
    if (max_weight != 0): 
      #integrate suggested
      prop_rules, prop_weights = integrate_rules_all(self.institutional_pool_rules, self.ilc_weights, self.A, max_rules, max_weight,self.increase_factor)
  else:
    a, b, approved_rules = ee.Oracle6('rule', 0, self,self.sources_of_opinion, self.sources_of_knowledge, self.knowledge_codification,self.suggested_rules, self.suggested_ruleweights)
    #integrate endorced
    prop_rules, prop_weights = integrate_maj_rules2(approved_rules,self.institutional_pool_rules, self.ilc_weights,self.increase_factor) 
  return prop_rules, prop_weights

#consider only max-min proposed rules (called by agents)
def integrate_rules_max(rules, weights, A, max_keys, max_values):
  new_weights = weights.copy()
  new_rules = rules.copy()    
  if (max_keys == 0):
    return rules, weights
  for i in max_keys:
    if (new_weights.get(i) is not None):
      w_cur = new_weights.get(i)
    else: 
      w_cur = 0
      new_rules.append(i)
    w_new = w_cur+ A*(1-w_cur)
    new_weights[i] = w_new
  total = sum(new_weights.values())
  flag = 0
  for key, value in new_weights.items(): 
    new_weights[key] = value/total
    if (new_weights.get(key)<0.05):
      new_weights[key] = 0
      flag = 1
  new_w = new_weights.copy()
  if (flag):
    total = sum(new_weights.values())
    for key, value in new_weights.items(): 
      if (value == 0):
        new_w.pop(key)
      else:
        new_w[key] = value/total
  new_rules = list(new_w.keys())
  return new_rules, new_w

#consider all proposed rules (called by institution)
def integrate_rules_all(rules, weights, A, max_keys, max_values,increase_factor):
  #repeat for things in 
  new_weights = weights.copy()
  new_rules = rules.copy()
  if (max_keys == 0):
    return rules, weights
  for key, value in max_values.items(): 
    if (key not in new_rules):
      new_rules.append(key)
    new_weights[key] = new_weights.get(key,0) + value*increase_factor
  total = sum(new_weights.values())
  flag = 0
  for key, value in new_weights.items(): 
    new_weights[key] = value/total
    if (new_weights.get(key)<0.025):
      new_weights[key] = 0
      flag = 1
  new_w = new_weights.copy()
  if (flag):
    total = sum(new_weights.values())
    for key, value in new_weights.items(): 
      if (value == 0):
        new_w.pop(key)
      else:
        new_w[key] = value/total
  new_rules = list(new_w.keys())
  return new_rules, new_w

def integrate_maj_rules2(majority_vote,inst_rules,inst_weights,increase_factor):
  #repeat for things in
  rules = inst_rules.copy()
  weights = inst_weights.copy()
  for j in majority_vote:
    if (j not in rules):
      rules.append(j)
      weights[j] = increase_factor
    elif (weights.get(j) is None):
      weights[j] = increase_factor
    else:
      weights[j] = weights.get(j)*increase_factor
      #print(weights[j])
  total = sum(weights.values())
  flag = 0 
  for key, value in weights.items(): 
    weights[key] = value/total
    if (weights.get(key)<0.025):
      flag = 1
      weights[key] = 0
      rules.remove(key)
  w = weights.copy()
  if (flag):
    total = sum(weights.values())
    for key, value in weights.items():
      if (value == 0):
        w.pop(key)
      else:
        w[key] = value/total  
  rules = list(w.keys())
  return rules, w

def self_reflection_institution(self, my_prop_rules, my_prop_weights ,prop_rules, prop_weights):
  diff1 = 0
  diff2 = 0
  for key, value in my_prop_weights.items():
    if (self.popular_order_weights.get(key) is None):
      diff1 += value
    else:
      diff1 += abs(value-self.popular_order_weights.get(key))
  for key, value in prop_weights.items():
    if (self.popular_order_weights.get(key) is None):
      diff2 += value
    else:
      diff2 += abs(value-self.popular_order_weights.get(key))
  if (diff1 < diff2):
    self.confidence = min(self.confidence + self.A*(1 - self.confidence),1)
    self.oracletrust = max(self.oracletrust - self.B*self.oracletrust,0)
  elif (diff1 > diff2):
    self.confidence = max(self.confidence - self.B*self.confidence,0)
    self.oracletrust = min(self.oracletrust + self.A*(1-self.oracletrust),1)
