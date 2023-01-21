import unittest
from src.Moves  import Moves  as rmov
from src.Matrix import Matrix as rmat
import numpy as np
import copy
import os

class TestRubikInit( unittest.TestCase ):
  def setUp( self ):
    self.c = rmat.Rubik3Matrix()

  def tearDown( self ):
    pass

  @unittest.skip( "demonstrating skipping" )
  def test_nothing_skip( self ):
    self.fail( "shouldn't happen" )

  def test_initial_cube_size( self ):
    self.assertEqual( len( self.c.cube ), rmov.TOTAL_SQUARE_ELEMENTS )

  def test_initial_cube_values( self ):
    self.assertTrue( np.array_equal( self.c.cube, rmat.CUBE_IDENTITY ) )

class TestRubikInputAndCheck( unittest.TestCase ):
  def setUp( self ):
    pass

  def tearDown( self ):
    pass

  @unittest.expectedFailure
  def test_cube_default_not_ident( self ):
    c = rmat.Rubik3Matrix( rmat.DEFAULT_TEST_CUBE_STR )
    self.assertTrue( np.array_equal( c.cube, rmat.CUBE_IDENTITY ) )

  def test_too_many_elements( self ):  
    with self.assertRaises( IndexError ):
      too_many_elements = rmat.DEFAULT_TEST_CUBE_STR + 'D'
      c = rmat.Rubik3Matrix( too_many_elements )

  def test_illegal_square_elements( self ):  
    # we try an illegal square element 'X' (allowed are 'U' 'F' 'B' 'R' 'L' 'D') at the end of a correct input
    with self.assertRaises( ValueError ):
      illegal_square = rmat.DEFAULT_TEST_CUBE_STR[:-1] + 'X'
      c = rmat.Rubik3Matrix( illegal_square )

  def test_internal_value_out_of_bounds( self ):  
    # values allowed 0..5, we try 6
    with self.assertRaises( IndexError ):
      c = rmat.Rubik3Matrix()
      c.cube = np.append( c.cube[:-1], 6 )
      c.check_cube()

  def test_too_many_U( self ):  
    # we try too many 'U' elements
    with self.assertRaises( IndexError ):
      too_many_U = rmat.DEFAULT_TEST_CUBE_STR[:-1] + 'U'
      c = rmat.Rubik3Matrix( too_many_U )

class TestRubikReadWrite( unittest.TestCase ):
  def setUp( self ):
    self.test_file = 'test.rub'
    self.c = rmat.Rubik3Matrix()
    self.c.write_file( self.test_file )

  def tearDown( self ):
    os.remove( self.test_file )
    pass

  
  def test_read( self ):
    c = rmat.Rubik3Matrix()
    c.read_file( self.test_file )
    self.assertTrue( np.array_equal( self.c.cube, c.cube ) )

class TestRubikMovesIdent( unittest.TestCase ):
  def setUp( self ):
    self.c = rmat.Rubik3Matrix()
    self.c_save = copy.deepcopy( self.c )

  def tearDown( self ):
    pass

  # moves (equal)
  def test_initial_cube_R14( self ):
    self.c.cube =  rmov.R14.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )

  def test_initial_cube_R24( self ):
    self.c.cube = rmov.R24.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )
    
  def test_initial_cube_D14( self ):
    self.c.cube = rmov.D14.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )
    
  def test_initial_cube_D24( self ):
    self.c.cube = rmov.D14.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )
    
  def test_initial_cube_F14( self ):
    self.c.cube = rmov.F14.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )
    
  def test_initial_cube_F24( self ):
    self.c.cube = rmov.F24.dot( self.c.cube )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )

  # move combinations
  def test_initial_cube_R12_F12_x_6( self ):
    move_sequence = [ rmov.R12, rmov.F12 ] * 6
    self.c.exec_move_sequence( move_sequence )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )

  def test_initial_cube_F11_R11_x_105( self ):
    move_sequence = [ rmov.F11, rmov.R11 ] * 105
    self.c.exec_move_sequence( move_sequence )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )

class TestRubikMovesNotIdent( unittest.TestCase ):
  def setUp( self ):
    self.c = rmat.Rubik3Matrix()
    self.c_save = copy.deepcopy( self.c )

  def tearDown( self ):
    pass

  # moves not equal
  @unittest.expectedFailure
  def test_initial_cube_R12_F12_x_3( self ):
    move_sequence = [ rmov.R12, rmov.F12 ] * 3
    self.c.exec_move_sequence( move_sequence )
    self.assertTrue( np.array_equal( self.c.cube, self.c_save.cube ) )

@unittest.skip( "showing class skipping" )
class TestRubikSkipClass( unittest.TestCase ):
  def test_nothing_class( self ):
    self.fail( "shouldn't happen" )

if __name__ == '__main__':
  unittest.main()
