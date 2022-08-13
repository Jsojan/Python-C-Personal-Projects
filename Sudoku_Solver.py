def getel(s):
    #Returns the unique element in a singleton set (or list).
    assert len(s) == 1
    return list(s)[0]

import json

class Sudoku(object):

    def __init__(self, elements):
        if isinstance(elements, Sudoku):
            # We let self.m consist of copies of each set in elements.m
            self.m = [[x.copy() for x in row] for row in elements.m]
        else:
            assert len(elements) == 9
            for s in elements:
                assert len(s) == 9
            # We let self.m be our Sudoku problem, a 9x9 matrix of sets.
            self.m = []
            for s in elements:
                row = []
                for c in s:
                    if isinstance(c, str):
                        if c.isdigit():
                            row.append({int(c)})
                        else:
                            row.append({1, 2, 3, 4, 5, 6, 7, 8, 9})
                    else:
                        assert isinstance(c, set)
                        row.append(c)
                self.m.append(row)


    def show(self, details=False):
        # Prints out the Sudoku matrix.  If details=False, we print out
        # the digits only for cells that have singleton sets (where only
        # one digit can fit).  If details=True, for each cell, we display the
        # sets associated with the cell."""
        if details:
            print("+-----------------------------+-----------------------------+-----------------------------+")
            for i in range(9):
                r = '|'
                for j in range(9):
                    # We represent the set {2, 3, 5} via _23_5____
                    s = ''
                    for k in range(1, 10):
                        s += str(k) if k in self.m[i][j] else '_'
                    r += s
                    r += '|' if (j + 1) % 3 == 0 else ' '
                print(r)
                if (i + 1) % 3 == 0:
                    print("+-----------------------------+-----------------------------+-----------------------------+")
        else:
            print("+---+---+---+")
            for i in range(9):
                r = '|'
                for j in range(9):
                    if len(self.m[i][j]) == 1:
                        r += str(getel(self.m[i][j]))
                    else:
                        r += "."
                    if (j + 1) % 3 == 0:
                        r += "|"
                print(r)
                if (i + 1) % 3 == 0:
                    print("+---+---+---+")


    def to_string(self):
        # This method is useful for producing a representation that
        # can be used in testing."""
        as_lists = [[list(self.m[i][j]) for j in range(9)] for i in range(9)]
        return json.dumps(as_lists)


    @staticmethod
    def from_string(s):
        """Inverse of above."""
        as_lists = json.loads(s)
        as_sets = [[set(el) for el in row] for row in as_lists]
        return Sudoku(as_sets)


    def __eq__(self, other):
        """Useful for testing."""
        return self.m == other.m

#Let us input a problem (the Sudoku example found on [this Wikipedia page](https://en.wikipedia.org/wiki/Sudoku)) and check that our serialization and deserialization works.

# Let us ensure that nose is installed.
try:
    from nose.tools import assert_equal, assert_true
    from nose.tools import assert_false, assert_almost_equal
except:
    # !pip install nose
    from nose.tools import assert_equal, assert_true
    from nose.tools import assert_false, assert_almost_equal

from nose.tools import assert_equal

sd = Sudoku([
    '53__7____',
    '6__195___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___419__5',
    '____8__79'
])
sd.show()
sd.show(details=True)
s = sd.to_string()
sdd = Sudoku.from_string(s)
sdd.show(details=True)
assert_equal(sd, sdd)

# Let's test our constructor statement when passed a Sudoku instance.

sd1 = Sudoku(sd)
assert_equal(sd, sd1)

class Unsolvable(Exception):
    pass


def sudoku_ruleout(self, i, j, x):
    #The input consists in a cell (i, j), and a value x.
    # The function removes x from the set self.m[i][j] at the cell, if present, and:
    # if the result is empty, raises Unsolvable;
    # if the cell used to be a non-singleton cell and is now a singleton
    # cell, then returns the set {(i, j)};
    # otherwise, returns the empty set."""
    c = self.m[i][j]
    n = len(c)
    c.discard(x)
    self.m[i][j] = c
    if len(c) == 0:
        raise Unsolvable()
    return {(i, j)} if 1 == len(c) < n else set()

