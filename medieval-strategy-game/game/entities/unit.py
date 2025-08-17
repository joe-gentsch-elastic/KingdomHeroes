import pygame
import math
import random
import os

class Unit:
    def __init__(self, x, y, unit_type, owner="player", upgrade_bonus=1.0):
        self.x = x
        self.y = y
        self.unit_type = unit_type
        self.owner = owner
        self.size = 48
        
        # Unit stats based on type
        self.stats = self._get_unit_stats(unit_type)
        
        # Apply upgrade bonuses to stats (but not cost) for player units
        if owner == "player" and upgrade_bonus > 1.0:
            self.health = int(self.stats['max_health'] * upgrade_bonus)
            self.max_health = int(self.stats['max_health'] * upgrade_bonus)
            self.speed = int(self.stats['speed'] * upgrade_bonus)
            self.attack_damage = int(self.stats['attack_damage'] * upgrade_bonus)
            self.attack_range = int(self.stats['attack_range'] * upgrade_bonus)
        else:
            self.health = self.stats['max_health']
            self.max_health = self.stats['max_health']
            self.speed = self.stats['speed']
            self.attack_damage = self.stats['attack_damage']
            self.attack_range = self.stats['attack_range']
        
        self.cost = self.stats['cost']  # Cost never changes
        
        # Make enemy units weaker than players
        if self.owner == "enemy":
            self.health = int(self.health * 0.5)  # 50% less health
            self.max_health = int(self.max_health * 0.5)
            self.attack_damage = int(self.attack_damage * 0.5)  # 50% less damage
            self.speed = int(self.speed * 0.8)  # 20% slower
        
        # Movement and combat
        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.target_enemy = None
        self.last_attack_time = 0
        self.attack_cooldown = 1  # 1 second between attacks
        
        # Selection
        self.selected = False
        
        # Visual effects
        self.combat_flash = 0
        self.movement_trail = []
        
        # Colors based on unit type and owner
        self.colors = self._get_unit_colors(unit_type, owner)
        
        # Load unit image
        self.image = self._load_unit_image(unit_type)
        self.image_rect = self.image.get_rect() if self.image else None
        
        # Special battalion properties
        self.is_battalion = (unit_type == 'battalion')
        self.spawned_knights = []  # Track spawned knights for battalions
        
        # Special dragoons properties
        self.is_dragoons = (unit_type == 'dragoons')
        self.spawned_cavalry = []  # Track spawned cavalry for dragoons
        
        # Special commander properties
        self.is_commander = (unit_type == 'commander')
        self.command_mode = False  # Whether commander is actively leading units
        self.command_target = None  # Target enemy castle for leading attack
    
    def _get_unit_stats(self, unit_type):
        stats = {
            'peasant': {
                'max_health': 60,
                'speed': 100,
                'attack_damage': 25,
                'attack_range': 20,
                'cost': {'gold': 10, 'food': 5}
            },
            'knight': {
                'max_health': 120,
                'speed':45,
                'attack_damage': 40,
                'attack_range': 20,
                'cost': {'gold': 40, 'food': 20, 'stone': 10}
            },
            'archer': {
                'max_health': 60,
                'speed': 70,
                'attack_damage': 40,
                'attack_range': 100,
                'cost': {'gold': 30, 'food': 15, 'wood': 10}
            },
            'cavalry': {
                'max_health': 150, #150
                'speed': 180,
                'attack_damage': 80, #80
                'attack_range': 30,
                'cost': {'gold': 0, 'food': 0, 'stone': 0}
            },
            'catapult': {
                'max_health': 250,
                'speed': 30,
                'attack_damage': 60,
                'attack_range': 200,
                'cost': {'gold': 100, 'food': 30, 'wood': 40, 'stone': 20}
            },
            'musket': {
                'max_health': 60,
                'speed': 60,
                'attack_damage': 50,
                'attack_range': 300,
                'cost': {'gold': 30, 'food': 25, 'wood': 15, 'stone': 10}
            },
            'cannon': {
                'max_health': 200,
                'speed': 25,
                'attack_damage': 200,
                'attack_range': 175,
                'cost': {'gold': 80, 'food': 30, 'wood': 34, 'stone': 25}
            },
            'battalion': {
                'max_health': 150,  # Battalion commander health
                'speed': 80,
                'attack_damage': 40,
                'attack_range': 25,
                'cost': {'gold': 0, 'food': 0, 'wood': 0, 'stone': 0}
            },
            'dragoons': {
                'max_health': 120,  # Dragoon commander health
                'speed': 180,
                'attack_damage': 30,
                'attack_range': 35,
                'cost': {'gold': 100, 'food': 40, 'wood': 0, 'stone': 0}
            },
            'commander': {
                'max_health': 120,  # Commander health
                'speed': 180,
                'attack_damage': 150,
                'attack_range': 25,
                'cost': {'gold': 80, 'food': 20, 'wood': 5, 'stone': 5}
            },
            'giant': {
                'max_health': 300,  # Giant health - very high
                'speed': 40,         # Very slow
                'attack_damage': 150, # Massive damage
                'attack_range': 20,   # Good reach
                'cost': {'gold': 100, 'food': 50, 'wood': 0, 'stone': 15}
            }
        }
        return stats.get(unit_type, stats['peasant'])
    
    def _get_unit_colors(self, unit_type, owner):
        # Base colors for each unit type
        type_colors = {
            'peasant': {
                'player': (100, 150, 255),    # Light blue
                'enemy': (255, 150, 100),     # Light red/orange
                'neutral': (150, 150, 150)   # Gray
            },
            'knight': {
                'player': (50, 100, 200),     # Dark blue
                'enemy': (200, 100, 50),      # Dark red
                'neutral': (100, 100, 100)   # Dark gray
            },
            'archer': {
                'player': (100, 255, 100),    # Green
                'enemy': (255, 100, 255),     # Magenta
                'neutral': (150, 200, 150)   # Light gray-green
            },
            'cavalry': {
                'player': (150, 100, 255),    # Purple
                'enemy': (255, 100, 150),     # Pink
                'neutral': (175, 125, 175)   # Light purple-gray
            },
            'catapult': {
                'player': (200, 200, 100),    # Yellow
                'enemy': (200, 100, 200),     # Purple
                'neutral': (150, 150, 100)   # Brown-gray
            },
            'musket': {
                'player': (128, 128, 128),    # Gray
                'enemy': (169, 169, 169),     # Dark gray
                'neutral': (105, 105, 105)   # Dim gray
            },
            'cannon': {
                'player': (60, 60, 60),       # Dark gray
                'enemy': (80, 80, 80),        # Darker gray
                'neutral': (50, 50, 50)       # Very dark gray
            },
            'battalion': {
                'player': (255, 215, 0),      # Gold
                'enemy': (255, 140, 0),       # Dark orange
                'neutral': (218, 165, 32)     # Golden rod
            },
            'dragoons': {
                'player': (138, 43, 226),     # Blue violet
                'enemy': (148, 0, 211),       # Dark violet
                'neutral': (186, 85, 211)     # Medium orchid
            },
            'commander': {
                'player': (255, 215, 0),      # Gold
                'enemy': (255, 140, 0),       # Dark orange
                'neutral': (218, 165, 32)     # Golden rod
            },
            'giant': {
                'player': (139, 69, 19),      # Brown
                'enemy': (160, 82, 45),       # Saddle brown
                'neutral': (205, 133, 63)     # Peru
            }
        }
        
        return type_colors.get(unit_type, type_colors['peasant']).get(owner, (128, 128, 128))
    
    def _load_unit_image(self, unit_type):
        try:
            # Get the path to the images folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(current_dir, '..', 'ui', 'images')
            image_path = os.path.join(images_dir, f"{unit_type}.jpeg")
            
            # Load and scale image
            image = pygame.image.load(image_path)
            # Scale to unit size (16x16 pixels)
            scaled_image = pygame.transform.scale(image, (self.size, self.size))
            return scaled_image
        except pygame.error:
            print(f"Could not load image for {unit_type}")
            return None
    
    def _apply_color_tint(self, image, tint_color):
        """Apply a color tint to an image while preserving transparency"""
        if image is None:
            return None
        
        # Create a copy of the image
        tinted_image = image.copy()
        
        # Create a surface with the tint color
        tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*tint_color, 128))  # 128 is alpha for 50% transparency
        
        # Blend the tint with the image
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_image
    
    def move_to(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.is_moving = True
    
    def attack(self, target):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_attack_time >= self.attack_cooldown:
            # Calculate distance to target center
            target_x = target.x
            target_y = target.y
            
            # If target is a castle, use its center instead of top-left corner
            if hasattr(target, 'size') and target.size > 32:  # Castle has size 64+
                target_x = target.x + target.size // 2
                target_y = target.y + target.size // 2
            
            distance = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
            if distance <= self.attack_range:
                target.take_damage(self.attack_damage)
                self.last_attack_time = current_time
                self.combat_flash = 0.3  # Flash for 0.3 seconds
                return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
    
    def is_alive(self):
        return self.health > 0
    
    def update(self, dt):
        if not self.is_alive():
            return
        
        # Update visual effects
        if self.combat_flash > 0:
            self.combat_flash -= dt
        
        # Movement
        if self.is_moving:
            # Add to movement trail
            self.movement_trail.append((self.x, self.y))
            if len(self.movement_trail) > 5:  # Keep last 5 positions
                self.movement_trail.pop(0)
            
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 2:  # Still moving
                move_distance = self.speed * dt
                self.x += (dx / distance) * move_distance
                self.y += (dy / distance) * move_distance
            else:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
        else:
            # Clear movement trail when not moving
            if self.movement_trail:
                self.movement_trail.clear()
        
        # Combat AI for both player and enemy units
        if not self.is_moving:
            if self.owner == "enemy":
                # Enemy AI: find nearest player unit or move towards player castle
                nearest_target = self._find_nearest_player_target()
                if nearest_target:
                    distance = math.sqrt((self.x - nearest_target[0])**2 + (self.y - nearest_target[1])**2)
                    if distance > self.attack_range:
                        # Move towards target
                        self.move_to(nearest_target[0], nearest_target[1])
            elif self.owner == "player":
                # Player AI: find nearest enemy within 200 units and attack
                nearest_target = self._find_nearest_enemy_target()
                if nearest_target:
                    distance = math.sqrt((self.x - nearest_target[0])**2 + (self.y - nearest_target[1])**2)
                    if distance <= 200:  # Only engage enemies within 200 units
                        if distance > self.attack_range:
                            # Move towards target
                            self.move_to(nearest_target[0], nearest_target[1])
    
    def _find_nearest_player_target(self):
        # This method needs access to other units, so we'll implement it in UnitManager
        # For now, return None to avoid errors
        return None
    
    def _find_nearest_enemy_target(self):
        # This method needs access to other units, so we'll implement it in UnitManager
        # For now, return None to avoid errors
        return None
    
    def render(self, screen, camera):
        if self.is_alive() and camera.is_visible(self.x, self.y, self.size, self.size):
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            
            # Draw movement trail
            self._draw_movement_trail(screen, camera)
            
            # Draw unit shadow
            self._draw_shadow(screen, screen_x, screen_y)
            
            # Draw unit
            if self.image:
                # Apply color tint for enemy units
                if self.owner == "enemy":
                    tinted_image = self._apply_color_tint(self.image, (255, 150, 150))  # Red tint
                elif self.owner == "player":
                    tinted_image = self._apply_color_tint(self.image, (150, 150, 255))  # Blue tint
                else:
                    tinted_image = self.image
                
                # Apply combat flash effect
                if self.combat_flash > 0:
                    flash_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                    flash_surface.fill((255, 255, 255, int(self.combat_flash * 255)))
                    screen.blit(tinted_image, (screen_x, screen_y))
                    screen.blit(flash_surface, (screen_x, screen_y))
                else:
                    screen.blit(tinted_image, (screen_x, screen_y))
            else:
                # Fallback to colored circle if image fails to load
                color = self.colors
                if self.combat_flash > 0:
                    # Make brighter during combat flash
                    color = tuple(min(255, c + int(self.combat_flash * 100)) for c in color)
                pygame.draw.circle(screen, color, 
                                 (screen_x + self.size // 2, screen_y + self.size // 2), 
                                 self.size // 2)
            
            # Draw selection indicator with glow effect
            if self.selected:
                # Animated selection ring
                import time
                pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
                selection_color = (int(255 * pulse), int(255 * pulse), 0)
                pygame.draw.circle(screen, selection_color, 
                                 (screen_x + self.size // 2, screen_y + self.size // 2), 
                                 self.size // 2 + 4, 3)
                # Inner glow
                glow_surface = pygame.Surface((self.size + 16, self.size + 16), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 255, 0, 30), 
                                 (self.size // 2 + 8, self.size // 2 + 8), self.size // 2 + 8)
                screen.blit(glow_surface, (screen_x - 8, screen_y - 8))
            
            # Draw enhanced health bar
            if self.health < self.max_health:
                self._draw_enhanced_health_bar(screen, screen_x, screen_y)
    
    def _draw_movement_trail(self, screen, camera):
        """Draw a trail showing unit movement"""
        if len(self.movement_trail) > 1:
            for i, (trail_x, trail_y) in enumerate(self.movement_trail):
                if camera.is_visible(trail_x, trail_y, 4, 4):
                    screen_x, screen_y = camera.world_to_screen(trail_x, trail_y)
                    alpha = int((i / len(self.movement_trail)) * 100)  # Fade trail
                    trail_color = (*self.colors[:3], alpha) if isinstance(self.colors, tuple) else (100, 100, 100, alpha)
                    pygame.draw.circle(screen, trail_color[:3], 
                                     (screen_x + self.size // 2, screen_y + self.size // 2), 
                                     2)
    
    def _draw_shadow(self, screen, screen_x, screen_y):
        """Draw unit shadow for depth"""
        shadow_offset_x = 3
        shadow_offset_y = 3
        shadow_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Create shadow shape
        if self.image:
            # Shadow based on image shape (simplified as oval)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 60), 
                              (4, 4, self.size - 8, self.size // 2))
        else:
            # Shadow for circle units
            pygame.draw.circle(shadow_surface, (0, 0, 0, 60), 
                             (self.size // 2, self.size // 2), self.size // 2 - 2)
        
        screen.blit(shadow_surface, (screen_x + shadow_offset_x, screen_y + shadow_offset_y))
    
    def _draw_enhanced_health_bar(self, screen, screen_x, screen_y):
        """Draw enhanced health bar with gradient and border"""
        bar_width = self.size
        bar_height = 6
        bar_y = screen_y - 10
        
        # Health bar background with border
        pygame.draw.rect(screen, (0, 0, 0), (screen_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, (60, 60, 60), (screen_x, bar_y, bar_width, bar_height))
        
        # Health bar fill with gradient effect
        health_width = int((self.health / self.max_health) * bar_width)
        if health_width > 0:
            health_percent = self.health / self.max_health
            
            # Color based on health percentage
            if health_percent > 0.6:
                start_color = (0, 200, 0)
                end_color = (0, 255, 0)
            elif health_percent > 0.3:
                start_color = (200, 200, 0)
                end_color = (255, 255, 0)
            else:
                start_color = (200, 0, 0)
                end_color = (255, 0, 0)
            
            # Draw gradient health bar
            for i in range(health_width):
                progress = i / bar_width if bar_width > 0 else 0
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                pygame.draw.line(screen, (r, g, b), 
                               (screen_x + i, bar_y), (screen_x + i, bar_y + bar_height - 1))
    
    def get_bounds(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def contains_point(self, world_x, world_y):
        return self.get_bounds().collidepoint(world_x, world_y)
    
    def spawn_battalion_knights(self, unit_manager, upgrade_bonus=1.0):
        """Spawn 6 elite knights around the battalion commander"""
        if not self.is_battalion or self.spawned_knights:
            return  # Only spawn once and only for battalions
        
        knight_positions = [
            (-30, -30), (30, -30),    # Front row
            (-60, 0), (0, 0), (60, 0), # Middle row
            (-30, 30)                  # Back row
        ]
        
        for i, (offset_x, offset_y) in enumerate(knight_positions):
            knight_x = self.x + offset_x
            knight_y = self.y + offset_y
            
            # Create elite knight with enhanced stats and upgrade bonuses
            knight = Unit(knight_x, knight_y, 'knight', self.owner, upgrade_bonus)
            knight.health = int(knight.health * 1.5)  # 50% more health
            knight.max_health = int(knight.max_health * 1.5)
            knight.attack_damage = int(knight.attack_damage * 1.3)  # 30% more damage
            knight.speed = int(knight.speed * 1.2)  # 20% faster
            
            # Mark as elite knight
            knight.is_elite = True
            knight.battalion_commander = self
            
            self.spawned_knights.append(knight)
            unit_manager.add_unit(knight)
    
    def spawn_dragoon_cavalry(self, unit_manager, upgrade_bonus=1.0):
        """Spawn 6 cavalry around the dragoon commander"""
        if not self.is_dragoons or self.spawned_cavalry:
            return  # Only spawn once and only for dragoons
        
        cavalry_positions = [
            (-40, -40), (40, -40),    # Front row
            (-80, 0), (0, 0), (80, 0), # Middle row
            (-40, 40)                  # Back row
        ]
        
        for i, (offset_x, offset_y) in enumerate(cavalry_positions):
            cavalry_x = self.x + offset_x
            cavalry_y = self.y + offset_y
            
            # Create cavalry unit with upgrade bonuses
            cavalry = Unit(cavalry_x, cavalry_y, 'cavalry', self.owner, upgrade_bonus)
            
            # Mark as dragoon cavalry
            cavalry.is_dragoon_cavalry = True
            cavalry.dragoon_commander = self
            
            self.spawned_cavalry.append(cavalry)
            unit_manager.add_unit(cavalry)
    
    def start_command_attack(self, target_castle, unit_manager):
        """Start commanding nearby units to attack target castle"""
        if not self.is_commander:
            return
            
        self.command_mode = True
        self.command_target = target_castle
        
        # Find all player units within command range and order them to attack
        command_range = 300
        for unit in unit_manager.units:
            if (unit.owner == "player" and unit != self and 
                not unit.is_commander and unit.is_alive()):
                distance = ((self.x - unit.x)**2 + (self.y - unit.y)**2)**0.5
                if distance <= command_range:
                    # Order unit to attack the target castle
                    castle_center_x = target_castle.x + target_castle.size // 2
                    castle_center_y = target_castle.y + target_castle.size // 2
                    unit.move_to(castle_center_x, castle_center_y)
                    unit.command_target = target_castle
    
    def stop_command_attack(self):
        """Stop commanding units"""
        self.command_mode = False
        self.command_target = None

class UnitManager:
    def __init__(self):
        self.units = []
        self.selected_units = []
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
        if unit in self.selected_units:
            self.selected_units.remove(unit)
    
    def select_unit(self, unit):
        if unit not in self.selected_units:
            unit.selected = True
            self.selected_units.append(unit)
    
    def deselect_unit(self, unit):
        if unit in self.selected_units:
            unit.selected = False
            self.selected_units.remove(unit)
    
    def deselect_all(self):
        for unit in self.selected_units:
            unit.selected = False
        self.selected_units.clear()
    
    def move_selected_units(self, target_x, target_y):
        for i, unit in enumerate(self.selected_units):
            # Spread units out in formation
            offset_x = (i % 3 - 1) * 20
            offset_y = (i // 3 - 1) * 20
            unit.move_to(target_x + offset_x, target_y + offset_y)
    
    def get_unit_at(self, world_x, world_y):
        for unit in self.units:
            if unit.contains_point(world_x, world_y) and unit.is_alive():
                return unit
        return None
    
    def update(self, dt, player_castle=None, enemy_castles=None):
        # Update all units
        for unit in self.units[:]:
            # Set AI target for enemy units
            if unit.owner == "enemy" and not unit.is_moving:
                target = self._find_nearest_target_for_enemy(unit, player_castle)
                if target:
                    distance = math.sqrt((unit.x - target[0])**2 + (unit.y - target[1])**2)
                    if distance > unit.attack_range:
                        unit.move_to(target[0], target[1])
            
            # Set AI target for player units
            elif unit.owner == "player" and not unit.is_moving:
                target = self._find_nearest_target_for_player(unit, player_castle, enemy_castles)
                if target:
                    distance = math.sqrt((unit.x - target[0])**2 + (unit.y - target[1])**2)
                    if distance <= 200 and distance > unit.attack_range:  # Only engage within 200 units
                        unit.move_to(target[0], target[1])
            
            unit.update(dt)
            # Remove dead units
            if not unit.is_alive():
                self.remove_unit(unit)
    
    def _find_nearest_target_for_enemy(self, enemy_unit, player_castle):
        # Always prioritize attacking the player castle
        if player_castle and player_castle.is_alive():
            castle_center_x = player_castle.x + player_castle.size // 2
            castle_center_y = player_castle.y + player_castle.size // 2
            return (castle_center_x, castle_center_y)
        
        # Fallback to player units if castle is destroyed
        nearest_target = None
        nearest_distance = float('inf')
        
        for unit in self.units:
            if unit.owner == "player" and unit.is_alive():
                distance = math.sqrt((enemy_unit.x - unit.x)**2 + (enemy_unit.y - unit.y)**2)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_target = (unit.x, unit.y)
        
        return nearest_target
    
    def _find_nearest_target_for_player(self, player_unit, player_castle, enemy_castles=None):
        """Find nearest enemy unit or enemy castle for player units to attack"""
        nearest_target = None
        nearest_distance = float('inf')
        
        # Check enemy units first (priority target)
        for unit in self.units:
            if unit.owner == "enemy" and unit.is_alive():
                distance = math.sqrt((player_unit.x - unit.x)**2 + (player_unit.y - unit.y)**2)
                if distance < nearest_distance and distance <= 200:  # Only within 200 units
                    nearest_distance = distance
                    nearest_target = (unit.x, unit.y)
        
        # If no enemy units in range, target enemy castles
        if nearest_target is None and enemy_castles:
            for castle in enemy_castles:
                if castle.is_alive():
                    # Target castle center
                    castle_center_x = castle.x + castle.size // 2
                    castle_center_y = castle.y + castle.size // 2
                    distance = math.sqrt((player_unit.x - castle_center_x)**2 + (player_unit.y - castle_center_y)**2)
                    if distance < nearest_distance and distance <= 200:  # Only within 200 units
                        nearest_distance = distance
                        nearest_target = (castle_center_x, castle_center_y)
        
        return nearest_target
    
    def render(self, screen, camera):
        for unit in self.units:
            unit.render(screen, camera)
    
    def get_units_by_owner(self, owner):
        return [unit for unit in self.units if unit.owner == owner and unit.is_alive()]
    
    def apply_upgrade_bonus_to_existing_units(self, upgrade_bonus):
        """Apply upgrade bonuses to all existing player units"""
        for unit in self.units:
            if unit.owner == "player" and unit.is_alive():
                # Apply 15% bonus to existing stats
                unit.health = int(unit.health * 1.15)
                unit.max_health = int(unit.max_health * 1.15)
                unit.attack_damage = int(unit.attack_damage * 1.15)
                unit.speed = int(unit.speed * 1.15)
                unit.attack_range = int(unit.attack_range * 1.15)