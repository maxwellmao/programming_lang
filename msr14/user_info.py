#/usr/bin/python
import os, sys
import networkx as nx
import MySQLdb
import matplotlib.pyplot as plt

class User:
    def __init__(self, result):
        self.id=result[0]
        self.login=result[1]
        self.name=result[2]
        self.company=result[3]
        self.location=result[4]
        self.email=result[5]
        self.create_time=result[6]
        self.type=result[8]

    def __str__(self):
        return 'ID:%s Login:%s Name:%s Company:%s Location:%s Email:%s Create:%s Type:%s' % (self.id, self.login, self.name, self.company, self.location, self.email, self.create_time.strftime('%Y-%m-%d_%H:%M:%S'), self.type)

    __repr__=__str__

def find_developers():
    '''
    find the set of developers among these 90 repos
    '''
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM project_members'
    cursor.execute(sql)
    results=cursor.fetchall()
    developers=set()
    for r in results:
        developers.add(r[1])
    cursor.close()
    db.close()
    return developers


def user_pagerank(follow_net, developers=set()):
    pr=nx.pagerank(follow_net, alpha=0.85)
    lastRank=0
    lastValue=-1
    user_rank=dict()
    for prItem in sorted(pr.items(), key=lambda x:x[1], reverse=True):
        if lastValue!=prItem[1] or lastRank==0:
            lastRank+=1
        lastValue=prItem[1]
        user_rank[prItem[0]]=[lastRank, lastValue]
    fp=open('UserRank', 'w')
    fp.write('\n'.join(['%s\t%s\t%s' % (item[0], item[1][0], item[1][1]) for item in sorted(user_rank.items(), key=lambda x:x[1][0])]))
    fp.close()

    develop_rank=[]
    for item in sorted(user_rank.items(), key=lambda x:x[1][0]):
        if item[0] in developers:
            develop_rank.append([item[0], item[1][0], item[1][1]])
    print 'Ranking of developers'
    print '\n'.join(['%s\t%s\t%s' % (item[0], item[1], item[2]) for item in develop_rank])


def follow_relationship():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql = 'SELECT * FROM followers'
    cursor.execute(sql)
    results=cursor.fetchall()
    g=nx.DiGraph()
    for r in results:
        g.add_edge(r[0], r[1])
    in_degree_dist=dict()
    out_degree_dist=dict()
    for k,v in g.in_degree().items():
        in_degree_dist[v]=in_degree_dist.get(v, 0)+1
    for k, v in g.out_degree().items():
        out_degree_dist[v]=out_degree_dist.get(v, 0)+1
    sorted_in=sorted(in_degree_dist.items(), key=lambda x:x[0], reverse=True)
    sorted_out=sorted(out_degree_dist.items(), key=lambda x:x[0], reverse=True)
    plt.clf()
    plt.loglog([r[0] for r in sorted_in], [r[1] for r in sorted_in], '.', color='b')
    plt.loglog([r[0] for r in sorted_out], [r[1] for r in sorted_out], '.', color='r')
    plt.legend(['In-degree', 'Out-degree'])
    plt.savefig('FollowerDegree.png', dpi=500)

    in_ccdf=[]
    in_x=[]
    out_ccdf=[]
    out_x=[]
    cumulative=0
    for item in sorted_in:
        cumulative+=item[1]
        in_ccdf.append(cumulative)
        in_x.append(item[0])
    cumulative=0
    for item in sorted_out:
        cumulative+=item[1]
        out_ccdf.append(cumulative)
        out_x.append(item[0])
    plt.clf()
    plt.loglog(in_x, in_ccdf, '.', color='b')
    plt.loglog(out_x, out_ccdf, '.', color='r')
    plt.legend(['In-degree', 'Out-degree'])
    plt.savefig('FollowerDegree_ccdf.png', dpi=500)
    cursor.close()
    db.close()
    print 'Follow network construction completed!'
    print 'Number of users:%s, number of relationships:%s' % (len(g.nodes()), len(g.edges()))
    return g

def save_user_info():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql='select * from users'
    cursor.execute(sql)
    results=cursor.fetchall()
    fp=open('UserInfo', 'w')
    for r in results:
        fp.write('%s\n' % str(User(r)))
    fp.close()
    cursor.close()
    db.close()

def get_user_id_info():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql='select * from users'
    cursor.execute(sql)
    results=cursor.fetchall()
    user_id_info={}
    for r in results:
#        fp.write('%s\n' % str(User(r)))
        user=User(r)
        user_id_info[r[0]]=user
    cursor.close()
    db.close()
    return user_id_info

