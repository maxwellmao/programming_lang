#!/usr/bin/python
from __future__ import division
import os, sys
import networkx as nx
import scipy
import scipy.io
import codecs
from github_collaboration_network import CollaborationNet


class DBLPCollaborationNet(CollaborationNet):
    def __init__(self):
        CollaborationNet.__init__(self)
        self.author_id_map=dict()
        self.conf_id_map=dict()
        self.paper_id_map=dict()
        self.term_id_map=dict()

    def load_paper_author(self, file_path, table_name='Mda'):
        mat=scipy.io.loadmat(file_path)
        matrix=mat[table_name]
        value = matrix.data
        column_index = matrix.indices
        row_pointers = matrix.indptr
        for row_index in range(len(row_pointers)-1):
            for col_index in range(row_pointers[row_index], row_pointers[row_index+1]):
#                print row_index, column_index[col_index], value[col_index]
                self.bipartite_net.add_edge(('Paper%s'%row_index), ('Author%s' % column_index[col_index]), weight=value[col_index])

#        dense_mat=matrix.todense()
#        print len(dense_mat)
#        for i in range(len(dense_mat)):
#            for j in range(len(dense_mat[i][0][0][0][0])):
#                print dense_mat[i][0][0][0][0][j]


    def save_info(self, save_dir):
        self.save_net(save_dir)

        fp=codecs.open('_'.join([save_dir, 'Author']), 'w', 'utf-8')
        fp.write('\n'.join([('%s\t%s' % (k,v)) for k, v in self.author_id_map.items()]))
        fp.close()

#        fp=codecs.open('_'.join([save_dir, 'Conf']), 'w', 'utf-8')
#        fp.write('\n'.join([s for s in conf]))
#        fp.close()
        fp=codecs.open('_'.join([save_dir, 'Paper']), 'w', 'utf-8')
        fp.write('\n'.join([('%s\t%s' % (k, v)) for k, v in self.paper_id_map.items()]))
        fp.close()
#        fp=codecs.open('_'.join([save_dir, 'Term']), 'w', 'utf-8')
#        fp.write('\n'.join([s for s in term]))
#        fp.close()

    def load_name(self, file_path, table_name='name'):
        mat=scipy.io.loadmat(file_path)
        matrix=mat[table_name]
        author=[]
        conf=[]
        paper=[]
        term=[]
        for i in matrix.tolist():
            for j in i[0][0]:
                self.author_id_map[j[0][0]]=len(self.author_id_map)
#                author.append(j[0][0])
            for j in i[0][1]:
                self.conf_id_map[j[0][0]]=len(self.conf_id_map)
#                conf.append(j[0][0])
            for j in i[0][2]:
                self.paper_id_map[j[0][0]]=len(self.paper_id_map)
#                paper.append(j[0][0])
            for j in i[0][3]:
                self.term_id_map[j[0][0]]=len(self.term_id_map)
#                term.append(j[0][0])

if __name__=='__main__':
    dblp=DBLPCollaborationNet()
    dblp.load_paper_author(sys.argv[1])
    dblp.load_name(sys.argv[1])
    dblp.construct_collabrative_net('Paper')
    dblp.save_info(sys.argv[2])
