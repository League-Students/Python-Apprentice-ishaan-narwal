import turtle
import time

tina = turtle.Turtle()
tina.shape("turtle")
tina_path = [1,2,3,4,5]
tina_progress = 0
cam_num = 0

screen = turtle.Screen()
screen.setup(600, 600)

cam_colors = ["red", "grey", "white", "green", "blue"]

def move_tina():
    global tina_progress
    tina_progress += 1
    shown_anamatronics
    screen.ontimer(move_tina, 2000)
    
def show_anamatronics():
    global cam_num
    #tina show
    if(cam_num == tina_path[tina_progress]):
        tina.showturtle()
    else:
        tina.hideturtle()



def open_cam_1():
    global cam_num
    print("CAM 1 OPEN")
    screen.bgcolor(cam_colors[0])
    show_anamatronics()
def open_cam_2():
    global cam_num
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[1])
    show_anamatronics()
def open_cam_3():
    global cam_num
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[2])
    show_anamatronics()
def open_cam_4():
    global cam_num
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[3])
    show_anamatronics()
    
def open_cam_5():
    global cam_num
    print("CAM 2 OPEN")
    screen.bgcolor(cam_colors[4])
    show_anamatronics()
def exit_cam():
    print("CAM EXITED")
    screen.bgcolor("yellow")
    show_anamatronics()


screen.listen()
screen.onkey(open_cam_1, "1")
screen.onkey(open_cam_2, "2")
screen.onkey(open_cam_3, "3")
screen.onkey(open_cam_4, "4")
screen.onkey(open_cam_5, "5")
screen.onkey(exit_cam, "0")

screen.ontimer(move_tina, 2000)



turtle.exitonclick()









