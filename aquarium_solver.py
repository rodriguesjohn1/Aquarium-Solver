import itertools

from mpmath.libmp.backend import xrange
from pysat.solvers import Glucose3
"""
board = [
    [1, 1, 1],
    [1, 1, 3],
]

top_numbers = [2, 2, 1]
side_numbers = [3, 2]

board = [
    [1, 2, 2, 6, 6, 5],
    [1, 2, 2, 2, 6, 5],
    [2, 2, 2, 2, 6, 5],
    [3, 3, 2, 2, 2, 5],
    [3, 3, 3, 2, 4, 5],
    [3, 3, 3, 4, 4, 4],
]

top_numbers = [4, 3, 4, 5, 4, 2]
side_numbers = [3, 5, 5, 4, 2, 3]
"""


board = [
    [1, 1, 2, 2, 3, 4],
    [8, 7, 7, 6, 5, 5],
    [9, 10, 10, 6, 6, 11],
    [18, 18, 17, 15, 14, 12],
    [19, 19, 17, 15, 14, 12],
    [19, 16, 16, 16, 13, 13],
]

top_numbers = [3, 3, 5, 3, 3, 5]
side_numbers = [5, 4, 4, 2, 4, 3]



def index_to_nat(row, col):
    return row * len(board[0]) + col + 1


"""
print(index_to_nat(0, 3))
print(index_to_nat(1, 0))
print(index_to_nat(2, 0))
print(index_to_nat(3, 0))
"""

g = Glucose3()



def negate(vals):
    return [-v for v in vals]

def get_coord_below(cur_value, cur_row):
    places_below = []
    for rindex, row in enumerate(board):
        if rindex <= cur_row:
            continue
        for cindex, value in enumerate(row):
            if value == cur_value:
                places_below.append((rindex, cindex))

    return places_below


def all_positive(vals):
    for val in vals:
        if val < 0:
            return False
    return True


def all_negative(vals):
    for val in vals:
        if val > 0:
            return False
    return True


def num_positives(vals, num_positive):
    count = 0
    for val in vals:
        if val > 0:
            count += 1
    return num_positive == count

# From: https://stackoverflow.com/questions/14681609/create-a-2d-list-out-of-1d-list
def to_matrix(l, n):
    return [l[i:i + n] for i in xrange(0, len(l), n)]


"""
Constraints:

1) You have to "fill" the aquariums with water up to a certain level or leave it empty.

"""
for rindex, row in enumerate(board):
    for cindex, value in enumerate(row):
        places_below = [index_to_nat(rindex, cindex)]
        places_below = places_below + [index_to_nat(r, c) for (r, c) in get_coord_below(value, rindex)]

        places_below = [[str(-x), str(x)] for x in places_below]
        # print("places_below:", places_below)

        permutations = ([list(s) for s in itertools.product(*places_below)])

        for permutation in permutations:
            permutation = [int(v) for v in permutation]
            if not permutation[0] < 0 and not all_positive(permutation):
                # print("Adding:", permutation)
                g.add_clause(negate(permutation))
            else:
                pass
                # print("Excluding:", permutation)

        # print("Done!")

"""
CONSTRAINT 2:
2) The water level in each aquarium is one and the same across its full width.

"""

for rindex, row in enumerate(board):
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

            values = [[str(index_to_nat(rindex, v)), str(-index_to_nat(rindex, v))] for v in values]
            permutations = ([list(s) for s in itertools.product(*values)])
            # print(values)

            for permutation in permutations:
                permutation = [int(v) for v in permutation]
                if not all_positive(permutation) and not all_negative(permutation):
                    # print("Adding:", permutation)
                    g.add_clause(negate(permutation))
                else:
                    pass
                    # print("Excluding:", permutation)

        seen.add(value)

"""
3) The numbers outside the grid show the number of filled cells horizontally and vertically.
"""

# HORIZONTAL
for rindex, water_for_row in enumerate(side_numbers):
    values = []
    for i, v in enumerate(board[rindex]):
        values.append(index_to_nat(rindex, i))
    values = [[str(-v), str(v)] for v in values]
    permutations = ([list(s) for s in itertools.product(*values)])
    # print(values)

    for permutation in permutations:
        permutation = [int(v) for v in permutation]
        if not num_positives(permutation, water_for_row):
            # print("Adding:", permutation)
            g.add_clause(negate(permutation))
        else:
            pass
            # print("Excluding:", permutation)

# VERTICAL
for cindex, water_for_row in enumerate(top_numbers):
    values = []
    for rindex, v in enumerate(board):
        values.append(index_to_nat(rindex, cindex))
    values = [[str(-v), str(v)] for v in values]
    permutations = ([list(s) for s in itertools.product(*values)])
    #print(values)
    #print("water for col:", water_for_row)

    for permutation in permutations:
        permutation = [int(v) for v in permutation]
        if not num_positives(permutation, water_for_row):
            #print("Adding:", permutation)
            g.add_clause(negate(permutation))
        else:
            pass
            #print("Excluding:", permutation)

g.add_clause([-6, 6])
print("Satisfiable:", g.solve())

print("Solution:")
for list in to_matrix(g.get_model(), len(board[0])):
    print(list)

