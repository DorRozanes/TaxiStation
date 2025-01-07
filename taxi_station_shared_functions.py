import math
import random
from entities.order import Order, order_status
from entities.taxi import taxi_status


def distance(x1,y1,x2,y2):
    d2 = ((x1 - x2) ** 2) + ((y1 - y2) ** 2)
    return math.sqrt(d2)

def new_order(index):
    while True:
        order = Order(index, random.uniform(1,20000), random.uniform(1,20000))
        order_length = distance(order.pick_x, order.pick_y, order.dest_x, order.dest_y)
        if order_length <= 2000:
            return order

def choose_taxi_to_order(order, available_taxis):
    chosen_taxi = 0
    chosen_taxi_distance = distance(available_taxis[chosen_taxi].current_x, available_taxis[chosen_taxi].current_y, order.pick_x, order.pick_y)
    for i,taxi in enumerate(available_taxis[1:]):
        scanned_taxi_distance = distance(taxi.current_x, taxi.current_y, order.pick_x, order.pick_y)
        if scanned_taxi_distance < chosen_taxi_distance:
            chosen_taxi = i
            chosen_taxi_distance = distance(available_taxis[chosen_taxi].current_x, available_taxis[chosen_taxi].current_y, order.pick_x, order.pick_y)
    return available_taxis[chosen_taxi].index

def assign_taxi_to_order(order, taxi):
    order.taxi = taxi.index
    order.status = order_status.waiting
    taxi.order_index = order.index
    taxi.state = taxi_status.picking
    taxi.dest_x = order.pick_x
    taxi.dest_y = order.pick_y
    return order, taxi

def pick_up_order(taxi, order):
    order.taxi = taxi.index
    order.status = order_status.picked
    taxi.dest_x = order.dest_x
    taxi.dest_y = order.dest_y
    taxi.state = taxi_status.dropping
    return taxi, order

def drop_order(taxi):
    taxi.state = taxi_status.idle
    taxi.dest_x = None
    taxi.dest_y = None
    taxi.order_index = None
    return taxi

def driving_during_tick(taxi):
    dx = abs(taxi.dest_x - taxi.current_x)
    dy = abs(taxi.dest_y - taxi.current_y)
    remaining_velocity = taxi.velocity
    if dx != 0:
        if taxi.dest_x > taxi.current_x:
            forward = 1
        else:
            forward = -1

        if dx > taxi.velocity:
            taxi.current_x = taxi.current_x + (taxi.velocity * forward)
            return taxi
        else:
            remaining_velocity = taxi.velocity - dx
            taxi.current_x = taxi.dest_x

    if dy != 0:
        if taxi.dest_y > taxi.current_y:
            up = 1
        else:
            up = -1

        if dy > remaining_velocity:
            taxi.current_y = taxi.current_y + (remaining_velocity * up)
            return taxi
        else:
            taxi.current_y = taxi.dest_y
    return taxi
