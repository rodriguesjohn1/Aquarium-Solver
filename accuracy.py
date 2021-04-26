from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
from collections import deque

from aquarium_solver import AquariumSolver

'''
in order to run this script (more specifically selenium) you must download the chromedriver and insert the path 
if you do not have it you can download it from here:
https://chromedriver.chromium.org/downloads
'''

URL = "https://www.puzzle-aquarium.com/"
PATH = "D:/Rando/chromedriver_win32/chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get(URL)
html = driver.page_source
soup = bs(html, "html.parser")

# get the column numbers
numbers = soup.find_all(class_="cell task v")
top_numbers = []
for number in numbers:
    top_numbers.append(int(number.text))

# get the row numbers
numbers = soup.find_all(class_="cell task h")
side_numbers = []
for number in numbers:
    side_numbers.append(int(number.text))

# determine the sub-aquariums
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
    if i % 6 == 0 and i != 0:
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

for row in board:
    print(row)

solver = AquariumSolver(board, top_numbers, side_numbers)
solution = solver.solve()

# print(grid)
# sleep for 20 seconds to manual verify info is correct before window closes
time.sleep(40)
driver.close()
