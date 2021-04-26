import itertools

from pysat.solvers import Glucose3
from mpmath.libmp.backend import xrange


class AquariumSolver:
    def __init__(self, board, top_numbers, side_numbers):
        self.board = board
        self.top_numbers = top_numbers
        self.side_numbers = side_numbers
        self.sat = Glucose3()

    def solve(self):
        self.__create_constraints()
        return self.__generate_solution()

    def __generate_solution(self):
        print("Satisfiable:", self.sat.solve())
        print("Solution:")
        for lst in self.__to_matrix(self.sat.get_model(), len(self.board[0])):
            print(lst)

    def __create_constraints(self):
        self.__add_fill_constraint()
        self.__add_width_constraint()
        self.__add_horizontal_and_vertical_constraint()

    def __add_fill_constraint(self):
        for rindex, row in enumerate(self.board):
            for cindex, value in enumerate(row):
                places_below = [self.__index_to_nat(rindex, cindex)]
                places_below = places_below + [self.__index_to_nat(r, c) for (r, c) in
                                               self.__get_coord_below(value, rindex)]

                places_below = [[str(-x), str(x)] for x in places_below]
                # print("places_below:", places_below)

                permutations = ([list(s) for s in itertools.product(*places_below)])

                for permutation in permutations:
                    permutation = [int(v) for v in permutation]
                    if not permutation[0] < 0 and not self.__all_positive(permutation):
                        # print("Adding:", permutation)
                        self.sat.add_clause(self.__negate(permutation))
                    else:
                        pass
                        # print("Excluding:", permutation)

                # print("Done!")

    def __add_width_constraint(self):
        for rindex, row in enumerate(self.board):
            seen = set()
            for cindex, value in enumerate(row):
                # print(cindex, value)
                if value not in seen and value in row[cindex + 1:]:
                    # print("There is another value!")
                    values = [cindex]
                    a = row[cindex + 1:]
                    for cindex2, value2 in enumerate(a):
                        if value == value2:
                            values.append(cindex + 1 + cindex2)
                    # print(values)

                    values = [[str(self.__index_to_nat(rindex, v)), str(-self.__index_to_nat(rindex, v))] for v in
                              values]
                    permutations = ([list(s) for s in itertools.product(*values)])
                    # print(values)

                    for permutation in permutations:
                        permutation = [int(v) for v in permutation]
                        if not self.__all_positive(permutation) and not self.__all_negative(permutation):
                            # print("Adding:", permutation)
                            self.sat.add_clause(self.__negate(permutation))
                        else:
                            pass
                            # print("Excluding:", permutation)

                seen.add(value)

    def __add_horizontal_and_vertical_constraint(self):
        self.__add_horizontal_constraint()
        self.__add_vertical_constraint()

    def __add_horizontal_constraint(self):
        # HORIZONTAL
        for rindex, water_for_row in enumerate(self.side_numbers):
            values = []
            for i, v in enumerate(self.board[rindex]):
                values.append(self.__index_to_nat(rindex, i))
            values = [[str(-v), str(v)] for v in values]
            permutations = ([list(s) for s in itertools.product(*values)])
            # print(values)

            for permutation in permutations:
                permutation = [int(v) for v in permutation]
                if not self.__num_positives(permutation, water_for_row):
                    # print("Adding:", permutation)
                    self.sat.add_clause(self.__negate(permutation))
                else:
                    pass
                    # print("Excluding:", permutation)

    def __add_vertical_constraint(self):
        for cindex, water_for_row in enumerate(self.top_numbers):
            values = []
            for rindex, v in enumerate(self.board):
                values.append(self.__index_to_nat(rindex, cindex))
            values = [[str(-v), str(v)] for v in values]
            permutations = ([list(s) for s in itertools.product(*values)])
            # print(values)
            # print("water for col:", water_for_row)

            for permutation in permutations:
                permutation = [int(v) for v in permutation]
                if not self.__num_positives(permutation, water_for_row):
                    # print("Adding:", permutation)
                    self.sat.add_clause(self.__negate(permutation))
                else:
                    pass
                    # print("Excluding:", permutation)

    def __negate(self, lst):
        return [-element for element in lst]

    def __index_to_nat(self, row, col):
        return row * len(self.board[0]) + col + 1

    def __get_coord_below(self, cur_value, cur_row):
        places_below = []
        for rindex, row in enumerate(self.board):
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


"""
Constraints:

1) You have to "fill" the aquariums with water up to a certain level or leave it empty.

"""

"""
CONSTRAINT 2:
2) The water level in each aquarium is one and the same across its full width.

"""

"""
3) The numbers outside the grid show the number of filled cells horizontally and vertically.
"""
