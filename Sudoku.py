# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 11:24:32 2024

@author: Juan Carlos Llamas Núñez
"""

import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from termcolor import colored
import time
import copy
import itertools

"""Auxiliary functions"""

"""Get the row, column and box of a certain position in the grid"""
def getRow(position):
  return position[0]
def getColumn(position):
  return position[1]
def getBox(position):
  return 3*(position[0]//3) + position[1]//3

"""Given a certain row, column and box, get all the cells in that row,
 column and box"""
def positions_box(box):
  positions=[]
  for i in range(3):
    for j in range(3):
      positions.append([3*(box // 3)+i,3*(box % 3)+j])
  return positions
def positions_row(row):
  return [[row,i] for i in range(9)]
def positions_column(column):
  return [[i,column] for i in range(9)]

def other_two_boxes_same_row(box):
    return [i for i in [3*(box//3) + i for i in range(3)] if i!= box]

def other_two_boxes_same_column(box):
    return [i for i in [box%3+ 3*i for i in range(3)] if i!= box]


def string_to_grid(sudoku_string):
  """Parse from string to grid"""
  sudoku_grid = []
  for i in range(9):
    sudoku_grid.append([])
    for j in range(9):
      sudoku_grid[i].append(sudoku_string[0])
      sudoku_string=sudoku_string[1:]
  return sudoku_grid


def grid_to_string(sudoku_grid):
  """Parse from grid to string"""
  sudoku_string = []
  for i in range(9):
    for j in range(9):
      sudoku_string.append(sudoku_grid[i][j])
  return ''.join(sudoku_string)

def only_one_place_availabe_for_num_in_cells(cells, num, marks):
  """If there is only one place in the set of positions 'cells' where 'num' is
  available given the restrictions in 'marks', returns that position.
  Otherwise returns -1"""
  places=0
  key_position=[]
  for position in cells:
    if marks[position[0]][position[1]][num]:
      places=places+1
      key_position=position
  if places==1:
    return key_position
  else:
    return -1

def only_one_num_availabe_in_cell(i,j,marks):
  """If there is only one number avaliable in cell (i,j) given the
  restrictions in 'marks', returns that number.
  Otherwise returns -1"""
  
  numbers=0
  number=-1
  for num in range(9):
    if marks[i][j][num]:
      numbers=numbers+1
      number=num
  if numbers==1:
    return number
  else:
    return -1

def obvious_set(n, positions, marks):
  """Checks if there is a subset of 'n' elements in 'positions'
  whose set of marked numbers has size 'n'. If so checks if there
  is any of this marks in the complementary subset of cells.
  If this is the case, the marks in the complementary set have to be removed 
  and the set of cells, the set of marks and the set of remove marks are
  returned. otherwise, None is returned"""
  
  for subset in itertools.combinations(positions, n):
      numbers_in_subset=set({})
      for element in subset:
        for num in range(9):
          if marks[element[0]][element[1]][num]:
            numbers_in_subset.add(num)
      if len(numbers_in_subset)==n:
        removed_marks=[]
        for pos in positions:
          if pos not in subset:
            for num in numbers_in_subset:
              if marks[pos[0]][pos[1]][num]:
                marks[pos[0]][pos[1]][num]=False
                removed_marks.append((pos,num))
        if len(removed_marks)>0:
          return {'subset': subset, 'numbers_in_subset': numbers_in_subset, 'removed_marks': removed_marks}
  return

class Sudoku:
    """Sudoku class with solver and printer"""
    
    def __init__(self,sudoku_string):
        self.sudoku_string_original=sudoku_string
        self.sudoku_grid_original=string_to_grid(sudoku_string)
        self.sudoku_grid=string_to_grid(sudoku_string)
        self.marks=np.ones((9,9,9),dtype=bool)
        self.rows=np.zeros((9,9),dtype=bool)
        self.columns=np.zeros((9,9),dtype=bool)
        self.boxes=np.zeros((9,9),dtype=bool)
      
        for i in range(9):
          for j in range(9):
            num=self.sudoku_grid[i][j]
            if num != '0':
              num=int(num)-1
              #box marks
              for position in positions_box(getBox([i,j])):
                self.marks[position[0]][position[1]][num]=False
              #row marks
              for position in positions_row(getRow([i,j])):
                self.marks[position[0]][position[1]][num]=False
              #column marks
              for position in positions_column(getColumn([i,j])):
                self.marks[position[0]][position[1]][num]=False
              #other numbers marks
              for other_number in range(9):
                self.marks[i][j][other_number]=False
              self.marks[i][j][num]=True
              self.rows[i][num]=True
              self.columns[j][num]=True
              self.boxes[getBox([i,j])][num]=True
        
    def printer(self,i=-1, j=-1):
        black='\033[90m'
        blue='\033[94m'
        magenta='\033[95m'
        for row in range(9):
          if row % 3==0:
            print(black + '-------------------------'+ black)
          for column in range(9):
            if column % 3==0:
              print( black +'|'+ black, end=' ')
            if self.sudoku_grid_original[row][column] != '0':
              print(black + self.sudoku_grid[row][column] + black, end=' ')
            elif i==row and j==column:
              print(magenta + self.sudoku_grid[row][column] + magenta, end=' ')
            elif self.sudoku_grid[row][column] == '0':
              print(' ', end=' ')
            else:
              print(blue + self.sudoku_grid[row][column] + blue, end=' ')
          print(black +'|'+ black)
        print(black + '-------------------------'+ black)
        
    def is_complete(self):
        """Check if the sudoku grid is complete"""
        for row in self.sudoku_grid:
          for cell in row:
            if cell=='0':
              return False
        return True
  
    def unsolvable(self):
        """Check if the sudoku grid is complete"""
        for i in range(9):
          for j in range(9):
            if len([num for num in range(9) if self.marks[i][j][num]])==0:
              return True
        return False
    
    def solve_sudoku(self, PRINT_SUDOKUS=True):
        """Sudoku solver"""
        self.PRINT_SUDOKUS=PRINT_SUDOKUS
        start = time.time()
        if self.PRINT_SUDOKUS:
          self.printer()
        while True:
          if self.unsolvable():
            return 'Unsolvable'
          if self.put_immediate_number():
            if self.is_complete():
              break
            else:
              continue
          if self.update_marks():
             continue
          else:
            if len(self.back_tracking())>0:
              break
        end = time.time()
        if self.PRINT_SUDOKUS:
          print('The sudoku has been solved in '+str(end - start)+' seconds!')
        return grid_to_string(self.sudoku_grid)
    
    def put_immediate_number(self):
        """Checks if it is possible to complete a number in the sudoku grid if
        any of immediate rules apply. If it is possible, the number is written,
        the marks are updated and True is immediately returned after the first
        successful rule is fulfilled. Otherwise False is returned"""
        
        #RULE 1: Check if a number has only one place available in a certain box:
        for num in range(9):
            for box in range(9):
              if not self.boxes[box][num]:
                position=only_one_place_availabe_for_num_in_cells(positions_box(box), num, self.marks)
                if position != -1: # Complete a cell
                  #box marks
                  for pos in positions_box(getBox(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #row marks
                  for pos in positions_row(getRow(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #column marks
                  for pos in positions_column(getColumn(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #that cell
                  for other_number in range(9):
                    self.marks[position[0]][position[1]][other_number]=False
                  self.marks[position[0]][position[1]][num]=True
                  self.rows[position[0]][num]=True
                  self.columns[position[1]][num]=True
                  self.boxes[box][num]=True
                  self.sudoku_grid[position[0]][position[1]]=str(num+1)
                  if self.PRINT_SUDOKUS:
                    print('There is only a cell where it is possible to put number '+str(num+1)+' in box '+ str(box+1))
                    self.printer(position[0], position[1])
                  return True
              
        #RULE 2: Check if a number has only one place available in the row:
        for num in range(9):
            for row in range(9):
              if not self.rows[row][num]:
                position=only_one_place_availabe_for_num_in_cells(positions_row(row), num, self.marks)
                if position != -1:
                  #box marks
                  for pos in positions_box(getBox(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #row marks
                  for pos in positions_row(getRow(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #column marks
                  for pos in positions_column(getColumn(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #that cell
                  for other_number in range(9):
                    self.marks[position[0]][position[1]][other_number]=False
                  self.marks[position[0]][position[1]][num]=True
                  self.rows[position[0]][num]=True
                  self.columns[position[1]][num]=True
                  self.boxes[getBox(position)][num]=True
                  self.sudoku_grid[position[0]][position[1]]=str(num+1)
                  if self.PRINT_SUDOKUS:
                    print('There is only a cell where it is possible to put number '+str(num+1)+' in row '+ str(row+1))
                    self.printer(position[0], position[1])
                  return True
        #RULE 3: Check if a number has only one place available in the column:
        for num in range(9):
            for column in range(9):
              if not self.columns[column][num]:
                position=only_one_place_availabe_for_num_in_cells(positions_column(column), num, self.marks)
                if position != -1:
                  #box marks
                  for pos in positions_box(getBox(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #row marks
                  for pos in positions_row(getRow(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #column marks
                  for pos in positions_column(getColumn(position)):
                    self.marks[pos[0]][pos[1]][num]=False
                  #that cell
                  for other_number in range(9):
                    self.marks[position[0]][position[1]][other_number]=False
                  self.marks[position[0]][position[1]][num]=True
                  self.rows[position[0]][num]=True
                  self.columns[position[1]][num]=True
                  self.boxes[getBox(position)][num]=True
                  self.sudoku_grid[position[0]][position[1]]=str(num+1)
                  if self.PRINT_SUDOKUS:
                    print('There is only a cell where it is possible to put number '+str(num+1)+' in column '+ str(column+1))
                    self.printer(position[0], position[1])
                  return True
        #RULE 4: Check if a cell has only one available number:
        for i in range(9):
            for j in range(9):
              if self.sudoku_grid[i][j]=='0':
                num=only_one_num_availabe_in_cell(i,j, self.marks)
                if num != -1:
                  #box marks
                  for pos in positions_box(getBox([i,j])):
                    self.marks[pos[0]][pos[1]][num]=False
                  #row marks
                  for pos in positions_row(getRow([i,j])):
                    self.marks[pos[0]][pos[1]][num]=False
                  #column marks
                  for pos in positions_column(getColumn([i,j])):
                    self.marks[pos[0]][pos[1]][num]=False
                  #that cell
                  for other_number in range(9):
                    self.marks[i][j][other_number]=False
                  self.marks[i][j][num]=True
                  self.rows[i][num]=True
                  self.columns[j][num]=True
                  self.boxes[getBox([i,j])][num]=True
                  self.sudoku_grid[i][j]=str(num+1)
                  print('The only possible correct number in cell ('+str(i+1)+','+str(j+1)+') is '+ str(num+1))
                  self.printer(i, j)
                  return True
        return False
    
    def update_marks(self):        
        """Check if any marks can be removed with a series of logical tests. 
        Returns True if a mark has been removed or False otherwise """
        
        # FIRST APPROACH: POINTING ROWS AND COLUMNS
        
        pointing_rows = np.zeros((9,9),dtype=set) # for each box and number, contains a list with the rows with at least one mark
        pointing_columns = np.zeros((9,9),dtype=set) # for each box and number, contains a list with the columns with at least one mark
        for box in range(9):
          for num in range(9):
            pointing_rows[box][num]=set({})
            pointing_columns[box][num]=set({})
            if not self.boxes[box][num]:
              for pos in positions_box(box):
                if self.marks[pos[0]][pos[1]][num]:
                  pointing_rows[box][num].add(pos[0])
                  pointing_columns[box][num].add(pos[1])
        for box in range(9):
          for num in range(9):
            # 2 ROWS
            if len(pointing_rows[box][num])==2:
              # Check if another box in the same row of boxes has the exact same two
              # pointing rows AND the other box has a pointing row belonging to those
              # two same pointing rows
              boxes=other_two_boxes_same_row(box)
              # 2 ROWS OPTION A
              if pointing_rows[boxes[0]][num]==pointing_rows[box][num] and len(pointing_rows[boxes[1]][num].intersection(pointing_rows[box][num]))>0:
                removed_marks=[]
                for pos in positions_box(boxes[1]):
                  if pos[0] in pointing_rows[box][num] and self.marks[pos[0]][pos[1]][num]:
                    self.marks[pos[0]][pos[1]][num]=False
                    removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Boxes " + str(box+1) + " and " + str(boxes[0]+1) +
                      " share pointing marked rows " +  str([i+1 for i in pointing_rows[box][num]]) +
                      " for number " + str(num+1) + " so all the marks for number " +
                      str(num+1) + " in row(s) " +
                      str([i+1 for i in pointing_rows[boxes[1]][num].intersection(pointing_rows[box][num])])+
                      " of box " + str(boxes[1] + 1) +
                      " shall be removed, i.e." + str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
               # 2 ROWS OPTION B
              if pointing_rows[boxes[1]][num]==pointing_rows[box][num] and len(pointing_rows[boxes[0]][num].intersection(pointing_rows[box][num]))>0:
                removed_marks=[]
                for pos in positions_box(boxes[0]):
                  if pos[0] in pointing_rows[box][num] and self.marks[pos[0]][pos[1]][num]:
                    self.marks[pos[0]][pos[1]][num]=False
                    removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Boxes " + str(box+1) + " and " + str(boxes[1]+1) +
                      " share pointing marked rows " + str([i+1 for i in pointing_rows[box][num]])
                      + " for number " + str(num+1) + " so all the marks for number "
                      + str(num+1) + " in row(s) " +
                      str([i+1 for i in pointing_rows[boxes[0]][num].intersection(pointing_rows[box][num])])+
                      " of box " + str(boxes[0]+1) +
                      " shall be removed, i.e."+ str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
            # 1 ROW
            if len(pointing_rows[box][num])==1:
              # Check if another box in the same row of boxes has a pointing mark
              # of the same number in the same row
              boxes=other_two_boxes_same_row(box)
      
              if len(pointing_rows[boxes[1]][num].intersection(pointing_rows[box][num])) > 0 or len(pointing_rows[boxes[0]][num].intersection(pointing_rows[box][num])) > 0:
                removed_marks=[]
                for b in boxes:
                  for pos in positions_box(b):
                    if pos[0] in pointing_rows[box][num] and self.marks[pos[0]][pos[1]][num]:
                      self.marks[pos[0]][pos[1]][num]=False
                      removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Box " + str(box+1) + " has only a pointing marked row " +
                      str([i +1 for i in pointing_rows[box][num]]) + " for number " +
                      str(num+1) + " so all the marks for number " + str(num+1) + " in row " +
                      str([i +1 for i in pointing_rows[box][num]]) +
                      " of boxes " + str([b+1 for b in boxes]) +
                      " shall be removed, i.e." + str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
            # 2 COLUMNS
            if len(pointing_columns[box][num])==2:
              # Check if another box in the same column of boxes has the exact same two
              # pointing columns AND the other box has a pointing column belonging to those
              # two same pointing columns
              boxes=other_two_boxes_same_column(box)
              # 2 COLUMN OPTION A
              if pointing_columns[boxes[0]][num]==pointing_columns[box][num] and len(pointing_columns[boxes[1]][num].intersection(pointing_columns[box][num]))>0:
                removed_marks=[]
                for pos in positions_box(boxes[1]):
                  if pos[1] in pointing_columns[box][num] and self.marks[pos[0]][pos[1]][num]:
                    self.marks[pos[0]][pos[1]][num]=False
                    removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Boxes " + str(box+1) + " and " + str(boxes[0]+1) +
                      " share pointing marked columns " +  str([i+1 for i in pointing_columns[box][num]]) +
                      " for number " + str(num+1) + " so all the marks for number " +
                      str(num+1) + " in column(s) " +
                      str([i+1 for i in pointing_columns[boxes[1]][num].intersection(pointing_columns[box][num])])+
                      " of box " + str(boxes[1] + 1) +
                      " shall be removed, i.e." + str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
               # 2 COLUMN OPTION B
              if pointing_columns[boxes[1]][num]==pointing_columns[box][num] and len(pointing_columns[boxes[0]][num].intersection(pointing_columns[box][num]))>0:
                removed_marks=[]
                for pos in positions_box(boxes[0]):
                  if pos[1] in pointing_columns[box][num] and self.marks[pos[0]][pos[1]][num]:
                    self.marks[pos[0]][pos[1]][num]=False
                    removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Boxes " + str(box+1) + " and " + str(boxes[1]+1) +
                      " share pointing marked columns " + str([i+1 for i in pointing_columns[box][num]])
                      + " for number " + str(num+1) + " so all the marks for number "
                      + str(num+1) + " in column(s) " +
                      str([i+1 for i in pointing_columns[boxes[0]][num].intersection(pointing_columns[box][num])])+
                      " of box " + str(boxes[0]+1) +
                      " shall be removed, i.e."+ str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
            # 1 COLUMN
            if len(pointing_columns[box][num])==1:
              # Check if another box in the same column of boxes has a pointing mark
              # of the same number in the same column
              boxes=other_two_boxes_same_column(box)
      
              if len(pointing_columns[boxes[1]][num].intersection(pointing_columns[box][num])) > 0 or len(pointing_columns[boxes[0]][num].intersection(pointing_columns[box][num])) > 0:
                removed_marks=[]
                for b in boxes:
                  for pos in positions_box(b):
                    if pos[1] in pointing_columns[box][num] and self.marks[pos[0]][pos[1]][num]:
                      self.marks[pos[0]][pos[1]][num]=False
                      removed_marks.append(pos)
                if self.PRINT_SUDOKUS:
                  print("Box " + str(box+1) + " has only a pointing marked column " +
                      str([i +1 for i in pointing_columns[box][num]]) + " for number " +
                      str(num+1) + " so all the marks for number " + str(num+1) + " in column " +
                      str([i +1 for i in pointing_columns[box][num]]) +
                      " of boxes " + str([b+1 for b in boxes]) +
                      " shall be removed, i.e." + str([[pos[0]+1,pos[1]+1] for pos in removed_marks]))
                return True
      
        # SECOND APPROACH: OBVIOUS SETS
        
        #Obvious sets in box
        for box in range(9):
            cells=[pos for pos in positions_box(box) if self.sudoku_grid[pos[0]][pos[1]]=='0']
            for n in range(len(cells)-2):
              dev = obvious_set(n, cells, self.marks)
              if dev != None:
                if self.PRINT_SUDOKUS:
                  print("Box " + str(box+1) + " has a set of "+ str(len(dev['subset']))+ " cells " + str([[pos[0]+1,pos[1]+1] for pos in dev['subset']]) +
                      " where the only marks are " +  str([i+1 for i in dev['numbers_in_subset']]) +
                      " so no marks of those numbers are possible in the other cells of the box, i.e., the following marks should be removed " +
                      str([([pos[0]+1,pos[1]+1],num+1) for (pos,num) in dev['removed_marks']]))
                return True
        # Obvious sets in row
        for row in range(9):
            cells=[pos for pos in positions_row(row) if self.sudoku_grid[pos[0]][pos[1]]=='0']
            for n in range(len(cells)-2):
              dev = obvious_set(n, cells, self.marks)
              if dev != None:
                if self.PRINT_SUDOKUS:
                  print("Row " + str(row+1) + " has a set of "+ str(len(dev['subset']))+ " cells " + str([[pos[0]+1,pos[1]+1] for pos in dev['subset']]) +
                      " where the only marks are " +  str([i+1 for i in dev['numbers_in_subset']]) +
                      " so no marks of those numbers are possible in the other cells of the row, i.e., the following marks should be removed " +
                      str([([pos[0]+1,pos[1]+1],num+1) for (pos,num) in dev['removed_marks']]))
                return True
        # Obvious sets in column
        for column in range(9):
            cells=[pos for pos in positions_column(column) if self.sudoku_grid[pos[0]][pos[1]]=='0']
            for n in range(len(cells)-2):
              dev = obvious_set(n, cells, self.marks)
              if dev != None:
                if self.PRINT_SUDOKUS:
                  print("Column " + str(column+1) + " has a set of "+ str(len(dev['subset']))+ " cells " + str([[pos[0]+1,pos[1]+1] for pos in dev['subset']]) +
                      " where the only marks are " +  str([i+1 for i in dev['numbers_in_subset']]) +
                      " so no marks of those numbers are possible in the other cells of the column, i.e., the following marks should be removed " +
                      str([([pos[0]+1,pos[1]+1],num+1) for (pos,num) in dev['removed_marks']]))
                return True
        return False
    
    def back_tracking(self):
        """Expands a tree search trying all the alternatives in a cell with
        multiple marks. First, tries the cells with the lowest number
        of marks. """
        for posible_marks in range(2,9):
          for i in range(9):
            for j in range(9):
              possible_marks_in_cell=[num for num in range(9) if self.marks[i][j][num]]
              if len(possible_marks_in_cell)==posible_marks:
                possible_solutions=[]
                for num in possible_marks_in_cell:                 
                  sudoku_grid_branch=copy.deepcopy(self.sudoku_grid)
                  sudoku_grid_branch[i][j]=str(num+1)
                  print('Let\'s suppose that the correct number in cell ('+str(i+1)+','+str(j+1)+') is '+str(num+1))
                  sudoku_branch=Sudoku(grid_to_string(sudoku_grid_branch))                  
                  solution=sudoku_branch.solve_sudoku(False)
                  if solution == 'Unsolvable':
                    print('It leads to the sudoku being unsolvable, so mark '+
                          str(num+1)+' is removed from cell ('+str(i)+','+str(j)+')')
                    self.marks[i][j][num]=False
                    return []
                  else:
                    possible_solutions.append(solution)
                    print('This supposition leads to a complete grid')
                if len(possible_solutions)>1:
                  print('There are more than one possible solution so the sudoku is ill-posed: ' + str(possible_solutions))
                  return possible_solutions
                if len(possible_solutions)==1:
                  return possible_solutions[0]
        


"""TESTS"""

easy = Sudoku('004300209005009001070060043006002087190007400050083000600000105003508690042910300')
difficult1 = Sudoku('045020000000001005000080300210000080070000010000000693001906000600000000900300008')
difficult2 = Sudoku('093470060080000000000600001800000030034009005100040000000005200067090010400000000')
difficult3 = Sudoku('040800005090000030308007002030000000000060007105900020000009500004000000802500010')
difficult4 = Sudoku('600130008800000275000728000000069007003080090000400016096000000150604000080000009')
difficult5 = Sudoku('200300010500000000008205000000000235480000100090000800067040000000008070000010003')
difficult6 = Sudoku('600108250510000984800040010400001032281090745700402090926010070058060020000000560')
difficult7 = Sudoku('000000010000002003000400000000000500401600000007100000050000200000080040030910000')
sudoku_ill_posed = Sudoku('000000010000002003000400000000000500401600000007100000050000200000080040030900000')

solution = easy.solve_sudoku()
solution = difficult1.solve_sudoku()
solution = difficult2.solve_sudoku()
solution = difficult3.solve_sudoku()
solution = difficult4.solve_sudoku()
solution = difficult5.solve_sudoku()
solution = difficult6.solve_sudoku()
solution = difficult7.solve_sudoku()
# solution = sudoku_ill_posed.solve_sudoku()


# df1 = pd.read_csv('sudoku.csv', delimiter=',', nrows = None)
# df1.dataframeName = 'sudoku.csv'
# nRow, nCol = df1.shape
# print(f'There are {nRow} rows and {nCol} columns')


# for i in range(nRow):
#     if i % 10000==0:
#         print(i)
#     solution=Sudoku(df1.iloc[i]['quizzes']).solve_sudoku(False)
#     if solution!=df1.iloc[i]['solutions']:
#       print(solution)
#       print(df1.iloc[i]['solutions'])
#       print(str(i)+' ERROR!!!')
#       break
  
        