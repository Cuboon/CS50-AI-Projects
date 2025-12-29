import sys
import copy

from crossword import Crossword, Variable


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # make a deep copy of the domain first
        copyD = copy.deepcopy(self.domains)

        # then iterate domains of that copy
        for variable in copyD:
            # getting the variable length
            Stretch = variable.length
            # iterate through the words in the given domain
            for word in copyD[variable]:
                if len(word) != Stretch:
                    # if the length of the word can't fit the variable, delete it from the original variable
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # get the overlapping cells in x and y, then unpack their coordinated to variables
        overX, overY = self.crossword.overlaps[x, y]

        # make a describing variable when revision is made
        done_revise = False

        # make copies of the domain
        copy_DomS = copy.deepcopy(self.domains)

        # if an overlap occurs
        if overX is not None:
            # iterate through the words in domain x
            for wordX in copy_DomS[x]:
                found_match = False
                # iterate through the words in domain y
                for wordY in self.domains[y]:
                    # if the word in x and y have a common letter in an overlapping area
                    if wordX[overX] == wordY[overY]:
                        found_match = True
                        break
                if found_match:
                    continue
                else:
                    self.domains[x].remove(wordX)
                    done_revise = True

        # return boolean when a revision is made
        return done_revise

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = [
                (x, y)
                for x in self.domains
                for y in self.crossword.neighbors(x)
            ]
        else:
            queue = arcs

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        the assignment parameter is for mapping from variables to assigned values
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # all values have the correct length, are distinct, and don't conflict with variables

        # check if the values are distinct
        words = [*assignment.values()]
        if len(words) != len(set(words)):
            return False

        # check if all values have the correct length
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False

        # check if there are conflicts for neighouring variables
        for variable in assignment:
            for neighbour in self.crossword.neighbors(variable):
                if neighbour in assignment:
                    x, y = self.crossword.overlaps[variable, neighbour]
                    if assignment[variable][x] != assignment[neighbour][y]:
                        return False

        # with all cases check corrctly, true is returned
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        counts = []

        for value in self.domains[var]:
            elimin = 0
            for neighbor in self.crossword.neighbors(var):
                # skip neighbors already assigned
                if neighbor in assignment:
                    continue

                # get overlapping var and neighbor positions
                lapOver = self.crossword.overlaps[var, neighbor]
                if lapOver is None:
                    continue

                a, b = lapOver
                for word in self.domains[neighbor]:
                    # count any incompatible words the value would then rule our
                    if value[a] != word[b]:
                        elimin += 1

            counts.append((value, elimin))
        # sort values to ensured the ones eliminiating the fewest options
        counts.sort(key=lambda x: x[1])

        return [value for value, _ in counts]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        dict_choice = {}

        # iterate through variables in domains
        for variable in self.domains:
            # iterating through variables in assignment
            if variable not in assignment:
                # if the variables are not in the assignment, add them to a temporary dictionary
                dict_choice[variable] = self.domains[variable]

        # sort the variable list by the number of remaining values
        list_sorting = [v for v, k in sorted(dict_choice.items(), key=lambda item: len(item[1]))]

        # return the variables with the min number of remaining values
        return list_sorting[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if the assignment is prepared prior
        if len(assignment) == len(self.domains):
            return assignment

        # select an unassigned variable
        variable = self.select_unassigned_variable(assignment)

        # iterate through the variables words
        for value in self.domains[variable]:
            # make a copy of the assignment with updated variables
            copy_assignment = assignment.copy()
            copy_assignment[variable] = value
            # get the result of the backtrack after checking for consistency
            if self.consistent(copy_assignment):
                result = self.backtrack(copy_assignment)
                if result is not None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
