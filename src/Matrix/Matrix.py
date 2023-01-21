#! /usr/bin/python
# $Header$

import os
import numpy as np
import copy
import time
from colorama import init, Fore, Back, Style
from src.Moves import Moves as rmov

from threading import Thread # for experiments only 
from multiprocessing import Process # for experiments only

'''
  this is software to simulate a 3x3x3 rubiks cube

  cube identity
  0 0 0                     U U U
  0 0 0                     U U U
  0 0 0                     U U U 
  1 1 1 2 2 2 4 4 4 3 3 3   F F F R R R B B B L L L
  1 1 1 2 2 2 4 4 4 3 3 3   F F F R R R B B B L L L
  1 1 1 2 2 2 4 4 4 3 3 3   F F F R R R B B B L L L
  5 5 5                     D D D
  5 5 5                     D D D
  5 5 5                     D D D
'''

# cube squares
COLORS  = [ Back.BLUE, Back.YELLOW, Back.RED, Back.MAGENTA, Back.WHITE, Back.GREEN ]     
SQUARES = [ 'U', 'F', 'R', 'L', 'B', 'D' ] # (U)p, (F)ront, (R)ight, (L)eft, (B)ack, (D)own
INV_SQUARES = { 'U':0, 'F':1, 'R':2, 'L':3, 'B':4, 'D':5 }

# types
cube_type  = list[ int ]
moves_type = list

# solved cube
CUBE_IDENTITY = np.array( [
  0, 0, 0,
  0, 0, 0,
  0, 0, 0,
  1, 1, 1, 2, 2, 2, 4, 4, 4, 3, 3, 3,
  1, 1, 1, 2, 2, 2, 4, 4, 4, 3, 3, 3,
  1, 1, 1, 2, 2, 2, 4, 4, 4, 3, 3, 3,
  5, 5, 5,
  5, 5, 5,
  5, 5, 5,
  ] )

# replaces numbers with corresponding letter
# eg. 0 -> 'U' .. 5 -> 'D'
CUBE_IDENTITY_STRING = ''.join( [ SQUARES[ CUBE_IDENTITY[ k ] ] for k in range( len( CUBE_IDENTITY ) ) ] )

# this is an easy default test cube
DEFAULT_TEST_CUBE_STR = '''
  // test input
  // move sequence [ R' D R ] -> solution [ R' D' R ]

  // (U)p
  UUU
  UUU
  UUL
  // (F)ront (R)ight (B)ack (L)eft
  FFD        FRR     BBB    LLL
  FFD        FRR     BBB    LLL
  LLF        URR     BRR    DBB
  // (D)own
  DDR
  DDD
  FFD // lst input line
  '''
# compares 2 cube numerical arrays
# this is faster than __eq__ in class
def compare( c1:cube_type, c2:cube_type ) -> bool:
  # take fastest one
  return ( c1 == c2 ).all()
  #return ( operator.eq( c1, c2)).all()
  #return np.array_equal( c1, c2 )

