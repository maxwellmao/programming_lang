#!/usr/bin/python
from __future__ import division
import os, sys
sys.path.append('../crawler')
from crawling_github import Repository, User
import matplotlib.pyplot as plt
import networkx as nx
import scipy
import scipy.io
import codecs
from scipy.sparse import *
import numpy as np
from math import log, log10
import re

(_normal, _loglog)=range(2)
(_pdf, _ccdf, _cdf)=range(3)

class CollaborationNet:
    def __init__(self):
        self.bipartite_net=nx.Graph()
        self.collabrative_net=nx.Graph()
        self.self_weight=dict()

    def plot_dist(self, data_dict, data_range=None, N=1000, c='b', scale=_normal, type=_pdf):
        '''
            the format of data_dict is {statistic, frequency}
        '''
        if data_range is None:
            data_range=(min(data_dict.keys()), max(data_dict.keys()))
        print 'Data range:', data_range
        bins=np.arange(data_range[0], data_range[1]+(data_range[1]-data_range[0])/N, (data_range[1]-data_range[0])/N)
        hist=[0 for i in range(len(bins)-1)]
        current_bin=0
        for item in sorted(data_dict.items(), key=lambda x:x[0]):
            while(item[0]>bins[current_bin]) and current_bin<len(bins)-1:
                current_bin+=1
            if current_bin==0:
                hist[current_bin]+=item[1]
            else:
                hist[current_bin-1]+=item[1]
        print hist
        bin_center=[(bins[i+1]+bins[i])/2 for i in range(len(bins)-1)]
        if type==_pdf:
            if scale==_normal:
                plt.plot(bin_center, [h/sum(hist) for h in hist], '.', color=c)
            elif scale==_loglog:
                plt.loglog(bin_center, [h/sum(hist) for h in hist], '.', color=c)
        elif type==_cdf:
            cdf=[]
            cumulative=0
            for h in hist:
                cumulative+=h
                cdf.append(cumulative)
            if scale==_normal:
                plt.plot(bin_center, [h/cumulative for h in cdf], '.', color=c)
            elif scale==_loglog:
                plt.loglog(bin_center, [h/cumulative for h in cdf], '.', color=c)
        elif type==_ccdf:
            ccdf=[]
            cumulative=0
            for h in hist[::-1]:
                cumulative+=h
                ccdf.append(cumulative)
            ccdf.reverse()
            if scale==_normal:
                plt.plot(bin_center, [h/cumulative for h in ccdf], '.', color=c)
            elif scale==_loglog:
                plt.loglog(bin_center, [h/cumulative for h in ccdf], '.', color=c)

    def save_net(self, save_dir):
        fp=open('_'.join([save_dir, 'Bipartite_Net.nx']), 'w')
        fp.write('\n'.join([('%s\t%s\t%s' % (e[0], e[1], e[2]['weight'])) for e in self.bipartite_net.edges(data=True)]))
        fp.close()

