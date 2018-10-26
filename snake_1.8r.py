"""
A Simple Snake Game
2018.10.22
"""
import random
import tkinter as tk
import mysql.connector
from tkinter.simpledialog import askstring
from tkinter import messagebox

__author__ = "Wally Yang"
__version__ = "1.8.5 BETA"


class SnakeGame(object):
    """A snake game can be played while waiting the queue"""

    def __init__(self, master):
        """
        Parameters:
        master(tk.Toplevel): the top level window to run the game
        """
        self._master = master
        self._master.title('Snake game')
        self._master.geometry('250x320+400+50')
        self._master.config(bg='black')

        # Information title
        top_frame = tk.Frame(self._master, height=20, width=300)
        top_frame.config(bg='black')
        top_frame.pack(expand=0, fill=tk.X)
        self._goal = tk.Label(top_frame, text='SCORE: 0', bg='black', fg='white')
        self._goal.pack(side=tk.LEFT)
        self._hiscore_lbl = tk.Label(top_frame, text='HI-SCORE: 0', bg='black', fg='white')
        self._hiscore_lbl.pack(side=tk.RIGHT)

        self._hiscore = 0
        self._current_score = 0

        # The main game area
        self._cv = tk.Canvas(self._master, bg='black')
        self._cv.pack(expand=1, fill=tk.BOTH)
        self._cv.bind_all("<Key>", self.get_input)

        # game introduction content
        self._intro = tk.Frame(self._cv)
        self._intro.config(bg='lightblue')
        self._intro.pack(pady=50)
        self._title = tk.Label(self._intro, text='Welcome', font=20, bg='lightblue')
        self._title.pack(ipadx=50, ipady=10)
        self._text = tk.Label(self._intro, text="Use 'w','a','s','d' to control the snake.\n" +
                                                "Press 'r' to start \nPress 'q' to pause\nPress 'x' to show leaderboard",
                              bg='lightblue', justify=tk.LEFT)
        self._text.pack()

        #leaderboard
        self._leader_statue = True
        try:
            self._leader = LeaderData()
        except:
            self._leader_statue = False
            messagebox.showinfo('Warning','Cannot connect to the server, you will not be able to access Laderboard or add your record into leaders')
        self._leader_frame = tk.Frame(self._cv)
        self._leader_frame.config(bg = 'lightblue')
        leader_title = tk.Label(self._leader_frame, text = "LeaderBoard", font = 20,bg = 'lightblue').grid(row = 0,column =0,columnspan = 3)
        self._leader_lines = []
        for rank in range (1,11):
              rank_lbl = tk.Label(self._leader_frame,text = '-',bg = 'lightblue',padx= 2,pady=1)
              rank_lbl.grid(row = rank , column = 0)
              name_lbl = tk.Label(self._leader_frame,text = '---',bg = 'lightblue',padx= 2,pady=1)
              name_lbl.grid(row = rank,column = 1)
              score_lbl = tk.Label(self._leader_frame,text = '---',bg = 'lightblue',padx= 2,pady=1)
              score_lbl.grid(row = rank,column = 2)
              self._leader_lines.append( (rank_lbl,name_lbl,score_lbl) )
        leader_exit = tk.Label(self._leader_frame, text = "Press 'x' again to close leaderboard",bg='lightblue').grid(row = 11,column = 0, columnspan = 3,ipady=3)
        self._leader_show = False

        # starting position
        self._x, self._y = -1, -1
        self._dx, self._dy = 0, 0
        # a list of dot made up snake's body
        self._body = []

        # self._alive = 0 means snake is dead, self._alive = 1 means snake is alive, self._alive = -1 means paused
        self._alive = 0
        self._eating = False
        self._direction = 'w'
        self._auto = False
        self._turn = False

        self._food = None

    def start_game(self):
        """The reset function to reset all variable to original statue and start game"""
        # reset all variables
        self._cv.delete(tk.ALL)
        self._x, self._y = 120, 150
        self._dx, self._dy = 0, -10
        self._body = []
        self._direction = 'w'
        #self._auto = False

        # create the body of snake
        for i in range(0, 6):
            self._intro.forget()
            self._leader_frame.forget()
            self._y += self._dy
            dot = self._cv.create_rectangle(self._x, self._y, self._x + 10, self._y + 10, fill='white')
            self._body.append(dot)

        self._alive = 1
        self.create_food()

    def pause(self):
        """Pause the game"""
        if self._alive == 1:
            self._alive = -1
        elif self._alive == -1:
            self._intro.forget()
            self._alive = 1
            self.main_control()
        else:
            pass

    def show_leader(self):
        """switch showing between intro and leaderboard"""
        if self._leader_show:
              self._leader_frame.forget()
              self._intro.pack(pady=50)
              self._leader_show = False
        else:
              self.update_leader()
              self._leader_frame.pack(pady = 20)
              self._intro.forget()
              self._leader_show = True

    def update_leader(self):
        """Update leaderboard every time when leaderboard show up"""
        result = self._leader.get_leader()
        for rank in range(0,10):
              try:
                    name = result[rank][1]
                    score = result[rank][2]
                    self._leader_lines[rank][0].config(text = rank+1)
                    self._leader_lines[rank][1].config(text = name)
                    self._leader_lines[rank][2].config(text = score)
              except:
                    break
    def set_new_leader(self):
          """Put the new record into leaderboard"""
          name = askstring("Enter Name", "Please enter your name:")
          self._leader.set_new_record(name,self._current_score)
          self.show_leader()
              
    def get_input(self, e):
        """Get different input to control the game, snake cannot move backward
            press w to go up
            press a to go right
            press s to go down
            press d to go left
            press r while game over to restart
            press x to visit leaderboard or close leader
            press c to add current record into leader
        """
        if (e.char == 'w' and self._direction != 's'):
            self._direction = 'w'
        elif (e.char == 'a' and self._direction != 'd'):
            self._dx, self._dy = -10, 0
            self._direction = 'a'
        elif (e.char == 's' and self._direction != 'w'):
            self._dx, self._dy = 0, 10
            self._direction = 's'
        elif (e.char == 'd' and self._direction != 'a'):
            self._dx, self._dy = 10, 0
            self._direction = 'd'
        elif e.char == 'q':
            self.pause()
        elif e.char == 'f':
            self._auto = True
        elif (e.char == 'r' and self._alive == 0):
            self.start_game()
            self.main_control()
        elif (e.char == 'x' and self._alive == 0 and self._leader_statue):
            self.show_leader()
        elif (e.char == 'c' and self._alive == 0 and self._leader_statue):
            self.set_new_leader()
        else:
            pass

    def create_food(self):
        """create a food to a random position"""
        food_x = 10 * random.randint(0, 24)
        food_y = 10 * random.randint(0, 29)
        self._food = self._cv.create_rectangle(food_x, food_y, food_x + 10, food_y + 10,
                                               fill='red')

    def info_update(self):
        """Update the information showing on the top bar"""
        self._current_score = len(self._body) - 6
        self._goal.config(text='SCORE: {0}'.format(self._current_score))

        if self._hiscore < self._current_score:
            self._hiscore = self._current_score
        self._hiscore_lbl.config(text='HI-SCORE: {0}'.format(self._hiscore))

    def moving(self):
        if self._direction == 'w':
            self._dx, self._dy = 0, -10
        elif self._direction == 'a':
            self._dx, self._dy = -10, 0
        elif self._direction == 's':
            self._dx, self._dy = 0, 10
        elif self._direction == 'd':
            self._dx, self._dy = 10, 0

    def auto_move(self):
        horiz = ('d', 'a')
        vertical = ('w','s')
        if ( (self._x < 10 or self._x > 230 or self._y < 10 or self._y > 280) and self._turn == False):
            self._turn = True
            new_dirc = random.randint(0,1)
            if self._direction in horiz:
                self._direction = vertical[new_dirc]
            else:
                self._direction = horiz[new_dirc]
            print("boarder",self._direction,self._x,self._y)
        if ( (self._x > 10 and self._x < 230 and self._y > 10 and self._y < 280) and self._turn == True):
            self._turn = False
           
        if len(self._cv.find_overlapping(self._x - 3, self._y - 3, self._x - 6, self._y - 6)) > 1:
            for dot in self._cv.find_overlapping(self._x - 3, self._y - 3, self._x - 6, self._y - 6):
                if dot != self._food:
                    new_dirc = random.randint(0,1)
                if self._direction in horiz:
                    self._direction = vertical[new_dirc]
                else:
                    self._direction = horiz[new_dirc]

    def main_control(self):
        """main control function"""
        # drop the tail if no food was eaten
        if(self._auto == True):
            self.auto_move()

        self.moving()

        if self._eating:

            self._eating = False
            self.create_food()
        else:
            last_dot = self._body.pop(0)
            self._cv.delete(last_dot)

        # moving snake by creating a new head
        self._x += self._dx
        self._y += self._dy
        dot = self._cv.create_rectangle(self._x, self._y, self._x + 10, self._y + 10, fill='white')
        self._body.append(dot)

        # when head of snake hit something. if something is food, eat and become longer, else, game over.
        if len(self._cv.find_overlapping(self._x + 3, self._y + 3, self._x + 6, self._y + 6)) > 1:
            for dot in self._cv.find_overlapping(self._x + 3, self._y + 3, self._x + 6, self._y + 6):
                if dot == self._food:
                    self._eating = True
                    self._cv.delete(self._food)
                    break
                else:
                    self._alive = 0

        # to test if snake hit the boader
        if (self._x < 0 or self._x > 240 or self._y < 0 or self._y > 290):
            self._alive = 0

        self.info_update()

        # if snake is alive ,do the next move,
        # if paused, show paused title,
        #  if dead, show game over info
        if self._alive == 1:
            self._master.after(100, self.main_control)
        elif self._alive == -1:
            self._title.config(text='Game Paused')
            self._text.config(text="Press 'q' to continue")
            self._intro.pack(pady=50)
        else:
            self._title.config(text='Game Over')
            self._text.config(text="Press 'r' to restart\nPress'x' to show leaderboard\nPress'c' to add your score \nof this round to leaderboard")
            self._intro.pack(pady=50)

