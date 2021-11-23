# Commented out IPython magic to ensure Python compatibility.
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import SimultaneousActivation
import random
from mesa.datacollection import DataCollector
from scipy.stats import bernoulli

import sklearn.metrics.pairwise as pw  

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

import sys
from math import log

import network as nt
import generators as gen


def compute_power_law(model):
  model.nof_nodes_summing_50_perc = 0 #init with zero
  total_asked = sum(model.finally_asked_this_round.values())
  for key, value in model.finally_asked_this_round.items():
    model.freq_finally_asked_this_round[key] = value/max(1,total_asked)
  model.freq_finally_asked_this_round =  {k: v for k, v in sorted(model.freq_finally_asked_this_round.items(), key=lambda item: item[1], reverse=True)}
  # nof nodes replied
  m_d = model.freq_finally_asked_this_round.copy()
  for key,value in model.freq_finally_asked_this_round.items():
    if (value == 0):
      m_d.pop(key)
  model.nof_nodes_replied = len(m_d)
  model.sum_all_nof_replied += model.nof_nodes_replied
  model.avg_all_nof_replied = model.sum_all_nof_replied/max(1,model.rounds)
  perc = 0
  freq_dict = model.freq_finally_asked_this_round.copy()
  while (perc < 0.5):
    if (freq_dict != {}):
      firstv = list(freq_dict.values())[0]
      firstk = list(freq_dict.keys())[0]
      perc += firstv
      freq_dict.pop(firstk)
      model.nof_nodes_summing_50_perc += 1
    else:
      break

def kl_divergence_exp(d1,d2):
  # d1 = {'lc1':0.1,'lc2':0.8,'lc7':0.1}
  # d3 = {'lc1':0.1,'lc2':0.79,'lc7':0.11}
  # d2 = {'lc3':0.25,'lc1':0.25,'lc7':0.25,'lc2':0.25}
  p = []
  q = []
  for i in d1.keys():
    el = d1.get(i,0)
    el2 = d2.get(i,0)
    p.append(el)
    q.append(el2) 
  d12 = sum(p[i] * log(max(p[i],sys.float_info.min)/max(q[i],sys.float_info.min)) for i in range(len(p)))
  return d12

def kl_divergence_lc(d1,d2):
  p = []
  q = []
  gen_list = ['lc1','lc2','lc3','lc4','lc5','lc6','lc7','lc8']
  for i in gen_list:
    el = d1.get(i,0)
    el2 = d2.get(i,0)
    p.append(el)
    q.append(el2) 
  d12 = sum(p[i] * log(max(p[i],sys.float_info.min)/max(q[i],sys.float_info.min)) for i in range(len(p)))
  return d12

def cluster_similarity_KL(model):
  #if RTSI there are no rule experts, we define experts the ones asked for opinion
  #KL
  model.ensemble_divergenceKL = 0
  model.experts_divergenceKL = 0
  model.ensemble_from_institution_divergenceKL = 0
  model.expert_from_institution_divergenceKL = 0
  model.ensemble_from_common_divergenceKL = 0
  model.expert_from_common_divergenceKL = 0
  already_measured = []
  nof_comp1 = 0
  nof_comp2 = 0
  nof_comp3 = 0
  nof_comp4 = 0
  for agent1 in model.schedule.agents:
    already_measured.append(agent1.unique_id)
    if (agent1.unique_id in model.activity_list):
      nof_comp3 += 1
      model.ensemble_from_common_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.ilc_weights)
      model.ensemble_from_institution_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.popular_order_weights)
      if (model.framework == 'RTSI'):
        if (agent1.unique_id in model.sources_of_opinion):
          nof_comp4 += 1
          model.expert_from_institution_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.ilc_weights)
          model.expert_from_common_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.popular_order_weights)
      else:
        if (agent1.unique_id in model.sources_of_knowledge):
          nof_comp4 += 1
          model.expert_from_institution_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.ilc_weights)
          model.expert_from_common_divergenceKL += kl_divergence_lc(agent1.rule_weights, model.popular_order_weights)
          # print('exp from inst:',model.expert_from_institution_divergenceKL)
          # print('exp from common:',model.expert_from_common_divergenceKL)
      for agent2 in model.schedule.agents:
        if ((agent2.unique_id in model.activity_list) and (agent2.unique_id not in already_measured) and (agent1.unique_id != agent2.unique_id)):
          nof_comp1 += 1
          model.ensemble_divergenceKL += kl_divergence_lc(agent1.rule_weights, agent2.rule_weights)
          if (model.framework == 'RTSI'):
           if ((agent2.unique_id in model.sources_of_opinion) and (agent1.unique_id in model.sources_of_opinion)):
              nof_comp2 += 1
              model.experts_divergenceKL += kl_divergence_lc(agent1.rule_weights, agent2.rule_weights) 
          else:
            if ((agent2.unique_id in model.sources_of_knowledge) and (agent1.unique_id in model.sources_of_knowledge)):
              nof_comp2 += 1
              model.experts_divergenceKL += kl_divergence_lc(agent1.rule_weights, agent2.rule_weights)
  model.ensemble_divergenceKL = model.ensemble_divergenceKL/(max(1,nof_comp1))
  model.experts_divergenceKL = model.experts_divergenceKL/(max(1,nof_comp2))
  model.ensemble_from_institution_divergenceKL = model.ensemble_from_institution_divergenceKL/(max(1,nof_comp3))
  model.expert_from_institution_divergenceKL = model.expert_from_institution_divergenceKL/(max(1,nof_comp4))
  model.ensemble_from_common_divergenceKL = model.ensemble_from_common_divergenceKL/(max(1,nof_comp3))
  model.expert_from_common_divergenceKL = model.expert_from_common_divergenceKL/(max(1,nof_comp4))
  return

