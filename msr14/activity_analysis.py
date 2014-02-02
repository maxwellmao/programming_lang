#!/usr/bin/python
import os, sys
import MySQLdb
import matplotlib.pyplot as plt
import datetime
from msr_db import hist_data
from msr_db import _pdf, _ccdf

mySQLdb=MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
cursor=mySQLdb.cursor()

def plot_repo_activity():
    sql='select id, url, owner_id, name from projects'
    cursor.execute(sql)
    results=cursor.fetchall()
    id_repo={}
    for r in results:
        id_repo[r[0]]=r[1].replace('https://api.github.com/repos/', '').replace('/', '_')

    sql='select project_members.repo_id, commits.author_id, commits.committer_id, commits.sha, commits.created_at from commits join project_members on commits.project_id=project_members.repo_id;'
    print 'Activity stat'
    cursor.execute(sql)
    results=cursor.fetchall()
    repo_activities={}
    for r in results:
        activity_time=repo_activities.get(r[0], [])
        activity_time.append(r[-1].date())
        repo_activities[r[0]]=activity_time
    for k, v in repo_activities.items():
        day_activity={}
        last_day=datetime.date(1999,1,1)
        day=[]
        freq=[]
        for d in sorted(v):
            if last_day!=d:
                if last_day.year==1999:
                    day.append(1)
                    first_day=d
                else:
                    day.append((d-first_day).days+1)
                freq.append(1)
            else:
                freq[-1]+=1
            last_day=d
        plt.clf()
        plt.plot(day, freq, '.')

        plt.xlabel('Days - start from %s' % first_day.strftime('%Y-%m-%d'))
        plt.ylabel('No. of commits')
        plt.savefig('results/activity/%s_time_series.png' % id_repo[k], dpi=500)
        print id_repo[k], first_day
        arrival=[]
        for i in set(range(1, max(day)+1))-set(day):
            arrival.append(0)
        arrival+=freq
        plt.clf()
        hist, bin_edge=hist_data(arrival, N=max(arrival)-min(arrival)+1, type=_ccdf)
        plt.plot(bin_edge[:-1], hist, '.', color='r')
        hist, bin_edge=hist_data(arrival, N=max(arrival)-min(arrival)+1, type=_pdf)
        plt.plot(bin_edge[:-1], hist, '.', color='b')
        plt.xlabel('No of commits per day')
        plt.ylabel('Probability')
        plt.legend(['CCDF', 'PDF'])
        plt.savefig('results/activity/%s_rate.png' % id_repo[k], dpi=500)

if __name__=='__main__':
    plot_repo_activity()
