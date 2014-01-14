#!/usr/bin/python
from __future__ import division
import os, sys
import matplotlib.pyplot as plt
import networkx as nx
from github_collaboration_network import CollaborationNet
import numpy as np
import re
from github_collaboration_network import _pdf, _cdf, _ccdf

class File_User_CollaborationNet(CollaborationNet):
    def __init__(self):
        CollaborationNet.__init__(self)
        self.user_id_map=dict()
        self.id_user_map=dict()
        self.file_id_map=dict()
        self.id_file_map=dict()

    def parse_from_log(self, log_path):
        fp=open(log_path)
        for line in fp.readlines():
            items=line.strip().split('\t')
            if len(items)==3:
                user=items[-1]
                user_id=self.user_id_map.get(user, len(self.user_id_map))
                if user_id==len(self.user_id_map):
                    self.user_id_map[user]=user_id
                    self.id_user_map[user_id]=user

                file=items[1]
                file_id=self.file_id_map.get(file, len(self.file_id_map))
                if file_id==len(self.file_id_map):
                    self.file_id_map[file]=file_id
                    self.id_file_map[file_id]=file
                previous_w=self.bipartite_net.get_edge_data('User%s' % user_id, 'File%s' % file_id)
                if previous_w is None:
                    self.bipartite_net.add_edge('User%s'%user_id, 'File%s'%file_id, weight=1)
                else:
                    self.bipartite_net.add_edge('User%s' % user_id, 'File%s' % file_id, weight=previous_w['weight']+1)
        fp.close()

    def save_info(self, save_dir):
        self.save_net(save_dir)
        fp=open('_'.join([save_dir, 'UserInfo']), 'w')
        print 'Saving ', '_'.join([save_dir, 'UserInfo'])
        fp.write('\n'.join([('%s\t%s' % (k, v)) for k, v in self.user_id_map.items()]))
        fp.close()

        print 'Saving ', '_'.join([save_dir, 'FileInfo'])
        fp=open('_'.join([save_dir, 'FileInfo']), 'w')
        fp.write('\n'.join([('%s\t%s' % (k, v)) for k, v in self.file_id_map.items()]))
        fp.close()

if __name__=='__main__':
    net=File_User_CollaborationNet()
    net.parse_from_log(sys.argv[1])
    print 'User:%s\tFile:%s' % (len(net.user_id_map), len(net.file_id_map))
    print 'Finished parsing'
    net.bipartite_net_degree_dist(sys.argv[-1])
    net.bipartite_net_degree_dist(sys.argv[-1], _cdf)
    net.bipartite_net_degree_dist(sys.argv[-1], _ccdf)
    net.save_info(sys.argv[-1])
    net.kl_divergence(sys.argv[-1])
