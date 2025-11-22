#include <iostream>
#include <sstream>
#include <vector>
#include <random>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <girgs/Generator.h>
#include <boost/graph/adjacency_list.hpp>

using namespace std;
using namespace girgs;


typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS	
		>					graph;
typedef boost::graph_traits<graph>::vertex_descriptor		vertex_desc;		
typedef boost::graph_traits<graph>::adjacency_iterator adj_it;		
typedef boost::graph_traits<graph>::edge_iterator edge_it;

string coloringMethod ="";

vector<int> generate_colors_random(int n, int seed) {
    coloringMethod = "rand";
    std::mt19937 rng(seed); 
    std::uniform_int_distribution<int> dist(0, 1); 
    
    std::vector<int> colors;
    for (int i = 0; i < n; ++i) {
        colors.push_back(dist(rng));
    }
    return colors;
}


vector<int> generate_colors_heavy(int n, const std::vector<double>& weights) {
    coloringMethod = "heavy";
    std::vector<int> colors;
    for (int i = 0; i < n; ++i) {
        if(weights[i]*weights[i] > n){
            colors.push_back(0);
        }else{
            colors.push_back(1);
        }
    }
    return colors;
}

vector<int> generate_colors_location(int n, int seed, double radius, const std::vector<std::vector<double>>& pos) {
    coloringMethod = "loc";
    std::mt19937 rng(seed); 
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    // double x = dist(rng);
    // double y = dist(rng);

    double x = 0.5;
    double y = 0.5;

    std::vector<int> colors;
    for (int i = 0; i < n; ++i) {

        if((abs(pos[i][0]-x)<radius || 1-abs(pos[i][0]-x)<radius) && (abs(pos[i][1]-y)<radius || 1-abs(pos[i][1]-y)<radius) ){
            colors.push_back(0);
        }else{
            colors.push_back(1);
        }
    }
    return colors;
}

vector<int> generate_colors_strip(int n, const std::vector<std::vector<double>>& pos) {
    coloringMethod = "strip";

    std::vector<int> colors;
    for (int i = 0; i < n; ++i) {

        if(pos[i][0]<0.5){
            colors.push_back(0);
        }else{
            colors.push_back(1);
        }
    }
    return colors;
}

vector<int> generate_colors_circ(int n, double radius, const std::vector<std::vector<double>>& pos) {
    coloringMethod = "circ";
    double x = 0.5;
    double y = 0.5;

    std::vector<int> colors;
    for (int i = 0; i < n; ++i) {

        if((pos[i][0]-x)*(pos[i][0]-x) + (pos[i][1]-y)*(pos[i][1]-y) <radius*radius){
            colors.push_back(0);
        }else{
            colors.push_back(1);
        }
    }
    return colors;
}


void draw_graph(string filename){
    std::string command = "python3.11 graphDrawing.py " +  filename;
    system(command.c_str());
}

void save_graph_to_file(const graph& g, const std::vector<std::vector<double>>& pos, const std::vector<double>& weights, const std::vector<int>& colors,
                    const std::vector<int>& neighbour_col, double tau, double alpha, int seed, int iter, bool colorless) {

    auto num_vertices = boost::num_vertices(g);
    auto num_edges = boost::num_edges(g);

    auto foldername1 = [&]() {
        std::ostringstream oss;
        oss << "n=" << num_vertices  << "_tau=" << to_string(tau);
        return oss.str();
    }();
    auto foldername2 = [&]() {
        std::ostringstream oss;
        oss << "a=" << to_string(alpha);
        return oss.str();
    }();
    auto foldername3= [&]() {
        std::ostringstream oss;
        oss << "col=" << coloringMethod;
        return oss.str();
    }();

    auto foldername4 = [&]() {
        std::ostringstream oss;
        oss << "seed=" << seed;
        return oss.str();
    }();
    auto base_path = "graph_data/" + foldername1 + "/" + foldername2 + "/" + foldername3 + "/" + foldername4;

    filesystem::create_directories(base_path);


    auto filename = "iteration=" + to_string(iter) + ".txt";

    auto file_path = base_path + "/" + filename;

    std::ofstream file(file_path);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file for writing.\n";
        return;
    }
    // Write the first line: number of vertices, edges, timestep, seed
    file << num_vertices << " " << num_edges << " " << tau << " " << alpha << " " << seed << " " << iter << " " << int(colorless) << "\n";
    
    // Write vertex data
    for (int i=0; i< num_vertices; i++) {
        file << i << " " 
             << pos[i][0] << " " 
             << pos[i][1] << " " 
             << weights[i] << " " 
             << colors[i] << " "
             << neighbour_col[i] << " "
             << degree(i, g) <<"\n";
    }

    // Write edge data
    graph::edge_iterator ei, ei_end;
    for (boost::tie(ei, ei_end) = boost::edges(g); ei != ei_end; ++ei) {
        file << boost::source(*ei, g) << " " << boost::target(*ei, g) << "\n";
    }

    // Close the file
    file.close();
    std::cout << "Graph data saved to " << file_path << "\n";
    draw_graph(file_path);
}