class LeaderData(object):
      """A class link to locla database to manage leaderboard inofrmation"""
      def __init__(self):
            """To start the link with mysql"""
            self._con = mysql.connector.connect(
              host="localhost",
              user="root",
              passwd="",
              database = "snakey")
            self._leaderboard = self._con.cursor()

      def get_leader(self):
            """(list)<tuple>:Returns player id,name,hi_score tuple in record"""
            self._leaderboard.execute("SELECT id,name,hi_score FROM temp_leader ORDER BY hi_score DESC")
            leader_show = self._leaderboard.fetchall()
            return leader_show

      def in_list(self):
            """Will be the method to manage score from the same player"""
            pass

      def get_last_id(self):
            """(int):returns the final id of all player"""
            self._leaderboard.execute("SELECT MAX(id) FROM temp_leader")
            last_id = self._leaderboard.fetchall()
            return last_id[0][0]

      def set_new_record(self,name,score):
            """Put a new record into database as well as leaderboard"""
            pid = self.get_last_id() +1
            sql = "INSERT INTO temp_leader (id,name, hi_score) VALUES (%s, %s, %s)"
            val = (str(pid),name,score)
            self._leaderboard.execute(sql, val)
            self._con.commit()

def main():
    root = tk.Tk()
    snake = SnakeGame(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
