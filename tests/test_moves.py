import unittest

from src.Moves import Moves as rmov

import numpy as np
import copy

# for internal tests
# there are a unique number in each element to see errors in move matrices
# a real cube later run has only [0..5] values
IDENTITY_ARRAY = np.array( [ k for k in range( rmov.TOTAL_SQUARE_ELEMENTS ) ] )

class TestMovesIdentity( unittest.TestCase ):
  def setUp( self ):
    self.result_array = copy.copy( IDENTITY_ARRAY )

  def tearDown( self ):
    pass

  def test_F14( self ):
    self.result_array = rmov.F14.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_F24( self ):
    self.result_array = rmov.F24.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_R14( self ):
    self.result_array = rmov.R14.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_R24( self ):
    self.result_array = rmov.R24.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_D14( self ):
    self.result_array = rmov.D14.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_D24( self ):
    self.result_array = rmov.D24.dot( self.result_array ) 
    self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )

  def test_move_sequence( self ):
    result = rmov.IDENT
    move_list = [ rmov.F12, rmov.R12 ] * 6
    result = rmov.execute_move_sequence( result, move_list )
    if ( result == rmov.IDENT ).all():
      print( rmov.display_rotator_matrix( result ) )
  
  '''
  def test_xx( self ):
    for mat in rm.MOVES:
      self.result_array = mat.dot( self.result_array ) 
    #self.assertTrue( np.array_equal( self.result_array, IDENTITY_ARRAY ) )
  '''

if __name__ == '__main__':
  unittest.main()
