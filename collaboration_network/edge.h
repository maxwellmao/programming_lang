class Edge
{
public:
    Edge(int node1, int node2);
    bool operator < (const Edge &e) const;
    
    bool operator == (const Edge &e) const;
    
    int larger_node;
    int smaller_node;
};