def experts_KL_divergence(model):
  #if RTSI there are no rule experts, we define experts the ones asked for opinion
  #KL
  model.exp_distr_change_from_prev_asked = 0
  model.exp_distr_change_from_prev_source = 0
  prob_asked_help = {}
  prob_ruled_help = {}
  prob_SoP_help = {}
  prob_SoK_help = {}
  f1 = sum(model.all_times_asked.values())
  f2 = sum(model.all_times_rule.values())
  f3 = sum(model.all_times_source_opinion.values())
  f4 = sum(model.all_times_source_knowledge.values())
  for agent1 in model.schedule.agents:
    prob_asked_help[agent1.unique_id] = model.all_times_asked.get(agent1.unique_id,0)/max(1,f1)
    prob_ruled_help[agent1.unique_id] = model.all_times_rule.get(agent1.unique_id,0)/max(1,f2)
    prob_SoP_help[agent1.unique_id] = model.all_times_source_opinion.get(agent1.unique_id,0)/max(1,f3)
    prob_SoK_help[agent1.unique_id] = model.all_times_source_knowledge.get(agent1.unique_id,0)/max(1,f4)
  if (model.framework == 'RTSI'):
    model.exp_distr_change_from_prev_asked = kl_divergence_exp(prob_asked_help,model.prob_asked)
    model.exp_distr_change_from_prev_source = kl_divergence_exp(prob_SoP_help,model.prob_SoP)
  else:
    model.exp_distr_change_from_prev_asked = kl_divergence_exp(prob_ruled_help,model.prob_ruled)
    model.exp_distr_change_from_prev_source = kl_divergence_exp(prob_SoK_help,model.prob_SoK)
  #UPDATE for next round
  model.prob_asked = prob_asked_help
  model.prob_ruled = prob_ruled_help
  model.prob_SoP = prob_SoP_help
  model.prob_SoK = prob_SoK_help
  return

def euclidean_distance(x,y):
  dist = 0
  for key, value in x.items():
    if key not in y:
      dist +=pow(value,2)
    else:
      dist += pow(value-y.get(key,0),2)
  #add keys that are not in x
  for key, value in y.items():
    if key not in x.items():
      dist +=pow(value,2)
  return math.sqrt(dist)

def expert_divergence(model):
  model.experts = 0
  model.silly = 0
  model.average = 0
  # model.mediocre = 0
  for agent1 in model.schedule.agents:
    if (model.framework == 'RTSI'):
      if (model.all_times_source_opinion.get(agent1.unique_id,0)/max(1,model.rounds) >= 0.5):
        model.experts += 1
      elif (model.all_times_source_opinion.get(agent1.unique_id,0)/max(1,model.rounds) >= 0.1):
        model.average +=1
      else: 
        model.silly +=1
    else: 
      if (model.all_times_source_knowledge.get(agent1.unique_id,0)/max(1,model.rounds) >= 0.5):
        model.experts += 1
      elif (model.all_times_source_knowledge.get(agent1.unique_id,0)/max(1,model.rounds) >= 0.1):
        model.average +=1
      else: 
        model.silly +=1
  model.experts = model.experts/model.num_agents
  model.silly = model.silly/model.num_agents
  model.average = model.average/model.num_agents
  model.mediocre = model.mediocre/model.num_agents
  return


