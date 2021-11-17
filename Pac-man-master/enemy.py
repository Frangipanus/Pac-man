import pygame
from player import*
from settings import*
import sys
import random
import app_class
import time

vec = pygame.math.Vector2

class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.direction = vec(0,0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()
        
        

    def get_pix_pos(self):
        return vec((self.grid_pos[0]*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2, (self.grid_pos[1]*self.app.cell_height) +TOP_BOTTOM_BUFFER//2+self.app.cell_height//2)

    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction *self.speed
            if self.time_to_move():
                self.move()
        #for enemy in self.app.enemies:
         #   if enemy.personality == "random1" and enemy.grid_pos == self.player.grid_pos:
          #      self.enemy_reset()

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +self.app.cell_height//2)//self.app.cell_height+1


    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour, (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)
       

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        if self.personality == "random":
            number = random.randint(0,4)
            if number == 4:
                self.direction = self.get_random_direction()
            else:
                self.direction = self.get_path_direction(self.target)
        if self.personality == "random1":
            self.direction = self.get_random_direction()
        if self.personality == "go home":
            self.direction = self.get_path_direction(self.target)

        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)
                
    def get_random_direction(self):
        while True:
            number = random.randint(-2,1)
            if number == -2 :
                x_dir, y_dir = 1,0
            elif number ==-1:
                x_dir, y_dir = 0,1
            elif number == 1:
                x_dir, y_dir = -1,0
            else:
                x_dir, y_dir = 0,-1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest



    def set_colour(self):
        if self.number == 0:
            self.colour = (43, 78, 203)
        if self.number == 1:
            self.colour = (104, 43, 23)
        if self.number == 2:
            self.colour = RED
        if self.number == 3:
            self.colour = GREY
        
        return self.colour
    
    def set_personality(self):
        if self.number == 0:
            return "speedy"
            
        if self.number == 1:
            return "slow"
        if self.number == 2:
            return "random"
        if self.number == 3:
            return "scared"
        
    def set_target(self):
        if self.personality == "speedy" or self.personality == "slow" or self.personality == "random":
            return self.app.player.grid_pos
        elif self.personality == "go home":
            self.target = self.starting_pos
        elif self.personality == "chased":
            for enemy in self.app.enemies:
                self.colour = BLUE
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)
        else:
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)
            
    def set_speed(self):
        if self.personality in ["speedy", "scared"]:
            speed = 1.5
        else:
            speed = 1
        return speed

    

    
