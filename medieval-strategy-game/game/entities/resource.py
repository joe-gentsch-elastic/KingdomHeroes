import pygame
import random

class Resource:
    def __init__(self, x, y, resource_type, amount=None):
        self.x = x
        self.y = y
        self.resource_type = resource_type
        self.amount = amount or random.randint(20, 50)
        self.max_amount = self.amount
        self.size = 24
        self.harvest_rate = 2
        self.regeneration_rate = 0.5
        self.last_harvest_time = 0
        
        # Resource colors and properties
        self.resource_data = {
            'gold': {'color': (255, 215, 0), 'regen': False},
            'wood': {'color': (139, 69, 19), 'regen': True},
            'stone': {'color': (128, 128, 128), 'regen': False},
            'food': {'color': (255, 140, 0), 'regen': True}
        }
        
        self.color = self.resource_data[resource_type]['color']
        self.can_regenerate = self.resource_data[resource_type]['regen']
    
    def harvest(self, harvester):
        if self.amount > 0:
            harvested = min(self.harvest_rate, self.amount)
            self.amount -= harvested
            return harvested
        return 0
    
    def update(self, dt):
        # Regenerate resources over time if applicable
        if self.can_regenerate and self.amount < self.max_amount:
            self.amount = min(self.max_amount, self.amount + self.regeneration_rate * dt)
    
    def render(self, screen, camera):
        if self.amount > 0 and camera.is_visible(self.x, self.y, self.size, self.size):
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            
            # Draw resource
            pygame.draw.circle(screen, self.color, 
                             (screen_x + self.size // 2, screen_y + self.size // 2), 
                             self.size // 2)
            
            # Draw amount indicator
            if self.amount < self.max_amount:
                font = pygame.font.Font(None, 16)
                amount_text = font.render(str(int(self.amount)), True, (255, 255, 255))
                text_rect = amount_text.get_rect(center=(screen_x + self.size // 2, screen_y + self.size // 2))
                screen.blit(amount_text, text_rect)
    
    def get_bounds(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def contains_point(self, world_x, world_y):
        return self.get_bounds().collidepoint(world_x, world_y)
    
    def is_depleted(self):
        return self.amount <= 0

class ResourceManager:
    def __init__(self, game_map):
        self.game_map = game_map
        self.resources = []
        self.spawn_resources()
    
    def spawn_resources(self):
        # Spawn resources randomly on the map
        for _ in range(100):  # Spawn 100 resources
            x = random.randint(0, self.game_map.world_width - 32)
            y = random.randint(0, self.game_map.world_height - 32)
            
            # Check if location is valid (not water or mountain)
            if self.game_map.is_walkable(x, y):
                resource_type = random.choice(['gold', 'wood', 'stone', 'food'])
                self.resources.append(Resource(x, y, resource_type))
    
    def update(self, dt):
        # Update all resources
        for resource in self.resources[:]:
            resource.update(dt)
            # Remove depleted non-regenerating resources
            if resource.is_depleted() and not resource.can_regenerate:
                self.resources.remove(resource)
    
    def render(self, screen, camera):
        for resource in self.resources:
            resource.render(screen, camera)
    
    def get_resource_at(self, world_x, world_y):
        for resource in self.resources:
            if resource.contains_point(world_x, world_y) and not resource.is_depleted():
                return resource
        return None
    
    def harvest_resource_at(self, world_x, world_y, harvester):
        resource = self.get_resource_at(world_x, world_y)
        if resource:
            return resource.harvest(harvester)
        return 0