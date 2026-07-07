"""
A simple turtle program that moves the turtle randomly in the grid 

This program will perform a "random walk" by moving the turtle randomly in the grid.

Implement the random_walk function that will move the turtle randomly in the grid.

uid: eefj8Ioy
name: Random Walk
"""

import turtle
import random

# Set up the screen
screen = turtle.Screen()
screen.setup(width=600, height=600)
screen.bgcolor("white")

# Set up the turtle
walker = turtle.Turtle()
walker.shape("turtle")
walker.penup()
walker.speed(0)  # Set to the maximum speed
walker.goto(0, 0)  # Start in the middle of the grid
walker.pendown()

# Function to move the turtle randomly in the grid
def random_walk(walker, steps):
    """ Implement a random walk for the turtle

    The turtle will move on a grid, taking a random step in one of the four directions

    For each of the steps, the turtle will move in a random direction (N, E, S, W) 
    a fixed number of steps. For instance, the turtle should move 10 pixels each time, but
    in a random direction.

    Args:
    walker (turtle.Turtle): The turtle object
    steps (int): The number of steps to take

    """




# Start the random walk
random_walk(walker, 200)

# Close the turtle window on click
screen.exitonclick()