Sudoku.ruleout = sudoku_ruleout

### Define cell propagation

def sudoku_propagate_cell(self, ij):
    # Propagates the singleton value at cell (i, j), returning the list
    # of newly-singleton cells.
    i, j = ij
    if len(self.m[i][j]) > 1:
        # Nothing to propagate from cell (i,j).
        return set()
    # We keep track of the newly-singleton cells.
    newly_singleton = set()
    x = getel(self.m[i][j]) # Value at (i, j).
    # Same row.
    for jj in range(9):
        if jj != j: # Do not propagate to the element itself.
            newly_singleton.update(self.ruleout(i, jj, x))
    # Same column.
    import math
    for ii in range(9):
        if ii != i:
            newly_singleton.update(self.ruleout(ii, j, x))
    # Same block of 3x3 cells.

    for m in range(3):
        for n in range(3):
            mm = math.floor(i/3)*3 + m
            nn = math.floor(j/3)*3 + n
            if mm != i and nn != j:
                newly_singleton.update(self.ruleout(mm, nn, x))
        
    # Returns the list of newly-singleton cells.
    return newly_singleton

Sudoku.propagate_cell = sudoku_propagate_cell

### Tests for cell propagation

tsd = Sudoku.from_string('[[[5], [3], [2], [6], [7], [8], [9], [1, 2, 4], [2]], [[6], [7], [1, 2, 4, 7], [1, 2, 3], [9], [5], [3], [1, 2, 4], [8]], [[1, 2], [9], [8], [3], [4], [1, 2], [5], [6], [7]], [[8], [5], [9], [1, 9, 7], [6], [1, 4, 9, 7], [4], [2], [3]], [[4], [2], [6], [8], [5], [3], [7], [9], [1]], [[7], [1], [3], [9], [2], [4], [8], [5], [6]], [[1, 9], [6], [1, 5, 9, 7], [9, 5, 7], [3], [9, 7], [2], [8], [4]], [[9, 2], [8], [9, 2, 7], [4], [1], [9, 2, 7], [6], [3], [5]], [[3], [4], [2, 3, 4, 5], [2, 5, 6], [8], [6], [1], [7], [9]]]')
tsd.show(details=True)
try:
    tsd.propagate_cell((0, 2))
except Unsolvable:
    print("Good! It was unsolvable.")
else:
    raise Exception("Hey, it was unsolvable")

tsd = Sudoku.from_string('[[[5], [3], [2], [6], [7], [8], [9], [1, 2, 4], [2, 3]], [[6], [7], [1, 2, 4, 7], [1, 2, 3], [9], [5], [3], [1, 2, 4], [8]], [[1, 2], [9], [8], [3], [4], [1, 2], [5], [6], [7]], [[8], [5], [9], [1, 9, 7], [6], [1, 4, 9, 7], [4], [2], [3]], [[4], [2], [6], [8], [5], [3], [7], [9], [1]], [[7], [1], [3], [9], [2], [4], [8], [5], [6]], [[1, 9], [6], [1, 5, 9, 7], [9, 5, 7], [3], [9, 7], [2], [8], [4]], [[9, 2], [8], [9, 2, 7], [4], [1], [9, 2, 7], [6], [3], [5]], [[3], [4], [2, 3, 4, 5], [2, 5, 6], [8], [6], [1], [7], [9]]]')
tsd.show(details=True)
assert_equal(tsd.propagate_cell((0, 2)), {(0, 8), (2, 0)})

def sudoku_propagate_all_cells_once(self):
    """This function propagates the constraints from all singletons."""
    for i in range(9):
        for j in range(9):
            self.propagate_cell((i, j))

Sudoku.propagate_all_cells_once = sudoku_propagate_all_cells_once

sd = Sudoku([
    '53__7____',
    '6__195___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___419__5',
    '____8__79'
])
sd.show()
sd.propagate_all_cells_once()
sd.show()
sd.show(details=True)

