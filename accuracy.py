from bs4 import BeautifulSoup as bs
from selenium import webdriver
from collections import deque

from aquarium_solver import AquariumSolver

'''
in order to run this script (more specifically selenium) you must download the chromedriver and insert the file path 
if you do not have it you can download it from here:
https://chromedriver.chromium.org/downloads
'''
PATH = "D:/Rando/chromedriver_win32/chromedriver.exe"

"""

"""


class WebTest:
    """
    This class is responsible for taking in a list of settings and trying out our AquariumSolver on a website. It uses
    chromedriver to open the website, scrape the board, generate a solution, enter to solution on the website, and then
    see if the website likes the answer.
    """
    def __init__(self, settings):
        """
        This constructor expects an input list of tuples that specifies which board to run and for how many attempts.
        For example, an input list of [(0, 10), (8, 5)] would run against the 6x6 Easy 10 times and the 15x15 Hard 8
        times.

        Set the difficulty/grid size
        NOTE: 10x10 Easy and 15x15 Easy can take a while to finish running. We were unable to run through a large number
        of puzzles because occasionally you would run into boards that have very large aquariums and computing the
        permutations could take a long time.
        0 = 6x6 Easy
        1 = 6x6 Normal
        2 = 6x6 Hard
        3 = 10x10 Easy
        4 = 10x10 Normal
        5 = 10x10 Hard
        6 = 15x15 Easy
        7 = 15x15 Normal
        8 = 15x15 Hard
        :param settings: A list of tuples telling the class which board to try and for how many runs.
        """
        self.__settings = settings

    def run(self):
        """
        Run the accuracy test.
        :return:
        """
        for setting, total_runs in self.__settings:
            self.__reset_aggregation_values()
            self.__update_sizes(setting)
            self.__update_url(setting)
            self.__run_webdriver(total_runs)
            self.__print_results()

    def __reset_aggregation_values(self):
        self.__total_constraint_time = 0
        self.__total_generate_solution_time = 0
        self.__total_successes = 0
        self.__total_failures = 0

    def __update_sizes(self, setting):
        self.__current_setting = setting
        if setting < 3:
            self.__grid_size = 6
            self.__size = 25
        elif setting < 6:
            self.__grid_size = 10
            self.__size = 41
        else:
            self.__grid_size = 15
            self.__size = 61

    def __update_url(self, setting):
        self.__url = f"https://www.puzzle-aquarium.com/?size={setting}"

    def __run_webdriver(self, total_runs):
        driver = webdriver.Chrome(PATH)
        for _ in range(total_runs):
            driver.get(self.__url)
            html = driver.page_source
            soup = bs(html, "html.parser")

            top_numbers = self.__get_top_numbers(soup)
            side_numbers = self.__get_side_numbers(soup)
            board = self.__get_board(soup)

            solver = AquariumSolver(board, top_numbers, side_numbers)

            solution, constraint_time, generate_solution_time = solver.solve()

            # click on cells on website
            id = 2
            for row in solution:
                for num in row:
                    if num > 0:
                        cell = driver.find_element_by_xpath(f"//*[@id=\"game\"]/div[{self.__size}]/div[{id}]")
                        cell.click()
                    id += 1

            # click on 'done' to verify solution
            done = driver.find_element_by_xpath("//*[@id=\"btnReady\"]")
            done.click()

            if "Congratulations! You have solved the puzzle" in driver.page_source:
                self.__total_constraint_time += constraint_time
                self.__total_generate_solution_time += generate_solution_time
                self.__total_successes += 1
            else:
                print("Error: Solution was not successful")
                self.__total_failures += 1
                driver.close()
                driver = webdriver.Chrome(PATH)
        driver.close()

    def __get_top_numbers(self, soup):
        numbers = soup.find_all(class_="cell task v")
        top_numbers = []
        for number in numbers:
            top_numbers.append(int(number.text))
        return top_numbers

    def __get_side_numbers(self, soup):
        numbers = soup.find_all(class_="cell task h")
        side_numbers = []
        for number in numbers:
            side_numbers.append(int(number.text))
        return side_numbers

    def __get_board(self, soup):
        c = soup.find_all(tabindex="1")[1:]
        grid = []
        row = []
        """
        make a grid to see where the sides of the cell are
        ASSUME that all cells on edge already have either a top/bottom/left/right
        bl: border left
        br: border right
        bt: border top
        bb: border bottom
        empty brackets [] mean that a cell has no borders
        (it may still have a border if it is on an edge)
        """
        for i in range(len(c)):
            if i % self.__grid_size == 0 and i != 0:
                grid.append(row)
                row = []
            # split the div and extract the sides from the class
            r = str(c[i]).split("\"")[1]
            side = r.split()[2:-1]
            row.append(side)
        grid.append(row)

        board = [[0 for i in range(len(grid))] for j in range(len(grid))]

        seen_aquarium = set()
        aquarium_index = 1
        for i, row in enumerate(grid):
            for j, borders in enumerate(row):
                if (i, j) in seen_aquarium:
                    continue

                seen = set()
                stack = deque()
                stack.append((i, j))
                while len(stack) > 0:
                    x, y = stack.pop()
                    seen.add((x, y))
                    borders = grid[x][y]
                    if "bt" not in borders and x > 0 and (x - 1, y) not in seen:
                        stack.append((x - 1, y))
                    if "bb" not in borders and x < len(grid) - 1 and (x + 1, y) not in seen:
                        stack.append((x + 1, y))
                    if "bl" not in borders and y > 0 and (x, y - 1) not in seen:
                        stack.append((x, y - 1))
                    if "br" not in borders and y < len(grid) - 1 and (x, y + 1 not in seen):
                        stack.append((x, y + 1))
                for x, y in seen:
                    seen_aquarium.add((x, y))
                    board[x][y] = aquarium_index
                aquarium_index += 1

        return board

    def __print_results(self):
        print(f"Looking at setting:", self.__current_setting)
        print(f"Total Successes: {self.__total_successes}")
        print(f"Total Failures: {self.__total_failures}")
        print(f"Accuracy: {self.__total_successes / (self.__total_successes + self.__total_failures)}")
        print(f"Average constraint making time: {self.__total_constraint_time / self.__total_successes}s")
        print(f"Average solution generation time: {self.__total_generate_solution_time / self.__total_successes}s\n")


if __name__ == "__main__":
    settings = [(0, 10), (1, 10), (2, 10)]
    accuracy = WebTest(settings)
    accuracy.run()
