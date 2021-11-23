# functions for round updates of model 

#add institutional rules
def add_rules(self,to_be_added):
  new_list = self.agent_pool_rules.copy()
  new_list.extend(to_be_added)
  self.agent_pool_rules = list(dict.fromkeys(new_list))

#forget existing institutional rules (for restart mode)
def restart_rules(self,to_be_added):
  self.agent_pool_rules = to_be_added

  
