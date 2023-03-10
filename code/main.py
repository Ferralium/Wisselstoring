"""
    railsolver.py
    Door:
        Chiara Schut - 14676869
        Berber Siersma - 14472295
        Jeroen Steenhof - 12709425
    Minor Programmeren - Algoritmen en Heuristieken
    Attempts to solve heuristic problem with train stations.
"""

import csv
import copy
import time
import random
from algorithm import Algorithm
from station import Station
import pandas as pd
from typing import Any
from representatie import Mapdrawer, Gifgenerator
import sys

from algorithms.random_algo  import RandomAlgorithm
from algorithms.simulatedannealing import SimulatedAnnealing
from algorithms.GreedyAlgorithm import GreedyAlgorithm
from algorithms.heuristic_algorithm import HeuristicAlgorithm
from algorithms.dijkstra_algo import DijkstraAlgorithm
from heuristics.start_least_connections import least_connection_start_heuristic
from heuristics.start_most_connections import most_connection_start_heuristic
from heuristics.start_random import random_start_heuristic
from heuristics.start_7bridges import sevenbridges_start_heuristic
from heuristics.move_random import random_move_heuristic
from heuristics.move_visited_random import visited_random_move_heuristic
from heuristics.move_shortest import shortest_move_heuristic
from heuristics.move_shortest_preference import preference_shortest_move_heuristic


