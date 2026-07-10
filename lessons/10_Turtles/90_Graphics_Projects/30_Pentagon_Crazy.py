import turtle
import time

tina = turtle.Turtle()
tina.shape("turtle")
tina_path = [1,2,3,4,5]
tina_progress = 0


screen = turtle.Screen()
screen.setup(600, 600)

cam_colors = ["red", "grey", "white", "green", "blue"]



def show_anamatronics(cam_num):
    #tina show
    if(cam_num == tina_path[tina_progress]):
        tina.showturtle()
    else:
        tina.hideturtle()



def open_cam_1():
    print("CAM 1 OPEN")
    screen.bgcolor(cam_colors[0])
    show_anamatronics(1)
def open_cam_2():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[1])
    show_anamatronics(2)
def open_cam_3():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[2])
    show_anamatronics(3)
def open_cam_4():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[3])
    show_anamatronics(4)
    
def open_cam_5():
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[4])
    show_anamatronics(5)
def exit_cam():
    print("CAM EXITED")
    screen.bgcolor("yellow")
    show_anamatronics(-1)


screen.listen()
screen.onkey(open_cam_1, "1")
screen.onkey(open_cam_2, "2")
screen.onkey(open_cam_3, "3")
screen.onkey(open_cam_4, "4")
screen.onkey(open_cam_5, "5")
screen.onkey(exit_cam, "0")

while True:
    time.sleep(1)
    tina_progress += 1



turtle.exitonclick()









