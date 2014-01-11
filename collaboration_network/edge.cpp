#include "edge.h"

Edge::Edge(int node1, int node2)
{
    if(node1>node2)
    {
        this->larger_node=node1;
        this->smaller_node=node2;
    }
    else
    {
        this->larger_node=node2;
        this->smaller_node=node1;
    }
}

bool Edge::operator < (const Edge &e) const
{
    if(this->smaller_node==e.smaller_node)
    {
        return this->larger_node<e.larger_node;
    }
    else
    {
        return this->smaller_node<e.smaller_node;
    }
}

bool Edge::operator == (const Edge &e) const
{
    return this->larger_node == e.larger_node && this->smaller_node == e.smaller_node;
}
