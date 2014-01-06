#!/usr/bin/python
from __future__ import division
import os, sys
sys.path.append('../crawler')
from crawling_github import Repository, User
import networkx as nx

class CollaborationNet:
    def __init__(self):
        self.user_id_map=dict()
        self.id_user_map=dict()
        self.repository_id_map=dict()
        self.id_repository_map=dict()
        self.net=nx.Graph()

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

            self.net.add_edge(('Repos%s' % repos_id), ('User%s' % user_id), weight=weight)

        fp.close()

    def save_net(self, save_dir):
        fp=open('_'.join([save_dir, 'ReposInfo']), 'w')
        fp.write('\n'.join([('%s\t%s\t%s' % (k, k.lang, v)) for k, v in self.repository_id_map.items()]))
        fp.close()

        fp=open('_'.join([save_dir, 'UserInfo']), 'w')
        fp.write('\n'.join([('%s\t%s' % (k.user, v)) for k, v in self.user_id_map.items()]))
        fp.close()

        fp=open('_'.join([save_dir, 'Net.nx']), 'w')
        fp.write('\n'.join([('%s\t%s\t%s' % (e[0], e[1], e[2]['weight'])) for e in self.net.edges(data=True)]))
        fp.close()
    
    def load_net(self, load_dir):
        pass

if __name__=='__main__':
    net=CollaborationNet()
    net.parse_from_log(sys.argv[1])
    net.save_net(sys.argv[-1])
