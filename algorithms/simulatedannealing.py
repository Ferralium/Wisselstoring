import random
# voor deze hillclimber wordt er een greedy algoritme gebruikt, dus dat is
# een slim start station en slimme moves!


class SimulatedAnnealing:

    def __init__(self):
        """ Deze klas is de representatie van een hill climber algoritme om het Rail NL probleem op te lossen """
        pass


    def starting_station(self, station_dictionary, statnames):
        """"Picks a starting station with the least connections """

        first_number_connections = list(station_dictionary.values())[0]
        highest_unused_connections = first_number_connections.connection_count
        # highest_unused_connections = station_one.connection_count
        all_stations_true: int = 0

        for station in station_dictionary:
            check_connections: Station = station_dictionary.get(station)
            check_startingpoint: bool = all(station is True for station in check_connections.connection_visited.values())
            possible_current_station: Station = station_dictionary.get(str(check_connections))

            if check_startingpoint is True:
                all_stations_true += 1

            if check_connections.connection_count == 1:
                    if check_startingpoint is False:
                        current_station: Station = station_dictionary.get(str(possible_current_station))
                        break
            elif check_connections.connection_count != 1 or check_startingpoint == False:
                # possible_current_station = self.stations.get(str(check_connections))
                unused_connections: int = 0
                for connections in possible_current_station.connection_visited.values():
                    # print(connections)
                    if connections == False:
                        unused_connections += 1
                if unused_connections < highest_unused_connections and unused_connections != 0:
                    highest_unused_connections = unused_connections
                    current_station = station_dictionary.get(str(possible_current_station))

        if all_stations_true is len(station_dictionary):
            starting_point: str = random.choice(statnames)
            current_station = station_dictionary.get(starting_point)

        return current_station


    def quality_calc(self, fraction: float, list_of_numbers) -> None:
        T: int = list_of_numbers[1]
        Min: int = list_of_numbers[0]
        self.K: float = fraction*10000 - (T*100 + Min)
        self.quality = f'Quality: {self.K} = {fraction}*1000 - ({T}*100 + {Min})'
        print(self.quality)

        return self.K


    def move(self, current_station, train_stations, stations_dictionary):
        """ Moves to a smart next station """
        time = 0
        all_stations_true = 0

        # voeg de current station toe aan de lijst
        train_stations.append(current_station)
        print(current_station)


        while True:

            shortest_connection = 100
            print(f'hello {current_station.connection_visited}')

            check_stations: bool = all(station is True for station in current_station.connection_visited.values())

            if check_stations is True:
                for station in stations_dictionary:
                    # trein stopt als alle connecties zijn bereden
                #     check_connections = stations_dictionary.get(station)
                #     check_startingpoint: bool = all(station is True for station in check_connections.connection_visited.values())
                #     # print(check_startingpoint)
                #     if check_startingpoint is True:
                #         all_stations_true += 1
                # print(all_stations_true)
                # print(len(stations_dictionary))
                    if all_stations_true == len(stations_dictionary):
                        return train_stations, time
                    else:
                        for connections in current_station.connections:
                            check_connections = stations_dictionary.get(connections)
                            # print(check_connections)
                            for value in check_connections.connections.values():
                                if value < shortest_connection:
                                    shortest_connection = value
                                    # print(check_connections)
                                    next_station = stations_dictionary.get(connections)
            else:
                for connections in current_station.connections:
                    check_connections = stations_dictionary.get(connections)
                    # for possible_station in check_connections.connection_visited:
                    if current_station.connections[connections] < shortest_connection and current_station.connection_visited[connections] is False:
                    # if check_connections.connection_visited[possible_station] is False:
                        shortest_connection = current_station.connections[connections]
                        next_station = next_station = stations_dictionary.get(connections)
                            # print("v")
                            # print(shortest_connection)
                            # print(f' Current Station: {current_station}')
                # for connections in current_station.connections:
                #     check_connections = stations_dictionary.get(connections)
                #     print(check_connections)
                #     for value in check_connections.connections.values():
                #         if value < shortest_connection:
                #             shortest_connection = value
                #             # print(check_connections)
                #             next_station = stations_dictionary.get(connections)


            all_time: int = time + current_station.connections.get(str(next_station))
            # print(f'hi {all_time}')
            # print(train_stations, time)

            # stops if time is more than 3 hours
            if all_time > 180:
                print(f'hi {all_time}')
                print(f'this will be returned {time}')
                return train_stations, time
            else:
                time = time + current_station.connections.get(str(next_station))
                print(f'current {time}')

            print(f' Current Station: {current_station}')
            current_station.stationvisit(str(next_station))
            next_station.stationvisit(str(current_station))
            current_station = stations_dictionary.get(str(next_station))
            print(current_station.connection_visited)

            # voeg current_station toe aan de lijst
            train_stations.append(current_station)
            # print("treinstation toegevoegd")

            print(f' Next Station: {current_station}')
            print(time)
            print(" ")



    def make_or_break_change(self, quality: float, quality_2: float, train_dictionary, train_dictionary_2):
        """ Function that makes or breaks the mutation """

        delta = quality_2 - quality
        print(f'delta: {delta}')

        if delta > 1:

            # voer nieuwe state sowieso in
            train_dictionary = train_dictionary_2
            quality = quality_2

        else:

            chance = 2**delta


            if chance >= 1:

                # voer nieuwe state in
                train_dictionary = train_dictionary_2
                quality = quality_2

            if chance > 0 and chance < 1:

                # afhankelijk van de kans, voer hem in:
                guess = random.uniform(0, 1)

                print(f'guess: {guess}')

                if guess < chance:

                    train_dictionary = train_dictionary_2
                    quality = quality_2


        short_tuple = [train_dictionary, quality]
        return short_tuple

    # def mutation(self):
    #     """ Functie die een kleine mutatie maakt op de huidige state. """
    #     pass
    #     # make a mutation on this random algorithm
    #
    #     # hierin wordt eventueel het uiteinde van een random trein aangepast
    #     # kies eerst een random getal tussen de 1 en 20, en een getal tussen 1 of 2 (begin of eind van de trein)
    #     random_change = random.randint(0,19)
    #     front_or_back = random.randint(1,2)
