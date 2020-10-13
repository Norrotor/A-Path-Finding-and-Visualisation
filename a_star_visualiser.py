"""
A* path finding algorithm visualiser.

Keymap:
    - Mouse1 (left click): place node (first start, then end, then barriers)
    - Mouse2 (right click): remove node
    - SPACE: start the path generation and visualisation
    - Q: stop the path visualisation early
    - R: reset the grid

Node colors are as follow:
    - red: closed node (node and all neighbors already visited)
    - green: open node (node is open for visitation)
    - black: barrier (blocks path)
    - orange: start node
    - turquoise: end node
    - purple: path node

Last modified: 2020-10-13
Author: Norrotor
"""

import pygame
from queue import PriorityQueue
from time import sleep
from typing import Tuple, List, Dict

# Screen dimensions (square screen)
SCREEN_WIDTH = 600

# Number of rows in the grid. Also represents the number of cells per row.
NUM_ROWS = 25

# Time between each step of the algorithm.
SLEEP_TIME = 0.0

# RGB colours for the game
colors = {
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "turquoise": (0, 255, 255),
    "purple": (255, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 200, 0)
}

GAME_WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption("A* path visualisation tool")


class Node:
    """Class of nodes in the grid."""

    # Map from color to node state and backwards
    states = {
        colors["red"]: "closed",
        "closed": colors["red"],

        colors["green"]: "open",
        "open": colors["green"],

        colors["black"]: "barrier",
        "barrier": colors["black"],

        colors["orange"]: "start",
        "start": colors["orange"],

        colors["turquoise"]: "end",
        "end": colors["turquoise"],

        colors["purple"]: "path",
        "path": colors["purple"],
    }

    def __init__(self, row: int, column: int, width: int, total_rows: int) -> None:
        """Initialise a node's properties. The x and y represent the node's coordinates in pygame.

        :param row: node's row (in the grid)
        :param column: node's column (in the grid)
        :param width: node's width, also the height because it's a square
        :param total_rows: total number of rows; is also the number of nodes per row
        """

        self.row = row
        self.column = column
        self.width = width
        self.total_rows = total_rows
        self.x = row * width  # Node's x coordinate, used when drawing the node
        self.y = column * width  # Node's y coordinate, used when drawing the node
        self.color = colors["white"]
        self.neighbors = list()  # List of available (non-barrier) neighbor nodes

    def get_pos(self) -> Tuple[int, int]:
        return self.row, self.column

    # Following are a bunch of getters and setters for the node's color

    def is_closed(self) -> bool:
        return self.color == self.states["closed"]

    def is_open(self) -> bool:
        return self.color == self.states["open"]

    def is_barrier(self) -> bool:
        return self.color == self.states["barrier"]

    def is_start(self) -> bool:
        return self.color == self.states["start"]

    def is_end(self) -> bool:
        return self.color == self.states["end"]

    def is_path(self) -> bool:
        return self.color == self.states["path"]

    def make_closed(self) -> None:
        self.color = self.states["closed"]

    def make_open(self) -> None:
        self.color = self.states["open"]

    def make_barrier(self) -> None:
        self.color = self.states["barrier"]

    def make_start(self) -> None:
        self.color = self.states["start"]

    def make_end(self) -> None:
        self.color = self.states["end"]

    def make_path(self) -> None:
        self.color = self.states["path"]

    def reset(self) -> None:
        self.color = colors["white"]
        self.neighbors = list()

    # End of getters and setters for the color

    def draw_node(self, surface: pygame.display) -> None:
        """Draws the node on the given surface.

        :param surface: surface to draw on
        """

        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid: List[list]) -> None:
        """Adds the non-barrier neighbor nodes to the list of neighbor nodes.

        :param grid: grid containing the nodes
        """

        # Node above
        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.column])

        # Node below
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.column])

        # Node on the left
        if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column - 1])

        # Node on the right
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column + 1])

    def __lt__(self, other):
        """This is needed because PriorityQueue compares nodes and we don't care about the comparison."""
        return False


