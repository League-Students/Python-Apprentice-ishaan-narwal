import turtle

tina = turtle.Turtle()

screen = turtle.Screen()
screen.setup(600, 600)

cam_colors = ["red", "black", "white", "green", "blue"]

def open_cam_1():
    print("CAM 1 OPEN")
    screen.bgcolor(cam_colors[0])

def open_cam_2():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[1])
    
def open_cam_3():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[2])
def open_cam_4():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[3])
def open_cam_5():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[4])
def exit_cam():
    print(CAM EXITED)
    screen.bgcolor("yellow")


screen.listen()
screen.onkey(open_cam_1, "1")
screen.onkey(open_cam_2, "2")
screen.onkey(open_cam_3, "3")
screen.onkey(open_cam_4, "4")
screen.onkey(open_cam_5, "5")
screen.onkey(exit_cam_0, "0")


turtle.exitonclick()
