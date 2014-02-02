#!/usr/bin/python
from __future__ import division
import MySQLdb
import sys
import csv
from msr_db import hist_data
import math
import matplotlib.pyplot as plt
import datetime
(_pdf, _ccdf)=range(2)

def label_dist():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM repo_labels'
    cursor.execute(sql)
    results=cursor.fetchall()
    label_dist=dict()
    for r in results:
        label_list=label_dist.get(r[1], [])
        label_list.append(r[3])
        label_dist[r[1]]=label_list
    print '\n'.join(['%s %s %s' % (k, len(v), len(set(v))) for k,v in label_dist.items()])
    cursor.close()
    db.close()

class Project:
    def __init__(self, id):
        self.id=id
        self.repo_label=[]
        self.commit_label=[]
        self.issue_label=[]
        self.member=[]
        self.watcher=[]
        self.issue_num=0
        self.commit_num=0
        self.create_time=datetime.datetime(1999,1,1)
        self.owner_id=0
        self.url=''
        self.member_join_time=[]
        self.miss_member_join_time=[]
        self.join_time_is_user_time=[]
        self.join_time_is_project_time=[]
        self.fork_projects=[]
        self.description=''

class Developer:
    def __init__(self, id):
        self.id=id
        self.repos=[]
        self.location=''
        self.company=''
        self.name=''
        self.create_time=datetime.datetime(1999,1,1)

def get_commit(projects, proj_info):
    pass

def get_repo_labels(proj_info):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM repo_labels'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        if proj_info.has_key(r[1]):
            proj=proj_info.get(r[1], Project(r[1]))
            proj.repo_label.append(r[2])
            proj_info[r[1]]=proj
    cursor.close()
    db.close()

#def get_issue_label(projects, proj_info):
#    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
#    cursor = db.cursor()
#    sql = 'SELECT * FROM issue_labels'
#    cursor.execute(sql)
#    results=cursor.fetchall()
#    for r in results:
#        if r[1] in projects:
#            proj=proj_info.get(r[1], Project())
#            proj.repo_label.append(r[2])
#            proj_info[r[1]]=proj
#    cursor.close()
#    db.close()

def project_member():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM project_members'
    cursor.execute(sql)
    results=cursor.fetchall()
    proj_info=dict()
    developer=set()
    for r in results:
        proj=proj_info.get(r[0], Project(r[0]))
        proj.member.append(r[1])
        proj_info[r[0]]=proj
        developer.add(r[1])
    cursor.close()
    db.close()
    return proj_info, developer

def get_watcher(proj_info):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM watchers'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        if proj_info.has_key(r[0]):
            proj=proj_info.get(r[0], Project(r[0]))
            proj.watcher.append(r[1])
            proj_info[r[0]]=proj
    cursor.close()
    db.close()

def get_issue_num(proj_info):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM issues'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        if proj_info.has_key(r[1]):
            proj=proj_info.get(r[1], Project(r[1]))
            proj.issue_num+=1
            proj_info[r[1]]=proj
    cursor.close()
    db.close()

def get_commit_num(proj_info):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM commits'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        if proj_info.has_key(r[4]):
            proj=proj_info.get(r[4], Project(r[4]))
            proj.commit_num+=1
            proj_info[r[4]]=proj
    cursor.close()
    db.close()

def developer_info(developer):
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM users'
    cursor.execute(sql)
    results=cursor.fetchall()
    company_set=set()
    location_set=set()
    developer_dict=dict()
    for r in results:
        if r[0] in developer:
            dev=Developer(r[0])
            dev.name=r[2]
            dev.company=r[3]
            dev.location=r[4]
            dev.create_time=r[6]
            company_set.add(r[3])
            location_set.add(r[4])
            print dev.company, dev.location
            developer_dict[r[0]]=dev
    cursor.close()
    db.close()
    print 'Number of different companies: %s' % len(company_set)
    print 'Number of different locations: %s' % len(location_set)
    return developer_dict