def compute_expert_knowledge(model):
  model.experts_knowledge = {}
  total = 0
  for agent in model.schedule.agents:
    if (model.framework == 'RTSI'):
      if agent.unique_id in model.sources_of_opinion:
        total += 1
        for key, value in agent.rule_weights.items():
          if (model.experts_knowledge.get(key) is None):
            model.experts_knowledge[key] = value
          else:
            model.experts_knowledge[key] += value
    else:
      if agent.unique_id in model.sources_of_knowledge:
        total += 1
        for key, value in agent.rule_weights.items():
          if (model.experts_knowledge.get(key) is None):
            model.experts_knowledge[key] = value
          else:
            model.experts_knowledge[key] += value
  for key, value in model.experts_knowledge.items():
    model.experts_knowledge[key] = value/max(1,total)
  return  

def compute_cos_sim(d1,d2):
  #d1,d2 dictionaries
  list1 = []
  list2 = []
  gen_list = ['lc1','lc2','lc3','lc4','lc5','lc6','lc7','lc8']
  for i in gen_list:
    el = d1.get(i,0)
    el2 = d2.get(i,0)
    list1.append(el)
    list2.append(el2)
  np_list1 = np.array(list1)
  np_list2 = np.array(list2)
  cos = pw.cosine_similarity(np_list1.reshape(1,-1),np_list2.reshape(1,-1))
  value = cos[0]
  value2 = value[0]
  return value2

def intellectual_level(model):
  model.average_intellectual_level = 0
  for agent in model.schedule.agents:
    if (agent.unique_id in model.activity_list):
      model.average_intellectual_level += compute_cos_sim(agent.rule_weights,model.experts_knowledge)
  model.average_intellectual_level = model.average_intellectual_level/max(1,model.nofactive)
  # print(agent.rule_weights)
  # print(model.experts_knowledge)
  #print(model.average_intellectual_level)

def cluster_similarity_crown(model):
  #if RTSI there are no rule experts, we define experts the ones asked for opinion
  #euclidean
  model.ensemble_divergence = 0
  model.experts_divergence = 0
  model.ensemble_from_institution_divergence = 0
  model.expert_from_institution_divergence = 0
  model.ensemble_from_common_divergence = 0
  model.expert_from_common_divergence = 0
  model.experts_divergence_over_rounds = 0
  already_measured = []
  nof_comp1 = 0
  nof_comp2 = 0
  nof_comp3 = 0
  nof_comp4 = 0
  for agent1 in model.schedule.agents:
    already_measured.append(agent1.unique_id)
    if (agent1.unique_id in model.activity_list):
      nof_comp3 += 1
      model.ensemble_from_common_divergence += euclidean_distance(agent1.rule_weights, model.ilc_weights)
      model.ensemble_from_institution_divergence += euclidean_distance(agent1.rule_weights, model.popular_order_weights)
      if (model.framework == 'RTSI'):
        if (agent1.unique_id in model.sources_of_opinion):
          nof_comp4 += 1
          model.expert_from_institution_divergence += euclidean_distance(agent1.rule_weights, model.ilc_weights)
          model.expert_from_common_divergence += euclidean_distance(agent1.rule_weights, model.popular_order_weights)
      else:
        if (agent1.unique_id in model.sources_of_knowledge):
          nof_comp4 += 1
          model.expert_from_institution_divergence += euclidean_distance(agent1.rule_weights, model.ilc_weights)
          model.expert_from_common_divergence += euclidean_distance(agent1.rule_weights, model.popular_order_weights)
      for agent2 in model.schedule.agents:
        if ((agent2.unique_id in model.activity_list) and (agent2.unique_id not in already_measured) and (agent1.unique_id != agent2.unique_id)):
          nof_comp1 += 1
          model.ensemble_divergence += euclidean_distance(agent1.rule_weights, agent2.rule_weights)
          if (model.framework == 'RTSI'):
            model.experts_divergence_over_rounds += (model.all_times_source_opinion.get(agent1.unique_id,0) - model.all_times_source_opinion.get(agent2.unique_id,0))/model.rounds
            if ((agent2.unique_id in model.sources_of_opinion) and (agent1.unique_id in model.sources_of_opinion)):
              nof_comp2 += 1
              model.experts_divergence += euclidean_distance(agent1.rule_weights, agent2.rule_weights) 
          else:
            model.experts_divergence_over_rounds += (model.all_times_source_knowledge.get(agent1.unique_id,0) - model.all_times_source_knowledge.get(agent2.unique_id,0))/model.rounds
            if ((agent2.unique_id in model.sources_of_knowledge) and (agent1.unique_id in model.sources_of_knowledge)):
              nof_comp2 += 1
              model.experts_divergence += euclidean_distance(agent1.rule_weights, agent2.rule_weights)
  model.ensemble_divergence = model.ensemble_divergence/(max(1,nof_comp1)*math.sqrt(2))
  model.experts_divergence = model.experts_divergence/(max(1,nof_comp2)*math.sqrt(2))
  model.ensemble_from_institution_divergence = model.ensemble_from_institution_divergence/(max(1,nof_comp3)*math.sqrt(2))
  model.expert_from_institution_divergence = model.expert_from_institution_divergence/(max(1,nof_comp4)*math.sqrt(2))
  model.ensemble_from_common_divergence = model.ensemble_from_common_divergence/(max(1,nof_comp3)*math.sqrt(2))
  model.expert_from_common_divergence = model.expert_from_common_divergence/(max(1,nof_comp4)*math.sqrt(2))
  model.experts_divergence_over_rounds = model.experts_divergence_over_rounds/max(1,nof_comp1)
  return

  
