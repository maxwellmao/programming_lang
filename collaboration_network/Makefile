include Makefile.config

MAIN = collaborative_network
$(MAIN): $(MAIN).cpp Snap.o edge.o
	$(CC) -o $(MAIN) $(MAIN).h $(MAIN).cpp edge.o Snap.o -I$(CGLIB) $(LDFLAGS) $(LIBS)

edge.o: edge.h edge.cpp
	$(CC) -c edge.h edge.cpp

#Snap.o: *.h *.cpp $(CGLIB)/*.h $(CGLIB)/*.cpp
#	$(CC) -c $(CXXFLAGS) $(CSNAP)/Snap.cpp -I$(CGLIB)
