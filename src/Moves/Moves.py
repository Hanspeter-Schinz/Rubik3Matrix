#! /usr/bin/python
# $Header$

import numpy as np
import copy
from colorama import init, Fore, Back, Style

class Moves:
  pass

  

'''
  here are the move 54x54 matrices for a 3x3x3 rubiks cube
  and some tests
'''

CUBE_SIZE = 3 # 3x3x3 cube
NUMBER_OF_SQUARES = 6 # a cube has 6 squares
MOVES_PER_SLICE = 4 # a move can be 90, 180, 270 or 360(identity) degree
TOTAL_SQUARE_ELEMENTS = NUMBER_OF_SQUARES * CUBE_SIZE * CUBE_SIZE # a cube has 6 squares with CUBE_SIZE*CUBE_SIZE elements

# for internal tests ( should not be used anywhere else )
# there are a unique number in each element to see errors in move matrices
# a real cube later run has only [0..NUMBER_OF_SQUARES-1] values
__IDENTITY_ARRAY = np.array( [ k for k in range( TOTAL_SQUARE_ELEMENTS ) ] )

'''
for displaying nxnxn cube over multiple lines

3x3x3 cube output layout (indices)
( 0- 3)  00 01 02
( 3- 6)  03 04 05
( 6- 9)  06 07 08
( 9-21)  09 10 11 12 13 14 15 16 17 18 19 20
(21-33)  21 22 23 24 25 26 27 28 29 30 31 32
(33-45)  33 34 35 36 37 38 39 40 41 42 43 44
(45-48)  45 46 47
(48-51)  48 49 50
(51-54)  51 52 53

2x2x2 cube output layout (indices)
( 0- 2) 00 01
( 2- 4) 02 03
( 4-12) 04 05 06 07 08 09 10 11
(12-20) 12 13 14 15 16 17 18 19
(20-22) 20 21
(22-24) 22 23
'''
def line_display_offset( s:int = CUBE_SIZE ):
  num_elems_per_line = []
  num_elems_per_line.extend( [                             s for k in range( s ) ] )
  num_elems_per_line.extend( [ ( NUMBER_OF_SQUARES - 2 ) * s for k in range( s ) ] )
  num_elems_per_line.extend( [                             s for k in range( s ) ] )

  offsets_1 = [ sum( num_elems_per_line[:k] ) for k in range( len( num_elems_per_line ) ) ]
  offsets_2 = offsets_1[1:]
  offsets_2.append( NUMBER_OF_SQUARES * s * s )

  offset_pairs = list( tuple( zip( tuple( offsets_1 ), tuple( offsets_2 ) ) ) )

  # if you want to understand the construction please set debug_print = True
  debug_print = False
  #debug_print = True
  if debug_print:
    print( f'num_elems_per_line: {num_elems_per_line}')
    print( f'offsets_1: {offsets_1}')
    print( f'offsets_2: {offsets_2}')
    print( f'offset_pairs: {offset_pairs}')
  return offset_pairs
  
LINE_DISPLAY_OFFSETS = line_display_offset()
  
# types
permut_type = list[ list [ int ] ]

def display_test_array( cube:str = __IDENTITY_ARRAY ) -> str:
  out = ''
  for ( x, y ) in LINE_DISPLAY_OFFSETS:
    out += ' '.join( [ f'{cube[ i ]:02d}' for i in range( x, y ) ] ) + '\n'
  return out


'''
There are 3 possible moves per slice (90, 180 and 270 degrees, 360 is the identity or zero move)
With a fix upper left back corner we have 3 move directions to use (front,right and down)
The number of slices is 1 less than the dimension of the cube
for eg. a 2x2x2 cube, we have   1 slice,  3 moves and 3 directions -> 1*3*3     =       9 possible moves
for eg. a 3x3x3 cube, we have   2 slices, 3 moves and 3 directions -> 2*3*3     =      18 possible moves
for eg. a nxnxn cube, we have n-1 slices, 3 moves and 3 directions -> (n-1)*3*3 = (n-1)*9 possible moves

for all subsequent moves we have 3 moves less to try, because we do not have to turn the same slice twice
eg. when we start with a front move F(90) and have a second F(180) we could have started with a single F(270) move
eg for 3*3*3 cube Sn = 1 + 18 * sum( 15^k ) k [0..(n-1)]
eg for 2*2*2 cube Sn = 1 +  9 * sum(  6^k ) k [0..(n-1)]
'''
def calc_move_sum(  n: int ) -> int:
  num_moves = len( MOVES_INDEX )
  return 1 + num_moves * sum( [ ( num_moves - MOVES_PER_SLICE + 1 ) ** k for k in range( n ) ] )