def manhattan_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
    """Calculate and return the Manhattan distance between two points.

    :param point1: first point
    :param point2: second point
    :return: Manhattan distance between the two points
    """

    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)


def create_grid(total_rows: int, surface_width: int) -> List[list]:
    """Create and return a grid (list of lists) of white nodes.

    :param total_rows: total number of rows; is also the number of nodes per row
    :param surface_width: width of surface
    :return: grid of nodes
    """

    node_width = surface_width // total_rows
    grid = [[Node(row, column, node_width, total_rows) for column in range(total_rows)] for row in range(total_rows)]

    return grid


def draw_grid_lines(surface: pygame.display, total_rows: int, surface_width: int) -> None:
    """Draw the lines separating the nodes on the given surface.

    :param surface: surface to draw on
    :param total_rows: total number of rows; is also the number of nodes per row
    :param surface_width: width of the surface
    """

    node_width = surface_width // total_rows
    for i in range(total_rows):
        pygame.draw.line(surface, colors["gray"], (0, i * node_width), (surface_width, i * node_width))
        pygame.draw.line(surface, colors["gray"], (i * node_width, 0), (i * node_width, surface_width))


def draw_nodes_in_grid(surface: pygame.display, grid: list, total_rows: int, surface_width: int) -> None:
    """Draw the nodes and the grid (lines separating the nodes) on the given surface.

    :param surface: surface to draw on
    :param grid: grid containing the nodes
    :param total_rows: total number of rows; is also the number of nodes per row
    :param surface_width: width of the surface
    """

    surface.fill(colors["white"])

    for row in grid:
        for node in row:
            node.draw_node(surface)

    draw_grid_lines(surface, total_rows, surface_width)
    pygame.display.update()


def reconstruct_path(draw_function: callable, origin_node: Dict[Node, Node], end_node: Node) -> None:
    """Reconstruct the path from the end node to the first.

    :param draw_function: function which updates the screen with the changes made
    :param origin_node: map of node to the previous node
    :param end_node: node where the path ends
    """

    current_node = end_node

    while current_node in origin_node:
        current_node = origin_node[current_node]
        current_node.make_path()
        draw_function()


def generate_path(draw_function: callable, grid: List[list],
                  start_node: Node, end_node: Node) -> None:
    """The path-finding algorithm.

    :param draw_function: function which updates the screen with the changes made
    :param grid: list of nodes
    :param start_node: node where the path starts
    :param end_node: node where the path ends
    """

    # Keeps track of how many nodes are checked; used for the 'f_score':
    # if a node has a 'count' lower than another, it means that it was checked earlier, so the path
    # is probably shorter.
    #
    # Using a counter also makes the path smoother.
    count = 0
    origin_node = dict()

    open_set = PriorityQueue()
    open_set.put((0, count, start_node))  # Format is '(f_score, count, node)'

    # This is used to check if a node is present in the open set,
    # because PriorityQueue doesn't support the 'in' operator.
    open_set_hash = {start_node}

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start_node] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start_node] = manhattan_distance(start_node.get_pos(), end_node.get_pos())

    while not open_set.empty():
        for event in pygame.event.get():
            # Path visualisation can be stopped by either pressing the quit button or the 'Q' key.
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                return

        current_node = open_set.get()[2]
        open_set_hash.remove(current_node)  # The node has to removed from both, but the 'get' method does that for us.

        if current_node == end_node:  # The algorithm ends when the end node has the lowest score.
            reconstruct_path(draw_function, origin_node, end_node)
            # The end nodes get changed to path nodes, so we have to make them the correct color again.
            end_node.make_end()
            start_node.make_start()
            return

        for neighbor in current_node.neighbors:
            temp_g_score = g_score[current_node] + 1  # Lower g_score is better

            if temp_g_score < g_score[neighbor]:  # Lower g_score is better
                origin_node[neighbor] = current_node
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + manhattan_distance(neighbor.get_pos(), end_node.get_pos())

                # Neighbor node not present in the open set, so it gets added.
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        if current_node != start_node:
            current_node.make_closed()

        # When it gets added to the open set its color changes, so it has to be set back, else it would stay green
        # until the path reconstruction happens.
        #
        # Could instead check that the neighbor is not the end node when changing the color, but I guess checking
        # for every neighbor is more expensive than just changing it anyways.
        end_node.make_end()

        draw_function()  # Updates the color changes in the grid

        sleep(SLEEP_TIME)  # Waits the appropriate amount of time before the next step