class Rubik3Matrix:
  def __init__( self, cube_text = CUBE_IDENTITY_STRING ):
    self.read_cube( cube_text )
    self.recursion_depth = 0
    self.num_solutions = 0
    self.num_calls = 0
    self.format = 0
    self.found_solution = False
    self.move_list = []
    self.intermediate_show = False
    self.solutions = {}

  def __eq__( self, other ):
    return ( self.cube == other.cube).all() 

  def copy( self ):
    return copy.deepcopy( self )

  def __str__( self, comment = '', color = True ):
    init( autoreset = True )
    out = comment if '' == comment else '// ' + comment + '\n'
    for ( x, y ) in rmov.LINE_DISPLAY_OFFSETS:
        if color:
          out += ''.join( [ f'{COLORS[ self.cube[ i ] ] }{SQUARES[ self.cube[ i ] ]:2}{Style.RESET_ALL}' for i in range( x, y ) ] ) + '\n'
        else:
          out += ' '.join( [ f'{SQUARES[ self.cube[ i ] ] }' for i in range( x, y ) ] ) + '\n'
    return out

  def statistics( self, run_time_secs ):
    out = ( 80 * '=' ) + '\n'
    out += 'Statistics\n'
    out += f'Recursion depth:     {self.recursion_depth}\n'
    out += f'Found solution:      {self.found_solution}\n'
    out += f'Number of solutions: {self.num_solutions}\n'
    out += f'Number of calls:     {self.num_calls}\n'
    out += f'Number of calls/sec: {self.num_calls / run_time_secs}\n'
    out += f'Runtime in seconds:  {run_time_secs}\n'
    out += ( 80 * '=' ) + '\n'
    return out


  def cube_init( self, cube_input = CUBE_IDENTITY ):
    self.cube = np.array( cube_input ) 

  def check_cube( self ):
    # basic sanity check of a cube
    # number of elements
    if rmov.TOTAL_SQUARE_ELEMENTS != len( self.cube ):
      raise IndexError( f'!!!! error in Cube, number of square elements must be {rmov.TOTAL_SQUARE_ELEMENTS} but is {len( self.cube )}' )

    # squares check (each square must appear exactly CUBE_SIZE**2)
    sum_squares = [ 0, 0, 0, 0, 0, 0 ]
    for square in self.cube:
        try:
            sum_squares[ square ] += 1
        except:
            raise IndexError( f"!!!! error in Cube, square {square} out of range: must be in {INV_SQUARES}" )
    for idx, square in enumerate( sum_squares ):
        if rmov.CUBE_SIZE * rmov.CUBE_SIZE != square:
            raise ValueError( f"!!!! error in Cube, wrong number of square '{SQUARES[ idx ]}' = {idx}: must occur {rmov.CUBE_SIZE * rmov.CUBE_SIZE} times but is {square} times" )

  '''
  reads a file with 3x3x3 rubik's cube data
  comments have to start with //
  translates input squares into their corresponding integer 
  -> see INV_SQUARES definition
  file content see -> DEFAULT_CUBE_STR
  '''
  def read_cube( self, cube_text: str ):
    c = []
    for num_line, line in enumerate( cube_text.split( '\n' ) ):
        # eliminate all comments (must begin with //)
        code = ( line.split( '//' ) ) [ 0 ]

        # eliminate all whitespaces from line
        for num_col, ch in enumerate( ''.join( code.split() ) ):
            # only interested T, F, R, B, L, D
            if ch in SQUARES:
                #print( f'ch "{ch}, val "{INV_SQUARES[ ch ]}""' )
                c.append( INV_SQUARES[ ch ] )
            else:
                raise ValueError( f"got square element '{ch}' at line {num_line + 1} position {num_col + 1} but must have one of {SQUARES}" ) 
    self.cube_init( c )
    self.check_cube()

  def write_cube( self, msg:str = None )->str:
    text_array = [ SQUARES[ k ] for k in self.cube ]
    out =  f'// {rmov.CUBE_SIZE}x{rmov.CUBE_SIZE}x{rmov.CUBE_SIZE} cube' + '\n'
    if msg:
      out += '// ' + msg + '\n'
    out += '\n'
    for ( x, y ) in rmov.LINE_DISPLAY_OFFSETS:
      out += ' '.join( [ f'{text_array[ i ]}' for i in range( x, y ) ] ) + '\n'
    return out
    
  def read_file( self, file_name: str ):
    with open( file_name, 'r' ) as f:
      out = f.read()
    self.read_cube( out )

  def write_file( self, file_name: str, msg:str = None ):
    out = self.write_cube( msg )
    with open( file_name, 'w' ) as f:
      f.write( out )

  '''
      cube (numpy array)
      move_list (normal array)
      n.  recursion depth
  '''
  def find_solutions( self, cube: cube_type, move_list: moves_type, rec_level: int ):
    self.num_calls += 1
    if rec_level >= self.recursion_depth:
      return

    threads = []    
    processes = []
    modulus = ( rmov.CUBE_SIZE - 1 ) * (rmov.MOVES_PER_SLICE - 1 )    
    for ( index, move ) in enumerate( rmov.MOVES ):
      if 0 == len( move_list ) or 0 != ( move_list[ -1 ] - index ) % modulus:
        cube_n = move.dot( cube ) # do the actual move
        # do a real copy of the array
        # take fastest one
        move_list_n = move_list[:]
        #move_list_n = copy.copy( move_list )
        #move_list_n = [ n for n in move_list ]

        move_list_n.append( rmov.MOVES_INDEX[ index ] )
        
        if compare( CUBE_IDENTITY, cube_n ):
          self.num_solutions += 1
          move_list_txt = ' '.join( [ rmov.DISPLAY_MOVES[ self.format ][ i ] for i in move_list_n ] )
          self.solutions[ self.num_solutions ] = ( self.num_calls, len( move_list_n ), move_list_txt )
          if self.intermediate_show:
            print( f'  Solution #: {self.num_solutions:5d}; Call #: {self.num_calls:11d}; {len( move_list_n):2d} Move(s): ' + move_list_txt )
          self.found_solution = True
          # return # only shortest solution of a path wanted
        
        if rec_level == -1:
          # process experiments
          p = Process( target = self.find_solutions, args = ( cube_n, move_list_n, rec_level + 1 ) )
          processes.append( p )
          p.start()
          # thread experimenrts
          t = Thread( target = self.find_solutions, args = ( cube_n, move_list_n, rec_level + 1 ) )
          threads.append( t )
          t.start()
        else:
          self.find_solutions( cube_n, move_list_n, rec_level + 1 )

    # wait for the threads to complete
    if rec_level == -1:
      # process experiments
      for p in processes:
        p.join()
      # threads experiments
      for t in threads:
        t.join()
    
  def exec_move_sequence( self, move_sequence: list ):
    cube_n = self.cube
    for move in move_sequence:
      cube_n = move.dot( cube_n )
    self.cube = cube_n

  def search_for_solutions( self ):
    self.find_solutions( self.cube, self.move_list, 0 )

  def display_move_list( self ):
    print( f"{'Solution'};{'Calls'};{'Len'};{'Moves'}")
    for cnt in self.solutions:
      calls, length, move_txt = self.solutions[ cnt ] 
      print( f'{cnt};{calls};{length};' + move_txt )  

