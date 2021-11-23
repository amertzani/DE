import networkx as nx
import matplotlib.pyplot as plt
# import hierarchical clustering libraries
import scipy.cluster.hierarchy as sch
import sklearn.metrics.pairwise as pw  
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, normalize
import numpy as np 

def print_graphs():
  model_history = SWSFmodel.datacollector.get_model_vars_dataframe()
  model_history.plot()
  model_history_2 = SWSFmodel.datacollector_2.get_model_vars_dataframe()
  model_history_2.plot()
  model_history_3 = SWSFmodel.datacollector_3.get_model_vars_dataframe()
  model_history_3.plot()
  model_history_4 = SWSFmodel.datacollector_4.get_model_vars_dataframe()
  model_history_4.plot()
  model_history_5 = SWSFmodel.datacollector_5.get_model_vars_dataframe()
  model_history_5.plot()
  model_history_6 = SWSFmodel.datacollector_6.get_model_vars_dataframe()
  model_history_6.plot()
  model_history_7 = SWSFmodel.datacollector_7.get_model_vars_dataframe()
  model_history_7.plot()
  model_history_9 = SWSFmodel.datacollector_9.get_model_vars_dataframe()
  model_history_9.plot()

def print_model_network(self):
    f = plt.figure() 
    f.set_figwidth(10) 
    f.set_figheight(10) 
    pos = nx.spring_layout(self.G)  # positions for all nodes
    nx.draw_networkx_nodes(self.G, pos)#, nodelist=self.central, node_color="r")
    # nx.draw_networkx_nodes(self.G, pos, nodelist=self.notcentral, node_color="b")
    nx.draw_networkx_edges(self.G, pos, width=1.0, alpha=0.5)
    #plt.plot()
    #plt.show()
    print('N:',self.num_agents)
    print('Central:',self.central)
    print('NotCentral:',self.notcentral)

    
def predict_dendro(points):
  # create dendrogram
  plt.figure(figsize =(6, 6))
  dendrogram = sch.dendrogram(sch.linkage(points, method='ward')) #variance minimization algorithm
  # create clusters
  hc = AgglomerativeClustering(n_clusters=2, affinity = 'euclidean', linkage = 'ward')
  # save clusters for chart
  y_hc = hc.fit_predict(points)
  name = 'dendro_' + SWSFmodel.framework + '_dynamic.png'
  name2 = f'{name}'
  plt.savefig(name2)
  return y_hc

def print_scatter(points,y_hc):  
  plt.figure(figsize=(7,5))
  plt.scatter(points[y_hc ==0,0], points[y_hc == 0,1], s=100, c='red')
  plt.scatter(points[y_hc==1,0], points[y_hc == 1,1], s=100, c='black')
  plt.scatter(points[y_hc ==2,0], points[y_hc == 2,1], s=100, c='blue')
  plt.scatter(points[y_hc ==3,0], points[y_hc == 3,1], s=100, c='cyan')
  plt.scatter(points[y_hc ==4,0], points[y_hc == 4,1], s=100, c='orange')
  name = 'scatter_plot_' + SWSFmodel.framework + '_dynamic.png'
  name2 = f'{name}'
  plt.savefig(name2)

def print_silhuette(points):
  # create clusters
  hc2 = AgglomerativeClustering(n_clusters=2, affinity = 'euclidean', linkage = 'ward')
  hc3 = AgglomerativeClustering(n_clusters=3, affinity = 'euclidean', linkage = 'ward')
  hc4 = AgglomerativeClustering(n_clusters=4, affinity = 'euclidean', linkage = 'ward')
  hc5 = AgglomerativeClustering(n_clusters=5, affinity = 'euclidean', linkage = 'ward')
  hc6 = AgglomerativeClustering(n_clusters=6, affinity = 'euclidean', linkage = 'ward')
  # save clusters for chart
  y_hc2 = hc2.fit_predict(points)
  y_hc3 = hc3.fit_predict(points)
  y_hc4 = hc4.fit_predict(points)
  y_hc5 = hc5.fit_predict(points)
  y_hc6 = hc6.fit_predict(points)
  k = [2, 3, 4, 5, 6]
  silhouette_scores = []
  #The Silhouette Coefficient is calculated using 
  #the mean intra-cluster distance (a) and the mean nearest-cluster distance (b) for each sample. 
  #(b - a) / max(a, b)
  #[-1,1]: 1->far from others, 0->close to decision boundary -1->might wrong clustering
  silhouette_scores.append(silhouette_score(points, hc2.fit_predict(points)))
  silhouette_scores.append(silhouette_score(points, hc3.fit_predict(points)))
  silhouette_scores.append(silhouette_score(points, hc4.fit_predict(points)))
  silhouette_scores.append(silhouette_score(points, hc5.fit_predict(points)))
  silhouette_scores.append(silhouette_score(points, hc6.fit_predict(points)))
  plt.figure(figsize=(6,4))
  plt.bar(k, silhouette_scores)
  # plt.xlabel('Number of clusters', fontsize = 20)
  # plt.ylabel('S(i)', fontsize = 20)
  name = 'silhuette_' + SWSFmodel.framework + '_dynamic.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()

