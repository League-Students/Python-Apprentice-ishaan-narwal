import turtle

tina = turtle.Turtle()

screen = turtle.Screen()
screen.setup(500, 500)

cam_colors = ["red", "black", "white", "green", "blue"]

def open_cam_1():
    print("CAM 1 OPEN")
    screen.bgcolor(cam_colors[0])


screen.listen()
screen.onkey(open_cam_1, "1")

turtle.exitonclick()
