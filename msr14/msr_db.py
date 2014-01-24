#!/usr/bin/python
from __future__ import division
from pymongo import Connection
from pymongo import MongoClient
import matplotlib.pyplot as plt
import networkx as nx
import MySQLdb
import datetime
import numpy as np
from github_collaboration_network import GitHub_CollaborationNet

(_pdf, _ccdf)=range(2)

def project_membership():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM project_members'
    cursor.execute(sql)
    results=cursor.fetchall()
    proj_mem=dict()
    user_contribution=dict()
    fp=open('Proj_Membership', 'w')
    for r in results:
        member=proj_mem.get(r[0], set())
        member.add(r[1])
        proj_mem[r[0]]=member
        proj=user_contribution.get(r[1], set())
        proj.add(r[0])
        user_contribution[r[1]]=proj
        fp.write('%s\t%s\t%s\n' % (r[0], r[1], r[2].strftime('%Y-%m-%d_%H:%M:%s')))
#    print proj_mem
    print 'Number of projects:%s' % len(proj_mem)
    print 'Number of contributors:%s' % len(user_contribution)
    fp.close()
    return proj_mem, user_contribution

def project_committer():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    fp=open('Proj_Committer', 'w')
    for r in results:
        fp.write('%s\t%s\t%s\n' % (r[4], r[3], r[5].strftime('%Y-%m-%d_%H:%M:%s')))
    fp.close()
    cursor.close()
    db.close()


def organization_analysis():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM organization_members'
    cursor.execute(sql)
    results=cursor.fetchall()
    org_mem=dict()
    for r in results:
        mem_set=org_mem.get(r[0], set())
        mem_set.add(r[1])
        org_mem[r[0]]=mem_set
    degree=dict()
    print 'Number of organizations:%s' % len(org_mem)
    for org, mem in org_mem.items():
        degree[len(mem)]=degree.get(len(mem), 0)+1
    sorted_deg=sorted(degree.items(), key=lambda x:x[0], reverse=True)
    deg=[]
    ccdf=[]
    cumulative=0
    for item in sorted_deg:
        cumulative+=item[1]
        deg.append(item[0])
        ccdf.append(cumulative)
    plt.clf()
    plt.loglog(deg, ccdf,  '.')
    plt.savefig('Org_member.png', dpi=500)
    cursor.close()
    db.close()
    return org_mem

def watchers_analysis():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM watchers'
    cursor.execute(sql)
    results=cursor.fetchall()
    repos_dict=dict()
    for r in results:
        watcher=repos_dict.get(r[0], set())
        watcher.add(r[1])
        repos_dict[r[0]]=watcher
    print 'Number of repos:%s' % len(repos_dict)
    degree=dict()
    for repos, watchers in repos_dict.items():
        degree[len(watchers)]=degree.get(len(watchers), 0)+1
    sorted_deg=sorted(degree.items(), key=lambda x:x[0], reverse=True)
    deg=[]
    ccdf=[]
    cumulative=0
    for item in sorted_deg:
        cumulative+=item[1]
        deg.append(item[0])
        ccdf.append(cumulative)
    plt.clf()
    plt.loglog(deg, ccdf,  '.')
    plt.savefig('Repos_watchers.png', dpi=500)
    cursor.close()
    db.close()
    return repos_dict

def contributor_watcher_analysis(repos_mem, repos_watcher):
    member_seq=[]
    watcher_seq=[]
    for repos, member in repos_mem.items():
        member_seq.append(len(member))
        if repos_watcher.has_key(repos):
            watcher_seq.append(len(repos_watcher[repos]))
        else:
            watcher_seq.append(0)
    plt.clf()
    plt.loglog(member_seq, watcher_seq, '.')
    plt.xlabel('Number of members')
    plt.ylabel('Number of watchers')
    plt.savefig('Member_watcher.png', dpi=500)

def hist_data(data_list, data_range=None, N=1000, type=_pdf):
    if data_range is None:
        data_range=(min(data_list), max(data_list))
    bins=np.arange(data_range[0], data_range[1]+(data_range[1]-data_range[0])/N, (data_range[1]-data_range[0])/N)
    hist=[0 for i in range(len(bins)-1)]
    current_bin=0
    for item in sorted(data_list):
        while(item>bins[current_bin]) and current_bin<len(bins)-1:
            current_bin+=1
        if current_bin==0:
            hist[current_bin]+=1
        else:
            hist[current_bin-1]+=1
    bin_center=[(bins[i+1]+bins[i])/2 for i in range(len(bins)-1)]
    if type==_pdf:
        s=sum(hist)
        return [h/s for h in hist], bins
    else:
        cumulative=0
        ccdf_hist=[]
        for h in hist[::-1]:
            cumulative+=h
            ccdf_hist.append(cumulative)
        ccdf_hist.reverse()
        return [h/cumulative for h in ccdf_hist], bins

class ReposInfo:
    def __init__(self, result):
        self.id=result[0]
        self.url=result[1]
        self.owner_id=result[2]
        self.name=result[3]
        self.description=result[4]
        self.language=result[5]
        self.create_time=result[6]
        self.ext_id=result[7]
        self.fork_from=result[8]