def print_cluster_data():
  points = prep_data()
  y_hc = predict_dendro(points)
  print_scatter(points,y_hc)
  print_silhuette(points)
  #print_cropped_divergence_of_experts()
  
def printing2():
  model_18 = SWSFmodel.datacollector_18.get_model_vars_dataframe()
  model_19 = SWSFmodel.datacollector_19.get_model_vars_dataframe()
  model_20 = SWSFmodel.datacollector_20.get_model_vars_dataframe()
  model_21 = SWSFmodel.datacollector_17.get_model_vars_dataframe()
  model_intel = SWSFmodel.datacollector_13.get_model_vars_dataframe()
  model_exp = SWSFmodel.datacollector_12.get_model_vars_dataframe()
  plt.figure(figsize=(9,5))
  model_18.plot()
  plt.axis(ymin=0, ymax=1)
  name = 'EU_ens_exp_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  model_19.plot()
  plt.axis(ymin=0, ymax=1)
  name = 'EU_ens_exp_inst_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  model_20.plot()
  plt.axis(ymin=0, ymax=1)
  name = 'EU_ens_exp_com_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()  
  # plt.figure(figsize=(9,5))
  # model_21.plot()
  # plt.axis(xmin=0, xmax=1000, ymin=0, ymax=1)
  # name = 'EU_expert_over_rounds_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '.png'
  # name2 = f'{name}'
  # plt.savefig(name2)
  # plt.show()
  plt.figure(figsize=(9,5))
  model_intel.plot()
  plt.axis(ymin=0, ymax=1)
  name = 'COS_intel_level_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()  
  plt.figure(figsize=(9,5))
  model_exp.plot()
  plt.axis(ymin=0, ymax=1)
  name = 'exp_groups_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()  

def printing3():
  m_18 = SWSFmodel.d_18.get_model_vars_dataframe()
  m_19 = SWSFmodel.d_19.get_model_vars_dataframe()
  m_20 = SWSFmodel.d_20.get_model_vars_dataframe()
  m_21 = SWSFmodel.d_21.get_model_vars_dataframe()
  m_22 = SWSFmodel.d_22.get_model_vars_dataframe()
  plt.figure(figsize=(9,5))
  m_18.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'KL_ens_exp_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  m_19.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'KL_ens_exp_inst_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  m_20.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'KL_ens_exp_com_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()   
  plt.figure(figsize=(9,5))
  m_21.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'KL_exp_div_asked_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()   
  plt.figure(figsize=(9,5))
  m_22.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'KL_exp_div_Source_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()   

def printing4():
  m_18 = SWSFmodel.d_14.get_model_vars_dataframe()
  m_19 = SWSFmodel.d_15.get_model_vars_dataframe()
  m_20 = SWSFmodel.d_16.get_model_vars_dataframe()
  m_21 = SWSFmodel.d_17.get_model_vars_dataframe()
  plt.figure(figsize=(9,5))
  m_18.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'A_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  m_19.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'I_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()
  plt.figure(figsize=(9,5))
  m_20.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'E_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()   
  plt.figure(figsize=(9,5))
  m_21.plot()
  # plt.axis(ymin=0, ymax=1)
  name = 'O_' + SWSFmodel.framework + '_' + SWSFmodel.knowledge_codification + '_' + SWSFmodel.oracle_strategy + '.png'
  name2 = f'{name}'
  plt.savefig(name2)
  plt.show()

def prep_data():
  o = np.zeros((SWSFmodel.nofactive,8))
  line = 0
  for agent in SWSFmodel.schedule.agents:
    if (agent.unique_id in SWSFmodel.activity_list):
      for key,value in agent.rule_weights.items():
        if (key == 'lc1'):
          o[line,0] = value
        if (key == 'lc2'):
          o[line,1] = value
        if (key == 'lc3'):
          o[line,2] = value
        if (key == 'lc4'):
          o[line,3] = value
        if (key == 'lc5'):
          o[line,4] = value
        if (key == 'lc6'):
          o[line,5] = value
        if (key == 'lc7'):
          o[line,6] = value
        if (key == 'lc8'):
          o[line,7] = value
      line +=1
  simple_points = o
  points = normalize(simple_points) #Normalizing the data so that the data approximately
  return points
