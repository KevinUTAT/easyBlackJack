#!/usr/bin/python3
#
# table.py
#
# Implements a two-dimension table where all cells must be of same type
#
 
from collections.abc import Sized
 
class Table:
   #
   # Initializes an instance of Table class
   #
   # celltype: type of each cell in table
   # xlabels: labels of x-axis
   # ylables: labels of y-axis
   # unit: unit of each cell (printed as suffix)
   #
    def __init__(self, celltype, xlabels, ylabels, unit=""):
       if not isinstance(celltype, type):
           raise TypeError("celltype must be a type (e.g. str, float)")
       self.celltype = celltype
       self.xlabels = tuple(xlabels)
       self.ylabels = tuple(ylabels)
       self.unit = unit
 
       self.table = [[None for j in range(24)] for i in range(35)] 
       # TODO: finish me
       return
  
   #
   # "private" member function to validate key
   #
    def _validate_key(self, key):
       if not isinstance(key, Sized):
           raise TypeError("key must be a sized container")
       if len(key) != 2:
           raise KeyError("key must have exactly two elements")
       # unpack key to row and column
       row, col = key   
       if row not in self.ylabels:
           raise KeyError("%s is not a valid y-label"%str(row))
       if col not in self.xlabels:
           raise KeyError("%s is not a valid x-label"%str(col))
       return row, col
      
   #
   # Overloads index operator for assigning to a cell
   #
   # key: key of the cell
   # value: value of the cell (must be of type 'celltype')
   #   
    def __setitem__(self, key, value):
       if not isinstance(value, self.celltype):
           raise TypeError("value must be of type %s"%(self.celltype.__name__))
       row, col = self._validate_key(key)
 
       self.table[self.ylabels.index(row)][self.xlabels.index(col)] = value
      
       return self.table[self.ylabels.index(row)][self.xlabels.index(col)]
 
   #
   # Overloads index operator for retrieving a value from a cell
   #
   # key: key of the cell
   #   
    def __getitem__(self, key):
       row, col = self._validate_key(key)
      
       # TODO: implement me
       return self.table[self.ylabels.index(row)][self.xlabels.index(col)]
 
   #
   # Overloads index operator for deleting a cell's value. You should
   # set the cell's value back to None
   #
   # key: key of the cell
   # 
    def __delitem__(self, key):
       row, col = self._validate_key(key)
       self.table[self.ylabels.index(row)][self.xlabels.index(col)] = None
       # TODO: implement me
       return

    def __str__(self):
        # column width
        colwidth = 6 if self.celltype is float else 2
    
        # y-label width (for first column)
        ylwidth = max([len(str(y)) for y in self.ylabels])
    
        # print title row (space delimited labels)
        print(" ".join([ " "*ylwidth ] + 
            [ str(x)[:colwidth].center(colwidth) for x in self.xlabels ]))
    
        # print each row from the table
        for y in self.ylabels:
            row = [ str(y).rjust(ylwidth) ]
            for x in self.xlabels:
                val = self[y,x]
                if val is None:
                    text = '-' * colwidth
                elif self.unit == '%':
                    # crash now if probability table has a value error
                    assert(isinstance(val, float) and val >= 0.)
                    text = "%.3f%%"%(val*100)
                elif isinstance(val, float):
                    text = "%.3f"%val if val < 0 else " %.3f"%val
                else:
                    text = str(val)[:colwidth].center(colwidth)
                row.append(text)
            print(" ".join(row))
        return '\nEnd Table\n'
  
 


