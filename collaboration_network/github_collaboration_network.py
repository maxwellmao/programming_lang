#!/usr/bin/python
from __future__ import division
import os, sys
sys.path.append('../crawler')
from crawling_github import Repository, User
import networkx as nx
import scipy
import scipy.io
import codecs
from scipy.sparse import *
import re

class CollaborationNet:
    def __init__(self):
        self.bipartite_net=nx.Graph()
        self.collabrative_net=nx.Graph()
        self.self_weight=dict()

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


    def load_net(self, load_dir):
        fp=open('_'.join([load_dir, 'Net.nx']))
        for line in fp.readlines():
            items=line.strip().split()
            if len(items)==3:
                self.bipartite_net.add_edge(items[0], items[1], weight=int(items[-1]))
        fp.close()

    def bipartite_net_degree_dist(self, save_dir):
        degree_dist_dict=dict()
        for k, v in self.bipartite_net.degree().items():
            type=re.findall(r'[A-Za-z]+', k)
            if degree_dist_dict.has_key(type):
                degree_dist_dict[type][v]=degree_dist_dict[type].get(v, 0)+1
            else:
                degree_dist_dict[type]=dict({v:1})
        for k, v in degree_dist_dict.items():
            fp=open('_'.join([save_dir, k]), 'w')
            fp.write('\n'.join([('%s\t%s' % (d[0], d[1])) for d in sorted(v.items(), key=lambda x:x[0])]))
            fp.close()

    def collabrative_net_degree_dist(self, save_dir):
        if len(self.collabrative_net.nodes())==0:
            print 'Construct the collabrative network first'
            return
        degree_dict=dict()
        for k, v in self.collabrative_net.degree.items():
            degree_dict[v]=degree_dict.get(v, 0)+1
        fp=open('_'.join([save_dir, 'Collabrative']))
        fp.write('\n'.join([('%s\t%s' % (d[0], d[1])) in sorted(degree_dict.items(), key=lambda x:x[0])]))
        fp.close()

    def connected_components(self):
        pass

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
            if col_id==10792 or col_id==2068 or col_id==20246:
                print edge
            col.append(col_id)
            row.append(row_id)
            data.append(1)
        people_type_mat=csr_matrix((data, (col, row)))
        type_people_mat=csr_matrix((data, (row, col)))
        comat=people_type_mat*type_people_mat
        
        value = comat.data
        column_index = comat.indices
        row_pointers = comat.indptr
        print len(value)
        if len(save_dir)>0:
            fp_net=open('_'.join([save_dir, 'Collaboration_Net.nx']), 'w')
            fp_self_weight=open('_'.join([save_dir, 'Collaboration_Self_weight']), 'w')

        for row_index in range(len(row_pointers)-1):
            for col_index in range(row_pointers[row_index], row_pointers[row_index+1]):
                if len(save_dir)>0:
                    if row_index==column_index[col_index]:
                        fp_self_weight.write('%s\t%s\n' % (row_index, value[col_index]))
                    else:
                        fp_net.write('%s\t%s\t%s\n' % (row_index, column_index[col_index], value[col_index]))
                else:
                    if row_index==column_index[col_index]:
                        self.self_weight[row_index]=value[col_index]
                    else:
                        self.collabrative_net.add_edge(row_index, column_index[col_index], weight=value[col_index])

        if len(save_dir)>0:
            fp_net.close()
            fp_self_weight.close()

        print len(self.collabrative_net.edges()), len(self.collabrative_net.nodes())
        

class GitHub_CollaborationNet(CollaborationNet):
    def __init__(self):
        CollaborationNet.__init__(self)
        self.user_id_map=dict()
        self.id_user_map=dict()
        self.repository_id_map=dict()
        self.id_repository_map=dict()

    def parse_from_log(self, log_path):
        fp=open(log_path)
        repos_index=6
        repos_lang_index=7
        user_index=8
        total_index=9
        for line in fp.readlines():
            items=line.strip().split()
            if items[repos_index].startswith('Repository'):
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

    
    def load_info(self, load_dir):
        self.load_net(load_dir)
        fp=open('_'.join([load_dir, 'ReposInfo']))
        for line in fp.readlines():
            items=line.strip().split()
            repos=ReposInfo(items[0])
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
    net.construct_collabrative_net('Repos', sys.argv[-1])
    print 'Finished multiplication'
    net.save_net(sys.argv[-1])
#    elif len(sys.argv)==3:
#        read_from_mat(sys.argv[1], sys.argv[2], sys.argv[2])
