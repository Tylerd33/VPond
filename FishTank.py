import pygame
import random

# Initialize Pygame
pygame.init()

# Get the screen resolution
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# Constants
CELL_SIZE = 20
CREATURE_SIZE_X = 18
CREATURE_SIZE_Y = 12
CREATURE_SPEED = 1
FPS = 60

# Boundary Constants
TOP_MARGIN = 50
SIDE_MARGIN = 50
BOTTOM_MARGIN = 50
SWIM_ZONE_TOP = TOP_MARGIN
SWIM_ZONE_BOTTOM = SCREEN_HEIGHT - BOTTOM_MARGIN
SWIM_ZONE_LEFT = SIDE_MARGIN
SWIM_ZONE_RIGHT = SCREEN_WIDTH - SIDE_MARGIN

class CollisionHandler:
    @staticmethod
    def check_collision(entity1, entity2):
        """Check if two entities' rectangles overlap"""
        return entity1.rect.colliderect(entity2.rect)

    @staticmethod
    def resolve_collision(entity1, entity2):
        """Push entities apart when they collide"""
        # Calculate center points
        center1 = pygame.math.Vector2(entity1.rect.center)
        center2 = pygame.math.Vector2(entity2.rect.center)
        
        # Calculate collision direction
        collision_vec = center1 - center2
        if collision_vec.length() > 0:  # Avoid division by zero
            collision_vec.normalize_ip()
        else:
            collision_vec = pygame.math.Vector2(1, 0)  # Default push direction if centers overlap
        
        # Push both entities apart
        push_distance = (entity1.rect.width + entity2.rect.width) * 0.51
        push_vec = collision_vec * push_distance * 0.5
        
        # Update positions
        entity1.x += push_vec.x
        entity1.y += push_vec.y
        entity2.x -= push_vec.x
        entity2.y -= push_vec.y
        
        # Update rectangles
        entity1.rect.x = entity1.x
        entity1.rect.y = entity1.y
        entity2.rect.x = entity2.x
        entity2.rect.y = entity2.y
        
        # Reverse directions
        entity1.direction = (-collision_vec.x, -collision_vec.y)
        entity2.direction = (collision_vec.x, collision_vec.y)
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
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Grid World")
        self.clock = pygame.time.Clock()
        self.creatures = []
        self.running = True
        self.is_fullscreen = True
        self.show_connections = False
        self.collision_handler = CollisionHandler()

    def setup(self):
        for _ in range(10):
            x = random.randint(SWIM_ZONE_LEFT, SWIM_ZONE_RIGHT - CREATURE_SIZE_X)
            y = random.randint(SWIM_ZONE_TOP, SWIM_ZONE_BOTTOM - CREATURE_SIZE_Y)
            new_tetra = Tetra(x, y, self.creatures)
            self.creatures.append(new_tetra)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
                elif event.key == pygame.K_l:
                    self.show_connections = not self.show_connections

    def update(self):
        for creature in self.creatures:
            creature.move()

    def draw(self):
        # Fill screen with black
        self.screen.fill((0, 0, 0))

        # Define colors
        DARK_BLUE = (23, 30, 230)
        LIGHT_BLUE = (135, 206, 235)
        
        # Draw light blue above swim zone
        pygame.draw.rect(self.screen, LIGHT_BLUE, 
                        (SWIM_ZONE_LEFT, 0, 
                         SWIM_ZONE_RIGHT - SWIM_ZONE_LEFT, SWIM_ZONE_TOP))
        
        # Draw dark blue swimming zone
        pygame.draw.rect(self.screen, DARK_BLUE, 
                        (SWIM_ZONE_LEFT, SWIM_ZONE_TOP,
                         SWIM_ZONE_RIGHT - SWIM_ZONE_LEFT, 
                         SWIM_ZONE_BOTTOM - SWIM_ZONE_TOP))

        # Draw creatures
        for creature in self.creatures:
            if not creature.isAlive:
                color = (255, 255, 255)  # White color for dead fish
            else:
                hunger_factor = creature.hunger / 100
                base_color = creature.color
                
                white_transition = 255 * (1 - hunger_factor)
                
                color = (
                    min(255, int(base_color[0] + white_transition)),
                    min(255, int(base_color[1] + white_transition)),
                    min(255, int(base_color[2] + white_transition))
                )
            
            pygame.draw.rect(self.screen, color, creature.rect)
            
            if self.show_connections and creature.nearest_neighbor and creature.isAlive:
                start_pos = (creature.x + CREATURE_SIZE_X//2, creature.y + CREATURE_SIZE_Y//2)
                end_pos = (creature.nearest_neighbor.x + CREATURE_SIZE_X//2, 
                          creature.nearest_neighbor.y + CREATURE_SIZE_Y//2)
                pygame.draw.line(self.screen, (255, 255, 255), start_pos, end_pos, 1)

        pygame.display.flip()

    def run(self):
        self.setup()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()