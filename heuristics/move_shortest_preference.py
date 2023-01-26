from station import Station
import random


def preference_shortest_move_heuristic(curr: Station, visited: list[Station], stations: dict[str, Station]) -> Station:
    """Preference for moving to the next connection that has not been visited yet and has the least travel time"""
    shortest_connection: int = 100
    check_stations: bool = all(station is True for station in curr.connection_visited.values())

    if check_stations is True:
            # stoppen met treinen rijden als alle connecties zijn bereden.
            # if all_stations_true == len(stations_dictionary):
            #     return train_stations, time
            # else:
        # finds the shortest connection and weights the preference 70%
        for connections in curr.connections:
            check_connections = stations.get(connections)
            for value in check_connections.connections.values():
                if value < shortest_connection:
                    shortest_connection: int = value
                    chance: float = random.uniform(0,10)
                    if chance < 7:
                        next_station: Station | None = stations.get(connections)
                    else:
                        possible_next_station: Station | None = random.choice(list(curr.connections.keys()))
                        next_station = stations.get(str(possible_next_station))
    else:
        # finds the shortest connection and weights the preference 70%
        for connections in curr.connections:
            check_connections: Station | None = stations.get(connections)
            if curr.connections[connections] < shortest_connection and curr.connection_visited[connections] is False:
                shortest_connection = curr.connections[connections]
                chance: float = random.uniform(0,10)
                if chance < 7:
                    next_station = next_station = stations.get(connections)
                else:
                    possible_next_station = random.choice(list(curr.connections.keys()))
                    next_station = stations.get(str(possible_next_station))


    return next_station