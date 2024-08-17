import turtle

class Paddle:
    def __init__(self, position):
        self.paddle = turtle.Turtle()
        self.paddle.speed(0)
        self.paddle.shape("square")
        self.paddle.color("blue")
        self.paddle.shapesize(stretch_wid=1, stretch_len=5)
        self.paddle.penup()
        self.paddle.goto(position)
        self.lives_max = 3
        self.lives = self.lives_max

    def move_left(self):
        x = self.paddle.xcor()
        if x > -350:
            x -= 30
        self.paddle.setx(x)

    def move_right(self):
        x = self.paddle.xcor()
        if x < 350:
            x += 30
        self.paddle.setx(x)

class Ball:
    def __init__(self):
        self.ball = turtle.Turtle()
        self.ball.speed(0)
        self.ball.shape("circle")
        self.ball.color("red")
        self.ball.penup()
        self.ball.goto(0, 0)
        self.ball.dx = 0.2
        self.ball.dy = 0.2

    def move(self):
        self.ball.setx(self.ball.xcor() + self.ball.dx)
        self.ball.sety(self.ball.ycor() + self.ball.dy)

    def bounce_y(self):
        self.ball.dy *= -1

    def bounce_x(self):
        self.ball.dx *= -1

    def reset_position(self):
        self.ball.goto(0, 0)
        self.bounce_y()

class Game:
    def __init__(self):
        self.window = turtle.Screen()
        self.window.title("Ping Pong para un Jugador")
        self.window.bgcolor("white")
        self.window.setup(width=800, height=600)
        self.window.tracer(0)

        self.score = 0
        self.episodes = 0
        self.episodes_max = 5
        self.paddle = Paddle((0, -250))
        self.ball = Ball()

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color("black")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.update_score()

        self.window.listen()
        self.window.onkeypress(self.paddle.move_left, "Left")
        self.window.onkeypress(self.paddle.move_right, "Right")

        self.run_game()

    def update_score(self):
        self.pen.clear()
        self.pen.write(f"Puntaje: {self.score}, Vidas: {self.paddle.lives} / {self.paddle.lives_max}, Episodio: {self.episodes} /  {self.episodes_max} ", align="center", font=("Courier", 24, "normal"))

    def check_collisions(self):
        # Rebote en el borde superior
        if self.ball.ball.ycor() > 290:
            self.ball.ball.sety(290)
            self.ball.bounce_y()

        # Rebote en los bordes laterales
        if self.ball.ball.xcor() > 390 or self.ball.ball.xcor() < -390:
            self.ball.bounce_x()

        # Rebote en la paleta
        if (self.ball.ball.ycor() > -240 and self.ball.ball.ycor() < -230) and \
           (self.paddle.paddle.xcor() + 50 > self.ball.ball.xcor() > self.paddle.paddle.xcor() - 50):
            self.ball.ball.sety(-230)
            self.ball.bounce_y()
            self.score += 10
            self.episodes += 1
            self.update_score()

        # Revisar si la pelota toca el borde inferior
        if self.ball.ball.ycor() < -290:
            self.ball.reset_position()
            self.score -= 10
            self.episodes += 1
            self.paddle.lives -= 1
            self.update_score()

    def run_game(self):
        while self.score >= 0 and self.paddle.lives > 0 and self.episodes <= self.episodes_max:
            self.window.update()
            self.ball.move()
            self.check_collisions()
        

# Ejecutar el juego
if __name__ == "__main__":
    Game()