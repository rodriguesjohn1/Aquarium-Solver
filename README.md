# Aquarium-Solver
Aquarium puzzle solver for CS2800 Final Project


## Getting Started

### Dependencies
In order to run this file, you'll need to install a python SAT-solver library. We used [PySat](https://pysathq.github.io/installation.html)

You can install this by running `pip install python-sat[pblib,aiger]`

### Using the file to solve Aquarium
At the top of the file, you will see a 2-d array and two 1-d arrays. These are used to represent a game board. The 2-d array is populated by unique aquariums.

For example, take the image below:

![image](https://user-images.githubusercontent.com/10966946/114499997-3dbcac80-9bf5-11eb-9c6c-0dfb01567d9d.png)


This is equavalent to a 2-d array of 


```
[
[1, 2, 2, 2, 3, 3],
[1, 1, 1, 1, 4, 3],
[1, 5, 5, 1, 4, 3],
[1, 5, 5, 4, 4, 3],
[1, 5, 5, 6, 6, 6],
[5, 5, 5, 5, 5, 6],
]
```

There are many possible ways to represent the same board, but just make sure that the input is correct and that each tank has a unique number.

The two other 1-d lists are for representing the amount of water at each row/column.

In the same example as above, top_numbers would be ```[3, 1, 1, 2, 3, 4]``` and side_numbers would be ```[2, 1, 1, 4, 1, 5]```.

After you have the board and top/side numbers, you should be able to run the file.

### Interpreting the results

After the file runs, you will see an output like:

```
Satisfiable: True
Solution:
[1, 2, 3, 4, -5, 6]
[-7, 8, 9, -10, 11, 12]
[13, 14, 15, -16, -17, 18]
[-19, -20, 21, 22, -23, -24]
[-25, -26, 27, 28, 29, 30]
[31, -32, -33, -34, 35, 36]
```

The "Satisfiable" lets you know if the problem has a solution.

The "Solution" (if there is one) can be interpreted as follows:

* If a number is positive, that coordinate should be filled with water
* If a number is negative, that coordinate should not be filled with water

### Test in the real world!

Try generating a game from https://www.puzzle-aquarium.com/ and plugging it in to the code! Test the results by adding water to the solution's corresponding coordinates.

### How to test:

Install the chromedriver and insert the filepath:
https://chromedriver.chromium.org/downloads
Ex. PATH = "D:/Rando/chromedriver_win32/chromedriver.exe"

Install BeautifulSoup Python library
`pip install beautifulsoup4
