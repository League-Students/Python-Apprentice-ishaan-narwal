"""
LeagueBot

Write your own turtle program! Here is what your program should do

1) Change the turtle image to 'leaguebot_bot.gif'
2) Change the turtle size to 10x10
3) Change the turtle line color to 'blue'
4) Draw a hexagon using a loop and variables.
"""

import turtle

screen = turtle.Screen()
screen.setup(width=600, height=600)
screen.bgcolor('white')

t = turtle.Turtle()
"""
Copy the code from the previous lesson, 10_More_Turtle_Programs.ipynb,
from the section "Change the Turtle's Image"

Then change the code so that the turtle has a different image ( look in the 'images'
directory ) and moves to the corners of the screen in a square pattern.
"""

import turtle                                           # Import the turtle module

screen = turtle.Screen()                                    # Set up the screen
screen.setup(width=600, height=600)                         # Set the size of the window
screen.bgcolor('white')                                     # Set the background color

t = turtle.Turtle()                                         # Create a turtle
t.shape("turtle")                                           # Set the shape of the turtle
t.turtlesize(stretch_wid=10, stretch_len=10, outline=4)     # Make the turtle really big

def turtle_clicked(t, x, y):
    """Function that gets called when the user clicks on the turtle

    This function will make the turtle tilt 20 degrees 18 times, making a full
    circle. It is called by the turtle when the user clicks on it.

    Args:
        t (Turtle): The turtle object that was clicked
        x (int): The x coordinate of the click
        y (int): The y coordinate of the click
    """

    print('turtle clicked!')
    
    for i in range(0,360, 20):  # Full circle, 20 degrees at a time
        t.tilt(20)              # Tilt the turtle 20 degrees

# Connect the turtle to the turtle_clicked function
t.onclick(lambda x, y, t=t: turtle_clicked(t, x, y))

turtle.done() # Important! Use `done` not `exitonclick` to keep the window open
... # Your Code Here