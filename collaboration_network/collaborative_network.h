#include <stdio.h>
#include <stdlib.h>
#include <map>
#include <string>
#include <set>
#include "edge.h"
#include "../tools/Snap-2.1/snap-core/Snap.h"

class CollabrativeNet
{
public:
    PUNGraph collaborative_graph;
    std::map<Edge, int> edge_weight;
    std::set<int> node_set;
    CollabrativeNet()
    {
        this->collaborative_graph=TUNGraph::New();
    }
    void read_to_construct_net(std::string file_path);
    void save_net(std::string dir);
    void degree_distribution(std::string dir);
    void strength_distribution(std::string dir);
    void connected_component(std::string dir);
    void get_diameter();
};