'''
  size: size of cube array
  permuts: a list of all 4 element permutation to execute

  Example permutation with 4 elements

  Cube C eg one square:
  1 2 -> 4 1
  4 3    3 2

  Permutation (rotate clock wise) P:
  ( 1 2 3 4 )
  ( 4 1 2 3 )

  Orthogonal Matrix M:
        1 2 3 4
  
  1  ( 0 0 0 1 )   ( 1 )   ( 4 )
  2  | 1 0 0 0 | * | 2 | = | 1 |
  3  | 0 1 0 0 |   | 3 |   | 2 |
  4  ( 0 0 1 0 )   ( 4 )   ( 3 )
'''
def construct_rotator_matrix( size: int, permuts: permut_type = [] ):
  # start with identity and modify the permut stuff
  # dtype i8 seems to be the quickest one
  matrix = np.identity( size, dtype = 'i8' )
  for perm in permuts:
    # do the permutation
    matrix[ perm[ 0 ], perm[ 3 ] ] = 1
    matrix[ perm[ 3 ], perm[ 2 ] ] = 1
    matrix[ perm[ 2 ], perm[ 1 ] ] = 1
    matrix[ perm[ 1 ], perm[ 0 ] ] = 1
    for elem in perm:
      # unset diagonal elements
      matrix[ elem, elem ] = 0
  return( matrix )

def display_rotator_matrix( mat )->str:
  # find actual input parameter variable name
  init( autoreset = True )
  globals_dict = globals()
  locals_dict  = locals()
  dict = globals_dict | locals_dict
  my_name = [ var_name for var_name in dict if dict[ var_name ] is mat ]
  disp_name = 'unknown'
  try:
    disp_name = my_name[ 0 ]
  except:
    pass
  my_size = len( mat )
  out = ''
  out += f"Colored rotator matrix: {disp_name}, size {my_size}" + '\n'
  out += '    ' + f''.join( [f'{n:3}' for n in range( my_size )] ) + '\n' # rows titles
  out += f'{Style.RESET_ALL}\n'.join( [ f'{idx:2}: ' + ''.join( [ Fore.RED + f'{item:3}' if item > 0 else Fore.GREEN + f'{item:3}' for item in row ] ) for idx, row in enumerate( mat ) ] ) + '\n'
  return out

# move matrices
IDENT = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS )
  
F11 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [  6, 12, 47, 44 ],
    [  7, 24, 46, 32 ],
    [  8, 36, 45, 20 ],
    [  9, 11, 35, 33 ],
    [ 10, 23, 34, 21 ],
  ] )
F12 = F11.dot( F11 )
F13 = F12.dot( F11 )
F14 = F13.dot( F11 ) # identity

F21 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [  3, 13, 50, 43 ],
    [  4, 25, 49, 31 ],
    [  5, 37, 48, 19 ],
] )
F22 = F21.dot( F21 )
F23 = F22.dot( F21 )
F24 = F23.dot( F21 ) # identity

R11 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [  2, 39, 47, 11 ],
    [  5, 27, 50, 23 ],
    [  8, 15, 53, 35 ],
    [ 12, 14, 38, 36 ],
    [ 13, 26, 37, 24 ],
  ] )
R12 = R11.dot( R11 )
R13 = R12.dot( R11 )
R14 = R13.dot( R11 ) # identity

R21 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [  1, 40, 46, 10 ],
    [  4, 28, 49, 22 ],
    [  7, 16, 52, 34 ],
  ] )
R22 = R21.dot( R21 )
R23 = R22.dot( R21 )
R24 = R23.dot( R21 ) # identity

D11 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [ 33, 36, 39, 42 ],
    [ 34, 37, 40, 43 ],
    [ 35, 38, 41, 44 ],
    [ 45, 47, 53, 51 ],
    [ 46, 50, 52, 48 ],
  ] )
D12 = D11.dot( D11 )
D13 = D12.dot( D11 )
D14 = D13.dot( D11 ) # identity

