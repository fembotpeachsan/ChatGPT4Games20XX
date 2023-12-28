import turtle

# Set up the screen
turtle.bgcolor('black')
turtle.setup(width=600, height=600)
turtle.tracer(0)

# Paddle A
paddle_a = turtle.Turtle()
paddle_a.speed(0)
paddle_a.shape('square')
paddle_a.color('white')
paddle_a.shapesize(stretch_wid=6, stretch_len=1)
paddle_a.penup()
paddle_a.goto(-250, 0)

# Paddle B
paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape('square')
paddle_b.color('white')
paddle_b.shapesize(stretch_wid=6, stretch_len=1)
paddle_b.penup()
paddle_b.goto(250, 0)

# Ball
ball = turtle.Turtle()
ball.speed(40)
ball.shape('square')
ball.color('white')
ball.penup()
ball.goto(0, 0)
ball.dx = 0.15
ball.dy = -0.15

# Function to move paddle A up
def paddle_a_up():
    y = paddle_a.ycor()
    y += 20
    paddle_a.sety(y)

# Function to move paddle A down
def paddle_a_down():
    y = paddle_a.ycor()
    y -= 20
    paddle_a.sety(y)

# Function to move paddle B up
def paddle_b_up():
    y = paddle_b.ycor()
    y += 20
    paddle_b.sety(y)

# Function to move paddle B down
def paddle_b_down():
    y = paddle_b.ycor()
    y -= 20
    paddle_b.sety(y)

# Keyboard bindings
turtle.listen()
turtle.onkeypress(paddle_a_up, 'w')
turtle.onkeypress(paddle_a_down, 's')
turtle.onkeypress(paddle_b_up, 'Up')
turtle.onkeypress(paddle_b_down, 'Down')

# Main game loop
while True:
    turtle.update()

    # Move the ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Border checking
    if ball.ycor() > 290:
        ball.sety(290)
        ball.dy *= -1

    if ball.ycor() < -290:
        ball.sety(-290)
        ball.dy *= -1

    if ball.xcor() > 290:
        ball.goto(0, 0)
        ball.dx *= -1

    if ball.xcor() < -290:
        ball.goto(0, 0)
        ball.dx *= -1

    # Paddle and ball collisions
    if (ball.xcor() > 240 and ball.xcor() < 250) and (ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
        ball.setx(240)
        ball.dx *= -1

    if (ball.xcor() < -240 and ball.xcor() > -250) and (ball.ycor() < paddle_a.ycor() + 50 and ball.ycor() > paddle_a.ycor() - 50):
        ball.setx(-240)
        ball.dx *= -1