#        fp=open('_'.join([save_dir, 'Collaboration_Net.nx']), 'w')
#        fp.write('\n'.join([('%s\t%s\t%s' % (e[0], e[1], e[2]['weight'])) for e in self.collabrative_net.edges(data=True)]))
#        fp.close()
#
#        fp=open('_'.join([save_dir, 'Collaboration_Self_weight']), 'w')
#        fp.write('\n'.join([('%s\t%s' % (k, v)) for k, v in self.self_weight.items()]))
#        fp.close()

    def kl_divergence(self, save_dir):
        plt.clf()
        total_commit=sum([e[2]['weight'] for e in self.bipartite_net.edges(data=True)])
        color_list=['b', 'r', 'g', 'k']
        node_commit=dict()
        kl_diverge=dict()
        for node in self.bipartite_net.nodes():
            node_commit[node]=sum([v['weight'] for k, v in self.bipartite_net[node].items()])

        for node in self.bipartite_net.nodes():
            kl_d=0.0
            for neighbor, neighbor_info in self.bipartite_net[node].items():
                kl_d+=(neighbor_info['weight']/node_commit[node])*(log(neighbor_info['weight']/node_commit[node])-log(node_commit[neighbor]/total_commit))
            kl_diverge[node]=kl_d

        type_kl_dict=dict()
        for k, v in kl_diverge.items():
            type=re.findall(r'[A-Za-z]+', k)
            if len(type)>0:
                type=type[0]
            if type_kl_dict.has_key(type):
                type_kl_dict[type][v]=type_kl_dict[type].get(v, 0)+1
            else:
                type_kl_dict[type]=dict({v:1})
        c_index=0
        leg=[]
        for k, v in type_kl_dict.items():
            leg.append(k)
            max_kl=max([item[0] for item in v.items()])
            min_kl=min([item[0] for item in v.items()])
            normal_kl=dict([[(stat-min_kl)/(max_kl-min_kl), freq] for stat, freq in v.items()])
            self.plot_dist(normal_kl, c=color_list[c_index], scale=_loglog)
            c_index+=1
            fp=open('_'.join([save_dir, k, 'KL', 'Diverge']), 'w')
            fp.write('\n'.join([('%s\t%s' % (s[0], s[1])) for s in sorted(normal_kl.items(), key=lambda x:x[0])]))
            fp.close()
        plt.xlabel('KL-Divergence')
        plt.ylabel('Probability')
        plt.legend(leg)
        plt.savefig('_'.join([save_dir, 'KL', 'Diverge'])+'.png', dpi=500)

    def load_net(self, load_dir):
        fp=open('_'.join([load_dir, 'Net.nx']))
        for line in fp.readlines():
            items=line.strip().split()
            if len(items)==3:
                self.bipartite_net.add_edge(items[0], items[1], weight=int(items[-1]))
        fp.close()

    def bipartite_net_degree_dist(self, save_dir, plot_type=_pdf):
        plt.clf()
        color_list=['b', 'r', 'g', 'k']
        degree_dist_dict=dict()
        for k, v in self.bipartite_net.degree().items():
            type=re.findall(r'[A-Za-z]+', k)
            if len(type)>0:
                type=type[0]
            if degree_dist_dict.has_key(type):
                degree_dist_dict[type][v]=degree_dist_dict[type].get(v, 0)+1
            else:
                degree_dist_dict[type]=dict({v:1})
        leg=[]
        c_index=0

        for node in self.bipartite_net.nodes():
            type=re.findall(r'[A-Za-z]+', node)
            type=type[0]+'Strength'
            strength=sum([v['weight'] for k, v in self.bipartite_net[node].items()])
            if degree_dist_dict.has_key(type):
                degree_dist_dict[type][strength]=degree_dist_dict[type].get(strength, 0)+1
            else:
                degree_dist_dict[type]=dict({strength:1})

        for k, v in degree_dist_dict.items():
            leg.append(k)
            fp=open('_'.join([save_dir, k, 'Degree']), 'w')
            print k
            if k.endswith('Strength'):
                print k, sum([strength*freq for strength, freq in v.items()])
            self.plot_dist(v, c=color_list[c_index], scale=_loglog, type=plot_type)
            c_index+=1
            fp.write('\n'.join([('%s\t%s' % (d[0], d[1])) for d in sorted(v.items(), key=lambda x:x[0])]))
            fp.close()
        plt.xlabel('Degree')
        plt.ylabel('Probability')
        lg=plt.legend(leg)
        lg.get_frame().set_alpha(0)
        if plot_type==_pdf:
            print 'Saving pdf'
            plt.savefig('_'.join([save_dir, 'Degree'])+'.png', dpi=500)
        elif plot_type==_cdf:
            print 'Saving cdf'
            plt.savefig('_'.join([save_dir, 'Degree', 'CDF'])+'.png', dpi=500)
        elif plot_type==_ccdf:
            print 'Saving ccdf'
            plt.savefig('_'.join([save_dir, 'Degree', 'CCDF'])+'.png', dpi=500)
        print 'Type', type

    def collabrative_net_degree_dist(self, save_dir, plot_type=_pdf):
        if len(self.collabrative_net.nodes())==0:
            print 'Construct the collabrative network first'
            return
        degree_dict=dict()
        plt.clf()
        for k, v in self.collabrative_net.degree().items():
            degree_dict[v]=degree_dict.get(v, 0)+1
        self.plot_dist(degree_dict, scale=_loglog, type=plot_type)
        fp=open('_'.join([save_dir, 'Collabration']), 'w')
        fp.write('\n'.join([('%s\t%s' % (d[0], d[1])) for d in sorted(degree_dict.items(), key=lambda x:x[0])]))
        fp.close()
        plt.xlabel('Number of people collaborating with')
        plt.ylabel('Probability')
        if plot_type==_pdf:
            plt.savefig('_'.join([save_dir, 'Collaboration.png']), dpi=500)
        elif plot_type==_cdf:
            plt.savefig('_'.join([save_dir, 'Collaboration_CDF.png']), dpi=500)
        elif plot_type==_ccdf:
            plt.savefig('_'.join([save_dir, 'Collaboration_CCDF.png']), dpi=500)
        plt.clf()
        co_commit_dict=dict()
        for e in self.collabrative_net.edges(data=True):
            co_commit_dict[e[2]['weight']]=co_commit_dict.get(e[2]['weight'], 0)+1
        self.plot_dist(co_commit_dict, scale=_loglog, type=plot_type)
        fp=open('_'.join([save_dir, 'CollaborationTimes']), 'w')
        fp.write('\n'.join([('%s\t%s' % (d[0], d[1])) for d in sorted(degree_dict.items(), key=lambda x:x[0])]))
        fp.close()
        plt.xlabel('Time of collaborations')
        plt.ylabel('Probability')
        if plot_type==_pdf:
            plt.savefig('_'.join([save_dir, 'CollaborationTimes.png']), dpi=500)
        elif plot_type==_cdf:
            plt.savefig('_'.join([save_dir, 'CollaborationTimes_CDF.png']), dpi=500)
        elif plot_type==_ccdf:
            plt.savefig('_'.join([save_dir, 'CollaborationTimes_CCDF.png']), dpi=500)
        


    def connected_components(self, save_dir):
        components=nx.algorithms.components.connected.connected_components(self.bipartite_net)
        component_size=[len(comp) for comp in components]
        size_dict=dict()
        for s in component_size:
            size_dict[s]=size_dict.get(s, 0)+1
        fp=open('_'.join([save_dir, 'CC_size_dist']), 'w')
        fp.write('\n'.join([('%s\t%s' % (v[0], v[1])) for v in sorted(size_dict.items(), key=lambda x:x[0])]))
        fp.close()

    def bipartite_net_diameter(self):
        d=nx.algorithms.diameter(self.bipartite_net)
        return d

    def collabrative_net_diameter(self):
        d=nx.algorithms.diameter(self.collabrative_net)
        return d

    def construct_collabrative_net(self, base_type, save_dir=''):
        '''
            base type will be the column nodes(Repository/Paper)
        '''
        row=[]
        col=[]
        data=[]
        for edge in self.bipartite_net.edges():
            if edge[0].startswith(base_type):
                col_id=re.findall('\d+$', edge[0])
                row_id=re.findall('\d+$', edge[1])
            elif edge[1].startswith(base_type):
                col_id=re.findall('\d+$', edge[1])
                row_id=re.findall('\d+$', edge[0])
            else:
                print 'Error base type'
                return
            if len(col_id)==1 and len(row_id)==1:
                col_id=int(col_id[0])
                row_id=int(row_id[0])
            else:
                print 'Error in matching index!'
                return
            col.append(col_id)
            row.append(row_id)
            data.append(1)
        people_type_mat=csr_matrix((data, (row, col)))
        type_people_mat=csr_matrix((data, (col, row)))
        comat=people_type_mat*type_people_mat
#        comat=type_people_mat*people_type_mat
        
        value = comat.data
        column_index = comat.indices
        row_pointers = comat.indptr
        print len(value)
        if len(save_dir)>0:
            fp_net=open('_'.join([save_dir, 'Collaboration_Net.nx']), 'w')
            fp_self_weight=open('_'.join([save_dir, 'Collaboration_Self_weight']), 'w')

        self.collabrative_net=nx.Graph()
        for row_index in range(len(row_pointers)-1):
            for col_index in range(row_pointers[row_index], row_pointers[row_index+1]):
                if len(save_dir)>0:
                    if row_index==column_index[col_index]:
                        fp_self_weight.write('%s\t%s\n' % (row_index, value[col_index]))
                    else:
                        fp_net.write('%s\t%s\t%s\n' % (row_index, column_index[col_index], value[col_index]))
                if row_index==column_index[col_index]:
                    self.self_weight[row_index]=value[col_index]
                else:
                    self.collabrative_net.add_edge(row_index, column_index[col_index], weight=value[col_index])

        if len(save_dir)>0:
            fp_net.close()
            fp_self_weight.close()

        print 'Collaboration net nodes: %s edges: %s'% (len(self.collabrative_net.nodes()), len(self.collabrative_net.edges()))
        