int single_vertex_all_neighbours(graph& g, const std::vector<std::vector<double>>& pos, const std::vector<double>& weights, 
                                std::vector<int>& col, std::vector<int>& neighbour_col, std::vector<int>& iterations, 
                                double tau, double alpha, int aseed) {
    std::mt19937 rng(aseed); 
    std::uniform_int_distribution<int> vertex_dist(0, boost::num_vertices(g) - 1);



    

    set<int> flipable;
    for(int j=0; j<neighbour_col.size(); j++){
        if((neighbour_col[j]<0 && col[j] == 1) || (neighbour_col[j]>0 && col[j] == 0)){
            flipable.insert(j);
        }
    }

    int iter = 0;
    
    //save_graph_to_file(g, pos, weights, col,  neighbour_col, tau, alpha, aseed-4, iter, true);
    //save_graph_to_file(g, pos, weights, col,  neighbour_col, tau, alpha, aseed-4, iter, false);
    

    while(flipable.size()!=0){
        //Draw new vertices until one 
        int v = vertex_dist(rng);


        if(neighbour_col[v]==0 || (neighbour_col[v]<0 && col[v] == 0) || (neighbour_col[v]>0 && col[v] == 1) ){
            //continue;
        }else{
            iter+=1;
            int change = abs(col[v]-1) -col[v];
            adj_it neighbor_start, neighbor_end;
            std::tie(neighbor_start, neighbor_end) = boost::adjacent_vertices(v, g);
            std::vector<int> neighbors(neighbor_start, neighbor_end);
            
            for(int neighbour : neighbors){
                
                bool wasFlip = false;
                if((neighbour_col[neighbour]<0 && col[neighbour] == 1) || (neighbour_col[neighbour]>0 && col[neighbour] == 0)){
                    wasFlip=true;
                }

                neighbour_col[neighbour]+=2*change;

                if((neighbour_col[neighbour]<0 && col[neighbour] == 1) || (neighbour_col[neighbour]>0 && col[neighbour] == 0)){
                    flipable.insert(neighbour);
                }else if(wasFlip){
                    flipable.erase(neighbour);
                }
            }

            col[v]+=change;

            flipable.erase(v);

            //cout << flipable.size() << endl;
            if (std::find(iterations.begin(), iterations.end(), iter) != iterations.end()) {
                //save_graph_to_file(g, pos, weights, col,  neighbour_col, tau, alpha, aseed-4, iter, false);
            }
        }

        
        
    }
    save_graph_to_file(g, pos, weights, col, neighbour_col, tau, alpha, aseed-4, iter, false);




    int count =0;
    for(int j=0; j<col.size(); j++){
        if(col[j]==0){
            count+=1;
        }
        
    }
    //cout << "No changes are possible after iteration " << iter << ". Program terminates." << endl;
    return count;
}


void all_vertex_all_neighbours(graph& g, const std::vector<std::vector<double>>& pos, const std::vector<double>& weights, 
                                std::vector<int>& col, std::vector<int>& neighbour_col, std::vector<int>& iterations, 
                                double tau, double alpha, int aseed) {
    std::mt19937 rng(aseed); 
    std::uniform_int_distribution<int> vertex_dist(0, boost::num_vertices(g) - 1);


    set<int> flipable;
    for(int j=0; j<neighbour_col.size(); j++){
        if((neighbour_col[j]<0 && col[j] == 1) || (neighbour_col[j]>0 && col[j] == 0)){
            flipable.insert(j);
        }
    }

    int iter = 0;
    
    save_graph_to_file(g, pos, weights, col,  neighbour_col, tau, alpha, aseed-4, iter, false);
    

    set<int> prev_flipable1, prev_flipable2;

    while(flipable.size()!=0){
        iter+=1;
        prev_flipable2 = prev_flipable1;
        prev_flipable1 = flipable;

        for (int v : flipable){
            int change = abs(col[v]-1) -col[v];
            adj_it neighbor_start, neighbor_end;
            std::tie(neighbor_start, neighbor_end) = boost::adjacent_vertices(v, g);
            std::vector<int> neighbors(neighbor_start, neighbor_end);
            
            for(int neighbour : neighbors){
                
                bool wasFlip = false;
                if((neighbour_col[neighbour]<0 && col[neighbour] == 1) || (neighbour_col[neighbour]>0 && col[neighbour] == 0)){
                    wasFlip=true;
                }

                neighbour_col[neighbour]+=2*change;
            }

            col[v]+=change;
        }


        flipable.clear();
        for(int j=0; j<neighbour_col.size(); j++){
            if((neighbour_col[j]<0 && col[j] == 1) || (neighbour_col[j]>0 && col[j] == 0)){
                flipable.insert(j);
            }
        }
        if (flipable == prev_flipable2) {
            cout << "Cycle of length 2 detected at iteration " << iter << ". Terminating." << endl;
            break;
        }

        if (std::find(iterations.begin(), iterations.end(), iter) != iterations.end()) {
                save_graph_to_file(g, pos, weights, col, neighbour_col, tau, alpha, aseed-4, iter, false);
        }
        

        
        
    }
    save_graph_to_file(g, pos, weights, col, neighbour_col, tau, alpha, aseed-4, iter, false);
    cout << "No changes are possible after iteration " << iter << ". Program terminates." << endl;

}





