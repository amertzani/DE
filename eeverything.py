# pip install mesa

# Commented out IPython magic to ensure Python compatibility.
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import SimultaneousActivation
import random
from mesa.datacollection import DataCollector
from scipy.stats import bernoulli

# %matplotlib inline
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import metrics 
import math
import collections

# import hierarchical clustering libraries
import scipy.cluster.hierarchy as sch
import sklearn.metrics.pairwise as pw  
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, normalize

import sys
from math import log

import network as nt
import generators as gen
import collector
import helpers as hp
from lpg_functions import round_upd as lpg_rupd
from lpg_functions import participate as lpg_part
from lpg_functions import res_col_distr as lpg_rcd
from lpg_functions import eval as lpg_eval
from lpg_functions import oracle_upd as lpg_oupd
from lpg_functions import inst_upd as lpg_iupd
from lpg_functions import ag_funct as lpg_aupd
# from test import blah1 as bl1


def prepare_rules_2_endorse(self,role,caller):
  rules_2_endorse = []
  weights_2_endorse = {}
  if (role == 'agents'):
    rules_2_endorse = self.pop_rules
    weights_2_endorse = self.popular_order_weights
  elif (role == 'institution'):
    rules_2_endorse = self.institutional_pool_rules
    weights_2_endorse = self.ilc_weights
  elif (role == 'knowledge'):
    rules_2_endorse = list(self.expert_rule_weights.keys())
    weights_2_endorse = self.expert_rule_weights
  elif (role == 'all'):
    if (caller == 'agents'):
      rules_2_endorse = self.institutional_pool_rules
      weights_2_endorse = self.ilc_weights  
    else:
      rules_2_endorse = self.pop_rules
      weights_2_endorse = self.popular_order_weights
  else: #(role == 'external'):
    rules_2_endorse = self.rules_2_endorse 
    weights_2_endorse = self.weights_2_endorse 
  return rules_2_endorse, weights_2_endorse

def prepare_nodes_2_endorse(self,role,caller):
  if (caller == 'agents'):
    if (role == 'external'):
      nodes_opinion = self.model.nodes_opinion
      nodes_rule = self.model.nodes_rule
    elif (role == 'institution'):
      nodes_opinion = self.model.nodes_opinion
      nodes_rule = self.model.nodes_rule
    else:
      nodes_opinion = self.model.sources_of_opinion 
      nodes_rule = self.model.sources_of_knowledge
  else:
    if (role == 'institution'):
      nodes_opinion = self.model.nodes_opinion
      nodes_rule = self.model.nodes_rule
    elif(role == 'external'): 
      nodes_opinion = self.nodes_opinion
      nodes_rule = self.nodes_rule
    else:
      nodes_opinion = self.sources_of_opinion
      nodes_rule = self.sources_of_knowledge
  return nodes_opinion, nodes_rule

def Oracle6(purpose, node, model, nodes_opinion, nodes_rule, knowledge_codification, rules_2_endorse,weights_2_endorse):
  #role = 'institution', 'agents', 'all', 'knowledge'
  #caller = 'institution', 'agent'
  #purpose = 'rule', 'SoE', 'SoK', 'update_time'
  #exp_factor = (0,1)
  #agent_factor = (0,1)
  if (purpose == 'rule'):
    approved_rules = []
    if (knowledge_codification == 'bit'):
      for i in model.majority_voted: #inst proposes nodes in majority vote
        if (i in rules_2_endorse):
          approved_rules.append(i)
      return 0,0,approved_rules
    else:
      return weights_2_endorse, weights_2_endorse.keys(), 0
  elif (purpose == 'SoE'):
    trusted = 0
    if (knowledge_codification == 'bit'):
      if (node in nodes_opinion): #model.sources_of_opinion
        trusted = 1
      else:
        trusted = 0
    else:  #(knowledge_codification == 'advice'):
      if (nodes_opinion != []):
        random_expert = random.choice(nodes_opinion)
        trusted = random_expert
      else:
        trusted = 0
    return trusted, nodes_opinion, nodes_rule
  elif (purpose == 'SoK'):
    if (knowledge_codification == 'bit'):
      if (node in nodes_rule): #model.sources_of_knowledge):
        trusted = 1
      else:
        trusted = 0
    else:
      if (nodes_rule != []):
        random_expert = random.choice(nodes_rule)
        trusted = random_expert
      else:
        trusted = 0    
    return trusted, nodes_opinion, nodes_rule
  elif (purpose == 'update_time'):
    print('hallo')


