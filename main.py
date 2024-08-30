from math import ceil, floor
import turtle

import numpy as np

class Game:

    class Ball:
        def __init__(self):
            self.skip = turtle.Turtle()
            self.skip.speed(0)
            self.skip.shape("circle")
            self.skip.color("red")
            self.skip.penup()
            self.skip.goto(0, 0)
            self.skip.dx = 2
            self.skip.dy = 2

        def move(self):
            self.skip.setx(self.skip.xcor() + self.skip.dx)
            self.skip.sety(self.skip.ycor() + self.skip.dy)

        def bounce_y(self):
            self.skip.dy *= -1

        def bounce_x(self):
            self.skip.dx *= -1

        def reset_position(self):
            self.skip.goto(0, 0)
            self.bounce_y()

    class Paddle:
        def __init__(self, position, game):

            # Inicializa el entorno grafico
            self.paddle = turtle.Turtle()
            self.paddle.speed(0)
            self.paddle.shape("square")
            self.paddle.color("blue")
            self.paddle.shapesize(stretch_wid=1, stretch_len=5)
            self.paddle.penup()
            self.paddle.goto(position)
            
            # Inicializa las condiciones del juego
            self.lives = game.lives_max
            self.lives_max = game.lives_max
            self.movement = game.movement
            self.actions = ['lelf','right']
            
            # Inicializa las variables y parametros de algoritmo Q-learning
            self.discount_factor = game.discount_factor
            self.learning_rate = game.learning_rate
            self.ratio_explotacion = game.ratio_explotacion

        def move_left(self):
            x = self.paddle.xcor()
            if x > -350:
                x -= self.movement
            self.paddle.setx(x)

        def move_right(self):
            x = self.paddle.xcor()
            if x < 350:
                x += self.movement
            self.paddle.setx(x)
        
        def update(self, game, old_state, action_taken, reward_action_taken, new_state, reached_end):
            idx_action_taken =list(game.action_space).index(action_taken)

            actual_q_value_options = self._q_table[old_state[0], old_state[1], old_state[2]]
            actual_q_value = actual_q_value_options[idx_action_taken]

            future_q_value_options = self._q_table[new_state[0], new_state[1], new_state[2]]
            future_max_q_value = reward_action_taken  +  self.discount_factor*future_q_value_options.max()
            if reached_end:
                future_max_q_value = reward_action_taken #maximum reward

            self._q_table[old_state[0], old_state[1], old_state[2], idx_action_taken] = actual_q_value + \
                                                self.learning_rate*(future_max_q_value -actual_q_value)

    def __init__(self, episodes_max, lives_max, width, height, movement, discount_factor, learning_rate, ratio_explotacion, ai=False):

        self.window = turtle.Screen()
        self.window.title("Ping Pong para un Jugador")
        self.window.bgcolor("white")
        self.window.setup(width=width, height=height)
        self.window.tracer(0)

        rows = ceil(height/movement)
        columns = ceil(width/movement)
        self.state_space = np.zeros((columns, columns, rows))
        self.movement = movement

        self.episodes_max = episodes_max
        self.lives_max = lives_max
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.ratio_explotacion = ratio_explotacion

        self.agent = self.Paddle((0, -250), self)
        self.ball = self.Ball()

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color("black")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.update_score()

        self.reset()
        self.window.listen()

        if ai == False:
            self.window.onkeypress(self.agent.move_left, "Left")
            self.window.onkeypress(self.agent.move_right, "Right")

        self.run_game()

    def update_score(self):
        self.pen.clear()
        #self.pen.write(f"Puntaje: {self.score}, Vidas: {self.paddle.lives} / {self.paddle.lives_max}, Jugadas: {self.plays}", align="center", font=("Courier", 24, "normal"))

    def update_position(self):
        self.pen.clear()
        self.pen.write(f"Paddle: {floor(self.agent.paddle.xcor())}, x: {floor(self.ball.skip.xcor())}, y: {floor(self.ball.skip.ycor())}", align="center", font=("Courier", 18, "normal"))

    def check_collisions(self):

        self.update_position()

        # Rebote en el borde superior
        if self.ball.skip.ycor() > 290:
            self.ball.skip.sety(290)
            self.ball.bounce_y()

        # Rebote en los bordes laterales
        if self.ball.skip.xcor() > 390 or self.ball.skip.xcor() < -390:
            self.ball.bounce_x()

        # Rebote en la paleta
        if (self.ball.skip.ycor() > -240 and self.ball.skip.ycor() < -230) and \
           (self.agent.paddle.xcor() + 50 > self.ball.skip.xcor() > self.agent.paddle.xcor() - 50):
            self.ball.skip.sety(-230)
            self.ball.bounce_y()
            self.score += 10
            self.plays += 1
            self.update_score()

        # Revisar si la pelota toca el borde inferior
        if self.ball.skip.ycor() < -290:
            self.ball.reset_position()
            self.score -= 10
            self.plays += 1
            self.paddle.lives -= 1
            self.update_score()

    def reset(self):
        self.state = [0,0,0]
        self.score = 0
        self.plays = 0
        self.total_reward = 0
    
    def step(self, action):

        if action == "left":
            self.paddle.move_left
        elif action == "right":
            self.paddle.move_right
            
        self.window.update()      
        self.update_position()
        self.ball.skip.move()
        self.check_collisions()

        self.state = (floor(self.paddle.xcor()), floor(self.ball.skip.xcor()), floor(self.ball.skip.ycor()))
        done = self.paddle.lives <=0 # final
        reward = self.score

        return self.state, reward , done

    def run_game(self):
        
        # Inicializacion de las estadistica de las jugadas
        max_points= -9999
        first_max_reached = 0
        total_rw=0
        steps=[]

        # Inicializar tabla de Q
        position = list(self.state_space.shape)
        position.append(len(self.agent.actions))
        self.agent._q_table = np.zeros(position)

        # Bucle de episodios
        for episode in range(self.episodes_max):
            # Inicializar el episodio
            self.reset()
    
            # Bucle de restricciones
            while self.score >= 0 and self.plays < 3000 and self.agent.lives > 0 and self.total_reward <= 1000:
                # Obtiene el estado actual
                current_state = np.array(self.state)


        #while True:
        #    self.window.update()
        #    self.ball.move()
        #    self.check_collisions()
         
        


# Ejecutar el juegox
if __name__ == "__main__":
    Game(ai=False, episodes_max=10, lives_max=3, width=800, height=600, movement=30, discount_factor = 0.1, learning_rate = 0.1, ratio_explotacion = 0.9)