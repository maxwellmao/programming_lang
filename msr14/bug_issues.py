#!/usr/bin/python
from __future__ import division
import os, sys
from pymongo import Connection
import datetime
import dateutil.parser
from commit_mongo import hist_data
from commit_mongo import _pdf, _ccdf
import matplotlib.pyplot as plt
import math


def bug_issue_events(bug_issues_set):
    action_dict={}
    commit_set=set()
    for result in db.issue_events.find():
        if result['issue_id'] in bug_issues_set:
        #result['commit_id'] is not None and 
            commit_set.add(result['commit_id'])
            action_dict[result['event']]=action_dict.get(result['event'], 0)+1
#            if result['event']=='subscribed':
#                print result['commit_id']
    print action_dict.keys()
    print '\n'.join(['%s %s' % (k,v) for k, v in action_dict.items()])
    print 'Number of commits related to bug issues:', len(commit_set)
    for sha in commit_set:
        for result in db.commits.find({'sha':sha}):
            print result['commit']['message'].replace('\n', ' ')

def find_issue_with_bug_labels():
    bug_issues_set=set()
    repo_bug={}
    bug_issue_time=[]
    for result in db.issues.find():
#        if len(result['labels']):
#            print result['labels']
        if 'bug' in set([l['name'].lower() for l in result['labels']]):
            bug_issues_set.add(result['id'])
            repo_info='/%s/%s' % (result['owner'], result['repo'])
            issue_set=repo_bug.get(repo_info, set())
            issue_set.add(result['url'])
            repo_bug[repo_info]=issue_set
#            print dateutil.parser.parse(result['created_at'])
#            datetime.datetime.strptime('%Y-%m-%d %H:%M:%S', result['created_at'].replace('T', ' ').replace('Z', ''))
            if result['closed_at'] is not None and result['created_at'] is not None:
                life_time=dateutil.parser.parse(result['closed_at'])-dateutil.parser.parse(result['created_at'])
#                bug_issue_time[life_time]=bug_issue_time.get(life_time, 0)+1
                bug_issue_time.append(life_time)
    print 'Total number of buggy issues: %s' % len(bug_issues_set)
#    print '\n'.join(['%s %s' % (k, len(v)) for k, v in repo_bug.items()])
    life_time_list=[int(math.ceil(t.days*24+t.seconds/3600)) for t in bug_issue_time]
#    print 'Zero:', len(filter(lambda x:x==0, life_time_list))
    plt.clf()
    hist, bin_edges=hist_data(life_time_list, N=max(life_time_list)-min(life_time_list)+1, type=_pdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='r')
    hist, bin_edges=hist_data(life_time_list, N=max(life_time_list)-min(life_time_list)+1, type=_ccdf)
    plt.loglog(bin_edges[:-1], hist, '.', color='b')
    plt.xlabel('Life time of bug-related issues')
    plt.ylabel('Probability')
    plt.legend(['PDF', 'CCDF'])
    plt.savefig('results/BugIssueLifeTime.png', dpi=500)
    return bug_issues_set
#    print '\n'.join(['%s %s' % (k, v) for k, v in bug_issue_time.items()])


if __name__=='__main__':
    con=Connection()
    db=con.msr14
    db.authenticate('msr14', 'msr14')
    bug_issues_set=find_issue_with_bug_labels()
    bug_issue_events(bug_issues_set)
