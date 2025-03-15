import random
import heapq
import numpy as np


class DungeonGenerator:
    """Generates a random dungeon map using procedural algorithms with pathfinding."""

    def __init__(self, width=20, height=10, num_rooms=5):
        self.width = width
        self.height = height
        self.num_rooms = num_rooms
        self.map = np.full((height, width), "#")  # Walls by default
        self.rooms = []
        self.start = None  # Entrance of the dungeon
        self.exit = None  # Exit of the dungeon

    def generate(self):
        """Generates the dungeon layout with rooms, corridors, and an exit."""
        self._generate_rooms()
        self._connect_rooms()
        self._place_traps_treasures_and_exit()

    def _generate_rooms(self):
        """Randomly places rooms in the dungeon."""
        for _ in range(self.num_rooms):
            w, h = random.randint(3, 7), random.randint(3, 7)

            # Ensure valid x and y ranges
            max_x = max(1, self.width - w - 2)
            max_y = max(1, self.height - h - 2)

            # Prevent randrange errors
            if max_x <= 1 or max_y <= 1:
                x, y = 1, 1  # Fallback placement at (1,1)
            else:
                x = random.randint(1, max_x)
                y = random.randint(1, max_y)

            if not self._room_overlaps(x, y, w, h):
                self.rooms.append((x, y, w, h))
                self._carve_room(x, y, w, h)

    def _room_overlaps(self, x, y, w, h):
        """Checks if a room overlaps with existing ones."""
        for rx, ry, rw, rh in self.rooms:
            if x < rx + rw and x + w > rx and y < ry + rh and y + h > ry:
                return True  # Overlapping
        return False

    def _carve_room(self, x, y, w, h):
        """Carves out a room by replacing walls with empty space."""
        for i in range(y, y + h):
            for j in range(x, x + w):
                self.map[i][j] = "."

    def _connect_rooms(self):
        """Connects rooms with corridors."""
        for i in range(len(self.rooms) - 1):
            x1, y1, _, _ = self.rooms[i]
            x2, y2, _, _ = self.rooms[i + 1]
            self._create_corridor(x1, y1, x2, y2)

    def _create_corridor(self, x1, y1, x2, y2):
        """Creates a simple L-shaped corridor between two points."""
        if random.choice([True, False]):
            self._horizontal_tunnel(x1, x2, y1)
            self._vertical_tunnel(y1, y2, x2)
        else:
            self._vertical_tunnel(y1, y2, x1)
            self._horizontal_tunnel(x1, x2, y2)

    def _horizontal_tunnel(self, x1, x2, y):
        """Creates a horizontal corridor."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[y][x] = "."

    def _vertical_tunnel(self, y1, y2, x):
        """Creates a vertical corridor."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[y][x] = "."

    def _place_traps_treasures_and_exit(self):
        """Places traps (T), treasures ($), entrance (E), and exit (X)."""
        for x, y, w, h in self.rooms:
            if random.random() < 0.5:
                self.map[y + random.randint(0, h - 1)][x + random.randint(0, w - 1)] = "T"  # Trap
            if random.random() < 0.7:
                self.map[y + random.randint(0, h - 1)][x + random.randint(0, w - 1)] = "$"  # Treasure

        # Select a start and exit point
        self.start = random.choice(self.rooms)[:2]
        self.exit = random.choice(self.rooms)[:2]
        self.map[self.start[1]][self.start[0]] = "E"  # Entrance
        self.map[self.exit[1]][self.exit[0]] = "X"  # Exit

    def find_shortest_path(self):
        """Finds the shortest path from Entrance (E) to Exit (X) using A* algorithm."""

        def heuristic(a, b):
            """Manhattan distance heuristic for A*."""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def neighbors(position):
            """Finds valid neighbors for A* search."""
            x, y = position
            options = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            return [(nx, ny) for nx, ny in options if
                    0 <= nx < self.width and 0 <= ny < self.height and self.map[ny][nx] != "#"]

        start, goal = self.start, self.exit
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in neighbors(current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return "No Path Found"

    def _reconstruct_path(self, came_from, current):
        """Reconstructs the shortest path from A* search."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        return path[::-1]

    def display(self):
        """Prints the dungeon map with shortest path."""
        path = self.find_shortest_path()
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in path:
                    print("*", end="")  # Mark shortest path with *
                else:
                    print(self.map[y][x], end="")
            print()


# --- Example Usage ---
if __name__ == "__main__":
    dungeon = DungeonGenerator(width=20, height=10, num_rooms=6)
    dungeon.generate()
    dungeon.display()
