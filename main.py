from math import ceil, floor
import turtle
import time
import numpy as np

class Game:

    class Ball:
        def __init__(self, game):
            self.skip = turtle.Turtle()
            self.skip.speed(0)
            self.skip.shape("circle")
            self.skip.color("red")
            self.skip.penup()
            self.skip.goto(0, 0)
            self.skip.dx = game.movement
            self.skip.dy = game.movement

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
            self.actions = ['Left','Right']
            
            # Inicializa las variables y parametros de algoritmo Q-learning
            self.discount_factor = game.discount_factor
            self.learning_rate = game.learning_rate
            self.ratio_exploration = game.ratio_exploration

        def move_left(self):
            x = self.paddle.xcor()
            if x > -350:
                x -= self.movement + 50
            self.paddle.setx(x)

        def move_right(self):
            x = self.paddle.xcor()
            if x < 350:
                x += self.movement + 50
            self.paddle.setx(x)
        
        #def update_Qtable(self, game, old_state, action_taken, reward_action_taken, new_state, reached_end):
        def update_Qtable(self, action_taken, old_state, new_state, reward_action_taken):
            idx_action_taken =list(self.actions).index(action_taken)
            
            actual_q_value_options = self._q_table[old_state[0], old_state[1], old_state[2]]
            actual_q_value = actual_q_value_options[idx_action_taken]

            #future_q_value_options = self._q_table[new_state[0], new_state[1], new_state[2]]
            #future_max_q_value = reward_action_taken  +  self.discount_factor*future_q_value_options.max()

            print("***********")
            #print(actual_q_value)
            #temp1 = np.array(new_state)
            #print(new_state)
            #print(type(new_state))
            #print(type(temp1))
            #print(temp1)
            print("old_state" + str(old_state))
            print("new_state" + str(new_state))
            #print(future_q_value_options)
            #print(future_max_q_value)
            
            """
            if reached_end:
                future_max_q_value = reward_action_taken #maximum reward

            self._q_table[old_state[0], old_state[1], old_state[2], idx_action_taken] = actual_q_value + \
                                                self.learning_rate*(future_max_q_value -actual_q_value)
            """
    
    def __init__(self, episodes_max, lives_max, width, height, movement, discount_factor, learning_rate, ratio_exploration, ai=False):

        self.window = turtle.Screen()
        self.window.title("Ping Pong para un Jugador")
        self.window.bgcolor("white")
        self.window.setup(width=width, height=height)
        self.window.tracer(0)

        self.rows = ceil(height/movement)
        self.columns = ceil(width/movement)
        self.state_space = np.zeros((self.columns, self.columns, self.rows))

        print("height -> " + str(height))
        print("width -> " + str(width))
        print("movement -> " + str(movement))
        print("rows -> " + str(self.rows))
        print("columns -> " + str(self.columns))
        print("state_space.shape -> " + str(self.state_space.shape))

        self.movement = movement
        self.episodes_max = episodes_max
        self.lives_max = lives_max
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.ratio_exploration = ratio_exploration
        
        self.state = [0,0,0]
        self.score = 0
        self.plays = 0
        self.total_reward = 0

        self.agent = self.Paddle((0, -250), self)
        self.ball = self.Ball(self)

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color("black")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 260)
        self.show_score()

        self.reset()
        self.window.listen()

        if ai == False:
            self.window.onkeypress(self.agent.move_left, "Left")
            self.window.onkeypress(self.agent.move_right, "Right")

        self.run_game()

    def show_score(self):
        self.pen.clear()
        #self.pen.write(f"Puntaje: {self.score}, Vidas: {self.agent.lives} / {self.agent.lives_max}, Jugadas: {self.plays}", align="center", font=("Courier", 24, "normal"))
        #self.show_position()

    def show_position(self):
        self.pen.clear()
        self.pen.write(f"Paddle: {floor(self.agent.paddle.xcor())}, x: {floor(self.ball.skip.xcor())}, y: {floor(self.ball.skip.ycor())}", align="center", font=("Courier", 18, "normal"))
        #self.pen.write(f"Paddle: {self.state[0]}, x: {self.state[1]}, y: {self.state[2]}", align="center", font=("Courier", 18, "normal"))
        #time.sleep(0.4)

    def check_collisions(self):

        self.show_position()

        # Rebote en el borde superior
        if self.ball.skip.ycor() >= 280:
            self.ball.skip.sety(280)
            self.ball.bounce_y()

        # Rebote en los bordes laterales
        if self.ball.skip.xcor() >= 380 or self.ball.skip.xcor() <= -380:
            self.ball.bounce_x()

        # Rebote en la paleta
        if (-260 <= self.ball.skip.ycor() <= -230) and \
           (self.agent.paddle.xcor() - 50 <= self.ball.skip.xcor() <= self.agent.paddle.xcor() + 50):
            self.ball.skip.sety(-230)
            self.ball.bounce_y()
            self.score += 10
            self.plays += 1
            self.show_score()

        # Revisar si la pelota toca el borde inferior
        if self.ball.skip.ycor() <= -280:
            self.ball.reset_position()
            self.score -= 10
            self.plays += 1
            self.agent.lives -= 1
            self.show_score()
        
        # Actualiza el estado    
        self.state = (ceil(self.agent.paddle.xcor()/self.movement +self.columns/2), ceil(self.ball.skip.xcor()/self.movement + self.columns/2), ceil(self.ball.skip.ycor()/self.movement +self.rows/2 ))
        print(self.state)

    def reset(self):
        self.state = [0,0,0]
        self.score = 0
        self.plays = 0
        self.total_reward = 0
    
    def take_action(self, action):

        if action == "Left":
            self.agent.move_left
        elif action == "Right":
            self.agent.move_right
        
        self.ball.move()
            
        self.window.update()      
        self.show_score()

    def run_game(self):
        
        # Inicializacion de las estadistica de las jugadas
        max_points= -9999
        first_max_reached = 0
        total_rw=0
        take_action = []

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
                # Observa el estado actual
                old_state = np.array(self.state)

                # Selecciona una accion basada en la política epsilon-greedy            
                if np.random.uniform() >= self.ratio_exploration:
                    next_action = np.random.choice(list(self.agent.actions))
                else:
                    # Tomar el maximo
                    index_action = np.random.choice(np.flatnonzero(
                           self.agent._q_table[self.state[0],self.state[1],self.state[2]] == self.agent._q_table[self.state[0],self.state[1],self.state[2]].max()
                        ))
                    next_action = list(self.agent.actions)[index_action]
                #print(np.flatnonzero(self.agent._q_table.shape))
                # Toma una accion 
                self.take_action(next_action)
                
                # Medir la recompensa
                self.check_collisions()
                
                # Actualizar la tabla Q
                #self.agent.update_Qtable(next_action, old_state, self.state, self.score)
                
                #break

# Ejecutar el juegox
if __name__ == "__main__":
    Game(ai=False, episodes_max=5000, lives_max=3, width=800, height=600, movement=10, discount_factor = 0.1, learning_rate = 0.1, ratio_exploration = 0.9)