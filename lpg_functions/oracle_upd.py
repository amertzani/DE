# functions for oracle updates
import random 

def find_sources(self):
  self.all_times_asked = {k: v for k, v in sorted(self.all_times_asked.items(), key=lambda item: item[1], reverse=True)}
  self.all_times_rule = {k: v for k, v in sorted(self.all_times_rule.items(), key=lambda item: item[1], reverse=True)}
  nofsources = 0
  sources_of_opinion = []
  times_asked = self.all_times_asked.copy()
  #remove not active
  for i in self.all_times_asked.keys():
    if (i not in self.activity_list):
      times_asked.pop(i)
  #find current sources
  while (nofsources < max(1,self.num_agents/10)):
    max_value = max(times_asked.values())  # maximum value
    max_keys = [k for k, v in times_asked.items() if v == max_value] # getting all keys containing the `maximum`
    l = len(max_keys)
    for i in range(0,l):
      key = random.choice(max_keys)
      max_keys.remove(key)
      sources_of_opinion.append(key)
      nofsources +=1
      times_asked.pop(key)
      if (nofsources  >= max(1,self.num_agents/10)):
        break
  #knowledge
  nofsources = 0
  sources_of_knowledge = []
  times_ruled = self.all_times_rule.copy()
  for i in self.all_times_rule.keys():
    if (i not in self.activity_list):
      times_ruled.pop(i)
  while (nofsources < self.num_agents/10):
    max_value = max(times_ruled.values())  # maximum value
    max_keys = [k for k, v in times_ruled.items() if v == max_value] # getting all keys containing the `maximum`
    l = len(max_keys)
    for i in range(0,l):
      key = random.choice(max_keys)
      max_keys.remove(key)
      sources_of_knowledge.append(key)
      times_ruled.pop(key)
      nofsources +=1
      if (nofsources  >= max(1,self.num_agents/10)):
        break
  #CALCULATE TIMES - UPDATE:
  current = []
  sum_times = 0 
  for i in sources_of_opinion:
    if (self.all_times_source_opinion.get(i) is None):
      self.all_times_source_opinion[i] = 1
    else:
      self.all_times_source_opinion[i] +=1
    current.append(self.all_times_source_opinion.get(i,1))
    sum_times += self.all_times_source_opinion.get(i,1)
  self.avg_op_times = sum_times/max(len(sources_of_opinion),1)
  self.opinion_times = current
  current = []
  sum_times = 0 
  for i in sources_of_knowledge:
    if (self.all_times_source_knowledge.get(i) is None):
      self.all_times_source_knowledge[i] = 1
    else:
      self.all_times_source_knowledge[i] +=1
    current.append(self.all_times_source_knowledge.get(i,1))
    sum_times += self.all_times_source_knowledge.get(i,1)
  self.avg_kn_times = sum_times/max(len(sources_of_opinion),1)
  self.knowledge_times = current
  return sources_of_opinion, sources_of_knowledge