if __name__ == "__main__": # pragma: no cover
  # execute only if run as a script

  test_input = DEFAULT_TEST_CUBE_STR
  
  id = Rubik3Matrix()
  print( id )  
  c = Rubik3Matrix( test_input )
  print( c )

  d = c.copy()
  print( d, 'd' )

  c.cube = rmov.R21.dot( c.cube )
  print( c, 'R21' )

  c.cube = rmov.R21.dot( c.cube )
  print( c, 'R22' )

  c.cube = rmov.R21.dot( c.cube )
  print( c, 'R2-' )

  c.cube = rmov.R21.dot( c.cube )
  print( c, 'R4' )

  #print( c.cube )
  #print( d.cube )

  if ( d == c ):
    print( 'equal' )
  else:
    print( 'not equal' )
            
  c.cube = rmov.R13.dot( c.cube )
  c.cube = rmov.D11.dot( c.cube )
  c.cube = rmov.R11.dot( c.cube )
  print( c )

  def perf_moves():
    c = Rubik3Matrix()
    # all possible moves 
    move_sequence = rmov.MOVES * 50000
    #move_sequence = [ F11, R11, D11 ] * 300000
      
    start = time.perf_counter()
    c.exec_move_sequence( move_sequence )
    end = time.perf_counter()
    total_time = end - start

    print( 'Move performance test' )
    print( f'total_time   : {total_time}' )
    print( f'# moves      : {len( move_sequence )}' )
    print( f'moves/sec    : {len(move_sequence) / total_time}' )

  def perf_compares():
    c1 = Rubik3Matrix()
    c2 = Rubik3Matrix( test_input )

    start = time.perf_counter()
    max = 900000
    for cnt in range( max ):
      cmp = compare( c1.cube, c2.cube )
    end = time.perf_counter()
    total_time = end - start

    print( 'Compare performance test' )
    print( f'total_time   : {total_time}' )
    print( f'# compares   : {max}' )
    print( f'compares/sec : {max / total_time}' )

  def perf_eq():
    c1 = Rubik3Matrix()
    c2 = Rubik3Matrix( test_input )

    start = time.perf_counter()
    max = 900000
    for cnt in range( max ):
      cmp = ( c1 == c2 )
    end = time.perf_counter()
    total_time = end - start

    print( '__eq__ performance test' )
    print( f'total_time   : {total_time}' )
    print( f'# compares   : {max}' )
    print( f'compares/sec : {max / total_time}' )

  perf_moves()
  perf_compares()
  perf_eq()

  txt = c.write_cube('My first test output' )
  print( txt )
  file = 'temp.rub3'
  c.write_file( file, txt )
  os.remove( file )