def match_rank(userInfo, userRank):
    fp=open(userInfo)
    user_info=dict()
    for line in fp.readlines():
        item=line.strip().split()
        if item[0].startswith('ID:'):
            user_info[int(item[0].split(':')[1])]=' '.join(item[1:])
    fp.close()
    fp=open(userRank)
    for line in fp.readlines():
        item=line.strip().split()
        if user_info.has_key(int(item[0])):
            print item[0], user_info[int(item[0])]
    fp.close()

def alias_detect():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql='select * from users'
    cursor.execute(sql)
    results=cursor.fetchall()
    all_user_info=dict()
    user_name=[]
    email=[]
    login=[]
    for r in results:
        all_user_info[r[0]]=r[1:]
        if r[1] is not None:
            login.append([r[1].lower(), r[0]])
        if r[2] is not None:
            user_name.append([r[2].lower(), r[0]])
        if r[5] is not None:
            email.append([r[5].lower(), r[0]])
    fp=open('UserLogin', 'w')
    fp.write('\n'.join(['Login:\"%s\"\t%s %s' % (item[0], item[1], ' '.join([str(i) for i in all_user_info[item[1]]])) for item in sorted(login, key=lambda x:x[0])]))
    fp.close()
    fp=open('UserName', 'w')
    fp.write('\n'.join(['Name:\"%s\"\t%s %s' % (item[0], item[1], ' '.join([str(i) for i in all_user_info[item[1]]])) for item in sorted(user_name, key=lambda x:x[0])]))
    fp.close()
    fp=open('UserEmail', 'w')
    fp.write('\n'.join(['Email:\"%s\"\t%s %s' % (item[0], item[1], ' '.join([str(i) for i in all_user_info[item[1]]])) for item in sorted(email, key=lambda x:x[0])]))
    fp.close()
    last=''
    last_item=[]
    alias_dict=dict()
    for item in sorted(email, key=lambda x:x[0]):
        if item[0].find('@')>0 and item[0].find('(')<0:
#            if last==item[0]:
#                print item[0], last_item[0], last_item[1]
#                print item[0], item[1], all_user_info[item[1]]
            last=item[0]
            alias_id_list=alias_dict.get(last, [])
            alias_id_list.append(item[1])
            alias_dict[last]=alias_id_list
            last_item=[item[1], all_user_info[item[1]]]
    email_alias_num=0
    commit_alias=0
    for k, v in alias_dict.items():
        if len(v)>1:
            email_alias_num+=1
#            query=' or '.join(['author_id=%s or committer_id=%s' % (id, id) for id in v])
            query=' or '.join(['committer_id=%s' % id for id in v])
            sys.stderr.write(query+'\n')
            sql='select * from commits where %s' % query
            cursor.execute(sql)
            results=cursor.fetchall()
            if len(results)>0:
                commit_alias+=1
            for r in results:
                print r
            print '-----------------------------------------------------------------'
    cursor.close()
    db.close()
    sys.stderr.write('Email alias number:%s, commit alias:%s\n' % (email_alias_num, commit_alias))

def name_alias():
    db = MySQLdb.connect('localhost', 'msr14', 'msr14', 'msr14')
    cursor = db.cursor()
    sql='select * from users'
    cursor.execute(sql)
    results=cursor.fetchall()
    user_name=dict()
    before_alias=0
    none_email=0
    name_char_set=set()
    none_name=0
    for r in results:
        if r[5] is not None:
            before_alias+=1
            name=r[5].split('@')[0]
            name_list=user_name.get(name, [])
            name_list.append(r[5])
            user_name[name]=name_list
        else:
            none_email+=1
#            print r
        if r[2] is not None:
            for c in r[2]:
                name_char_set.add(c)
        else:
            none_name+=1
#            print r
    print 'None email:%s' % none_email
    print 'None name:%s' % none_name
    print 'Before alias:%s, after alias:%s' % (before_alias, len(user_name))
    print 'Name characters:%s' % len(name_char_set)
    print name_char_set
    fp=open('NameAlias', 'w')
#    for k,v in user_name.items():
    fp.write('\n'.join(['%s\t%s' % (k, ' '.join([n for n in v])) for k, v in user_name.items()]))
    fp.close()
    cursor.close()
    db.close()

if __name__=='__main__':
#    save_user_info()
#    name_alias()
    alias_detect()
#    match_rank(sys.argv[1], sys.argv[2])
#    g=follow_relationship()
#    developers=find_developers()
#    user_pagerank(g)