D21 = construct_rotator_matrix( TOTAL_SQUARE_ELEMENTS,
  [
    [ 21, 24, 27, 30 ],
    [ 22, 25, 28, 31 ],
    [ 23, 26, 29, 32 ],
] )
D22 = D21.dot( D21 )
D23 = D22.dot( D21 )
D24 = D23.dot( D21 ) # identity

# enumerate moves
F11I = 0
F21I = 1
R11I = 2
R21I = 3
D11I = 4
D21I = 5

F12I = 6
F22I = 7
R12I = 8
R22I = 9
D12I = 10
D22I = 11

F13I = 12
F23I = 13
R13I = 14
R23I = 15
D13I = 16
D23I = 17

MOVES_INDEX = [ # 0,    1,    2,    3,    4,    5
                  F11I, F21I, R11I, R21I, D11I, D21I,
                  F12I, F22I, R12I, R22I, D12I, D22I,
                  F13I, F23I, R13I, R23I, D13I, D23I,
            ] 

# permutation matrices
MOVES = [ # 0,   1,   2,   3,   4,   5
            F11, F21, R11, R21, D11, D21,
            F12, F22, R12, R22, D12, D22,
            F13, F23, R13, R23, D13, D23,
        ] 

# my moves
DISPLAY_MOVES = {
  'standard' :
  [ # 0,     1,     2,     3,     4,     5
    "F",   "S",   "R",   "M",   "D",   "E",
    "FF",  "SS",  "RR",  "MM",  "DD",  "EE",
    "F'",  "S'",  "R'",  "M'",  "D'",  "E'",
  ],
  'mine' :
  [ # 0,     1,     2,     3,     4,     5
    'F1',  'F2',  'R1',  'R2',  'D1',  'D2',
    'F12', 'F22', 'R12', 'R22', 'D12', 'D22',
    'F1-', 'F2-', 'R1-', 'R2-', 'D1-', 'D2-',
  ],
  'color' :
  [ # 0,     1,     2,     3,     4,     5
    'Y ',  'y ',  'O ',  'o ',  'G ',  'g',
    'Y2',  'y2',  'O2',  'o2',  'G2',  'g2',
    'Y-',  'y-',  'O-',  'o-',  'G-',  'g-',
  ],
}

def execute_move_sequence( mat, move_sequence ):
  for move in move_sequence:
    mat = move.dot( mat )
  return mat  

if __name__ == "__main__": # pragma: no cover
  m = Moves()
  # execute only if run as a script
  print( DISPLAY_MOVES )
  print( MOVES_INDEX )

  for idx, mat in enumerate( MOVES ): 
    print( f'Index: {idx}: {mat}' )
    # lasts quite long
    #display_rotator_matrix( mat )

  print( display_rotator_matrix( IDENT ) )
  print( display_rotator_matrix( MOVES[ 0 ] ) )

  # print out the number of moves for a specific recursion level
  gods_number = 20
  for n in range( 0, gods_number + 1 ):
    # eg. 1234567 -> 1'234'567
    print( f' {n:2d}: {calc_move_sum( n ):,}'.replace( ',', "'" ) )

  for num in range( 5 ):
    print( f'Cube size: {num}' )
    op = line_display_offset( num )
    print( f'Offset pairs[{len( op ):02d}]: {op}' )
    print( 80 * '=' )

  print( display_rotator_matrix( IDENT ) )
  print( display_rotator_matrix( MOVES[ 0 ] ) )

  print( display_test_array() )
  print( display_test_array( __IDENTITY_ARRAY ) )

  move_array = MOVES
  move_array = [ D11 ]
  result_array = copy.copy( __IDENTITY_ARRAY )
  for mat in move_array:
    result_array = mat.dot( result_array )
  
  print( display_test_array( result_array ) )

  # find identity move sequences (repeated)
  result = IDENT
  for cnt in range( 1, 1001 ):
    move_list = MOVES
    move_list = [ F11, R11, D11, F12, R12, D12, F13, R13, D13, F21, R21, D21, F22, R22, D22, F23, F23, F23 ]
    result = execute_move_sequence( result, move_list )
    if ( result == IDENT ).all():
      print( display_rotator_matrix( result ) )
      print( f'{cnt}' )
      break
  
