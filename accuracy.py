from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
from collections import deque

from aquarium_solver import AquariumSolver

'''
in order to run this script (more specifically selenium) you must download the chromedriver and insert the file path 
if you do not have it you can download it from here:
https://chromedriver.chromium.org/downloads
'''
PATH = "C:/Users/John/Downloads/chromedriver_win32/chromedriver.exe"

"""
Set the difficuly/grid size
0 = 6x6 Easy
1 = 6x6 Normal
2 = 6x6 Hard
3 = 10x10 Easy
4 = 10x10 Normal
5 = 10x10 Hard
6 = 15x15 Easy
7 = 15x15 Normal
8 = 15x15 Hard
9 = 20x20 Special Daily
10 = 25x25 Special Weekly
11 = 30x30 Special Monthly
"""
setting = 10

URL = f"https://www.puzzle-aquarium.com/?size={setting}"
# set constants for parsing html
if 0 <= setting < 3:
    GRID_SIZE = 6
    SIZE = 25
elif 3 <= setting < 6:
    GRID_SIZE = 10
    SIZE = 41
elif 6 <= setting < 9:
    GRID_SIZE = 15
    SIZE = 61 
elif setting == 9:
    GRID_SIZE = 20
    SIZE = 81 
elif setting == 10:
    GRID_SIZE = 25
    SIZE = 101 
elif setting == 11:
    GRID_SIZE = 30
    SIZE = 121 



# //*[@id="game"]/div[25]/div[2]
# //*[@id="game"]/div[41]/div[2]
# //*[@id="game"]/div[61]/div[2]
# //*[@id="game"]/div[81]/div[2]
#25 6x6 
#41 10x10
#61 15x15
#81 special (20x20)

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
    if i % GRID_SIZE == 0 and i != 0:
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

# click on cells on website
id = 2
for row in solution:
    for num in row:
        if num > 0:
            cell = driver.find_element_by_xpath(f"//*[@id=\"game\"]/div[{SIZE}]/div[{id}]")
            cell.click()
        id+=1



# click on 'done' to verify solution
done = driver.find_element_by_xpath("//*[@id=\"btnReady\"]")
done.click()

try:
    driver.find_element_by_xpath("//*[@id=\"ajaxResponse\"]/p[1]")
    print("Success! Solution was correct")
except:
    print("Error: Solution was not successful")

# print(grid)
# sleep to manual verify info is correct before window closes
time.sleep(5)
driver.close()
