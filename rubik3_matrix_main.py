#! /usr/bin/python
# $Header$

import argparse
import time

from src.Moves  import Moves  as rmov
from src.Matrix import Matrix as rmat

# read (and display) command line arguments
# default value display with given formatter_class
c_size = rmov.CUBE_SIZE
parser = argparse.ArgumentParser(
  description =
f'''
rubik {c_size}x{c_size}x{c_size} matrix test app:
this app will test a given {c_size}x{c_size}x{c_size} cube for solutions in the given depth range
'''
  , formatter_class = argparse.ArgumentDefaultsHelpFormatter
  )
parser.add_argument(
  '-i'
  , '--input_file'
  , action = 'store'
  , dest = 'input_file'
  , type = argparse.FileType( 'rt' )
  , help = f'input rubiks cube file ( *.rub{c_size} )'
  )

parser.add_argument(
  '-d'
  , '--depth'
  , action = 'store'
  , default = 5
  , dest = 'recursion_depth'
  , type = int
  , choices = range( 12 )
  , help = 'recursion depth(more than 7 could be very slow !!!!)'
  )

parser.add_argument(
  '-f'
  , '--format'
  , action = 'store'
  , default = list( rmov.DISPLAY_MOVES.keys() )[ 0 ]
  , dest = 'format'
  , type = str
  , choices = rmov.DISPLAY_MOVES.keys()
  , help = 'move display format'
  )

parser.add_argument(
  '--show'
  , action = argparse.BooleanOptionalAction
  , default = True
  , help = 'shows intermediate results during find solutions'
  )

parser.add_argument(
  '-v'
  , '--version'
  , action = 'version'
  , version = f'rubic {c_size} matrix 1.0 beta'
  , help = 'gives out program version'
  )

args = ''
try:
  # print parser.parse_args()
  args = parser.parse_args()
except IOError as err:
  parser.error( str( err ) )

rubik_file = args.input_file

# default input if no input file defined
cube_str = rmat.DEFAULT_TEST_CUBE_STR

c = rmat.Rubik3Matrix()

try:
  if rubik_file:
    c.read_file( rubik_file )
  else:
    c.read_cube( cube_str )
except Exception as err:    
  print( err )
  exit( 3 )        

c.recursion_depth   = args.recursion_depth
c.intermediate_show = args.show
c.format            = args.format

print( c )

# performance measurement
start = time.perf_counter()
c.search_for_solutions()
end = time.perf_counter()
total_time = end - start

if not c.intermediate_show:
  c.display_move_list()

# statistics
print( c.statistics( total_time ) )

exit( 0 )        
