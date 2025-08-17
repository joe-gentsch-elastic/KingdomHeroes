import pygame
import os

class Castle:
    def __init__(self, x, y, owner="player"):
        self.x = x
        self.y = y
        self.owner = owner
        self.level = 1
        self.max_level = 5
        self.health = 5500
        self.max_health = 5500
        self.size = 128  # Larger size for castle images
        
        # Load castle image
        self.image = self._load_castle_image()
        
        # Resources stored in castle
        self.resources = {
            'gold': 100,
            'wood': 50,
            'stone': 30,
            'food': 80
        }
        
        # Units garrisoned in castle
        self.garrison = []
        self.max_garrison = 10
        
        # Permanent upgrade bonuses for all player units
        self.upgrade_bonus = 1.0  # Multiplier for unit stats (starts at 1.0 = no bonus)
        
        # Load saved castle level and upgrade bonus if this is a player castle
        if self.owner == "player":
            self.load_castle_upgrades()
        
        # Defense system (only for player castles)
        if self.owner == "player":
            self.defense_range = 500  # Attack range for castle defenses
            self.defense_damage = 60  # Damage per attack #40
            self.defense_cooldown = 1.0  # Seconds between attacks
            self.last_defense_attack = 0
            self.defense_target = None
            self.defense_flash = 0  # Visual effect for attacks
        
        # Castle colors based on owner
        self.colors = {
            'player': (100, 100, 200),
            'enemy': (200, 100, 100),
            'neutral': (150, 150, 150)
        }
    
    def upgrade(self):
        if self.level < self.max_level:
            # Cost to upgrade
            cost = {
                'gold': 50 * self.level,
                'wood': 30 * self.level,
                'stone': 40 * self.level
            }
            
            # Check if player has enough resources
            if all(self.resources.get(resource, 0) >= amount for resource, amount in cost.items()):
                # Deduct resources
                for resource, amount in cost.items():
                    self.resources[resource] -= amount
                
                # Upgrade castle
                self.level += 1
                self.max_health += 50
                self.health = self.max_health
                self.max_garrison += 5
                self.size += 8
                
                # Apply permanent 15% bonus to all player units
                if self.owner == "player":
                    self.upgrade_bonus *= 1.15  # 15% increase
                    # Save the new castle level and upgrade bonus
                    self.save_castle_upgrades()
                    
                return True
        return False
    
    def get_upgrade_cost(self):
        """Get the cost for the next upgrade"""
        if self.level < self.max_level:
            return {
                'gold': 50 * self.level,
                'wood': 30 * self.level,
                'stone': 40 * self.level
            }
        return None
    
    def save_castle_upgrades(self):
        """Save castle level and upgrade bonus to file"""
        try:
            with open("castle_upgrades.txt", "w") as f:
                f.write(f"{self.level}\n")
                f.write(f"{self.upgrade_bonus}\n")
        except Exception as e:
            print(f"Could not save castle upgrades: {e}")
    
    def load_castle_upgrades(self):
        """Load castle level and upgrade bonus from file"""
        try:
            with open("castle_upgrades.txt", "r") as f:
                saved_level = int(f.readline().strip())
                saved_bonus = float(f.readline().strip())
                
                # Apply the saved upgrades
                level_difference = saved_level - self.level
                if level_difference > 0:
                    # Upgrade castle to saved level
                    for _ in range(level_difference):
                        self.level += 1
                        self.max_health += 50
                        self.max_garrison += 5
                        self.size += 8
                    
                    # Set health to max after upgrades
                    self.health = self.max_health
                    
                # Set the saved upgrade bonus
                self.upgrade_bonus = saved_bonus
                
        except FileNotFoundError:
            # File doesn't exist yet, use defaults
            pass
        except Exception as e:
            print(f"Could not load castle upgrades: {e}")
    
    def add_resources(self, resource_type, amount):
        if resource_type in self.resources:
            self.resources[resource_type] += amount
    
    def can_recruit_unit(self, unit_cost):
        return all(self.resources.get(resource, 0) >= amount for resource, amount in unit_cost.items())
    
    def recruit_unit(self, unit_type, unit_cost):
        if self.can_recruit_unit(unit_cost):
            # Deduct resources
            for resource, amount in unit_cost.items():
                self.resources[resource] -= amount
            
            # Add unit to garrison (no limit)
            self.garrison.append(unit_type)
            return True
        return False
    
    def render(self, screen, camera):
        if camera.is_visible(self.x, self.y, self.size, self.size):
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            
            # Draw castle image if available
            if self.image:
                screen.blit(self.image, (screen_x, screen_y))
                
                # Draw castle border
                pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, self.size, self.size), 2)
                
                # Draw level indicator with background
                font = pygame.font.Font(None, 24)
                level_text = font.render(str(self.level), True, (255, 255, 255))
                text_rect = level_text.get_rect(center=(screen_x + self.size // 2, screen_y + self.size // 2))
                
                # Add background for level text for better visibility
                bg_rect = pygame.Rect(text_rect.x - 5, text_rect.y - 2, text_rect.width + 10, text_rect.height + 4)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
                pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1)
                screen.blit(level_text, text_rect)
            else:
                # Fallback to colored rectangles if image fails to load
                color = self.colors.get(self.owner, (150, 150, 150))
                pygame.draw.rect(screen, color, (screen_x, screen_y, self.size, self.size))
                
                # Add castle details
                self._draw_castle_details(screen, screen_x, screen_y)
                
                # Draw castle border
                pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, self.size, self.size), 2)
                
                # Draw level indicator
                font = pygame.font.Font(None, 24)
                level_text = font.render(str(self.level), True, (255, 255, 255))
                text_rect = level_text.get_rect(center=(screen_x + self.size // 2, screen_y + self.size // 2))
                screen.blit(level_text, text_rect)
            
            # Draw enhanced health bar
            self._draw_health_bar(screen, screen_x, screen_y)
            
            # Draw defense effects for player castle
            if self.owner == "player":
                self._draw_defense_effects(screen, screen_x, screen_y, camera)
    
    def _draw_castle_details(self, screen, screen_x, screen_y):
        """Draw detailed castle graphics"""
        # Castle towers
        tower_size = self.size // 4
        pygame.draw.rect(screen, (80, 80, 80), 
                        (screen_x, screen_y, tower_size, tower_size))
        pygame.draw.rect(screen, (80, 80, 80), 
                        (screen_x + self.size - tower_size, screen_y, tower_size, tower_size))
        pygame.draw.rect(screen, (80, 80, 80), 
                        (screen_x, screen_y + self.size - tower_size, tower_size, tower_size))
        pygame.draw.rect(screen, (80, 80, 80), 
                        (screen_x + self.size - tower_size, screen_y + self.size - tower_size, tower_size, tower_size))
        
        # Castle gate
        gate_width = self.size // 3
        gate_height = self.size // 2
        gate_x = screen_x + (self.size - gate_width) // 2
        gate_y = screen_y + self.size - gate_height
        pygame.draw.rect(screen, (40, 40, 40), 
                        (gate_x, gate_y, gate_width, gate_height))
        
        # Castle flags
        if self.owner == "player":
            flag_color = (0, 0, 255)
        elif self.owner == "enemy":
            flag_color = (255, 0, 0)
        else:
            flag_color = (128, 128, 128)
        
        # Draw flags on towers
        pygame.draw.rect(screen, flag_color, 
                        (screen_x + tower_size//2 - 2, screen_y - 8, 4, 8))
        pygame.draw.rect(screen, flag_color, 
                        (screen_x + self.size - tower_size//2 - 2, screen_y - 8, 4, 8))
    
    def _draw_health_bar(self, screen, screen_x, screen_y):
        """Draw enhanced health bar with background"""
        bar_width = self.size
        bar_height = 6
        bar_y = screen_y - 12
        
        # Health bar background
        pygame.draw.rect(screen, (100, 100, 100), 
                        (screen_x, bar_y, bar_width, bar_height))
        
        # Health bar border
        pygame.draw.rect(screen, (0, 0, 0), 
                        (screen_x, bar_y, bar_width, bar_height), 1)
        
        # Health bar fill
        health_width = int((self.health / self.max_health) * bar_width)
        if health_width > 0:
            # Color based on health percentage
            health_percent = self.health / self.max_health
            if health_percent > 0.6:
                health_color = (0, 255, 0)
            elif health_percent > 0.3:
                health_color = (255, 255, 0)
            else:
                health_color = (255, 0, 0)
            
            pygame.draw.rect(screen, health_color, 
                            (screen_x, bar_y, health_width, bar_height))
    
    def _draw_defense_effects(self, screen, screen_x, screen_y, camera):
        """Draw castle defense system visual effects"""
        import math
        import time
        
        castle_center_x = screen_x + self.size // 2
        castle_center_y = screen_y + self.size // 2
        
        # Draw defense range indicator (subtle circle)
        if hasattr(self, 'defense_range'):
            # Convert world defense range to screen pixels
            range_radius = int(self.defense_range * camera.zoom if hasattr(camera, 'zoom') else self.defense_range)
            
            # Pulsing defense range circle
            pulse = abs(math.sin(time.time() * 2)) * 0.3 + 0.7
            range_alpha = int(30 * pulse)
            
            # Create a surface for the range circle
            range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (0, 255, 0, range_alpha), 
                             (range_radius, range_radius), range_radius, 2)
            screen.blit(range_surface, (castle_center_x - range_radius, castle_center_y - range_radius))
        
        # Draw defense flash effect when attacking
        if hasattr(self, 'defense_flash') and self.defense_flash > 0:
            flash_intensity = int(self.defense_flash * 255)
            flash_surface = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 0, flash_intensity))
            screen.blit(flash_surface, (screen_x - 10, screen_y - 10))
            
            # Draw projectile effect if we have a target
            if hasattr(self, 'defense_target') and self.defense_target:
                target_screen_x, target_screen_y = camera.world_to_screen(
                    self.defense_target.x, self.defense_target.y)
                target_center_x = target_screen_x + (self.defense_target.size // 2 if hasattr(self.defense_target, 'size') else 0)
                target_center_y = target_screen_y + (self.defense_target.size // 2 if hasattr(self.defense_target, 'size') else 0)
                
                # Draw energy beam
                pygame.draw.line(screen, (255, 255, 0, flash_intensity), 
                               (castle_center_x, castle_center_y), 
                               (target_center_x, target_center_y), 3)
                
                # Draw impact effect at target
                impact_radius = int(10 * self.defense_flash)
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (target_center_x, target_center_y), impact_radius, 2)
        
        # Draw defense turrets on castle corners
        turret_size = 8
        turret_positions = [
            (screen_x + 5, screen_y + 5),  # Top-left
            (screen_x + self.size - turret_size - 5, screen_y + 5),  # Top-right
            (screen_x + 5, screen_y + self.size - turret_size - 5),  # Bottom-left
            (screen_x + self.size - turret_size - 5, screen_y + self.size - turret_size - 5)  # Bottom-right
        ]
        
        for turret_x, turret_y in turret_positions:
            # Draw turret base
            pygame.draw.rect(screen, (80, 80, 80), 
                           (turret_x, turret_y, turret_size, turret_size))
            # Draw turret cannon
            pygame.draw.circle(screen, (60, 60, 60), 
                             (turret_x + turret_size // 2, turret_y + turret_size // 2), 3)
    
    def get_bounds(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def contains_point(self, world_x, world_y):
        return self.get_bounds().collidepoint(world_x, world_y)
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
    
    def is_alive(self):
        return self.health > 0
    
    def defense_attack(self, target):
        """Castle defense system attacks a target"""
        if self.owner != "player":
            return False
            
        import pygame
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_defense_attack >= self.defense_cooldown:
            # Calculate distance to target
            target_x = target.x + (target.size // 2 if hasattr(target, 'size') else 0)
            target_y = target.y + (target.size // 2 if hasattr(target, 'size') else 0)
            castle_center_x = self.x + self.size // 2
            castle_center_y = self.y + self.size // 2
            
            distance = ((castle_center_x - target_x)**2 + (castle_center_y - target_y)**2)**0.5
            if distance <= self.defense_range:
                target.take_damage(self.defense_damage)
                self.last_defense_attack = current_time
                self.defense_flash = 0.5  # Flash for 0.5 seconds
                self.defense_target = target
                return True
        return False
    
    def update_defense(self, dt, enemy_units):
        """Update castle defense system"""
        if self.owner != "player":
            return
            
        # Update visual effects
        if self.defense_flash > 0:
            self.defense_flash -= dt
        
        # Find nearest enemy within range
        nearest_enemy = None
        nearest_distance = float('inf')
        castle_center_x = self.x + self.size // 2
        castle_center_y = self.y + self.size // 2
        
        for enemy in enemy_units:
            if enemy.is_alive():
                enemy_x = enemy.x + (enemy.size // 2 if hasattr(enemy, 'size') else 0)
                enemy_y = enemy.y + (enemy.size // 2 if hasattr(enemy, 'size') else 0)
                distance = ((castle_center_x - enemy_x)**2 + (castle_center_y - enemy_y)**2)**0.5
                
                if distance <= self.defense_range and distance < nearest_distance:
                    nearest_distance = distance
                    nearest_enemy = enemy
        
        # Attack nearest enemy
        if nearest_enemy:
            self.defense_attack(nearest_enemy)
    
    def _load_castle_image(self):
        """Load castle image based on owner"""
        try:
            # Get the path to the images folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(current_dir, '..', 'ui', 'images')
            
            # Choose image based on owner
            if self.owner == "player":
                image_path = os.path.join(images_dir, "your_castle.jpeg")
            else:
                image_path = os.path.join(images_dir, "enemy_castle.jpeg")
            
            # Load and scale image
            image = pygame.image.load(image_path)
            # Scale to castle size
            scaled_image = pygame.transform.scale(image, (self.size, self.size))
            return scaled_image
        except pygame.error:
            print(f"Could not load castle image for {self.owner}")
            return None