def get_clicked_position(coords: Tuple[float, float], total_rows: int, surface_width: int) -> Tuple[int, int]:
    """Calculate and return row and column from the mouse coordinates given by pygame.

    :param coords: mouse coordinates given by pygame
    :param total_rows: number of rows; is also the number of nodes per row
    :param surface_width: width of the surface (game window)
    :return: (row, column) which was clicked
    """

    node_width = surface_width // total_rows
    x, y = coords

    row = int(x // node_width)
    column = int(y // node_width)

    return row, column


def main(window: pygame.display, window_width: int) -> None:
    """Main visualiser loop.

    :param window: pygame window
    :param window_width: width of the window; is also the height since it's a square
    """

    grid = create_grid(NUM_ROWS, window_width)  # List of the nodes

    start_node = None
    end_node = None

    run = True

    while run:
        draw_nodes_in_grid(window, grid, NUM_ROWS, window_width)
        for event in pygame.event.get():
            # Ends game if the user presses the exit button.
            if event.type == pygame.QUIT:
                run = False

            # User pressed left mouse button
            elif pygame.mouse.get_pressed()[0]:
                mouse_click_position = pygame.mouse.get_pos()
                x, y = get_clicked_position(mouse_click_position, NUM_ROWS, window_width)
                clicked_node = grid[x][y]

                # Start node not set; doesn't overwrite the end node
                if not start_node and clicked_node != end_node:
                    start_node = clicked_node
                    start_node.make_start()

                # End node not set; doesn't overwrite the start node
                elif not end_node and clicked_node != start_node:
                    end_node = clicked_node
                    end_node.make_end()

                # Both start and end node set, clicked node will become a barrier
                elif clicked_node != start_node and clicked_node != end_node:
                    clicked_node.make_barrier()

            # User pressed right mouse button
            elif pygame.mouse.get_pressed()[2]:
                mouse_click_position = pygame.mouse.get_pos()
                x, y = get_clicked_position(mouse_click_position, NUM_ROWS, window_width)
                clicked_node = grid[x][y]
                clicked_node.reset()

                # User wants to reset the start node
                if clicked_node == start_node:
                    start_node = None

                # User wants to reset the end node
                elif clicked_node == end_node:
                    end_node = None

            # Key presses
            elif event.type == pygame.KEYDOWN:
                # Starts the path generation and visualisation if the key 'SPACE' is pressed
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            # Resets every node, except barriers and the end points.
                            if not node.is_barrier() and not node.is_end() and not node.is_start():
                                node.reset()
                            node.update_neighbors(grid)  # Marks neighbors for visit

                    # Starts the path finding and visualisation
                    generate_path(lambda: draw_nodes_in_grid(GAME_WINDOW, grid, NUM_ROWS, SCREEN_WIDTH), grid,
                                  start_node, end_node)

                # Resets every node if the key 'R' is pressed
                elif event.key == pygame.K_r:
                    window.fill(colors["white"])
                    for row in grid:
                        for node in row:
                            node.reset()
                    start_node = None
                    end_node = None

    pygame.quit()


if __name__ == "__main__":
    main(GAME_WINDOW, SCREEN_WIDTH)
