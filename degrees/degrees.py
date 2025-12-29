"""
Date created: 24/12/2025
"""

import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Initialize a frontier to the starting position ONLY
    start = Node(state=source, parent=None, action=None)
    # add start to the frontier List
    front = StackFrontier()
    front.add(start)

    explore = set()
    # loop until a target is found
    while True:

        # if there is nothing left in a frontier, then there is no path
        if front.empty():
            return None

        # choose a node from the frontier
        node = front.remove()

        # if the given node is the goal, a solution is found
        if node.state == target:
            path = []

            # track the path from the target to the source
            while node.parent is not None:
                # add movies and person Id
                path.append((node.action, node.state))
                node = node.parent

            # reverse the path list
            path.reverse()

            return path

        # add the node to the explored set
        explore.add(node.state)

        # add the node neighbor to the frontier
        for action, state in neighbors_for_person(node.state):
            if not front.contains_state(state) and state not in explore:
                neighbor = Node(state=state, parent=node, action=action)
                front.add(neighbor)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    # look up all people with the given name (in lower case)
    people_list = list(names.get(name.lower(), set()))
    # if no person matches the name, return none
    if len(people_list) == 0:
        return None
    elif len(people_list) > 1:
        print(f"Which '{name}'?")
        # display all matching people with the birth year ( if available)
        for person_id in people_list:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            # prompt the user to specify the intended person by id
            person_id = input("Intended Person ID: ")
            if person_id in people_list:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return people_list[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    ids_movie = people[person_id]["movies"]
    neighbors = set()
    # iterate through all movies the person starred in
    for movie_id in ids_movie:
        # for each movie, add neighbors as co-stars
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
