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
from collaboration_network import CollaborationNet
from collaboration_network import _pdf, _cdf, _ccdf
import re

class GitHub_CollaborationNet(CollaborationNet):
    def __init__(self):
        CollaborationNet.__init__(self)
        self.user_id_map=dict()
        self.id_user_map=dict()
        self.repository_id_map=dict()
        self.id_repository_map=dict()

    def parse_from_log(self, log_path, alias_log_path):
        fp=open(alias_log_path)
        alias_dict=dict()
        for line in fp.readlines():
            items=line.strip().split()
            alias_dict[items[6].split(':')[1]]=items[7].split(':')[1]
        fp.close()
        fp=open(log_path)
        repos_index=6
        repos_lang_index=7
        user_index=8
        total_index=9
        for line in fp.readlines():
            items=line.strip().split()
            if items[repos_index].startswith('Repository'):
                if alias_dict.has_key(items[repos_index].split(':')[-1]):
                    repos=Repository(alias_dict[items[repos_index].split(':')[-1]])
                else:
                    repos=Repository(items[repos_index].split(':')[-1])
                repos.set_lang(items[repos_lang_index].split(':')[-1])
            else:
                print 'Cannot locate the repository!'
                continue

            weight=1

            if items[user_index].startswith('watchers'):
                user=User('/'+items[user_index].split(':')[-1])
            elif items[user_index].startswith('Contributor'):
                user=User('/'+items[user_index].split(':')[-1])
                if items[total_index].startswith('Total'):
                    weight=int(items[total_index].split(':')[-1])
                else:
                    print 'Cannot locate the total contributions!'
                    continue
            user_id=self.user_id_map.get(user, len(self.user_id_map))
            if user_id==len(self.user_id_map):
                self.user_id_map[user]=user_id
                self.id_user_map[user_id]=user

            repos_id=self.repository_id_map.get(repos, len(self.repository_id_map))
            if repos_id==len(self.repository_id_map):
                self.repository_id_map[repos]=repos_id
                self.id_repository_map[repos_id]=repos

            self.bipartite_net.add_edge(('Repos%s' % repos_id), ('User%s' % user_id), weight=weight)

        fp.close()

    def save_info(self, save_dir):
        self.save_net(save_dir)
        fp=open('_'.join([save_dir, 'ReposInfo']), 'w')
        fp.write('\n'.join([('%s\t%s\t%s' % (k, k.lang, v)) for k, v in self.repository_id_map.items()]))
        fp.close()

        fp=open('_'.join([save_dir, 'UserInfo']), 'w')
        fp.write('\n'.join([('%s\t%s' % (k.user, v)) for k, v in self.user_id_map.items()]))
        fp.close()

    
    def load_repos_user(self, load_dir):
        self.load_net(load_dir)
        fp=open('_'.join([load_dir, 'ReposInfo']))
        for line in fp.readlines():
            items=line.strip().split()
            repos=Repository(items[0])
            if len(items)==3:
                repos.lang=items[1]
            self.repository_id_map[repos]=int(items[-1])
            self.id_repository_map[int(items[-1])]=repos
        fp.close()

        fp=open('_'.join([load_dir, 'UserInfo']))
        for line in fp.readlines():
            items=line.strip().split()
            user=User('/'+items[0])
            self.user_id_map[user]=int(items[-1])
            self.id_user_map[int(items[-1])]=user
        fp.close()


if __name__=='__main__':
    net=GitHub_CollaborationNet()
    net.parse_from_log(sys.argv[1])
    print 'Finished parsing!'
#    net.construct_collabrative_net('Repos', sys.argv[-1])
    print 'Finished multiplication'
#    net.save_net(sys.argv[-1])
#    net.load_net(sys.argv[-1])
#    net.load_repos_user(sys.argv[-1])
    net.bipartite_net_degree_dist(sys.argv[-1])
    net.connected_components(sys.argv[-1])
    net.kl_divergence(sys.argv[-1])
#    net.kl_divergence(sys.argv[-1])
#    elif len(sys.argv)==3:
#        read_from_mat(sys.argv[1], sys.argv[2], sys.argv[2])
