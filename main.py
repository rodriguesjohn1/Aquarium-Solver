from aquarium_solver import AquariumSolver

example_board = [
    [1, 1, 2, 2, 3, 4],
    [8, 7, 7, 6, 5, 5],
    [9, 10, 10, 6, 6, 11],
    [18, 18, 17, 15, 14, 12],
    [19, 19, 17, 15, 14, 12],
    [19, 16, 16, 16, 13, 13],
]

example_top_numbers = [3, 3, 5, 3, 3, 5]
example_side_numbers = [5, 4, 4, 2, 4, 3]


def main():
    solver = AquariumSolver(example_board, example_top_numbers, example_side_numbers)
    solution, _, _ = solver.solve()
    for row in solution:
        print(row)


if __name__ == "__main__":
    main()