def compute_knowledge_EUdistance(model):
  model.genpop_inst_EU = hp.euclidean_distance(model.general_population_rules_dict,model.ilc_weights)
  model.optimal_inst_EU = hp.euclidean_distance(model.general_population_rules_dict,model.optimal_rules_dict)

"""##Model and Agents"""

class Agent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.opinion = random.randint(0, 1) #normalised opinion
        self.name = unique_id
        self.neighbors = []
        self.close_neighbors = []
        self.active_close_neighbors = []      
        self.degree = 0
        self.norm_distance = 0
        self.model.all_degree[self.unique_id] = self.degree
        self.active_neighbors = []
        #get activity list from model and define if you are active in this round
        self.state = 0
        self.activerounds = self.state  #agent active rounds
        self.activitylevel = self.activerounds/1.0 #normalised activity level
        self.participation = 0 # i think same as self.activerounds
        self.modelrounds = 1
        self.age = 0
        self.myrules = gen.pick_your_rules(model.agent_pool_rules)
        if (self.model.agent_ruleweights_init == 'random'):
          self.rule_weights = gen.init_agent_rule_weights_random(self.myrules) #dictionary
        else:
          self.rule_weights = gen.init_agent_rule_weights_equal(self.myrules)
        if (model.oracle_strategy == 'institution' and unique_id < 10):
          model.nodes_opinion.append(unique_id)
          self.myrules =  model.institutional_pool_rules.copy()
          self.rule_weights = model.ilc_weights.copy()
        elif (model.oracle_strategy == 'institution' and unique_id < 20):
          model.nodes_rule.append(unique_id)  
          self.myrules =  model.institutional_pool_rules.copy()
          self.rule_weights = model.ilc_weights.copy()
        self.cost = 0
        self.salary = 0 # allocation
        self.generated = 0 #random.uniform(0, 5)
        self.required =  0 #random.uniform(self.generated, 5) #not abundance
        self.provision = 0 #random.uniform(0, self.generated) #agent's contribution to cp
        self.demands = 0 #random.uniform(0, self.required)
        self.resources = 0 #self.generated - self.provision #what the agent gave to the institution
        self.timesallocated =  0
        self.allocationfreq =  0
        self.provisionlevel =  0 #self.provision/1
        self.requiredlevel =  0 #self.required/1
        self.allocationlevel =  0
        self.satisfaction = 0.5 #init satisfaction
        self.avg_satisfaction = 0.5
        self.model.all_avg_satisfaction[self.unique_id] = self.avg_satisfaction 
        self.normative_satisfaction = 0.5
        self.confidence = 0.5
        self.trust = gen.initialise_trust(list(self.model.G), self.model.trust_mode) #trust for evaluation to each node
        self.ruletrust  = gen.initialise_trust(list(self.model.G), self.model.ruletrust_mode) #trust for rule to each node
        self.network_evaluation = random.randint(0,1)
        self.my_evaluation = random.randint(0,1)
        self.evaluation = self.my_evaluation
        self.model.all_evaluations[self.unique_id] = self.evaluation
        self.model.all_times_asked[self.unique_id] = 0 #for lc7 - how frequently this node is asked
        self.model.all_times_rule[self.unique_id] = 0 #for lc8 - how frequently this node is asked
        self.model.all_trusted_weights[self.unique_id] = self.rule_weights
        self.model.all_times_source_opinion[self.unique_id] = 0
        self.model.all_times_source_knowledge[self.unique_id] = 0
        #agent specific coefficients for individual self-assessment
        self.a = 0.1 #trust pos
        self.b = 0.1 #trust neg
        self.d = 0.1 #satisfaction
        self.h = 0.1 #satisfaction
        self.c = 0.1#cost of computation 
        self.last_asked = random.choice(list(self.model.G))
        self.last_ruled = random.choice(list(self.model.G))
        self.my_borda_score = {}
        self.my_borda_sorting = {}
        #to be reconsidered
        self.oracletrust = 1
        self.insttrust = 1
        self.oracle_threshold = 0.5
        self.update_trust = 0
        self.last_trust = 0
        self.model.all_ages[self.unique_id] = self.age
        self.model.all_first_evaluation[self.unique_id] = random.randint(0,1)
        self.use_my_evaluation = 0
        self.model.prob_asked[self.unique_id] = 0
        self.model.prob_ruled[self.unique_id] = 0
        self.model.prob_SoP[self.unique_id] = 0
        self.model.prob_SoK[self.unique_id] = 0
        gen.init_PL_helpers_agent(self)

    def step(self):
        #SELF-REFLECTION TO AGENT
        if (self.unique_id in self.model.activity_list):  
          #if (self.unique_id == 1):
            #print('init',self.rule_weights)   
          #considers only one neighbor for now
          if (self.model.framework != 'RTSI_rule_reason'):
            diff1 = lpg_aupd.self_reflection(self, self.update_trust, self.last_trust)
          else:
            diff1 = lpg_aupd.self_correction(self, self.update_trust, self.last_trust)
          #for now let's keep the rest the same!
          if (self.model.framework != 'RTSI'): 
            #decide whether you will ask for a rule
            if (diff1 > self.model.agents_update_threshold): #you need to ask
              #ask network for rule
              if (self.model.ask_for_rules != 'oracle'):
                if (self.model.framework == 'RTSI_rules_oracle'):
                  max_value, max_keys, update_rule_trust = lpg_eval.rule_social_net_6_oracle_a(self) #rule_social_net_3(self)
                else: 
                  max_value, max_keys, update_rule_trust = lpg_eval.rule_social_net_4_a(self)
                  if (max_keys != 0): #check that something was proposed
                  #integrate new rule
                    self.myrules, self.rule_weights = lpg_iupd.integrate_rules_max(self.myrules, self.rule_weights, self.a,  max_keys, max_value)
                  if (update_rule_trust == 1): #update trust for rue
                    lpg_aupd.update_ruletrust(self, max_keys,self.model.majority_voted)
              if (self.model.ask_for_rules != 'network'):
                if (self.model.framework == 'RTSI_rules_oracle'): #ask also oracle
                  a_rules, a_weights = prepare_rules_2_endorse(self.model,self.model.oracle_strategy,'agents') 
                  if (self.model.knowledge_codification == 'advice'):
                    max_weight, max_rules, e = Oracle6('rule', 0, self.model,[],[], self.model.knowledge_codification, a_rules, a_weights)
                    if (max_weight != {}): 
                      #integrate suggested
                      self.myrules, self.rule_weights = lpg_iupd.integrate_rules_all(self.myrules, self.rule_weights, self.a,  max_rules, max_weight, self.model.increase_factor) 
          self.rule_weights = collections.OrderedDict(sorted(self.rule_weights.items()))
          self.model.all_trusted_weights[self.unique_id] = self.rule_weights 
          self.resources = 0

