#! /usr/bin/env python3
"""
A simple example of using curses to create an Etch A Sketch-like program in the terminal.  You can move the
cursor around the screen to draw using the arrow keys and reset it when you like.
"""

import curses
import enum
import logging


class Direction(enum.Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Window():
    """
    Class that contains all the functionality to 
    """
    def __init__(self, stdscr, cursor_x=None, cursor_y=None, buffer_top=1, buffer_bottom=1, 
                buffer_left=1, buffer_right=1, prev_point_char="#", curr_point_char="@", 
                prev_point_color_pair=(curses.COLOR_WHITE, curses.COLOR_BLACK),
                curr_point_color_pair=(curses.COLOR_RED, curses.COLOR_WHITE), message=None, 
                draw_border=True):
        self.stdscr = stdscr
        self.buffer_top = buffer_top
        self.buffer_bottom = buffer_bottom
        self.buffer_left = buffer_left
        self.buffer_right = buffer_right
        self.prev_point_char = prev_point_char
        self.curr_point_char = curr_point_char
        self.prev_point_color_pair = prev_point_color_pair
        self.curr_point_color_pair = curr_point_color_pair
        self.message = message
        self.draw_border = draw_border

        self.cursor_x = None
        self.cursor_y = None

        if cursor_x is None:
            self.initial_cursor_x = buffer_left + 1 if draw_border else buffer_left
        else:
            self.initial_cursor_x = cursor_x

        if cursor_y is None:
            self.initial_cursor_y = buffer_top + 2 if draw_border else buffer_top + 1
        else:
            self.initial_cursor_y = cursor_y

        self.draw_initial_screen()

        return

    def update_boundaries(self):
        """
        Update the window and cursor boundaries.
        """
        self.min_x = self.buffer_left
        self.min_y = self.buffer_top + 1
        self.max_x = curses.COLS - 2 - self.buffer_right
        self.max_y = curses.LINES - 1 - self.buffer_bottom

        if self.draw_border:
            self.cursor_min_x, self.cursor_max_x = self.min_x + 1, self.max_x - 1
            self.cursor_min_y, self.cursor_max_y = self.min_y + 1, self.max_y - 1
        else:
            self.cursor_min_x, self.cursor_max_x = self.min_x, self.max_x
            self.cursor_min_y, self.cursor_max_y = self.min_y, self.max_y

        return

    def draw_box(self):
        """
        Draw a box indicating the cursor boundaries.
        """
        for y in range(self.min_y, self.max_y + 1):
            self.stdscr.addstr(y, self.min_x, "|")
            self.stdscr.addstr(y, self.max_x, "|")

        for x in range(self.min_x, self.max_x + 1):
            self.stdscr.addstr(self.min_y, x, "-")
            self.stdscr.addstr(self.max_y, x, "-")

        return

    def cursor_position_in_bounds(self, x, y):
        """
        Determines whether position x, y is in bounds for the cursor

        Return:
            True: if cursor position is in bounds
            False: otherwise
        """
        if not (self.cursor_min_x <= x <= self.cursor_max_x) or \
                not (self.cursor_min_y <= y <= self.cursor_max_y):
            return False
        else:
            return True

    def update_cursor(self, x, y):
        """
        Updates the cursor potion.

        Args:
            x, y (int): coordinates for new cursor position

        Return:
            None
        """
        # NOTE: redraw the cursor even if the position hasn't changed.  This ensures
        #       a Window that is reinitialized draws the cursor

        # in bounds?
        if not self.cursor_position_in_bounds(x, y):
            raise ValueError(f"Cursor placement is out of bounds")

        # paint current position with prev_point_char
        if self.cursor_x is not None and self.cursor_y is not None:
            try:
                self.stdscr.addstr(self.cursor_y, self.cursor_x, self.prev_point_char, curses.color_pair(1))
            except Exception as e:
                logging.debug(f"error when trying to paint over old position: {e}")
                raise
 
        # paint new position with current_point_char
        try:
            self.stdscr.addstr(y, x, self.curr_point_char, curses.color_pair(2))
        except Exception as e:
            logging.debug(f"error when trying to paint new position: {e}")
            raise
 
        self.cursor_x = x
        self.cursor_y = y
 
        self.stdscr.refresh()
 
        return

    def move_cursor(self, direction, distance=1):
        """
        Move the cursor in specified direction the specified distance.  If new positions is out of
        bounds, do not move cursor.

        Args:
            direction (Direction enum): direction to move
            distance (int)

        Return:
            True:  cursor moved
            False: cursor not moved
        """
        if distance < 1:
            raise ValueError(f"distance ({distance}) must be greater than zero")

        if direction == Direction.LEFT:
            x, y = self.cursor_x - distance, self.cursor_y
        elif direction == Direction.RIGHT:
            x, y = self.cursor_x + distance, self.cursor_y
        elif direction == Direction.UP:
            x, y = self.cursor_x, self.cursor_y - distance
        elif direction == Direction.DOWN:
            x, y = self.cursor_x, self.cursor_y + distance
        else:
            raise ValueError(f"Direction not recognized {direction}")

        if not self.cursor_position_in_bounds(x, y):
            logging.debug(f"Cursor is attempting to move out of bounds, continue without change")
            return False
        
        self.update_cursor(x, y)

        return True

    def draw_initial_screen(self, reset_cursor=True):
        """
        Draw the initial screen with help message at the top, the initial location of the cursor, 
        and a border if specified.
        """
        # clear screen and initialize
        self.stdscr.clear()
        curses.curs_set(False)
        curses.start_color()
        curses.init_pair(1, *self.prev_point_color_pair)
        curses.init_pair(2, *self.curr_point_color_pair)
 
        self.update_boundaries()
        
        # write message
        if self.message is not None:
            self.stdscr.addstr(0, 0, self.message)
 
        # draw border
        if self.draw_border:
            self.draw_box()

        # draw cursor
        if reset_cursor:
            self.cursor_x, self.cursor_y = None, None
            self.update_cursor(self.initial_cursor_x, self.initial_cursor_y)
        else:
            self.update_cursor(self.cursor_x, self.cursor_y)
 
        self.stdscr.refresh()

        return 
    
    def get_key(self):
        """
        Get the key pressed by the user.

        Return:
            key (str)
        """
        return self.stdscr.getkey()


def main(stdscr):
    """
    """
    # User parameters
    log_fp = "logging.txt"
    help_text = "Use the arrow keys to move around. Type c or C to clear the drawing and start over. Type q or Q to exit."

    # NOTE: need to set a foreground and background color
    #   https://docs.python.org/3/howto/curses.html
    #   color options: 'COLOR_BLACK', 'COLOR_BLUE', 'COLOR_CYAN', 'COLOR_GREEN', 'COLOR_MAGENTA', 'COLOR_PAIRS', 'COLOR_RED', 'COLOR_WHITE', 'COLOR_YELLOW'
    prev_point_char = "#"
    curr_point_char = "@"
    prev_point_color_pair = (curses.COLOR_WHITE, curses.COLOR_BLUE)
    curr_point_color_pair = (curses.COLOR_RED, curses.COLOR_WHITE)
    curr_point_color_pair = (curses.COLOR_WHITE, curses.COLOR_GREEN)

    # set up logging
    logging.basicConfig(filename=log_fp, filemode="w", level=logging.INFO)


    # initialize Window object
    window = Window(stdscr,
                    prev_point_char=prev_point_char,
                    curr_point_char=curr_point_char,
                    prev_point_color_pair=prev_point_color_pair,
                    curr_point_color_pair=curr_point_color_pair,
                    message=help_text)

    # move the cursor around and trace its path
    while True:
        
        key = window.get_key() 
        logging.debug(f"key = {key}")

        if key == "KEY_LEFT":
            window.move_cursor(Direction.LEFT)
        elif key == "KEY_RIGHT":
            window.move_cursor(Direction.RIGHT)
        elif key == "KEY_UP":
            window.move_cursor(Direction.UP)
        elif key == "KEY_DOWN":
            window.move_cursor(Direction.DOWN)
        elif key in ("c", "C"):
            logging.debug("clearing")
            window.draw_initial_screen(reset_cursor=False)
            continue
        elif key in ("q", "Q"):
            logging.debug("quitting")
            break
        else:
            # ignore the key if it's not recognized
            logging.debug("key not recognized, continue")
            continue

    return


if __name__ == "__main__":
    curses.wrapper(main)
