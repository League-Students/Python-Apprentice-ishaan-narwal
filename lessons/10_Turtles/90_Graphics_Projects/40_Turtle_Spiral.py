import os
import turtle

# --- League Server Display Fix ---
# Forces the remote server to route the canvas screen into your web browser
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":1"

# --- Setup Window & Turtle Specs ---
window = turtle.Screen()
window.bgcolor("black")  # Deep space background for contrast

star = turtle.Turtle()
star.speed(0)  # Sets drawing speed to maximum turbo mode
star.width(3)  # Makes the outline line thicker

# --- Flaming Ninja Star Geometry Loop ---
# Runs 25 times to generate the complete overlapping spike pattern
for i in range(25):
    star.color("orange")
    star.forward(200)
    star.left(144)  # FIXED: Changed from turn_left to left

    star.color("yellow")
    star.forward(50)
    star.left(30)   # FIXED: Changed from turn_left to left

# --- Prevent Window From Instantly Closing ---
# Forces the completed drawing to stay locked on your browser canvas
turtle.done()