class Model(Model):
    def __init__(self,inst_adaptation = 'inactive',past_factor = 0.3,present_factor = 0.7, majority_method = 'max_rules', N = 200, m = round(200/3), miu = 0.8, nofactive = round(200/2), institutional_pool_rules = [], agent_pool_rules = [], initial_coins = 0, trust_mode = 'average', ruletrust_mode = 'average', inst_lc_weights = {}, update_time = 10, agents_update_threshold = 0.5, agent_mindset = 'not_ego',birth_framework = 'random',eval_inst_threshold = 0.5, eval_agent_threshold = 0.5, framework = 'RTSI_rules_oracle', oracle_strategy = 'all',  oracle_strategy_agents = 'all', e_factor = 0.5, a_factor = 0.5, setting = 'simple_evaluation',death_framework = 'random',elder_age = 100, knowledge_codification = 'bit', eval_method = 'order',ask_for_rules = 'network_oracle', agent_ruleweights_init = 'equal'):
        self.num_agents = N
        self.miu = miu
        self.m = m
        self.oracle_strategy = oracle_strategy
        self.agent_ruleweights_init = agent_ruleweights_init
        self.ask_for_rules = ask_for_rules
        self.majority_method = majority_method
        self.eval_method = eval_method
        self.past_factor = past_factor
        self.present_factor = present_factor
        self.inst_adaptation = inst_adaptation
        self.G, self.central, self.notcentral = nt.klemm_eguilez_network(N,m,miu)
        self.schedule = SimultaneousActivation(self)
        self.birth_framework = birth_framework
        self.death_framework = death_framework
        self.elder_age = elder_age
        self.nofactive = nofactive
        self.activity_list = random.sample(list(self.G),nofactive)
        self.institutional_pool_rules = institutional_pool_rules
        self.agent_pool_rules = agent_pool_rules #it is erased
        self.coins = initial_coins       
        self.ilc_weights = inst_lc_weights
        self.trust_mode = trust_mode
        self.ruletrust_mode = ruletrust_mode
        gen.init_helpers(self)
        self.update_time = update_time
        self.agent_mindset = agent_mindset
        self.agents_update_threshold = agents_update_threshold
        self.eval_inst_threshold = eval_inst_threshold  
        self.eval_agent_threshold = eval_agent_threshold   
        self.oracle_strategy_agents = oracle_strategy_agents
        self.framework = framework
        self.setting = setting
        self.knowledge_codification = knowledge_codification
        self.helper = 0
        self.ensemble_divergence = 0
        self.experts_divergence = 0
        self.ensemble_from_institution_divergence = 0
        self.expert_from_institution_divergence = 0
        self.ensemble_from_common_divergence = 0
        self.expert_from_common_divergence = 0
        self.experts_divergence_over_rounds = 0 
        self.ensemble_divergenceKL = 0
        self.experts_divergenceKL = 0
        self.ensemble_from_institution_divergenceKL = 0
        self.expert_from_institution_divergenceKL = 0
        self.ensemble_from_common_divergenceKL = 0
        self.expert_from_common_divergenceKL = 0
        self.exp_distr_change_from_prev_asked = 0
        self.exp_distr_change_from_prev_source = 0
        self.experts = 0     
        self.silly = 0  
        self.mediocre = 0
        self.average = 0
        self.experts_knowledge = {}
        self.average_intellectual_level = 0
        self.all_first_evaluation = {}
        self.prob_asked = {}
        self.prob_ruled = {}
        self.prob_SoP = {}
        self.prob_SoK = {}
        gen.init_PL_helpers(self)
        count = 0
        count2 = 0
        first_nodes = []
        second_nodes = []
        for i in range(self.num_agents):
          b = i
          a = Agent(i, self)
          self.schedule.add(a)
          #oracle not independent consultant
          if (count < 10):
            first_nodes.append(a.unique_id)
            count += 1
          self.nodes_opinion = first_nodes
          if (count >= 10 and count2 < 20):
            second_nodes.append(a.unique_id)
            count2+=1
          self.nodes_rule = second_nodes
          inst_weights = gen.generate_rule_weights_equal(institutional_pool_rules)
        if (self.framework == 'RTSI_rule_reason'): 
          self.general_population_rules_dict = {'lc1':1}  
          self.optimal_rules_dict = {'lc1':1}  
          self.genpop_inst_EU = 1 #euclidean_distance(model.general_population_rules_dict,model.ilc_weights)
          self.optimal_inst_EU = 1 #euclidean_distance(model.general_population_rules_dict,model.optimal_rules_dict)          
          #compute_knowledge_EUdistance(self)
        collector.init_collectors(self)  

    def round_updates(self,to_be_added,mode,generated_resources,rules_2_endorse,weights_2_endorse):
        self.rounds = self.rounds + 1
        self.generated_resources = generated_resources 
        self.rules_2_endorse = rules_2_endorse
        self.weights_2_endorse = weights_2_endorse
        if (to_be_added != []):
          if (mode == 'add'):
            lpg_rupd.add_rules(self,to_be_added)
          else:
            lpg_rupd.restart_rules(self,to_be_added)
        if (self.framework == 'RTSI_rule_reason'):
          lpg_rupd.compute_avg_rules_discovery(self)
        
    def participation(self,n_births,n_deaths):
        sorted_all_degree =  {k: v for k, v in sorted(self.all_degree.items(), key=lambda item: item[1], reverse=True)} #sort - largest first
        if (self.birth_framework == 'random'):
          lpg_part.choose_births(self,n_births)
        elif (self.birth_framework == 'degree_attachment'):
          lpg_part.choose_births_degree(self,n_births,sorted_all_degree)
        if (self.death_framework == 'random'):
          lpg_part.choose_dead(self,n_deaths)
        self.activity_list = random.sample(list(self.G),self.nofactive) #len activity list     

    def resource_collection_distribution(self):
        lpg_rcd.run_agents_resource_updates_new(self) #agents generate resources
        lpg_rcd.updates_lcs_and_Borda(self)
        self.payments, self.coins, self.start_coins, total_paid = lpg_rcd.share_resources_lc(self.Borda_score, self) #update payments and remaining resources
        self.number_of_paid_agents = total_paid/max(1,self.nofactive)
        self.average_satisfaction = self.start_coins/max(self.nofactive,1) #self.coins/nofactive  
        self.datacollector_11.collect(self)

    def evaluation(self):
        lpg_eval.run_agents_evaluation2(self)
        hp.compute_power_law(self)
        self.dc_1.collect(self)
        self.dc_2.collect(self)
        self.dc_3.collect(self)
        self.dc_4.collect(self)
        self.datacollector_9.collect(self)
        self.datacollector_10.collect(self) 
        self.actual_evaluation = sum(self.all_evaluations.values()) / max(len(self.all_evaluations),1) #sum(self.all_evaluations.values()) / max(len(self.all_evaluations),1) 
        if (self.actual_evaluation < self.eval_inst_threshold):
          self.avg_evaluation = 0 #unfair
        else:
          self.avg_evaluation = 1 #fair
        self.datacollector_2.collect(self)
        self.datacollector_3.collect(self)
        self.datacollector_17.collect(self)
        self.datacollector_15.collect(self)
        self.avg_over_rounds_do = 0
        self.avg_over_rounds_assign = 0

    def oracle_updates(self):
      self.sources_of_opinion, self.sources_of_knowledge = lpg_oupd.find_sources(self) #used when oracle
      self.pop_rules, self.popular_order_weights, self.exp_rules, self.expert_rule_weights, self.majority_voted, self.maj_voted_weights = lpg_aupd.proposed_rules_popular_majority_expert_MEMORY(self)
      hp.store_average_weights(self)
      self.datacollector_1.collect(self)
      self.datacollector_34.collect(self) 
      hp.update_ruleweights(self)
      self.d_14.collect(self)
      self.d_15.collect(self)
      self.d_16.collect(self)
      self.d_17.collect(self)
      self.datacollector_26.collect(self)
      self.datacollector_27.collect(self)
      self.datacollector_28.collect(self)
      self.datacollector_29.collect(self)
      self.datacollector_30.collect(self)
      self.datacollector_31.collect(self)
      self.datacollector_32.collect(self)
      self.datacollector_33.collect(self)

    def institutional_updates(self):
      hp.degree_age_updates(self) 
      self.datacollector_10.collect(self)
      self.datacollector_11.collect(self)
      if (self.framework != 'RTSI'):
        if (self.avg_evaluation == 0):
          self.counter = self.counter + 1
        else: 
          self.counter = max(self.counter-1,0)
        if (self.counter >= self.update_time):
          self.helper += 1
          # print(self.helper)
          if (self.framework == 'RTSI_rules'):
            self.institutional_pool_rules, self.ilc_weights = lpg_iupd.institution_my_update(self) #maj_rulesXupdate_factor
          else:
            my_prop_rules, my_prop_weights = lpg_iupd.institution_my_update(self) #integrates maj_rulesXupdate_factor
            prop_rules, prop_weights = lpg_iupd.institution_oracle_update2(self) #
            # print('own rules:', my_prop_weights)
            # print('oracle rules:', prop_weights)
            if (self.oracletrust < self.confidence):
              self.institutional_pool_rules, self.ilc_weights = my_prop_rules, my_prop_weights
            else:
              self.institutional_pool_rules, self.ilc_weights = prop_rules, prop_weights
            # print('final rules:',self.ilc_weights)
            lpg_iupd.self_reflection_institution(self, my_prop_rules, my_prop_weights ,prop_rules, prop_weights)
          self.counter = 0
          # print(self.ilc_weights)

    def collectors(self):
        self.freq_assign_task = self.times_assign_task/max(1,self.nofactive)
        self.freq_do_the_task = self.times_do_the_task/max(1,self.nofactive)
        self.most_asked = max(self.all_times_asked.values())  # maximum value
        self.most_ruled = max(self.all_times_rule.values()) 
        self.all_times_do += self.times_do_the_task
        self.all_times_assign += self.times_assign_task
        self.avg_over_rounds_do = self.all_times_do/max(1,self.rounds)
        self.avg_over_rounds_assign = self.all_times_assign/max(1,self.rounds)
        self.datacollector.collect(self)     
        self.d_35.collect(self)
        self.d_36.collect(self)
        self.satcol_1.collect(self)
        self.satcol_3.collect(self)

    def sample_divergence(self):
      hp.expert_divergence(self) #experts,average,naive
      self.datacollector_4.collect(self)
      self.datacollector_5.collect(self)
      self.datacollector_6.collect(self)
      self.datacollector_7.collect(self)
      self.datacollector_12.collect(self)
      hp.compute_expert_knowledge(self)
      hp.intellectual_level(self) #common from experts - it is cosine!!!!! 
      self.datacollector_13.collect(self)
      hp.cluster_similarity_crown(self)
      self.datacollector_17.collect(self)
      self.datacollector_18.collect(self)
      self.datacollector_19.collect(self)
      self.datacollector_20.collect(self) 
      hp.experts_KL_divergence(self)
      self.d_21.collect(self)
      self.d_22.collect(self)
      self.d_23.collect(self)
      self.d_24.collect(self)
      self.d_25.collect(self)
      self.d_26.collect(self)
      hp.cluster_similarity_KL(self)
      self.d_18.collect(self)
      self.d_19.collect(self)
      self.d_20.collect(self) 

    def step(self,n_births = 0,n_deaths = 0, nofactive = round(200/2), to_be_added = [], mode = 'add', generated_resources = 0, eval_inst_threshold = 0.5, rules_2_endorse = [],weights_2_endorse = {}):
        '''Advance the model by one step.'''
        self.round_updates(to_be_added,mode,generated_resources,rules_2_endorse,weights_2_endorse)  
        #PARTICIPATION
        self.participation(n_births,n_deaths)
        #RESOURCE DISTRIBUTION 
        self.resource_collection_distribution()
        #AVERAGE EVALUATION  
        self.evaluation()   
        self.oracle_updates()
        #SELF-REFLECTION TO AGENTS
        self.schedule.step() # run agent steps  
        #INSTITUTIONAL UPDATES
        if (self.inst_adaptation == 'active'):
          self.institutional_updates()
        self.sample_divergence()
        self.collectors() # collect all the values
        hp.restart_helpers(self) #restart for next the allocation of the next round
        return (self.G, self.central, self.notcentral)