### Exercise: define full propagation

def sudoku_full_propagation(self, to_propagate=None):
    if to_propagate is None:
        to_propagate = {(i, j) for i in range(9) for j in range(9)}
    # This code is the (A) code; will be referenced later.

    while len(to_propagate) > 0:
      m = to_propagate.pop()
      to_propagate.update(self.propagate_cell(m))


Sudoku.full_propagation = sudoku_full_propagation

### Tests for full propagation

sd = Sudoku([
    '53__7____',
    '6__195___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___419__5',
    '____8__79'
])
sd.full_propagation()
sd.show(details=True)
sdd = Sudoku.from_string('[[[5], [3], [4], [6], [7], [8], [9], [1], [2]], [[6], [7], [2], [1], [9], [5], [3], [4], [8]], [[1], [9], [8], [3], [4], [2], [5], [6], [7]], [[8], [5], [9], [7], [6], [1], [4], [2], [3]], [[4], [2], [6], [8], [5], [3], [7], [9], [1]], [[7], [1], [3], [9], [2], [4], [8], [5], [6]], [[9], [6], [1], [5], [3], [7], [2], [8], [4]], [[2], [8], [7], [4], [1], [9], [6], [3], [5]], [[3], [4], [5], [2], [8], [6], [1], [7], [9]]]')
assert_equal(sd, sdd)

sd = Sudoku([
    '53__7____',
    '6___95___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___41___5',
    '____8__79'
])
sd.show()
sd.full_propagation()
sd.show(details=True)


sd.show(details=True)
# Let's save this Sudoku for later.
sd_partially_solved = Sudoku(sd)

def sudoku_done(self):
    #Checks whether an instance of Sudoku is solved.
    for i in range(9):
        for j in range(9):
            if len(self.m[i][j]) > 1:
                return False
    return True

Sudoku.done = sudoku_done


def sudoku_search(self, new_cell=None):
    """Tries to solve a Sudoku instance."""
    to_propagate = None if new_cell is None else {new_cell}
    self.full_propagation(to_propagate=to_propagate)
    if self.done():
        return self # We are a solution
    # We need to search.  Picks a cell with as few candidates as possible.
    candidates = [(len(self.m[i][j]), i, j)
                   for i in range(9) for j in range(9) if len(self.m[i][j]) > 1]
    _, i, j = min(candidates)
    values = self.m[i][j]
    # values contains the list of values we need to try for cell i, j.
    # print("Searching values", values, "for cell", i, j)
    for x in values:
        # print("Trying value", x)
        sd = Sudoku(self)
        sd.m[i][j] = {x}
        try:
            # If we find a solution, we return it.
            return sd.search(new_cell=(i, j))
        except Unsolvable:
            # Go to next value.
            pass
    # All values have been tried, apparently with no success.
    raise Unsolvable()

Sudoku.search = sudoku_search


def sudoku_solve(self, do_print=True):
    #Wrapper function, calls self and shows the solution if any.
    try:
        r = self.search()
        if do_print:
            print("We found a solution:")
            r.show()
            return r
    except Unsolvable:
        if do_print:
            print("The problem has no solutions")

Sudoku.solve = sudoku_solve

sd = Sudoku([
    '53__7____',
    '6___95___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___41___5',
    '____8__79'
])
_ = sd.solve()



### Define full propagation with where can it go

def sudoku_full_propagation_with_where_can_it_go(self, to_propagate=None):
    """Iteratively propagates from all singleton cells, and from all
    newly discovered singleton cells, until no more propagation is possible."""
    if to_propagate is None:
        to_propagate = {(i, j) for i in range(9) for j in range(9)}
    while len(to_propagate) > 0:
        # Here is the previous solution but changed.

        while len(to_propagate) > 0:
          m = to_propagate.pop()
          to_propagate.update(self.propagate_cell(m))
          
        # Now we check whether there is any other propagation that we can
        # get from the where can it go rule.
        to_propagate = self.where_can_it_go()