def diversity(label_dist):
    entropy=0.0
    total=sum(label_dist.values())
    for l, f in label_dist.items():
        entropy-=(f/total)*math.log(f/total)/math.log(2)
    return entropy

def location_company_dist(proj_info, developer_dict):
    for proj in proj_info.values():
        location_dist=dict()
        company_dist=dict()
        for m in proj.member:
            if developer_dict.has_key(m):
                location_dist[developer_dict[m].location]=location_dist.get(developer_dict[m].location, 0)+1
                company_dist[developer_dict[m].company]=company_dist.get(developer_dict[m].company, 0)+1
#        print location_dist
#        print company_dist
        print 'Loc: %s Comp:%s' % (diversity(location_dist), diversity(company_dist))

def project_details():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM projects'
    cursor.execute(sql)
    results=cursor.fetchall()
    description=set()
    for r in results:
        if r[8] is None:
            print r[0], r[8], r[4]
#        description.add(r[4])
#    print '\n'.join(description)
    sys.stderr.write('%s\n' % len(description))
    cursor.close()
    db.close()
    
def query_project_info():
    proj_info, developer=project_member()
    developer_dict=developer_info(developer)
    location_company_dist(proj_info, developer_dict)
    get_repo_labels(proj_info)
    get_watcher(proj_info)
    get_issue_num(proj_info)
    get_commit_num(proj_info)
#    print 'Number of projects:%s' % len(proj_info)
#    with open('project_info.csv', 'w') as csvfile:
#        infowriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#        for proj in proj_info.values():
#            infowriter.writerow([proj.id, len(proj.repo_label), len(proj.member), len(proj.watcher), proj.commit_num, proj.issue_num])
#    print '\n'.join(['%s Labels:%s Members:%s Watchers:%s Commits:%s Issues:%s' % (proj.id, len(proj.repo_label), len(proj.member), len(proj.watcher), proj.commit_num, proj.issue_num) for proj in proj_info.values()])
#    print '\n'.join(['%s\t%s\t%s\t%s\t%s' % (len(proj.repo_label), len(proj.member), len(proj.watcher), proj.commit_num, proj.issue_num) for proj in proj_info.values()])
    plot_dist(proj_info)

def plot_dist(proj_info):
    dist_type=_ccdf
    member=[len(proj.member) for proj in proj_info.values()]
    hist, bin_edges=hist_data(member, N=max(member)-min(member), type=dist_type)
    plt.clf()
    plt.loglog(bin_edges[:-1], hist, '.')
    plt.xlabel('Number of members for in one project')
    plt.ylabel('Probability')
    plt.savefig('MemberDist.png', dpi=500)

    watcher=[len(proj.watcher) for proj in proj_info.values()]
    hist, bin_edges=hist_data(watcher, N=max(watcher)-min(watcher), type=dist_type)
    plt.clf()
    plt.loglog(bin_edges[:-1], hist, '.')
    plt.xlabel('Number of watchers for in one project')
    plt.ylabel('Probability')
    plt.savefig('WatcherDist.png', dpi=500)

    commit=[proj.commit_num for proj in proj_info.values()]
    hist, bin_edges=hist_data(commit, N=max(commit)-min(commit), type=dist_type)
    plt.clf()
    plt.loglog(bin_edges[:-1], hist, '.')
    plt.xlabel('Number of commits for in one project')
    plt.ylabel('Probability')
    plt.savefig('CommitDist.png', dpi=500)

    issue=[proj.issue_num for proj in proj_info.values()]
    hist, bin_edges=hist_data(issue, N=max(issue)-min(issue), type=dist_type)
    plt.clf()
    plt.loglog(bin_edges[:-1], hist, '.')
    plt.xlabel('Number of issues for in one project')
    plt.ylabel('Probability')
    print hist
    print bin_edges
    plt.savefig('IssueDist.png', dpi=500)

if __name__=='__main__':
#    label_dist()
    query_project_info()
#    project_details()
