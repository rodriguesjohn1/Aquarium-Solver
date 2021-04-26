import itertools

from pysat.solvers import Glucose3
from mpmath.libmp.backend import xrange
import time


class AquariumSolver:
    """
    This class is used to generate a solution to a game of Aquarium. It receives input in the form of a board, the list of
    top numbers, and the list of side numbers. The 2-d board is populated by unique aquariums that a represented with
    unique integers.
    """

    def __init__(self, board, top_numbers, side_numbers):
        self.__board = board
        self.__top_numbers = top_numbers
        self.__side_numbers = side_numbers
        self.__sat = Glucose3()

    def solve(self):
        """
        Return one of the Aquarium game's possible solutions, if it has one.
        :return: A tuple containing the solution of the game, the time it took to create the constraint encodings, and
        the time it took to generate a solution.
        """
        self.__create_constraints()
        return self.__generate_solution()

    def __generate_solution(self):
        start_time = time.time()
        self.__sat.solve()
        solution = self.__to_matrix(self.__sat.get_model(), len(self.__board[0]))
        return solution, self.__constraint_time, time.time() - start_time

    def __create_constraints(self):
        start_time = time.time()
        self.__add_fill_constraint()
        self.__add_width_constraint()
        self.__add_horizontal_and_vertical_constraint()
        self.__constraint_time = time.time() - start_time

    def __add_fill_constraint(self):
        """
        CONSTRAINT 1:
        You have to "fill" the aquariums with water up to a certain level or leave it empty.
        """
        for rindex, row in enumerate(self.__board):
            for cindex, value in enumerate(row):
                places_below = [self.__index_to_nat(rindex, cindex)]
                places_below = places_below + [self.__index_to_nat(r, c) for (r, c) in
                                               self.__get_coord_below(value, rindex)]

                places_below = [[str(-x), str(x)] for x in places_below]

                permutations = ([list(s) for s in itertools.product(*places_below)])

                for permutation in permutations:
                    permutation = [int(v) for v in permutation]
                    if not permutation[0] < 0 and not self.__all_positive(permutation):
                        self.__sat.add_clause(self.__negate(permutation))

    def __add_width_constraint(self):
        """
        CONSTRAINT 2:
        The water level in each aquarium is one and the same across its full width.
        """
        for rindex, row in enumerate(self.__board):
            seen = set()
            for cindex, value in enumerate(row):
                if value not in seen and value in row[cindex + 1:]:
                    values = [cindex]
                    a = row[cindex + 1:]
                    for cindex2, value2 in enumerate(a):
                        if value == value2:
                            values.append(cindex + 1 + cindex2)

                    values = [[str(self.__index_to_nat(rindex, v)), str(-self.__index_to_nat(rindex, v))] for v in
                              values]
                    permutations = ([list(s) for s in itertools.product(*values)])

                    for permutation in permutations:
                        permutation = [int(v) for v in permutation]
                        if not self.__all_positive(permutation) and not self.__all_negative(permutation):
                            self.__sat.add_clause(self.__negate(permutation))

                    seen.add(value)

    def __add_horizontal_and_vertical_constraint(self):
        """
        CONSTRAINT 3:
        The numbers outside the grid show the number of filled cells horizontally and vertically.
        """
        self.__add_horizontal_constraint()
        self.__add_vertical_constraint()

    def __add_horizontal_constraint(self):
        for rindex, water_for_row in enumerate(self.__side_numbers):
            values = []
            for i, v in enumerate(self.__board[rindex]):
                values.append(self.__index_to_nat(rindex, i))
            values = [[str(-v), str(v)] for v in values]
            permutations = ([list(s) for s in itertools.product(*values)])

            for permutation in permutations:
                permutation = [int(v) for v in permutation]
                if not self.__num_positives(permutation, water_for_row):
                    self.__sat.add_clause(self.__negate(permutation))

    def __add_vertical_constraint(self):
        for cindex, water_for_row in enumerate(self.__top_numbers):
            values = []
            for rindex, v in enumerate(self.__board):
                values.append(self.__index_to_nat(rindex, cindex))
            values = [[str(-v), str(v)] for v in values]
            permutations = ([list(s) for s in itertools.product(*values)])

            for permutation in permutations:
                permutation = [int(v) for v in permutation]
                if not self.__num_positives(permutation, water_for_row):
                    self.__sat.add_clause(self.__negate(permutation))

    def __negate(self, lst):
        return [-element for element in lst]

    def __index_to_nat(self, row, col):
        return row * len(self.__board[0]) + col + 1

    def __get_coord_below(self, cur_value, cur_row):
        places_below = []
        for rindex, row in enumerate(self.__board):
            if rindex <= cur_row:
                continue
            for cindex, value in enumerate(row):
                if value == cur_value:
                    places_below.append((rindex, cindex))

        return places_below

    def __all_positive(self, vals):
        for val in vals:
            if val < 0:
                return False
        return True

    def __all_negative(self, vals):
        for val in vals:
            if val > 0:
                return False
        return True

    def __num_positives(self, vals, num_positive):
        count = 0
        for val in vals:
            if val > 0:
                count += 1
        return num_positive == count

    # From: https://stackoverflow.com/questions/14681609/create-a-2d-list-out-of-1d-list
    def __to_matrix(self, input_list, n):
        return [input_list[i:i + n] for i in xrange(0, len(input_list), n)]