def restart_helpers(self):
  self.lc1 = {} #after you share
  self.lc2 = {} 
  self.lc3 = {} 
  self.lc4 = {} 
  self.lc5 = {} 
  self.lc6 = {}
  self.lc7 = {} 
  self.lc8 = {} 
  self.all_evaluations = {}
  self.all_required_resources = {}
  self.times_assign_task = 0
  self.times_do_the_task = 0
  # self.freq_assign_task = 0
  # self.freq_do_the_task = 0
  self.opinion_times = []
  self.avg_op_times = 0
  self.knowledge_times = []
  self.avg_kn_times = 0
  self.avg_degree = 0
  self.avg_age = 0
  self.all_degree = {}
  self.all_ages = {}
  self.rulerweight_1 = 0
  self.rulerweight_2 = 0
  self.rulerweight_3 = 0
  self.rulerweight_4 = 0
  self.rulerweight_5 = 0
  self.rulerweight_6 = 0
  self.rulerweight_7 = 0
  self.rulerweight_8 = 0


def degree_age_updates(self):
  N = 0
  sum = 0
  sum2 = 0
  for agent in self.schedule.agents:
    if (agent.unique_id in self.activity_list):
      sum += agent.age
      sum2 += agent.degree
      N +=1
  avg = sum/max(1,N)
  avg2 = sum2/max(1,N)
  self.avg_age = avg
  self.avg_degree = avg2  

