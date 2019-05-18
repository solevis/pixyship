import random

ship_layout = """
.
.......XXXXXXXXXX.......
.......XXXXXXXXXXXXXX...
.........XXXXXXXXXXXXX..
............XXXXXXXXXXX.
..........XXXXXXXXXXXXX.
..........XXXXXXXXXXXXX
............XXXXXXXXXXX.
...............XXXXXXXX.
.................XXXX...
...
"""


class Ship:
    ROOM_MARKERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz'
    SPACE = ' '
    SHIP = '.'

    def __init__(self, map_string):
        self.map_string = map_string
        self.layout = self._make_map()
        self.next_room_id = 0
        self.height = len(self.layout)
        self.width = len(self.layout[0])

    def _make_map(self):
        ship_map = self.map_string.replace('.', ' ').replace('X', self.SHIP)
        ship = ship_map.split('\n')

        # Ensure that each floor plan is the same length
        target_len = max([len(f) for f in ship])
        ship = [f + self.SPACE * (target_len - len(f)) for f in ship]

        # Trim empty floors, assumes that ship can't be separated
        ship = [f for f in ship if f.find(self.SHIP) >= 0]

        # Trim sides
        front_trim = min([f.find(self.SHIP) for f in ship])
        back_trim = min([f[::-1].find(self.SHIP) for f in ship])
        ship = [list(f[front_trim:-back_trim]) for f in ship]

        return ship

    def area(self):
        return sum([1 for floor in self.layout for c in floor if c == self.SHIP])

    def print(self):
        print('space:', self.area())
        for floor in self.layout:
            print(' '.join(floor))

    def can_place_room(self, size):
        """Will a room of this size fit?"""
        for y in range(0, len(self.layout)):
            for x in range(0, len(self.layout[0])):
                if self.layout[y][x] == self.SHIP and self._test_room_placement(x, y, size):
                    return True
        return False

    def place_room(self, size):
        """Try to place a room"""
        for y in range(0, len(self.layout)):
            for x in range(0, len(self.layout[0])):
                if self.layout[y][x] == self.SHIP and self._test_room_placement(x, y, size):
                    self._mark_room(x, y, size)
                    return (x, y)

        raise OutOfRoomException

    def place_room_at(self, size, x, y):
        """Try to place a room"""
        if self.layout[y][x] == self.SHIP and self._test_room_placement(x, y, size):
            self._mark_room(x, y, size)

        raise OutOfRoomException

    def place_random_room(self, size):
        """Try to place a room"""
        if not self.can_place_room(size):
            return None

        while True:
            x = random.randint(0, len(self.layout[0]) - 1)
            y = random.randint(0, len(self.layout) - 1)
            if self.layout[y][x] == self.SHIP and self._test_room_placement(x, y, size):
                self._mark_room(x, y, size)
                return (x, y)

    def place_rooms(self, size):
        try:
            while True:
                self.place_room(size)
        except OutOfRoomException:
            pass

    def place_random_rooms(self, size):
        try:
            last_loc = True
            while last_loc:
                last_loc = self.place_random_room(size)
        except OutOfRoomException:
            pass

    def _test_room_placement(self, x, y, size):
        if x + size[0] > len(self.layout[0]):
            return False
        if y + size[1] > len(self.layout):
            return False
        for dx in range(0, size[0]):
            for dy in range(0, size[1]):
                if self.layout[y + dy][x + dx] != self.SHIP:
                    return False
        return True

    def _mark_room(self, x, y, size):
        for dx in range(0, size[0]):
            for dy in range(0, size[1]):
                self.layout[y + dy][x + dx] = self.ROOM_MARKERS[self.next_room_id]
        self.next_room_id += 1

    def reset(self):
        # Remove all indicated rooms
        self.layout = [[c if c == self.SPACE else self.SHIP for c in floor] for floor in self.layout]
        self.next_room_id = 0


class OutOfRoomException(Exception):
    pass


def main():
    # seed = 5
    # print('Seed:', seed)
    # random.seed(seed)

    ship = Ship(ship_layout)
    ship.print()
    ship.place_random_rooms((3, 2))
    ship.print()
    print(ship.map_string)


# This is a script
if __name__ == '__main__':
    main()
