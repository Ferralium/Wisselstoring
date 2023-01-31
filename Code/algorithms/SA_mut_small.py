import random
from station import Station
# voor deze hillclimber wordt er een greedy algoritme gebruikt, dus dat is
# een slim start station en slimme moves!


class SimulatedAnnealing:
    """ Class that creates a simulated annealing algorithm to solve the case. """

    def __init__(self, start_heuristic, move_heuristic):
        """ Deze klas is de representatie van een hill climber algoritme om het Rail NL probleem op te lossen """
        self.start_heuristic = start_heuristic
        self.move_heuristic = move_heuristic


    def starting_station(self, station_dictionary, statnames):
        """"Picks a starting station with the least connections """
        return self.start_heuristic(station_dictionary)


    def quality_calc(self, fraction: float, list_of_numbers) -> None:

        # als de trein langer rijdt dan 180 minuten, mag het niet worden ingevoerd want de oplossing is ongeldig
        # zet dan de K op 0, dan is de kans op invoering extreem klein
        # if list_of_numbers[0] > 180:
        #     self.K = 0
        #     return self.K

        T: int = list_of_numbers[1]
        Min: int = list_of_numbers[0]
        self.K: float = fraction*10000 - (T*100 + Min)
        self.quality = f'Quality: {self.K} = {fraction}*10000 - ({T}*100 + {Min})'
        print(self.quality)

        return self.K


    def move(self, current_station, train_stations, stations_dictionary):
        """ Moves to a smart next station """
        time: float = 0
        train_stations.append(current_station)

        if current_station == None:
            return train_stations, time

        # one loop is a move from station A to station B
        while True:
            next_station: Station = self.move_heuristic(current_station, train_stations, stations_dictionary)
            if next_station is None:
                return train_stations, time

            # keeps track of the time the trajectory takes
            all_time: float = time + current_station.connections.get(str(next_station))

            # stops if time is more than 3 hours
            if all_time > 180:
                return train_stations, time
            else:
                time = all_time

            # sets connections to and from to visited
            current_station.stationvisit(str(next_station))
            next_station.stationvisit(str(current_station))

            current_station = next_station
            train_stations.append(current_station)


    def make_or_break_change(self, quality_old: float, quality_2: float, train_dictionary, train_dictionary_2, change_in_time, list_of_numbers, total_time_each_train, chosen_one):
        """ Function that makes or breaks the mutation """

        # Quality old was de kwaliteit van de vorige loop. Als Quality_2 beter is of de kans het zegt,
        # veranderen we Quality_old in Quality_2. Anders blijft het hetzelfde
        # Quality_old returnen we vervolgens.

        mutated: Bool = True
        delta = quality_2 - quality_old
        print(f'delta: {delta}')

        if delta >= 0:

            # voer nieuwe state sowieso in
            train_dictionary = train_dictionary_2
            quality_old = quality_2
            # voer de change in time ook in in de dictionary v
            total_time_each_train[chosen_one[0]] += change_in_time
            print("mutation accepted, verbetering of gelijk")
            print(f'the train has now ridden {total_time_each_train[chosen_one[0]]} min')


        else:

            chance = 2**delta
            print(f'chance to be accepted: {chance}')

            # als kans groter dan 1 is, voer het in
            if chance >= 1:

                # voer nieuwe state in
                train_dictionary = train_dictionary_2
                quality_old = quality_2
                total_time_each_train[chosen_one[0]] += change_in_time
                print("mutation accepted, want dat moest via de kans")

            # als kans tussen nul en 1 is, maak een gok of je het moet invoeren
            elif chance > 0 and chance < 1:

                # afhankelijk van de kans, voer hem in:
                guess = random.uniform(0, 1)

                print(f'guess: {guess}')

                if guess < chance:

                    train_dictionary = train_dictionary_2
                    quality_old = quality_2
                    total_time_each_train[chosen_one[0]] += change_in_time
                    print(f'the train has now ridden {total_time_each_train[chosen_one[0]]} min')
                    print("mutation accepted, chance says so")

                else:
                    print("mutation not accepted, chance too low")
                    # voer de change in time terug
                    list_of_numbers[0] -= change_in_time

                    # zet changed op False
                    mutated = False

            # kans is kleiner dan nul, dus voer je het niet in
            else:
                print("mutation not accepted, kans kleiner dan 0")
                # voer de change in time terug
                list_of_numbers[0] -= change_in_time

                mutated = False

        delta = 0
        short_tuple = [train_dictionary, quality_old]
        return short_tuple, mutated


    def reset_visiting_status(self, switching_stations, stations_library):
        """ Function that resets the visited-status of connections, in case a mutation is not persued after all. """

        # zet de nieuwe route die niet doorgaat op unvisited, maar alleen als er maar 1 visit is
        print("     reset visiting status")
        print()
        string_knooppunt = str(switching_stations[1])
        string_new = str(switching_stations[2])

        if switching_stations[2].check_number_visits(string_knooppunt) <= 1:
            switching_stations[2].station_unvisit(str(switching_stations[1]))
            switching_stations[1].station_unvisit(str(switching_stations[2]))

        else:
            switching_stations[2].one_less_visit(str(switching_stations[1]))
            switching_stations[1].one_less_visit(str(switching_stations[2]))

        switching_stations[0].stationvisit(str(switching_stations[1]))
        switching_stations[1].stationvisit(str(switching_stations[0]))


    def stations_to_be_switched(self, train_dictionary_2, stations_library, total_time_each_train):
        """ Functie die willekeurig uitkiest welke connecties worden gemuteerd. """

        # kies eerst willekeurig welke trein en welk uiteinde wordt verlegt.
        pick_train = random.choice(list(train_dictionary_2.keys()))
        print(f'trein die gemuteerd word: {pick_train}')
        front_or_back = random.randint(1,2)

        chosen_one = [pick_train, front_or_back]

    	# zoek deze op in de train_dictionary
        if front_or_back == 1:
            print("change front of train")

            # pak de lijst van de stations
            list_of_stations_for_mutation = train_dictionary_2[pick_train]
            print(f'wat gaat er mis met het oude station? {list_of_stations_for_mutation}')
            chosen_one.append(list_of_stations_for_mutation)
        	# ga naar het 2e station in de lijst
            station_for_mutation = list_of_stations_for_mutation[1]

            print(f'dit is het knooppuntstation: {station_for_mutation}')
        	# print(type(station_for_mutation))
            old_station_for_mutation = list_of_stations_for_mutation[0]
            print(f'oud station: {old_station_for_mutation}')

            connections_for_mutation = station_for_mutation.connections
            print(f'dit zijn de connecties: {connections_for_mutation}')

        else:
            print("change back of train")

            list_of_stations_for_mutation = train_dictionary_2[pick_train]
            chosen_one.append(list_of_stations_for_mutation)
            length_traject = len(list_of_stations_for_mutation)

        	# ga naar het 2e station in de lijst
            station_for_mutation = list_of_stations_for_mutation[length_traject - 2]

            print(f'dit is het knooppuntstation: {station_for_mutation}')

            old_station_for_mutation = list_of_stations_for_mutation[length_traject - 1]
            print(list_of_stations_for_mutation)

            print(f'oud station: {old_station_for_mutation}')

            connections_for_mutation = station_for_mutation.connections
            print(f'dit zijn de connecties: {connections_for_mutation}')


        #### voorwaarde lengte trein!
        new_station_for_mutation: Station = random.choice(list(connections_for_mutation.keys()))
        new_station_for_mutation = stations_library[new_station_for_mutation]
        # new_station = str(new_station_for_mutation)
        knooppunt = str(station_for_mutation)

        total_time_train = total_time_each_train[pick_train]
        # nu kijken wat de tijd is om daar te komen:
        time_new_connection = new_station_for_mutation.connections[knooppunt]
        time_old_connection = old_station_for_mutation.connections[knooppunt]
        time_difference = time_new_connection - time_old_connection
        time_spare = 180 - total_time_train

        while time_spare < time_difference:

            new_station_for_mutation: Station = random.choice(list(connections_for_mutation.keys()))

            # maak er een station object van:
            new_station_for_mutation = stations_library[new_station_for_mutation]


            # nu kijken wat de tijd is om daar te komen:
            time_new_connection = new_station_for_mutation.connections[knooppunt]
            time_old_connection = old_station_for_mutation.connections[knooppunt]
            time_difference = time_new_connection - time_old_connection
            time_spare = 180 - total_time_train

            print(f'nieuw station: {new_station_for_mutation}')

        # return uiteindelijk de stations
        switching_stations = [old_station_for_mutation, station_for_mutation, new_station_for_mutation]
        return switching_stations, chosen_one


    def mutation_small(self, train_dictionary_2, train_dictionary, switching_stations, chosen_one, stations_library):
        """ Functie die gekregen stations omwisselt, en daarbij de tijd veranderd, en de visited routes veranderd. """

        # Zet de nieuwe route op visited
        switching_stations[2].stationvisit(str(switching_stations[1]))
        switching_stations[1].stationvisit(str(switching_stations[2]))

        # unvisit de oude route (als daar maar 1 visit staat)
        string_knooppunt = str(switching_stations[1])
        string_oud = str(switching_stations[0])

        if switching_stations[0].check_number_visits(string_knooppunt) <= 1:
            switching_stations[0].station_unvisit(str(switching_stations[1]))
            switching_stations[1].station_unvisit(str(switching_stations[0]))

        else:
            switching_stations[0].one_less_visit(str(switching_stations[1]))
            switching_stations[1].one_less_visit(str(switching_stations[0]))


        # verander het in de train_dictionary
        if chosen_one[1] == 1:

            list_of_stations_for_mutation = train_dictionary_2[chosen_one[0]]
            list_of_stations_for_mutation[0] = switching_stations[2]
            train_dictionary[chosen_one[0]] = list_of_stations_for_mutation

        else:
            list_of_stations_for_mutation = train_dictionary_2[chosen_one[0]]
            length_traject = len(list_of_stations_for_mutation)
            list_of_stations_for_mutation[length_traject - 1] = switching_stations[2]
            train_dictionary[chosen_one[0]] = list_of_stations_for_mutation

        # # verander ook de tijd:
        change_in_time: float = 0
        old_station = switching_stations[0]
        new_station = switching_stations[2]

        temporary_name = switching_stations[1].connections[str(old_station)]
        print(f'min oude route {temporary_name}')
        change_in_time -= temporary_name
        # change_in_time -= station_for_mutation.connections[old_station]
        temporary_name_2 = switching_stations[1].connections[str(new_station)]
        print(f'min nieuwe route {temporary_name_2}')
        change_in_time += temporary_name_2
        print(f'change in time: {change_in_time}')

        return change_in_time