class Railsolver():
    """Main function to attempt to find the most optimal solution for RailNL"""

    # Initializes the stations dictionary for the railsolver
    def __init__(self, algorithm: Algorithm) -> None:
        self.stations = {}
        self.statnames = []
        self.load_stations()
        self.algo = algorithm

        # train number
        self.traincount: int = 1

    def load_stations(self) -> None:
        """Loads the stations with distances from the CSV.
           Also creates new stations for the connections if they are not already in the dict"""

        with open('../data/ConnectiesNationaal.csv') as f:
            # Skips the first line
            next(f)

            # For loop iterates over the lines in the csv and modifies them to usable format
            for line in f:
                templine: str = line
                templine = templine.strip().split(',')

                # Adds unique station names to list to select random point later
                for i in range(2):
                    if templine[i] not in self.statnames:
                        self.statnames.append(templine[i])

                # Checks if station already exists, if so adds connection
                if templine[0] in self.stations:
                    self.stations[templine[0]].add_station(templine[1], float(templine[2]))

                # If the station does not exist initializes the station and adds the connection
                elif templine[0] not in self.stations:
                    self.stations[templine[0]] = Station(templine[0])
                    self.stations[templine[0]].add_station(templine[1], float(templine[2]))

                # Checks whether the connection already exists in the stations and adds it if this is not the case
                if templine[1] not in self.stations:
                    self.stations[templine[1]] = Station(templine[1])
                    self.stations[templine[1]].add_station(templine[0], float(templine[2]))

                elif templine[1] in self.stations:
                    self.stations[templine[1]].add_station(templine[0], float(templine[2]))


    def quality_calc(self, fraction: float, list_of_numbers) -> None:
        """Calculates the quality of the driven routes"""
        T: int = list_of_numbers[1]
        Min: int = list_of_numbers[0]
        self.K: float = fraction*10000 - (T*100 + Min)
        self.quality = f'Quality: {self.K} = {fraction}*1000 - ({T}*100 + {Min})'
        print(self.quality)


    def fraction_calc(self) -> float:
        """Function calculates percentage of used connections"""
        connected = 0
        total = 0

        # counts the number of used connections
        for station_name in self.stations:
            temporary_station = self.stations[station_name]
            number_of_connections = len(temporary_station.connections)
            total += number_of_connections

            for connecties in temporary_station.connection_visited:
                if temporary_station.connection_visited[connecties] == True:
                    connected += 1

    	# calculates fraction used conenctions of all conenctions
        fraction: float = round(connected / total, 2)

        return fraction


    def table_of_trains(self, train_number, list_of_stations, time, train_dictionary):
        """Function that keeps track of all the train routes that have been made"""

        # Adds trains to the dictionary in the appropriate place
        train_dictionary[train_number] = list_of_stations


    def take_a_ride(self):
        """ Function that keeps the order of everything that must be done for the algorithm"""
        total_time: int = 0
        number_of_routes: int = 0
        total_time_each_train = {}

        for route in range(20):

            # Name the train
            train_number: str = "train_" + str(route + 1)

            # Make an emtpy list for the stations
            train_stations: list[Station] = []

            current_station: Station = self.algo.starting_station(self.stations, self.statnames)
            list_of_stations_and_time: tuple[list[Station], int] = self.algo.move(current_station, train_stations, self.stations)
            total_time_each_train[train_number] = list_of_stations_and_time[1]
            check_station = list_of_stations_and_time[0]

            # Checks if there are no more stations left to stop the loop
            if check_station == [None]:
                total_time_each_train.popitem()
                break
            else:
                # Adds the route to table of trains
                wisselstoring.table_of_trains(train_number, *list_of_stations_and_time, train_dictionary)
                time_trajectory: int = list_of_stations_and_time[1]

                # Add total time of all trajectories
                total_time += time_trajectory
                number_of_routes += 1

        list_of_numbers: list[int] = [total_time, number_of_routes]

        return list_of_numbers, total_time_each_train


    def loop_simulated_annealing(self, train_dictionary, best_qualities_checkpoints):
        """Loop controlling the simmulated annealing process"""

        # Initialize the train routes
        list_of_numbers, total_time_each_train = wisselstoring.take_a_ride()

        # Calculates fraction of the driven routes
        fraction: float = wisselstoring.fraction_calc()
        quality_old, quality_written_old = self.algo.quality_calc(fraction, list_of_numbers)
        print(quality_old)


        # Loops the mutations
        for i in range(20000):

            train_dictionary_2 = copy.deepcopy(train_dictionary)
            stations_library = wisselstoring.stations
            switching_stations, chosen_one = self.algo.stations_to_be_switched(train_dictionary_2, stations_library, total_time_each_train)
            change_in_time, train_dictionary_2 = self.algo.mutation_small(train_dictionary_2, train_dictionary, switching_stations, chosen_one, stations_library)
            list_of_numbers[0] += change_in_time


            fraction_new: float = self.algo.fraction_calc(stations_library)
            quality_2, quality_written_2 = self.algo.quality_calc(fraction_new, list_of_numbers)

            # If the list of numbers is below 1551 and the fraction is above 0.99, the whole run should be aborted as something is going wrong
            if list_of_numbers[0] < 1552 and fraction_new > 0.99:
                    print("         There is a bug ")
                    break

            # Compare these, if it is better or the chance of change requires it change the route
            short_tuple, mutated = self.algo.make_or_break_change(quality_old, quality_2, train_dictionary, train_dictionary_2, change_in_time, total_time_each_train, chosen_one)

            train_dictionary = short_tuple[0]
            quality_old = short_tuple[1]

            if mutated == False:
                self.algo.reset_visiting_status(switching_stations, stations_library)
                list_of_numbers[0] -= change_in_time

            if mutated == True:
                fraction = fraction_new
                quality_written_old = quality_written_2

            # Adds checkpoints: Stops if not better than the best solution
            if i == 20:
                print()
                print("         CHECKPOINT 1 (after 20 mutations)")
                print()

                print(f'quality old: {quality_old}, checkpoint_quality: {best_qualities_checkpoints[0]}')

                if quality_old >= best_qualities_checkpoints[0]:

                    best_qualities_checkpoints[0] = quality_old
                    print("checkpoint passed succesfully")

                else:
                    print("checkpoint failed, abort")
                    return quality_old, quality_written_old, best_qualities_checkpoints

            if i == 100:
                print()
                print("         CHECKPOINT 2 (after 100 mutations)")
                print()

                print(f'quality old: {quality_old}, checkpoint_quality: {best_qualities_checkpoints[1]}')

                if quality_old >= best_qualities_checkpoints[1]:

                    best_qualities_checkpoints[1] = quality_old
                    print("checkpoint passed succesfully")

                else:
                    print("checkpoint failed, abort")
                    return quality_old, quality_written_old, best_qualities_checkpoints

            if i == 250:
                print()
                print("         CHECKPOINT 3 (after 250 mutations)")
                print()

                print(f'quality old: {quality_old}, checkpoint_quality: {best_qualities_checkpoints[2]}')

                if quality_old >= best_qualities_checkpoints[2]:

                    best_qualities_checkpoints[2] = quality_old
                    print("checkpoint passed succesfully")

                else:
                    print("checkpoint failed, abort")
                    return quality_old, quality_written_old, best_qualities_checkpoints

            if i == 10000:
                print()
                print("         CHECKPOINT 4 (after 10k mutations)")
                print()

                print(f'quality old: {quality_old}, checkpoint_quality: {best_qualities_checkpoints[3]}')

                if quality_old >= best_qualities_checkpoints[3]:

                    best_qualities_checkpoints[3] = quality_old
                    print("checkpoint passed succesfully")

                else:
                    print("checkpoint failed, abort")
                    return quality_old, quality_written_old, best_qualities_checkpoints


        # Print which stations have been visited
        print("welke connecties zijn bezocht? ")
        for station_name in stations_library:

            temporary_station = stations_library[station_name]

            for connecties in temporary_station.connection_visited:
                print(temporary_station, connecties, temporary_station.connection_visited[connecties])

        return quality_old, quality_written_old, best_qualities_checkpoints


    def visualise(self, routes):
        """Uses the map visualisation module to create multiple images of the state of the map."""
        # Initializes the map
        self.drawmod = Mapdrawer()

        # Prints all stations on a map of the Netherlands
        self.drawmod.print_to_image()

        # Prints all connections between stations on a map of the Netherlands
        self.drawmod.print_connections()

        # Prints the driven routes with unique colors
        self.drawmod.print_driven_routes(routes)

        # Initializes gif generator
        self.gifmod = Gifgenerator()

    def final_csv(self, solution, bestscore):
       """Write score to CSV file"""
       header = ['train', 'stations']
       score = ['score']

       file1 = open(f'../results/output.csv', 'w')
       csvwriter = csv.writer(file1)
       csvwriter.writerow(header)
       for key, value in solution.items():
           csvwriter.writerow([key, value])
       score.append(bestscore)
       csvwriter.writerow(score)
       file1.close()




