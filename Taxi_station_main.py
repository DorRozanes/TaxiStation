import pandas as pd

import taxi_station_shared_functions as tssf
from entities.tick import Tick
from entities.taxi import Taxi, taxi_status
from entities.order import order_status
import streamlit as st
import altair as alt
import numpy as np

fps = 24 # ticks per second
velocity = 250 # meters per second
order_frequency = 10 # How many seconds for new order

# Function to update the plot
def update_plot(taxis, orders, plot_container, color_scale):
    taxi_x = [taxi.current_x for taxi in taxis]
    taxi_y = [taxi.current_y for taxi in taxis]
    taxi_df = pd.DataFrame({'x':taxi_x, 'y': taxi_y, 'series': 'Taxis'})

    waiting_x = [order.pick_x for order in orders if order.status == order_status.waiting]
    waiting_y = [order.pick_y for order in orders if order.status == order_status.waiting]
    waiting_df = pd.DataFrame({'x':waiting_x, 'y': waiting_y, 'series': 'Pending orders'})

    picked_x = [order.dest_x for order in orders if order.status == order_status.picked]
    picked_y = [order.dest_y for order in orders if order.status == order_status.picked]
    picked_df = pd.DataFrame({'x': picked_x, 'y': picked_y, 'series': 'Destinations'})

    data = pd.concat([taxi_df,waiting_df,picked_df])
    chart = alt.Chart(data).mark_point().encode(
        x='x',
        y='y',
        color=color_scale,  # Distinguish the series by color
        tooltip=['x', 'y', 'series']  # Add tooltips for interactivity
    ).properties(
        title="Taxi station",
        width=600,
        height=600
    )
    plot_container.altair_chart(chart, use_container_width=True)

st.set_page_config(page_title="Taxi station", layout="wide")
plot_container = st.empty()
color=alt.Color('series:N', scale=alt.Scale(domain=['Taxis', 'Pending orders', 'Destinations'], range=['#1f77b4', '#ff7f0e', '#2ca02c']))
print_container = st.container(height = 300, border=True)

new_order_reset = fps * order_frequency
velocity_per_tick = velocity / fps
all_taxis = []
for i in range(10):
    all_taxis.append(Taxi(i, velocity = velocity_per_tick))

order_index = 0
current_orders = []
new_order_counter = 0
try:
    while True:
        tick = Tick(fps)

        # Drive the taxis
        for index in range(len(all_taxis)):
            taxi = all_taxis[index]
            if taxi.state in [taxi_status.picking, taxi_status.dropping]:
                taxi = tssf.driving_during_tick(taxi)

                # Handle pick-up / drop-down
                if taxi.current_x == taxi.dest_x and taxi.current_y == taxi.dest_y:
                    # Pick-up
                    order_loc = taxi.order_location(current_orders)
                    if taxi.state == taxi_status.picking:
                        taxi, current_orders[order_loc] = tssf.pick_up_order(taxi, current_orders[order_loc])
                        print_container.write (f"Order {current_orders[order_loc].index} picked up by taxi {taxi.index}")
                    # Drop-down
                    elif taxi.state == taxi_status.dropping:
                        del current_orders[order_loc]
                        taxi = tssf.drop_order(taxi, )
                        print_container.write (f"Taxi {taxi.index} completed an order")
            all_taxis[index] = taxi

        # Create a new order every 20 seconds
        if new_order_counter > new_order_reset:
            order_index += 1
            current_orders.append(tssf.new_order(order_index))
            new_order_counter = 0
            print_container.write (f"Order {order_index} received")

        # Assign available taxis to orders
        for idx, order in enumerate(current_orders):
            if order.status != order_status.in_queue:
                continue
            available_taxis = [taxi for taxi in all_taxis if taxi.state == taxi_status.idle]
            if len(available_taxis) > 0:
                chosen_taxi_index = tssf.choose_taxi_to_order(order,available_taxis)
                chosen_taxi_loc = [i for i in range(len(all_taxis)) if all_taxis[i].index == chosen_taxi_index][0]
                current_orders[idx], all_taxis[chosen_taxi_loc] = tssf.assign_taxi_to_order(current_orders[idx], all_taxis[chosen_taxi_loc])
                print_container.write (f"Taxi {all_taxis[chosen_taxi_loc].index} drives to order {current_orders[idx].index}")

        if new_order_counter % 5 == 0:
            update_plot(all_taxis,current_orders, plot_container, color)

        # End tick
        new_order_counter += 1
        end_tick = tick.wait_for_tick()

        # Lower frame-rate if needed
        if not end_tick:
            print (f"Frame rate is too high. Reducing fps to {fps-1}")
            fps -= 1
            new_order_reset = fps * order_frequency
            velocity_per_tick = velocity / fps
            for i in range(len(all_taxis)):
                all_taxis[i].velocity = velocity_per_tick

except KeyboardInterrupt:
    print ("Thank you for using Dor's taxi service")