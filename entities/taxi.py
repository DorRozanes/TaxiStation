from enum import Enum
import random

class taxi_status(Enum):
    idle = 1
    picking = 2
    dropping = 3

class Taxi():
    def __init__(self, taxi_index, velocity = 0.3):
        self.index = taxi_index
        self.current_x = random.uniform(0,20000)
        self.current_y = random.uniform(0,20000)
        self.state = taxi_status.idle
        self.order_index = None
        self.dest_x = None
        self.dest_y = None
        self.velocity = velocity

    def order_location(self, order_list):
        for idx, order in enumerate(order_list):
            if order.index == self.order_index:
                return idx
        return -1

