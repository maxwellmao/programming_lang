#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <set>
#include "collaborative_network.h"

using namespace std;

void CollabrativeNet::read_to_construct_net(string file_path)
{
    ifstream fin(file_path.c_str());
    if(!fin)
    {
        std::cout << "File does not exist! " << file_path << std::endl;
    }
    string line;
    while(getline(fin, line))
    {
        stringstream ss(line);
        string n1_str, n2_str, w_str;
        ss >> n1_str >> n2_str >> w_str;
        int n1=atoi(n1_str.c_str());
        int n2=atoi(n2_str.c_str());
//        cout << n1 << " " << n2 << " " << w << endl;
        Edge e=Edge(n1, n2);
        pair<std::set<int>::iterator,bool> ret;
        ret=this->node_set.insert(n1);
        if(ret.second)
        {
            this->collaborative_graph->AddNode(n1);
        }
        ret=this->node_set.insert(n2);
        if(ret.second)
        {
            this->collaborative_graph->AddNode(n2);
        }
        this->collaborative_graph->AddEdge(n1, n2);
        if(w_str.length()!=0)
        {
            int w=atoi(w_str.c_str());
            this->edge_weight.insert(make_pair(e, w));
        }
        else
        {   
            this->edge_weight.insert(make_pair(e, 1));
        }
    }
    fin.close();
    cout << this->collaborative_graph->GetEdges() << " " << this->collaborative_graph->GetNodes() << endl;
    cout << this->edge_weight.size() << endl;
}

void CollabrativeNet::save_net(string dir)
{
    TFOut fOut((dir+"net.graph").c_str());
    this->collaborative_graph->Save(fOut);
    ofstream fout((dir+"edge_weight").c_str());
    if(!fout)
    {
        cerr << "File cannot open!" << dir << "edge_weight" << endl;
        return;
    }
    for(map<Edge, int>::iterator it=this->edge_weight.begin(); it!=this->edge_weight.end(); it++)
    {
        fout << it->first.smaller_node << "\t" << it->first.larger_node << "\t" << it->second << endl;
    }
    fout.close();
}

void CollabrativeNet::get_diameter()
{
    double effDia;
    int fullDia;
    TSnap::GetBfsEffDiam(this->collaborative_graph, this->collaborative_graph->GetNodes(), true, effDia, fullDia);
    cout << "Eff Dia:" << effDia << " Full Dia:" << fullDia << endl;
}

void CollabrativeNet::connected_component(string dir)
{
//    TCnComV sccComV;
//    TSnap::GetSccs(this->collaborative_graph, sccComV);
//
//    TCnComV wccComV;
//    TSnap::GetWccs(this->collaborative_graph, wccComV);
//
//    PNGraph scc=TSnap::GetMxScc(this->collaborative_graph);
//    PNGraph wcc=TSnap::GetMxWcc(this->collaborative_graph);
//    cout << "Max Scc:" << (double)scc->GetNodes()/(double)this->collaborative_network->GetNodes() << endl;
//    cout << "Max Wcc:" << (double)wcc->GetNodes()/(double)this->collaborative_network->GetNodes() << endl;
}

void CollabrativeNet::degree_distribution(string dir)
{
    TIntPrV deg;
    TSnap::GetDegCnt(this->collaborative_graph, deg);
    ofstream fout((dir+"degree").c_str());
    if(!fout)
    {
        cerr << "Cannot open file!" << dir << "degree" << endl;
        return;
    }
    for(int i=0; i!=deg.Len(); i++)
    {
        fout << deg[i].Val1 << "\t" << deg[i].Val2 << endl;
    }
    fout.close();
}

void CollabrativeNet::strength_distribution(string dir)
{
    TIntH StrengthToCntH;
    TIntPrV StrengthToCntV;
    for (TUNGraph::TNodeI NI = this->collaborative_graph->BegNI(); NI < this->collaborative_graph->EndNI(); NI++)
    {
        int strength=0;
        for (int index=0; index<NI.GetInDeg(); index++)
        {
            Edge e(NI.GetId(), NI.GetNbrNId(index));
            map<Edge, int>::iterator it = this->edge_weight.find(e);
            if(it!=edge_weight.end())
            {
                strength+=it->second;
            }
            else
            {
                cerr << "Error! No edge!" << NI.GetId() << "\t" << NI.GetNbrNId(index) << endl;
            }
        }
        StrengthToCntH.AddDat(strength)++; 
    }
    StrengthToCntV.Gen(StrengthToCntH.Len(), 0);
    for (int i = 0; i < StrengthToCntH.Len(); i++) 
    {
        StrengthToCntV.Add(TIntPr(StrengthToCntH.GetKey(i), StrengthToCntH[i])); 
    }
    StrengthToCntV.Sort();
    ofstream fout((dir+"strength").c_str());
    for(int index=0; index<StrengthToCntV.Len(); index++)
    {
        fout << StrengthToCntV[index].Val1 << "\t" << StrengthToCntV[index].Val2 << endl;
    }
    fout.close();
}

int main(int argc, char* argv[])
{
    CollabrativeNet net;
    net.read_to_construct_net(argv[1]);
    string dir(argv[2]);
    net.save_net(dir);
    net.strength_distribution(argv[2]);
//    cout << "Clustering coefficient:" << TSnap::GetClustCf(net.collaborative_graph) << endl;
//    net.get_diameter();
//   net.connected_component(argv[2]);
//    net.degree_distribution(argv[2]);
    return 0;
}