def select_heuristic(start_heurselect, move_heurselect):
    """Selects the heuristics with which the algorithms will perform their functions"""
    start_heuristic = None
    if start_heurselect == 1:
        start_heuristic = random_start_heuristic
    elif start_heurselect == 2:
        start_heuristic = least_connection_start_heuristic
    elif start_heurselect == 3:
        start_heuristic = most_connection_start_heuristic
    elif start_heurselect == 4:
        start_heuristic = sevenbridges_start_heuristic

    if move_heurselect == 1:
        return start_heuristic, random_move_heuristic
    elif move_heurselect == 2:
        return start_heuristic, visited_random_move_heuristic
    elif move_heurselect == 3:
        return start_heuristic, shortest_move_heuristic
    elif move_heurselect == 4:
        return start_heuristic, preference_shortest_move_heuristic



if __name__ == '__main__':
    start_time = time.time()
    algoselect = 1
    start_heuristic = None
    move_heuristic = None

    best_solution = {}
    best_score = 0
    best_calc = ''
    mean_solution = 0
    num_of_runs = 1
    histoscore = []

    # Proper handling of command line arguments
    if len(sys.argv) > 1:
        if not sys.argv[1].isnumeric():
            print('Usage: python3 main.py (Optional) n')
            sys.exit()
        num_of_runs = int(sys.argv[1])
        if num_of_runs < 1:
            print('Usage: python3 main.py (Optional) n')
            print('Number of runs must be 1 or higher')
            sys.exit()

        # error if wrong number of command line arguments has been given
        if len(sys.argv) == 4 or len(sys.argv) > 5:
            print('Usage: python3 main.py (1 -> n) n (1 -> x) algorithm')
            sys.exit()

        # error if non numbers are provided in the command line
        if len(sys.argv) > 2:
            if not sys.argv[2].isnumeric():
                print('Usage: python3 main.py (1 -> n) n (1 -> x) algorithm')
                sys.exit()
            algoselect = int(sys.argv[2])

            # error if number given is not valid
            if algoselect < 1 or algoselect > 5:
                print('Usage: python3 main.py (1 -> n) n (1 -> x) algorithm')
                print('Algorithm must be between 1 and 8')
                sys.exit()

            # different files if algorithm 1 or 2 is chosen
            if algoselect == 1 or algoselect == 2:
                file1 = open(f'../results/resultsformula{algoselect}.txt', 'w')
                file1.close()
                file2 = open(f'../results/score{algoselect}.txt', 'w')
                file2.close()

            # different files are created if algorithm 3, 4 or 5 are chosen
            if algoselect == 3 or algoselect == 5 or algoselect == 4:
                if len(sys.argv) < 5 or not sys.argv[3].isnumeric() or not sys.argv[4].isnumeric():
                    print('Usage: python3 main.py (1 -> n) n (1 -> x) algorithm (1 -> x) start_heuristic move_heuristic')
                    sys.exit()
                start_heurselect = int(sys.argv[3])
                move_heurselect = int(sys.argv[4])
                if start_heurselect < 1 or start_heurselect > 4 or move_heurselect < 1 or move_heurselect > 4:
                    print('Usage: python3 main.py (1 -> n) n (1 -> x) algorithm (1 -> x) start_heuristic move_heuristic')
                    print('Heuristic must be between 1 and 4')
                    sys.exit()
                start_heuristic, move_heuristic = select_heuristic(start_heurselect, move_heurselect)

                # Clears the respective result files
                file1 = open(f'../results/resultsformula{algoselect}{start_heurselect}{move_heurselect}.txt', 'w')
                file1.close()
                file2 = open(f'../results/score{algoselect}{start_heurselect}{move_heurselect}.txt', 'w')
                file2.close()


    # Command-line selection of algorithms
    if algoselect == 1:
        algo = RandomAlgorithm()
    elif algoselect == 2:
        algo = GreedyAlgorithm()
    elif algoselect == 3:
        algo = HeuristicAlgorithm(start_heuristic, move_heuristic)
    elif algoselect == 4:
        algo = SimulatedAnnealing(start_heuristic, move_heuristic)
    elif algoselect == 5:
        algo = DijkstraAlgorithm(start_heuristic, move_heuristic)

    # Loop for running the correct algorithms, split by SA and the others
    if algoselect == 4:

        best_quality_20 = 0
        best_quality_100 = 0
        best_quality_250 = 0
        best_quality_10k = 0
        best_qualities_checkpoints = [best_quality_20, best_quality_100, best_quality_250, best_quality_10k]

        for i in range(num_of_runs):
            print("Nieuwe run")
            train_dictionary = {}

            wisselstoring = Railsolver(algo)
            print("simulated annealing")
            quality_old, quality_written_old, best_qualities_checkpoints = Railsolver(algo).loop_simulated_annealing(train_dictionary, best_qualities_checkpoints)
            mean_solution += quality_old

            if quality_old > best_score:
                best_score = quality_old
                best_solution = train_dictionary
                best_calc = quality_written_old

            # adds calculation and result to file
            results = open(f'../results/resultsformula{algoselect}{start_heurselect}{move_heurselect}.txt', 'a')
            results.write(f'{quality_written_old}')
            results.write('\n')
            results.close()

            # adds score to seperate file
            score = open(f'../results/score{algoselect}{start_heurselect}{move_heurselect}.txt', 'a')
            score.write(str(quality_old))
            score.write('\n')
            score.close()

            print("Einde run")

    else:
        for i in range(num_of_runs):
            wisselstoring = Railsolver(algo)

            # Create empty dictionary in which the train routes are saved
            train_dictionary = {}

            list_of_numbers, total_time_each_train = wisselstoring.take_a_ride()

            # bereken de fractie van de bereden routes
            fraction: float = wisselstoring.fraction_calc()
            wisselstoring.quality_calc(fraction, list_of_numbers)
            mean_solution += wisselstoring.K

            # If the score is better than the current best score replace the saved best solution
            if wisselstoring.K > best_score:
                best_score = wisselstoring.K
                best_solution = train_dictionary
                best_calc = wisselstoring.quality

            # Appends the results to result files
            if algoselect == 1 or algoselect == 2:
                results = open(f'../results/resultsformula{algoselect}.txt', 'a')
                results.write(f'{wisselstoring.quality}')
                results.write('\n')
                results.close()

                score = open(f'../results/score{algoselect}.txt', 'a')
                score.write(str(wisselstoring.K))
                score.write('\n')
                score.close()
            else:
                results = open(f'../results/resultsformula{algoselect}{start_heurselect}{move_heurselect}.txt', 'a')
                results.write(f'{wisselstoring.quality}')
                results.write('\n')
                results.close()

                score = open(f'../results/score{algoselect}{start_heurselect}{move_heurselect}.txt', 'a')
                score.write(str(wisselstoring.K))
                score.write('\n')
                score.close()

    wisselstoring.visualise(best_solution)
    wisselstoring.gifmod.map_to_gif()
    # wisselstoring.final_csv(best_solution, wisselstoring.K)

    print(f'Best solution found: {best_calc}')
    print(f'Average solution: {mean_solution / num_of_runs}')
    print(f'Runtime: {time.time() - start_time}')
    print(f'Best Solution: {best_solution}')
