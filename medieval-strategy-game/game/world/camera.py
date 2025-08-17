import pygame

class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (top-left corner)
        self.x = 0
        self.y = 0
        
        # Camera movement speed
        self.speed = 300
        
        # Camera bounds
        self.min_x = 0
        self.min_y = 0
        self.max_x = max(0, world_width - screen_width)
        self.max_y = max(0, world_height - screen_height)
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Camera movement with arrow keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt
        
        # Clamp camera to world bounds
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))
    
    def world_to_screen(self, world_x, world_y):
        return (world_x - self.x, world_y - self.y)
    
    def screen_to_world(self, screen_x, screen_y):
        return (screen_x + self.x, screen_y + self.y)
    
    def is_visible(self, world_x, world_y, width, height):
        return not (world_x + width < self.x or 
                   world_x > self.x + self.screen_width or
                   world_y + height < self.y or
                   world_y > self.y + self.screen_height)