import pygame
import math
import random
from .base_state import BaseState

class MenuState(BaseState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("Kingdom Heroes", True, (255, 215, 0))
        self.start_text = pygame.font.Font(None, 36).render("Press SPACE to Begin Your Quest", True, (255, 255, 255))
        self.subtitle_text = pygame.font.Font(None, 32).render("Conquer the Realm", True, (200, 200, 200))
        
        # Animation variables
        self.time = 0
        self.particles = []
        self.init_particles()
        
        # Level selection system
        self.max_level = self.load_max_level()
        self.selected_level = 1
        self.current_level = 1
        self.level_fonts = {
            'title': pygame.font.Font(None, 48),
            'level': pygame.font.Font(None, 36),
            'description': pygame.font.Font(None, 24)
        }
        
        # Level definitions (21 levels total)
        self.levels = {
            1: {'name': 'Novice Knight', 'description': 'Learn the basics of warfare', 'enemy_mult': 1.0, 'spawn_rate': 1.0},
            2: {'name': 'Skilled Warrior', 'description': 'Face stronger opposition', 'enemy_mult': 1.3, 'spawn_rate': 0.9},
            3: {'name': 'Veteran Commander', 'description': 'Multiple enemy castles', 'enemy_mult': 1.6, 'spawn_rate': 0.8},
            4: {'name': 'Master Tactician', 'description': 'Elite enemy forces', 'enemy_mult': 2.0, 'spawn_rate': 0.7},
            5: {'name': 'Legendary Conqueror', 'description': 'Musket unlocked', 'enemy_mult': 2.5, 'spawn_rate': 0.6},
            6: {'name': 'Artillery Master', 'description': 'Cannon unlocked', 'enemy_mult': 3.0, 'spawn_rate': 0.5},
            7: {'name': 'Fortress Breaker', 'description': 'Heavily fortified enemies', 'enemy_mult': 3.5, 'spawn_rate': 0.45},
            8: {'name': 'War Machine', 'description': 'Endless enemy waves', 'enemy_mult': 4.0, 'spawn_rate': 0.4},
            9: {'name': 'Battle Hardened', 'description': 'Elite enemy commanders', 'enemy_mult': 4.5, 'spawn_rate': 0.35},
            10: {'name': 'Iron Fist', 'description': 'Massive enemy armies', 'enemy_mult': 5.0, 'spawn_rate': 0.3},
            11: {'name': 'Storm Bringer', 'description': 'Lightning fast enemies', 'enemy_mult': 5.5, 'spawn_rate': 0.28},
            12: {'name': 'Castle Crusher', 'description': 'Enemy siege weapons', 'enemy_mult': 6.0, 'spawn_rate': 0.26},
            13: {'name': 'Lord of War', 'description': 'Multiple enemy fronts', 'enemy_mult': 6.5, 'spawn_rate': 0.24},
            14: {'name': 'Death Dealer', 'description': 'Overwhelming odds', 'enemy_mult': 7.0, 'spawn_rate': 0.22},
            15: {'name': 'Apex Predator', 'description': 'Elite death squads', 'enemy_mult': 7.5, 'spawn_rate': 0.2},
            16: {'name': 'Nightmare Lord', 'description': 'Relentless assault', 'enemy_mult': 8.0, 'spawn_rate': 0.18},
            17: {'name': 'Demon Slayer', 'description': 'Supernatural enemies', 'enemy_mult': 8.5, 'spawn_rate': 0.16},
            18: {'name': 'God of War', 'description': 'Divine intervention needed', 'enemy_mult': 9.0, 'spawn_rate': 0.14},
            19: {'name': 'World Ender', 'description': 'Reality bending enemies', 'enemy_mult': 9.5, 'spawn_rate': 0.12},
            20: {'name': 'Omnipotent Ruler', 'description': 'Ultimate challenge', 'enemy_mult': 10.0, 'spawn_rate': 0.7},
            21: {'name': 'Giant Battle', 'description': 'Giant unlocked', 'enemy_mult': 10.5, 'spawn_rate': 0.5},
            22: {'name': 'Titan Clash', 'description': 'Colossal warfare', 'enemy_mult': 11.0, 'spawn_rate': 0.45},
            23: {'name': 'Behemoth Rising', 'description': 'Massive creatures emerge', 'enemy_mult': 11.5, 'spawn_rate': 0.4},
            24: {'name': 'Leviathan War', 'description': 'Sea monsters join battle', 'enemy_mult': 12.0, 'spawn_rate': 0.35},
            25: {'name': 'Kraken Storm', 'description': 'Tentacled terror', 'enemy_mult': 12.5, 'spawn_rate': 0.3},
            26: {'name': 'Dragon Emperor', 'description': 'Ancient wyrms awaken', 'enemy_mult': 13.0, 'spawn_rate': 0.25},
            27: {'name': 'Phoenix Apocalypse', 'description': 'Eternal flame enemies', 'enemy_mult': 13.5, 'spawn_rate': 0.2},
            28: {'name': 'Cosmic Overlord', 'description': 'Stellar domination', 'enemy_mult': 14.0, 'spawn_rate': 0.15},
            29: {'name': 'Void Master', 'description': 'Reality-warping foes', 'enemy_mult': 14.5, 'spawn_rate': 0.1},
            30: {'name': 'Ultimate Conqueror', 'description': 'Final challenge awaits', 'enemy_mult': 15.0, 'spawn_rate': 0.05}
    }


        
        # Background elements
        self.castle_points = [
            (100, 400), (120, 350), (140, 350), (160, 400),
            (180, 350), (200, 350), (220, 400), (240, 450)
        ]
        
        self.mountains = [
            [(50, 500), (80, 400), (110, 500)],
            [(700, 500), (730, 380), (760, 500)],
            [(600, 520), (640, 420), (680, 520)]
        ]
        #### add image of castle to menu
        self.castle_image = pygame.image.load("/Users/joegentsch/PycharmProjects/vibe_coding_copy/teddy_project/teddy_project_2/medieval-strategy-game/game/ui/images/menubackground.jpeg").convert_alpha()
        self.castle_image = pygame.transform.scale(self.castle_image, (self.screen_width, self.screen_height))  # Resize as needed
        #self.castle_image = pygame.transform.scale(self.castle_image, (200, 150))  # Resize as needed
        self.castle_pos = (self.screen_width // 1000, self.screen_height // 1000 )  # Adjust position
        #self.castle_pos = (self.screen_width // 2 - 100, self.screen_height // 2 - 200)  # Adjust position

        
    def init_particles(self):
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, 1500),
                'y': random.randint(0, 1000),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3),
                'alpha': random.randint(100, 1000) #woo, 255
            })
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.start_level()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.selected_level = max(1, self.selected_level - 1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_level = min(min(30, self.max_level), self.selected_level + 1)
            elif event.key == pygame.K_RETURN:
                self.start_level()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check level selection buttons (up to 30 levels in multiple rows)
            levels_per_row = 10
            max_display_level = min(30, self.max_level + 1)
            
            for i in range(1, max_display_level + 1):
                row = (i - 1) // levels_per_row
                col = (i - 1) % levels_per_row
                
                level_x = self.screen_width // 2 - 225 + col * 45
                level_y = self.screen_height // 2 + 20 + row * 50
                
                level_rect = pygame.Rect(level_x - 18, level_y - 18, 36, 36)
                if level_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_level = i
                    break
            
            # Check start button
            start_rect = self.start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 180))
            if start_rect.collidepoint(mouse_x, mouse_y):
                self.start_level()
    
    def update(self, dt):
        self.time += dt
        
        # Update particles
        for particle in self.particles:
            particle['y'] -= particle['speed']
            particle['alpha'] = int(150 + 50 * math.sin(self.time * 2 + particle['x'] * 0.01))
            
            if particle['y'] < 0:
                particle['y'] = 1000
                particle['x'] = random.randint(0, 1000)
    
    def render(self):
        # Animated gradient background
        for y in range(self.screen_height):
            t = y / self.screen_height
            r = int(10 + 20 * math.sin(self.time * 0.5 + t * 2))
            g = int(20 + 30 * math.sin(self.time * 0.3 + t * 3))
            b = int(40 + 40 * math.sin(self.time * 0.7 + t * 1.5))
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        # Draw mountains
        for mountain in self.mountains:
            pygame.draw.polygon(self.screen, (60, 60, 80), mountain)
            # Add snow caps
            if len(mountain) >= 3:
                peak = mountain[1]
                snow_points = [
                    (peak[0] - 15, peak[1] + 20),
                    peak,
                    (peak[0] + 15, peak[1] + 20)
                ]
                pygame.draw.polygon(self.screen, (200, 200, 220), snow_points)

        #Make castle
        self.screen.blit(self.castle_image, self.castle_pos) ### JOE ADDED HERE
        
        # Draw castle silhouette
        for i in range(len(self.castle_points) - 1):
            pygame.draw.line(self.screen, (40, 40, 60), 
                           self.castle_points[i], self.castle_points[i + 1], 3)
        
        # Draw animated particles (stars/fireflies)
        for particle in self.particles:
            alpha_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            alpha_surface.set_alpha(particle['alpha'])
            alpha_surface.fill((255, 255, 150))
            self.screen.blit(alpha_surface, (particle['x'], particle['y']))
        
        # Animated title with glow effect
        title_glow = pygame.font.Font(None, 78).render("Kingdom Heroes", True, (100, 50, 0))
        title_rect = title_glow.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        
        # Draw glow (offset in multiple directions)
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    glow_rect = title_rect.copy()
                    glow_rect.x += dx
                    glow_rect.y += dy
                    self.screen.blit(title_glow, glow_rect)
        
        # Draw main title
        title_rect = self.title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(self.title_text, title_rect)
        
        # Subtitle
        subtitle_rect = self.subtitle_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(self.subtitle_text, subtitle_rect)
        
        # Level selection UI
        level_title = self.level_fonts['title'].render("Select Level", True, (255, 215, 0))
        level_title_rect = level_title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        self.screen.blit(level_title, level_title_rect)
        
        # Level buttons (30 levels in 3 rows)
        levels_per_row = 10
        max_display_level = min(30, self.max_level + 1)
        
        for i in range(1, max_display_level + 1):
            row = (i - 1) // levels_per_row
            col = (i - 1) % levels_per_row
            
            level_x = self.screen_width // 2 - 225 + col * 45
            level_y = self.screen_height // 2 + 20 + row * 50
            
            # Determine button color and availability
            if i <= self.max_level:
                if i == self.selected_level:
                    color = (255, 215, 0)  # Gold for selected
                    bg_color = (100, 50, 0)
                else:
                    color = (255, 255, 255)  # White for available
                    bg_color = (50, 50, 50)
            else:
                color = (100, 100, 100)  # Gray for locked
                bg_color = (30, 30, 30)
            
            # Draw level button background
            pygame.draw.circle(self.screen, bg_color, (level_x, level_y), 18)
            pygame.draw.circle(self.screen, color, (level_x, level_y), 18, 2)
            
            # Draw level number
            font_size = 24 if i < 10 else 20  # Smaller font for double digits
            level_font = pygame.font.Font(None, font_size)
            level_text = level_font.render(str(i), True, color)
            level_text_rect = level_text.get_rect(center=(level_x, level_y))
            self.screen.blit(level_text, level_text_rect)
            
            # Draw lock icon for unavailable levels
            if i > self.max_level:
                lock_points = [(level_x - 4, level_y - 4), (level_x + 4, level_y - 4), 
                              (level_x + 4, level_y + 4), (level_x - 4, level_y + 4)]
                pygame.draw.polygon(self.screen, (150, 150, 150), lock_points)
        
        # Selected level info
        if self.selected_level <= self.max_level:
            level_info = self.levels[self.selected_level]
            level_name = self.level_fonts['level'].render(level_info['name'], True, (255, 215, 0))
            level_name_rect = level_name.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 130))
            self.screen.blit(level_name, level_name_rect)
            
            level_desc = self.level_fonts['description'].render(level_info['description'], True, (200, 200, 200))
            level_desc_rect = level_desc.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 155))
            self.screen.blit(level_desc, level_desc_rect)
        
        # Start button
        pulse = int(200 + 55 * math.sin(self.time * 3))
        start_color = (pulse, pulse, pulse)
        start_text = "Press SPACE or ENTER to Start" if self.selected_level <= self.max_level else "Complete Previous Levels"
        start_surface = pygame.font.Font(None, 32).render(start_text, True, start_color)
        start_rect = start_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 180))
        self.screen.blit(start_surface, start_rect)
        
        # Controls info
        controls_text = self.level_fonts['description'].render("Use A/D or Arrow Keys to select level", True, (150, 150, 150))
        controls_rect = controls_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 210))
        self.screen.blit(controls_text, controls_rect)
        
        # Draw decorative border
        border_color = (100, 100, 120)
        pygame.draw.rect(self.screen, border_color, (10, 10, self.screen_width - 20, self.screen_height - 20), 3)
        
        # Corner decorations
        corner_size = 30
        corners = [
            (20, 20), (self.screen_width - 50, 20),
            (20, self.screen_height - 50), (self.screen_width - 50, self.screen_height - 50)
        ]
        for corner in corners:
            pygame.draw.circle(self.screen, (150, 120, 80), corner, corner_size // 2, 2)
    
    def load_max_level(self):
        """Load the maximum level unlocked by the player"""
        try:
            with open('save_data.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 1  # Start with level 1 unlocked
    
    def save_max_level(self, level):
        """Save the maximum level unlocked"""
        try:
            with open('save_data.txt', 'w') as f:
                f.write(str(level))
        except:
            pass  # Ignore save errors
    
    def start_level(self):
        """Start the selected level if it's unlocked"""
        if self.selected_level <= self.max_level:
            # Update current level
            self.current_level = self.selected_level
            # Pass level info to game manager
            level_info = self.levels[self.selected_level]
            self.game_manager.start_level(self.selected_level, level_info)
            self.game_manager.change_state("game")
    
    def unlock_next_level(self):
        """Unlock the next level when current level is completed"""
        if self.max_level < 30:
            self.max_level += 1
            self.save_max_level(self.max_level)