from constants import *
import random

class Tetra:
    def __init__(self, x, y, all_tetras):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.color = (random.randint(0, 40), random.randint(125, 165), random.randint(215, 255))
        self.rect = pygame.Rect(x, y, CREATURE_SIZE_X, CREATURE_SIZE_Y)
        self.nearest_neighbor = None
        self.nearest_distance = float('inf')
        self.all_tetras = all_tetras
        self.collision_distance = CREATURE_SIZE_X

        # Variables for hunger and speed system
        self.max_speed = random.uniform(0.8, 1.2)
        self.current_speed = self.max_speed
        self.hunger = 50
        self.hunger_decay_base = 0.01
        self.isAlive = True

    def update_hunger_and_speed(self):
        if not self.isAlive:
            return

        speed_multiplier = self.current_speed / self.max_speed
        hunger_decay = self.hunger_decay_base * (1 + speed_multiplier)
        
        self.hunger = max(0, self.hunger - hunger_decay)

        if self.hunger < 30:
            hunger_speed_multiplier = self.hunger / 30
            self.current_speed = self.max_speed * hunger_speed_multiplier
        else:
            self.current_speed = self.max_speed

        if self.hunger <= 0:
            self.current_speed = 0
            self.isAlive = False

    def will_collide(self, new_x, new_y, other_tetra):
        future_rect = pygame.Rect(new_x, new_y, CREATURE_SIZE_X, CREATURE_SIZE_Y)
        return future_rect.colliderect(other_tetra.rect)

    def check_collision_ahead(self, new_x, new_y):
        for other in self.all_tetras:
            if other != self:
                if self.will_collide(new_x, new_y, other):
                    return True
        return False

    def move(self):
        if self.isAlive:
            self.update_hunger_and_speed()
            self.find_nearest_neighbor()

            if random.random() < 0.02:
                if random.random() < 0.6 and self.nearest_neighbor:
                    if (self.nearest_distance > 30):
                        self.direction = self.calculate_direction_to_neighbor()
                else:
                    self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

            new_x = self.x + (self.direction[0] * self.current_speed)
            new_y = self.y + (self.direction[1] * self.current_speed)

            if self.check_collision_ahead(new_x, new_y):
                self.direction = (-self.direction[0], -self.direction[1])
                new_x = self.x + (self.direction[0] * self.current_speed)
                new_y = self.y + (self.direction[1] * self.current_speed)

            if SWIM_ZONE_LEFT <= new_x < SWIM_ZONE_RIGHT - CREATURE_SIZE_X:
                self.x = new_x
            else:
                self.direction = (-self.direction[0], self.direction[1])
                self.x = max(SWIM_ZONE_LEFT, min(self.x, SWIM_ZONE_RIGHT - CREATURE_SIZE_X))

            if SWIM_ZONE_TOP <= new_y < SWIM_ZONE_BOTTOM - CREATURE_SIZE_Y:
                self.y = new_y
            else:
                self.direction = (self.direction[0], -self.direction[1])
                self.y = max(SWIM_ZONE_TOP, min(self.y, SWIM_ZONE_BOTTOM - CREATURE_SIZE_Y))
        else:
            sink_speed = 0.2
            self.direction = (0, 1)
            
            new_x = self.x
            new_y = self.y + (self.direction[1] * sink_speed)

            if self.check_collision_ahead(new_x, new_y):
                new_y = self.y
            
            if SWIM_ZONE_LEFT <= new_x < SWIM_ZONE_RIGHT - CREATURE_SIZE_X:
                self.x = new_x
                
            if new_y < SWIM_ZONE_BOTTOM - CREATURE_SIZE_Y:
                self.y = new_y
            else:
                self.y = SWIM_ZONE_BOTTOM - CREATURE_SIZE_Y

        self.rect.x = self.x
        self.rect.y = self.y

    def find_nearest_neighbor(self):
        self.nearest_distance = float('inf')
        self.nearest_neighbor = None
        
        for tetra in self.all_tetras:
            if tetra != self:
                distance = self.calculate_distance(tetra)
                if distance < self.nearest_distance:
                    self.nearest_distance = distance
                    self.nearest_neighbor = tetra

    def calculate_distance(self, other_tetra):
        return ((self.x - other_tetra.x) ** 2 + (self.y - other_tetra.y) ** 2) ** 0.5

    def calculate_direction_to_neighbor(self):
        if self.nearest_neighbor:
            dx = self.nearest_neighbor.x - self.x
            dy = self.nearest_neighbor.y - self.y
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                return (dx/distance, dy/distance)
        return self.direction