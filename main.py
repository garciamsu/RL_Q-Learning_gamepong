from math import ceil, floor
import turtle

import numpy as np

class Game:

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

    class Paddle:
        def __init__(self, position, game, policy=None):

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

            if policy is not None:
                self._Q_table = policy
            else:
                position = list(game.state_space.shape)
                position.append(len(self.actions))
                self._Q_table = np.zeros(position)

        def move_left(self):
            x = self.xcor()
            if x > -350:
                x -= self.movement
            self.paddle.setx(x)

        def move_right(self):
            x = self.xcor()
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

        self.reset()

        self.paddle = self.Paddle((0, -250), self)
        self.ball = self.Ball()

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color("black")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.update_score()

        self.window.listen()

        if ai == False:
            self.window.onkeypress(self.paddle.move_left, "Left")
            self.window.onkeypress(self.paddle.move_right, "Right")

        self.run_game()

    def update_score(self):
        self.pen.clear()
        self.pen.write(f"Puntaje: {self.score}, Vidas: {self.paddle.lives} / {self.paddle.lives_max}, Jugadas: {self.plays}", align="center", font=("Courier", 24, "normal"))

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
            self.plays += 1
            self.update_score()

        # Revisar si la pelota toca el borde inferior
        if self.ball.ball.ycor() < -290:
            self.ball.reset_position()
            self.score -= 10
            self.plays += 1
            self.paddle.lives -= 1
            self.update_score()

    def reset(self):
        self.state = [0,0,0]
        self.score = 0
        self.plays = 0
    
    def step(self, action):

        if action == "left":
            self.paddle.move_left
        elif action == "right":
            self.paddle.move_right
            
        self.window.update()        
        self.ball.move()
        self.check_collisions()

        print(self.ball.ball)
        self.state = (floor(1.1), floor(self.ball.ball.ycor()), floor(self.ball.ball.xcor()))
        done = self.paddle.lives <=0 # final
        reward = self.score

        return self.state, reward , done

    def run_game(self):

        for episode in range(self.episodes_max):
            # Inicializar el episodio
            self.reset()
    
            while self.score >= 0 and self.paddle.lives > 0:

                old_state = np.array(self.state)
                # Elegir acción usando la política epsilon-greedy            
                ##if np.random.uniform() <= self.ratio_explotacion:
                ##    # Tomar el maximo
                ##    index_action = np.random.choice(np.flatnonzero(
                ##            self.paddle._Q_table[self.state[0],self.state[1],self.state[2]] == self.paddle._Q_table[self.state[0],self.state[1],self.state[2]].max()
                ##        ))
                ##    next_action = list(self.paddle.actions)[index_action]
                ##else:
                ##    next_action = np.random.choice(list(self.paddle.actions))

                # Realizar acción y observar el resultado
                ##state, reward, done = self.step(next_action)

                # Actualizar Q-valor
                ##if episode > 1:
                ##    self.paddle.update(self, old_state, next_action, reward, state, done)
                


# Ejecutar el juegox
if __name__ == "__main__":
    Game(ai=False, episodes_max=10, lives_max=3, width=800, height=600, movement=30, discount_factor = 0.1, learning_rate = 0.1, ratio_explotacion = 0.9)