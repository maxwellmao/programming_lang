#!/usr/bin/python
from __future__ import division
import sys, os
import MySQLdb
import matplotlib.pyplot as plt
from msr_db import hist_data
from msr_db import _pdf, _ccdf
import math
from two_d_histogram import scatter_two
from two_d_histogram import _loglog, _normal

db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
cursor = db.cursor()
def number_of_issue_events():
    sql='select * from issue_events'
    cursor.execute(sql)
    results=cursor.fetchall()
    issues_events={}
    for r in results:
        issues_events[r[1]]=issues_events.get(r[1], 0)+1
    event_num=issues_events.values()
    plt.clf()
    hist, bin_edge=hist_data(event_num, N=max(event_num)-min(event_num), type=_ccdf)
    plt.loglog(bin_edge[:-1], hist, '.', color='b')
    hist, bin_edge=hist_data(event_num, N=max(event_num)-min(event_num), type=_pdf)

    plt.loglog(bin_edge[:-1], hist, '.', color='r')
    plt.xlabel('# of events for each issue')
    plt.ylabel('Probability')
    plt.legend(['CCDF', 'PDF'])
    plt.savefig('IssueEventNum.png', dpi=500)

def get_issue_life_time():
    issue_repo={}
    sql='select id, repo_id from issues'
    cursor.execute(sql)
    results=cursor.fetchall()
    for r in results:
        issue_repo[r[0]]=r[1]
    sql='select issue_id, min(created_at), max(created_at) from issue_events group by issue_id;'
    cursor.execute(sql)
    results=cursor.fetchall()
    repo_issues_life_time={}
    all_life_time=[]
    for r in results:
        all_life_time.append((r[2]-r[1]).days*24+(r[2]-r[1]).seconds/3600)
#        issues_life_time[r[0]]=r[2]-r[1]
        life_time_list=repo_issues_life_time.get(issue_repo[r[0]], [])
        life_time_list.append(r[2]-r[1])
        repo_issues_life_time[issue_repo[r[0]]]=life_time_list
#    issue_num_life_time=[]
    issue_num_life_time_dict={}
    for repo_id, life_time_list in repo_issues_life_time.items():
        print len(life_time_list)
        for life_time in life_time_list:
#            issue_num_life_time.append([len(life_time_list), life_time])
            issue_num_life_time_dict['%s\t%s' % (len(life_time_list), int(life_time.days*24+life_time.seconds/3600))]=issue_num_life_time_dict.get('%s\t%s' % (len(life_time_list), int(life_time.days*24+life_time.seconds/3600)), 0)+1

    hist, bin_edge=hist_data(all_life_time, N=int(max(all_life_time)-min(all_life_time))+1, type=_pdf)
    plt.clf()
    plt.loglog(bin_edge[:-1], hist, '.', color='b')
    hist, bin_edge=hist_data(all_life_time, N=int(max(all_life_time)-min(all_life_time))+1, type=_ccdf)
    plt.loglog(bin_edge[:-1], hist, '.', color='r')
    plt.legend(['PDF', 'CCDF'])
    plt.xlabel('Life time (hour)')
    plt.ylabel('Probability')
    plt.savefig('IssueLifeTime.png', dpi=500)

    plt.clf()
    x=[]
    y=[]
    z=[]
    total=sum(issue_num_life_time_dict.values())
    for k, v in issue_num_life_time_dict.items():
        if int(k.split()[0])>0 and int(k.split()[1])>0:
            x.append(math.log10(int(k.split()[0])))
            y.append(math.log10(int(k.split()[1])))
            z.append(math.log10(v/total))
#    print len(issue_num_life_time_dict)
    
#    plt.loglog([i[0] for i in issue_num_life_time], [i[1].days*24+i[1].seconds/3600 for i in issue_num_life_time])
    plt.scatter(x, y, c=z, s=10, vmin=min(z), vmax=max(z), lw=0)
    plt.xlabel('No. of Issues')
    plt.ylabel('Life time of each issue')
    plt.colorbar()
    plt.savefig('IssueNumLifeTime.png', dpi=500)

def issue_num_of_developer():
    sql='select count(distinct issue_id), actor_id from issue_events group by actor_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    issue_num=[]
    for r in results:
        issue_num.append(r[0])
        if r[0]>1000:
            print r[1]
    plt.clf()
    hist, bin_edge=hist_data(issue_num, N=int(max(issue_num)-min(issue_num))+1, type=_pdf)
    plt.loglog(bin_edge[:-1], hist, '.', color='b')
    hist, bin_edge=hist_data(issue_num, N=int(max(issue_num)-min(issue_num))+1, type=_ccdf)
    plt.loglog(bin_edge[:-1], hist, '.', color='r')
    plt.legend(['PDF', 'CCDF'])
    plt.xlabel('# of issues a developer involving')
    plt.ylabel('Probability')
    plt.savefig('results/InvolvingIssueNum.png', dpi=500)

def correlation_between_commit_issue():
    sql='select count(distinct issue_id), actor_id from issue_events group by actor_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    user_issue={}
    for r in results:
        user_issue[r[1]]=r[0]
    sql='select count(id), author_id from commits group by author_id'
    cursor.execute(sql)
    results=cursor.fetchall()
    user_commit={}
    for r in results:
        user_commit[r[1]]=r[0]

    commit_issue={}
    for id in set(user_commit.keys()).union(set(user_issue.keys())):
        result_str='%s-%s' % (user_commit.get(id, 0), user_issue.get(id, 0))
        commit_issue[result_str]=commit_issue.get(result_str, 0)+1
        if result_str.startswith('0') or result_str.endswith('-0'):
            print result_str
    data=[]
    for data_str, freq in commit_issue.items():
        data.append([int(data_str.split('-')[0]), int(data_str.split('-')[1]), freq])
    scatter_two(data, '', xlabel='Contribution', ylabel='# of involving issues', save_file='results/ContributionInvolingIssue', scale=_loglog)

if __name__=='__main__':
#    number_of_issue_events()
#    get_issue_life_time()
#    issue_num_of_developer()
    correlation_between_commit_issue()
    cursor.close()
    db.close()
