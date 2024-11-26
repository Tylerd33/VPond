import pygame 
import random

pygame.init()

from constants import *
from Tetra import Tetra

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