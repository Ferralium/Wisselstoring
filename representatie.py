from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Rework data to useable format

class Mapdrawer():
    def __init__(self):
        """Initializes the mapdrawer, loads in the correct coordinates from the csv"""
        self.correctcoords = {}
        with open("data/StationsNationaal.csv") as f:
            next(f)
            for line in f:
                tempcoords = []
                templine = line.strip().split(',')
                tempcoords.append(templine[1])
                tempcoords.append(templine[2])
                self.correctcoords[templine[0]] = tempcoords
                

        self.connections = []
        with open('data/ConnectiesNationaal.csv') as c:
            next(c)
            for line in c:
                tempconnect = []
                templine = line.strip().split(',')
                tempconnect.append(templine[0])
                tempconnect.append(templine[1])
                self.connections.append(tempconnect)
            
    def print_to_image(self):
        # Miller cylindrical projection
        self.m = Basemap(projection = 'mill', llcrnrlat = 50.730, llcrnrlon = 3.279, urcrnrlat = 53.491, urcrnrlon = 7.295, resolution = 'h')
        self.m.drawcoastlines()
        self.m.drawcountries(linewidth=1)
        self.m.fillcontinents(color = 'coral', lake_color = 'aqua')

        # Drawing points on the map
        for station in self.correctcoords:
            xcord, ycord = float(self.correctcoords[station][0]), float(self.correctcoords[station][1])
            xpt, ypt = self.m(ycord, xcord)
            self.m.plot(xpt, ypt, '.', markersize = 10, color = 'b')

        plt.savefig('puntopkaart.png', bbox_inches='tight', pad_inches=0)

    def print_connections(self):
        """Prints all connections between the stations"""
        # Pakt lijst met connecties
        # Print tussen de stations de connecties
        for i in range(len(self.connections)):
            stat1 = []
            stat2 = []
            station1, station2 = self.connections[i][0], self.connections[i][1]
            x_coords1, y_coords1 = float(self.correctcoords[station1][0]), float(self.correctcoords[station1][1])
            xpt1, ypt1 = self.m(y_coords1, x_coords1)
            stat1.append(xpt1)
            stat2.append(ypt1)
            x_coords2, y_coords2 = float(self.correctcoords[station2][0]), float(self.correctcoords[station2][1])
            xpt2, ypt2 = self.m(y_coords2, x_coords2)
            stat1.append(xpt2)
            stat2.append(ypt2)
            self.m.plot(stat1, stat2, color='k', linewidth = 1)
        plt.savefig('lijnenopkaart.png', bbox_inches = 'tight', pad_inches = 0)

    def print_driven_routes(self, routes):
        """Takes the trainroutes and prints them on the map with colors for each different route"""
        pass
        

mappings = Mapdrawer()
mappings.print_to_image()
mappings.print_connections()


# TODO: Map routes via dictionary met als values de coordinaten en lijnen tussen de punten, op kleur per route
# TODO: Visualisaties van meest bezochte stations in histogram etc