def update_ruleweights(self):
  n1 = 0
  n2 = 0
  n3 = 0
  n4 = 0
  n5 = 0
  n6 = 0
  n7 = 0
  n8 = 0
  self.rulerweight_1 = 0
  self.rulerweight_2 = 0
  self.rulerweight_3 = 0
  self.rulerweight_4 = 0
  self.rulerweight_5 = 0
  self.rulerweight_6 = 0
  self.rulerweight_7 = 0
  self.rulerweight_8 = 0
  self.exp_rw_1 = 0 #experts
  self.exp_rw_2 = 0
  self.exp_rw_3 = 0
  self.exp_rw_4 = 0
  self.exp_rw_5 = 0
  self.exp_rw_6 = 0
  self.exp_rw_7 = 0
  self.exp_rw_8 = 0
  for agent in self.schedule.agents:
    if ((agent.unique_id in self.activity_list) and (agent.unique_id in self.suggested_node_rule)): #if node is the suggested by oracle
      if ('lc1' in agent.rule_weights.keys()):
        self.rulerweight_1 += agent.rule_weights.get('lc1')
        n1 += 1
      if ('lc2' in agent.rule_weights.keys()):
        self.rulerweight_2 += agent.rule_weights.get('lc2')
        n2 += 1          
      if ('lc3' in agent.rule_weights.keys()):
        self.rulerweight_3 += agent.rule_weights.get('lc3')
        n3 += 1          
      if ('lc4' in agent.rule_weights.keys()):
        self.rulerweight_4 += agent.rule_weights.get('lc4')
        n4 += 1
      if ('lc5' in agent.rule_weights.keys()):
        self.rulerweight_5 += agent.rule_weights.get('lc5')
        n5 += 1
      if ('lc6' in agent.rule_weights.keys()):
        self.rulerweight_6 += agent.rule_weights.get('lc6')
        n6 += 1
      if ('lc7' in agent.rule_weights.keys()):
        self.rulerweight_7 += agent.rule_weights.get('lc7')
        n7 += 1
      if ('lc8' in agent.rule_weights.keys()):
        self.rulerweight_8 += agent.rule_weights.get('lc8')
        n8 += 1   
  self.rulerweight_1 = self.rulerweight_1/max(1,n1)
  self.rulerweight_2 = self.rulerweight_2/max(1,n2)
  self.rulerweight_3 = self.rulerweight_3/max(1,n3)
  self.rulerweight_4 = self.rulerweight_4/max(1,n4)
  self.rulerweight_5 = self.rulerweight_5/max(1,n5)
  self.rulerweight_6 = self.rulerweight_6/max(1,n6)
  self.rulerweight_7 = self.rulerweight_7/max(1,n7)
  self.rulerweight_8 = self.rulerweight_8/max(1,n8)
  self.ints_rw_1 = self.ilc_weights.get('lc1',0)
  self.ints_rw_2 = self.ilc_weights.get('lc2',0)
  self.ints_rw_3 = self.ilc_weights.get('lc3',0)
  self.ints_rw_4 = self.ilc_weights.get('lc4',0)
  self.ints_rw_5 = self.ilc_weights.get('lc5',0)
  self.ints_rw_6 = self.ilc_weights.get('lc6',0)
  self.ints_rw_7 = self.ilc_weights.get('lc7',0)
  self.ints_rw_8 = self.ilc_weights.get('lc8',0)
  for key, value in self.expert_rule_weights.items(): 
    if (key == 'lc1'):
      self.exp_rw_1 = value
    elif (key == 'lc2'):
      self.exp_rw_2 = value
    elif (key == 'lc3'):
      self.exp_rw_3 = value
    elif (key == 'lc4'):
      self.exp_rw_4 = value
    elif (key == 'lc5'):
      self.exp_rw_5 = value
    elif (key == 'lc6'):
      self.exp_rw_6 = value
    elif (key == 'lc7'):
      self.exp_rw_7 = value
    else:
      self.exp_rw_8 = value

def store_average_weights(self):
  self.lc1_w = 0
  self.lc2_w = 0
  self.lc3_w = 0
  self.lc4_w = 0
  self.lc5_w = 0
  self.lc6_w = 0
  self.lc7_w = 0
  self.lc8_w = 0
  for key, value in self.popular_order_weights.items():
    if (key == 'lc1'):
      self.lc1_w = value
    elif (key == 'lc2'):
      self.lc2_w = value
    elif (key == 'lc3'):
      self.lc3_w = value
    elif (key == 'lc4'):
      self.lc4_w = value
    elif (key == 'lc5'):
      self.lc5_w = value
    elif (key == 'lc6'):
      self.lc6_w = value
    elif (key == 'lc7'):
      self.lc7_w = value
    else:
      self.lc8_w = value


def distance(dict1,dict2):
  distance = 0
  for key, pos1 in dict1.items():
    pos2 = dict2.get(key)
    if (pos2 is not None):
      distance += abs(pos1 - pos2)
  #distance = distance/(len(dict1)*len(dict1))
  return distance

def distance2(dict1,dict2):
  distance = 0
  for key, pos1 in dict1.items():
    pos2 = dict2.get(key)
    if (pos2 is not None):
      if (pos2 != pos1):
        distance +=1
  return distance

def distance3(dict1,dict2):
  distance = 0
  for key, pos1 in dict1.items():
    pos2 = dict2.get(key)
    if (pos2 is not None):
      if ((pos1 == 0 and pos2 !=0) or (pos1 != 0 and pos2 ==0)):
        distance +=1
  return distance

def pairwise_comparison(sort1,sort2):
  distance = 0
  before = []
  for agent in sort1.keys():
    before.append(agent)
    flag = 0
    for agent2 in sort2.keys():
      if (agent == agent2):
        flag = 1
      if (agent2 not in before and flag == 0):
        distance+=1
  total_distance = 2*distance/max(1,len(sort1)*len(sort1)) 
  return total_distance


