from enum import Enum
import random
import math
import numpy as np

class order_status(Enum):
    waiting = 1
    picked = 2
    in_queue = 3

class Order():
    def __init__(self,
                 order_index,
                 x,
                 y,
                 ):
        self.pick_x = x
        self.pick_y = y
        self.status = order_status.in_queue
        self.index = order_index
        self.taxi = None

        # Generating random destination: up to 2000 m away, and inside the 20 km boundary
        angle = random.uniform(0,2 * np.pi)
        distance = random.uniform(0,2000)
        self.dest_x = x + (distance * np.cos(angle))
        self.dest_y = y + (distance * np.sin(angle))
        if self.dest_x > 20000:
            self.dest_x = 20000 - (self.dest_x - 20000)
        if self.dest_y > 20000:
            self.dest_y = 20000 - (self.dest_y - 20000)