int main()
{
    int n = 10000;
    
    vector<int> iterations = {};
    vector<double> taus = {2.5};
    for(double tau : taus){
    vector<int> survived;
    for(int j=0; j< 1; j++){
    std::vector<double> values = {1000000};
    for (double a : values){
    for(int k=31; k<=32; k++){
        
        survived.push_back(0);
        cout << tau << " Iteration " << k << endl;
    for(int i=99; i<100; i++){
        
        int dim = 2;
        double alpha = a;
        double s = k;
        s = s/100;
        //int deg = 3;
        //1804289383
        auto time_now = std::chrono::system_clock::now().time_since_epoch().count();
        int pseed = abs(static_cast<int>(time_now & 0xFFFFFFFF));
        //pseed =229735739;
        //cout << "Base Randomness " << pseed << endl;

        int wseed = pseed+1;
        int sseed = wseed+1;
        int cseed = sseed+1;
        int aseed = cseed+1;


        auto pos = generatePositions(n, dim, pseed);
        //cout << "pos done" << endl;
        
        auto weights = generateWeights(n, tau, wseed);
        
        //Scale weights such that average degree aligns
        auto average_deg = pow(2, dim) * pow(tau-1, 2) / pow(tau-2, 2);
        scaleWeights(weights, average_deg, dim, alpha);

        //cout << "weights done" << endl;
        /*for(int i=0; i<n; i++){
            cout  << pos[i][0] << ", "<< pos[i][1] << ", " << weights[i] << endl;
        }*/
        //cout << endl;
        //auto s = 
        auto edges = generateEdges(weights, pos, alpha, sseed);
        
        //return 0; 
        graph g(n);
        for(auto e : edges){
            boost::add_edge(e.first, e.second, g); 
        }
        //cout << "Edge count " << edges.size() << endl;

        vector<int> col;
        switch(j){
            case 0: col = generate_colors_random(n, cseed); break;
            case 1: col = generate_colors_circ(n, 0.23, pos); break;
            case 2: col = generate_colors_location(n, cseed, s, pos); break;
        }
        vector<int>  neighbour_col(boost::num_vertices(g), 0);
        for(int v=0; v < boost::num_vertices(g); v++){
            adj_it neighbor_start, neighbor_end;
            std::tie(neighbor_start, neighbor_end) = boost::adjacent_vertices(v, g);
            std::vector<int> neighbors(neighbor_start, neighbor_end);
            if (neighbors.empty()) {
                continue; 
            }
            int count0 = 0, count1 = 0;
            for (int neighbor : neighbors) {
                if (col[neighbor] == 0) {
                    neighbour_col[v]--;
                } else if (col[neighbor] == 1) {
                    neighbour_col[v]++;
                }
            }
        }

        int count = single_vertex_all_neighbours(g, pos, weights, col, neighbour_col, iterations, tau, alpha, aseed);
        if(count>3*n*s*s){
            survived[survived.size()-1]+=1;
        }
    }
    cout << survived[survived.size()-1] << "/100"  << endl;
    }

    }
    }
    string base_path = "graph_survival/";

    filesystem::create_directories(base_path);


    auto filename = "survivalTau=" + to_string(tau) +".txt";

    auto file_path = base_path + filename;

    std::ofstream file(file_path);
    for (int i=0; i< survived.size(); i++) {
        file << i+1 << ": " 
             << survived[i] <<"/100\n";
    }

    file.close();
}
}