### Define helper function to check once-only occurrence

from collections import defaultdict

def occurs_once_in_sets(set_sequence):
    # Returns the elements that occur only once in the sequence of sets set_sequence.
    l = defaultdict(int)
    for m in set_sequence:
      for n in m:
        l[n] += 1
    return {a for a in l if l.get(a) < 2}


### Tests for once-only

from nose.tools import assert_equal

assert_equal(occurs_once_in_sets([{1, 2}, {2, 3}]), {1, 3})
assert_equal(occurs_once_in_sets([]), set())
assert_equal(occurs_once_in_sets([{2, 3, 4}]), {2, 3, 4})
assert_equal(occurs_once_in_sets([set()]), set())
assert_equal(occurs_once_in_sets([{2, 3, 4, 5, 6}, {5, 6, 7, 8}, {5, 6, 7}, {4, 6, 7}]), {2, 3, 8})

### Exercise: write where_can_it_go

def sudoku_where_can_it_go(self):
    #Sets some cell values according to the where can it go
    # heuristics, by examining all rows, colums, and blocks.
    newly_singleton = set()

    import math
    values = set()

    # rows
    for idx, m in enumerate(self.m):
        put_in = []
        for n in m:
            put_in.append(n)
        for num, ind in upgraded_occurs(put_in):
            if len(self.m[idx][ind]) > 1:
                self.m[idx][ind] = {num}
                values.add((idx, ind))

    #columns
    for idx, x in enumerate(range(9)):
        put_in = []
        for y in range(9):
            put_in.append(self.m[y][x])
        for num, ind in upgraded_occurs(put_in):
            if len(self.m[ind][idx]) > 1:
                self.m[ind][idx] = {num}
                values.add((ind, idx))

    #blocks    
    for br in range(3):
        for bc in range(3):
            put_in = []
            rs = br*3
            cs = bc*3
            for x in range(3):
                for y in range(3):
                    put_in.append(self.m[rs+x][cs+y])
            for num, ind in upgraded_occurs(put_in):
                if len(self.m[rs+math.floor(ind/3)][cs+ind%3]) > 1:
                    self.m[rs+math.floor(ind/3)][cs+ind%3] = {num}
                    values.add((rs+math.floor(ind/3), cs+ind%3))
                

    #store newly_singleton in values
    newly_singleton = values

    # Returns the list of newly-singleton cells.
    return newly_singleton

Sudoku.where_can_it_go = sudoku_where_can_it_go

# Helper function which updates each rowm, column or block with values that can be added above

def upgraded_occurs(set_sequence):

    l = defaultdict(int)
    for m in set_sequence:
        for n in m:
            l[(n)] = l[n]+1
    one = {s for s in l if l.get(s) < 2}
    occur = set()
    for a in one:
        for idx, b in enumerate(set_sequence):
            if a in b:
                occur.add((a,idx))
    return occur

### Tests for where can it go

sd = Sudoku.from_string('[[[5], [3], [1, 2, 4], [1, 2, 6], [7], [1, 2, 6, 8], [4, 8, 9], [1, 2, 4], [2, 8]], [[6], [1, 4, 7], [1, 2, 4, 7], [1, 2, 3], [9], [5], [3, 4, 8], [1, 2, 4], [2, 7, 8]], [[1, 2], [9], [8], [1, 2, 3], [4], [1, 2], [3, 5], [6], [2, 7]], [[8], [1, 5], [1, 5, 9], [1, 7, 9], [6], [1, 4, 7, 9], [4, 5], [2, 4, 5], [3]], [[4], [2], [6], [8], [5], [3], [7], [9], [1]], [[7], [1, 5], [1, 3, 5, 9], [1, 9], [2], [1, 4, 9], [4, 5, 8], [4, 5], [6]], [[1, 9], [6], [1, 5, 7, 9], [5, 7, 9], [3], [7, 9], [2], [8], [4]], [[2, 9], [7, 8], [2, 7, 9], [4], [1], [2, 7, 9], [6], [3], [5]], [[2, 3], [4, 5], [2, 3, 4, 5], [2, 5, 6], [8], [2, 6], [1], [7], [9]]]')
print("Original:")
sd.show(details=True)
new_singletons = set()
while True:
    new_s = sd.where_can_it_go()
    if len(new_s) == 0:
        break
    new_singletons |= new_s