def repos_info():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM projects ORDER BY created_at'
    cursor.execute(sql)
    results=cursor.fetchall()
    proj_info_dict=dict()
    for r in results:
        proj_info_dict[r[0]]=ReposInfo(r)
    print 'No of projects:%s' % len(proj_info_dict)
    return proj_info_dict

def watchers_generative(repos_info_dict):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM watchers ORDER BY created_at'
    cursor.execute(sql)
    results=cursor.fetchall()
    create_time=dict()
    for r in results:
        repos_create_time=repos_info_dict[r[0]].create_time
        if r[2]!=repos_create_time:
            time_list=create_time.get(r[0], [])
            time_list.append(r[2])
            create_time[r[0]]=time_list
#    sql = 'SELECT * FROM watchers ORDER BY created_at'
#    cursor.execute(sql)
#    results=cursor.fetchall()

    arrival_time=[]
    fp=open('Watcher_arrival_time', 'w')
    for repos, time in create_time.items():
        last_time=datetime.datetime(1999,1,1)
#        print time
#        print [t.strftime('%Y-%m-%d_%H:%m:%s') for t in time]
        fp.write('%s\n' % ' '.join([t.strftime('%Y-%m-%d_%H:%m:%s') for t in time]))
        for t in time:
            if last_time.year>1999:
                arrival_time.append((t-last_time).days)
            last_time=t
    fp.close()
    hist, bin_center=hist_data(arrival_time, type=_ccdf)
    plt.clf()
#    print hist
#    print bin_center
    plt.loglog(bin_center, hist)
    plt.xlabel('Arrival time')
    plt.ylabel('Frequency')
    plt.savefig('WatchersGenerative.png', dpi=500)
    
def contributors_generative():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM project_members ORDER BY created_at'
    cursor.execute(sql)
    results=cursor.fetchall()
    create_time=dict()
    for r in results:
        time_list=create_time.get(r[0], [])
        time_list.append(r[2])
        create_time[r[0]]=time_list
    arrival_time=[]
    for repos, time in create_time.items():
#        print time
        last_time=datetime.datetime(1999,1,1)
        for t in time:
            if last_time.year>1999:
#                arrival_time.append((t-last_time).days)
                arrival_time.append((t-last_time).seconds)
            last_time=t
    hist, bin_center=hist_data(arrival_time)
    plt.clf()
    plt.plot(bin_center, hist)
    plt.xlabel('Arrival time')
    plt.ylabel('Frequency')
    plt.savefig('ContributorGenerative.png', dpi=500)


def mongo_db():
    con=Connection('localhost')
    client = MongoClient()
    db = client.msr14
    collection = db['']

def mysql_db():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT count(*) FROM projects'

def user_involvement_analysis(user_contribution):
    involve=[]
    for k,v in user_contribution.items():
        involve.append(len(v))
    hist, bin_center=hist_data(involve)
    plt.clf()
    plt.plot(bin_center, hist)
    plt.xlabel('Number of involving repos')
    plt.ylabel('Probability')
    plt.savefig('Involvement.png', dpi=500)
    print set(involve)

def commit_info():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM commit_comments'
    cursor.execute(sql)
    results=cursor.fetchall()
    commit_comments=dict()
#    for r in results:
#        commit_comments[]


def construct_net():
    github_net=GitHub_CollaborationNet()
#    net_type='Comembership'
    net_type='Cocommit'
#    file_name='Proj_Membership'
    file_name='Proj_Committer'
    github_net.parse_msr(file_name)
    github_net.bipartite_net_degree_dist(net_type)
    github_net.bipartite_net_degree_dist(net_type, _ccdf)
    print 'Bipartite_Net nodes: %s edge: %s' % (len(github_net.bipartite_net.nodes()), len(github_net.bipartite_net.edges()))
    github_net.kl_divergence(net_type)
    github_net.connected_components(net_type)
#    github_net.construct_collabrative_net('Repos', 'Collabrative')
    github_net.construct_collabrative_net('Repos', 'CoCommit')
    github_net.collabrative_net_degree_dist(net_type)
    github_net.collabrative_net_degree_dist(net_type, _ccdf)
    fp=open('%s_net' % net_type, 'w')
    for e in github_net.collabrative_net.edges(data=True):
        fp.write('%s\t%s\t%s\n' % (github_net.id_user_map[e[0]].user, github_net.id_user_map[e[1]].user, e[2]['weight']))
    fp.close()


if __name__=='__main__':
#    follow_relationship()
    repos_mem, user_contribution=project_membership()
#    print '\n'.join(['%s\t%s' % (k,len(v)) for k,v in user_contribution.items()]
#    user_involvement_analysis(user_contribution)
    project_committer()
    construct_net()
#    organization_analysis()
#    repos_watcher=watchers_analysis()
#    contributor_watcher_analysis(repos_mem, repos_watcher)
#    contributors_generative()
#    repos_info_dict=repos_info()
#    watchers_generative(repos_info_dict)
