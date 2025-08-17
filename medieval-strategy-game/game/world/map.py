import pygame
import random
import math
import os

class GameMap:
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.world_width = width * tile_size
        self.world_height = height * tile_size
        
        # Load background image
        self.background_image = self._load_background_image()
        
        # Generate terrain for collision detection (simplified)
        self.terrain = self._generate_terrain()
        
        # Parallax background layers
        self.bg_layers = self._create_background_layers()
        self.time = 0
    
    def _generate_terrain(self):
        terrain = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # All tiles are now grass
                tile_type = 'grass'
                row.append(tile_type)
            terrain.append(row)
        return terrain
    
    def render(self, screen, camera):
        self.time += 0.016  # Assume ~60 FPS
        
        # Render parallax background layers first
        self._render_background_layers(screen, camera)
        
        # Render background image
        if self.background_image:
            self._render_background_image(screen, camera)
        else:
            # Fallback to original tile rendering if image fails to load
            self._render_tiles_fallback(screen, camera)
    
    def get_tile_at(self, world_x, world_y):
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.terrain[tile_y][tile_x]
        return None
    
    def is_walkable(self, world_x, world_y):
        tile_type = self.get_tile_at(world_x, world_y)
        return tile_type not in ['water', 'mountain']
    
    
    def _create_background_layers(self):
        """Create parallax background layers for depth"""
        layers = []
        
        # Distant mountains layer
        mountains = []
        for i in range(20):
            x = i * 100 + random.randint(-20, 20)
            height = random.randint(80, 150)
            mountains.append((x, height))
        layers.append({'type': 'mountains', 'data': mountains, 'speed': 0.1})
        
        # Clouds layer
        clouds = []
        for i in range(15):
            x = random.randint(0, 2000)
            y = random.randint(50, 200)
            size = random.randint(30, 80)
            clouds.append((x, y, size))
        layers.append({'type': 'clouds', 'data': clouds, 'speed': 0.05})
        
        return layers
    
    def _render_background_layers(self, screen, camera):
        """Render parallax background layers"""
        screen_height = camera.screen_height
        
        # Sky gradient
        for y in range(screen_height // 3):
            progress = y / (screen_height // 3)
            r = int(135 + (200 - 135) * progress)
            g = int(206 + (230 - 206) * progress)
            b = int(235 + (255 - 235) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (camera.screen_width, y))
        
        # Render distant mountains
        mountains = self.bg_layers[0]['data']
        mountain_speed = self.bg_layers[0]['speed']
        for x, height in mountains:
            offset_x = -(camera.x * mountain_speed) % 2000
            screen_x = x + offset_x
            if -100 < screen_x < camera.screen_width + 100:
                # Draw mountain silhouette
                points = [
                    (screen_x - 50, screen_height // 3),
                    (screen_x, screen_height // 3 - height),
                    (screen_x + 50, screen_height // 3)
                ]
                pygame.draw.polygon(screen, (100, 120, 140), points)
        
        # Render clouds
        clouds = self.bg_layers[1]['data']
        cloud_speed = self.bg_layers[1]['speed']
        for x, y, size in clouds:
            offset_x = -(camera.x * cloud_speed) % 2000
            screen_x = x + offset_x + math.sin(self.time * 0.5 + x * 0.01) * 10
            if -size < screen_x < camera.screen_width + size:
                # Draw simple cloud
                cloud_color = (255, 255, 255, 180)
                self._draw_cloud(screen, screen_x, y, size)
    
    def _draw_cloud(self, screen, x, y, size):
        """Draw a simple cloud shape"""
        # Create cloud with multiple circles
        cloud_surface = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        cloud_color = (255, 255, 255, 120)
        
        # Main cloud body
        pygame.draw.circle(cloud_surface, cloud_color, (size, size // 2), size // 2)
        pygame.draw.circle(cloud_surface, cloud_color, (size // 2, size // 2), size // 3)
        pygame.draw.circle(cloud_surface, cloud_color, (size * 3 // 2, size // 2), size // 3)
        
        screen.blit(cloud_surface, (x - size, y - size // 2))
    
    def _calculate_lighting(self, x, y):
        """Calculate lighting factor for tiles"""
        # Simulate sunlight from top-left
        distance_from_light = math.sqrt(x * x + y * y) * 0.01
        base_light = 0.8 + 0.2 * math.sin(self.time * 0.3 + distance_from_light)
        return max(0.6, min(1.2, base_light))
    
    def _load_background_image(self):
        """Load the background landscape image"""
        try:
            # Get the path to the images folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(current_dir, '..', 'ui', 'images')
            image_path = os.path.join(images_dir, 'level_1_field.JPEG')
            
            # Load image
            image = pygame.image.load(image_path)
            
            # Scale image to match world dimensions
            scaled_image = pygame.transform.scale(image, (self.world_width, self.world_height))
            return scaled_image
        except pygame.error as e:
            print(f"Could not load background image: {e}")
            return None
    
    def _render_background_image(self, screen, camera):
        """Render the background image with camera offset"""
        # Calculate the portion of the image to display based on camera position
        source_rect = pygame.Rect(
            int(camera.x), int(camera.y),
            min(camera.screen_width, self.world_width - int(camera.x)),
            min(camera.screen_height, self.world_height - int(camera.y))
        )
        
        # Make sure we don't go outside image bounds
        if source_rect.x < 0:
            source_rect.x = 0
        if source_rect.y < 0:
            source_rect.y = 0
        if source_rect.right > self.world_width:
            source_rect.width = self.world_width - source_rect.x
        if source_rect.bottom > self.world_height:
            source_rect.height = self.world_height - source_rect.y
        
        # Calculate destination position on screen
        dest_x = max(0, -camera.x) if camera.x < 0 else 0
        dest_y = max(0, -camera.y) if camera.y < 0 else 0
        
        # Blit the visible portion of the background image
        if source_rect.width > 0 and source_rect.height > 0:
            screen.blit(self.background_image, (dest_x, dest_y), source_rect)
    
    def _render_tiles_fallback(self, screen, camera):
        """Fallback tile rendering if background image fails to load"""
        # Terrain colors with variations
        terrain_colors = {
            'grass': [(34, 139, 34), (50, 155, 50), (20, 120, 20)]
        }
        
        # Calculate visible tiles
        start_x = max(0, int(camera.x // self.tile_size))
        start_y = max(0, int(camera.y // self.tile_size))
        end_x = min(self.width, int((camera.x + camera.screen_width) // self.tile_size) + 1)
        end_y = min(self.height, int((camera.y + camera.screen_height) // self.tile_size) + 1)
        
        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.terrain[y][x]
                color_variants = terrain_colors[tile_type]
                
                # Choose color variant based on position for consistency
                color_index = (x + y * 3) % len(color_variants)
                base_color = color_variants[color_index]
                
                # Calculate screen position
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_x, screen_y = camera.world_to_screen(world_x, world_y)
                
                # Add subtle lighting effect
                light_factor = self._calculate_lighting(x, y)
                color = tuple(int(c * light_factor) for c in base_color)
                
                # Draw tile
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, self.tile_size, self.tile_size))
                
                # Add simple grass details
                pygame.draw.circle(screen, (20, 100, 20), 
                                 (screen_x + 6, screen_y + 10), 1)
                pygame.draw.circle(screen, (20, 100, 20), 
                                 (screen_x + 26, screen_y + 22), 1)
    
    def _add_ambient_shadows(self, screen, screen_x, screen_y, tile_x, tile_y):
        """Add subtle ambient shadows for depth"""
        # Create shadow based on surrounding tiles
        shadow_intensity = 0
        
        # Check surrounding tiles for height differences
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x, check_y = tile_x + dx, tile_y + dy
                if 0 <= check_x < self.width and 0 <= check_y < self.height:
                    neighbor_tile = self.terrain[check_y][check_x]
                    if neighbor_tile in ['mountain', 'forest']:
                        if dx == -1 and dy == 1:  # Bottom-left shadow
                            shadow_intensity += 20
        
        if shadow_intensity > 0:
            shadow_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, min(shadow_intensity, 60)))
            screen.blit(shadow_surface, (screen_x, screen_y))