assert_equal(new_singletons,
             {(3, 2), (2, 6), (7, 1), (5, 6), (2, 8), (8, 0), (0, 5), (1, 6),
              (2, 3), (3, 7), (0, 3), (5, 1), (0, 8), (8, 5), (5, 3), (5, 5),
              (8, 1), (5, 7), (3, 1), (0, 6), (1, 8), (3, 6), (5, 2), (1, 1)})
print("After where can it go:")
sd.show(details=True)
sdd = Sudoku.from_string('[[[5], [3], [1, 2, 4], [6], [7], [8], [9], [1, 2, 4], [2]], [[6], [7], [1, 2, 4, 7], [1, 2, 3], [9], [5], [3], [1, 2, 4], [8]], [[1, 2], [9], [8], [3], [4], [1, 2], [5], [6], [7]], [[8], [5], [9], [1, 9, 7], [6], [1, 4, 9, 7], [4], [2], [3]], [[4], [2], [6], [8], [5], [3], [7], [9], [1]], [[7], [1], [3], [9], [2], [4], [8], [5], [6]], [[1, 9], [6], [1, 5, 9, 7], [9, 5, 7], [3], [9, 7], [2], [8], [4]], [[9, 2], [8], [9, 2, 7], [4], [1], [9, 2, 7], [6], [3], [5]], [[3], [4], [2, 3, 4, 5], [2, 5, 6], [8], [6], [1], [7], [9]]]')
print("The above should be equal to:")
sdd.show(details=True)
assert_equal(sd, sdd)

sd = Sudoku([
    '___26_7_1',
    '68__7____',
    '1____45__',
    '82_1___4_',
    '__46_2___',
    '_5___3_28',
    '___3___74',
    '_4__5__36',
    '7_3_18___'
])
print("Another Original:")
sd.show(details=True)
print("Propagate once:")
sd.propagate_all_cells_once()
# sd.show(details=True)
new_singletons = set()
while True:
    new_s = sd.where_can_it_go()
    if len(new_s) == 0:
        break
    new_singletons |= new_s
print("After where can it go:")
sd.show(details=True)
sdd = Sudoku.from_string('[[[4], [3], [5], [2], [6], [9], [7], [8], [1]], [[6], [8], [2], [5], [7], [1], [4], [9], [3]], [[1], [9], [7], [8], [3], [4], [5], [6], [2]], [[8], [2], [6], [1], [9], [5], [3], [4], [7]], [[3], [7], [4], [6], [8], [2], [9], [1], [5]], [[9], [5], [1], [7], [4], [3], [6], [2], [8]], [[5], [1], [1, 2, 5, 6, 8, 9], [3], [2], [6], [1, 2, 8, 9], [7], [4]], [[2], [4], [1, 2, 8, 9], [9], [5], [7], [1, 2, 8, 9], [3], [6]], [[7], [6], [3], [4], [1], [8], [2], [5], [9]]]')
print("The above should be equal to:")
sdd.show(details=True)
assert_equal(sd, sdd)

sd = Sudoku(sd_partially_solved)
newly_singleton = sd.where_can_it_go()
print("Newly singleton:", newly_singleton)
print("Resulting Sudoku:")
sd.show(details=True)


Sudoku.full_propagation = sudoku_full_propagation_with_where_can_it_go

sd = Sudoku([
    '53__7____',
    '6___95___',
    '_98____6_',
    '8___6___3',
    '4__8_3__1',
    '7___2___6',
    '_6____28_',
    '___41___5',
    '____8__79'
])
print("Initial:")
sd.show()
sd.full_propagation()
print("After full propagation with where can it go:")
sd.show()

