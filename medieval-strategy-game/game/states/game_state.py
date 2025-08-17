import pygame
import random
from .base_state import BaseState
from ..world.map import GameMap
from ..world.camera import Camera
from ..world.castle import Castle
from ..entities.resource import ResourceManager
from ..entities.unit import UnitManager, Unit
from ..ui.hud import HUD

class GameState(BaseState):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # Initialize game world
        self.game_map = GameMap(50, 50)  # 50x50 tiles (smaller arena)
        self.camera = Camera(self.screen_width, self.screen_height, 
                           self.game_map.world_width, self.game_map.world_height)
        
        # Initialize player castle
        self.player_castle = Castle(200, 150, "player")
        
        # Initialize enemy castles (scaled by difficulty)
        level_num = getattr(self.game_manager, 'current_level', 1)
        if level_num == 1:
            self.enemy_castles = [Castle(1000, 750, "enemy")]
        elif level_num == 2:
            self.enemy_castles = [Castle(1000, 750, "enemy"), Castle(500, 1250, "enemy")]
        else:
            self.enemy_castles = [
                Castle(1000, 750, "enemy"),
                Castle(500, 1250, "enemy"),
                Castle(1400, 400, "enemy")
            ]
        
        # Initialize resource manager
        self.resource_manager = ResourceManager(self.game_map)
        
        # Initialize unit manager
        self.unit_manager = UnitManager()
        
        # Initialize HUD
        self.hud = HUD(self.screen_width, self.screen_height)
        
        # Game timer for resource generation
        self.resource_timer = 0
        self.resource_interval = 0.7  # Generate resources every 2 seconds
        
        # Enemy spawning timer (scaled by difficulty)
        self.enemy_spawn_timer = 0
        level_info = getattr(self.game_manager, 'current_level_info', None) or {'spawn_rate': 1.0, 'enemy_mult': 1.0}
        self.enemy_spawn_interval = 25.0 * level_info['spawn_rate']  # Spawn enemy units (faster = lower interval)
        self.enemy_multiplier = level_info['enemy_mult']
        
        # Game state
        self.game_over = False
        self.victory = False
        self.defeat = False
        
        # Mouse state
        self.mouse_drag_start = None
        self.selecting_units = False
        self.selection_rect = None
        self.move_target = None
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.change_state("menu")
            elif event.key == pygame.K_f:
                # Move selected units to mouse position
                if self.unit_manager.selected_units:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y)
                    self.unit_manager.move_selected_units(world_x, world_y)
                    self.move_target = (world_x, world_y)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if clicking on HUD
                current_level = getattr(self.game_manager, 'current_level', 1)
                if self.hud.handle_click(mouse_x, mouse_y, self.player_castle, self.unit_manager, current_level, 
                                       self.enemy_castles, self.unit_manager.selected_units):
                    return
                
                # Convert screen coordinates to world coordinates
                world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y)
                
                # Check if clicking on a unit
                clicked_unit = self.unit_manager.get_unit_at(world_x, world_y)
                if clicked_unit and clicked_unit.owner == "player":
                    if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        self.unit_manager.deselect_all()
                    self.unit_manager.select_unit(clicked_unit)
                else:
                    # Start selection rectangle
                    self.mouse_drag_start = (mouse_x, mouse_y)
                    self.selecting_units = True
                    self.unit_manager.deselect_all()
            
            # Right click functionality removed - now using F key for movement
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.selecting_units:
                    # End selection rectangle
                    self.selecting_units = False
                    self.selection_rect = None
                    self.mouse_drag_start = None
        
        elif event.type == pygame.MOUSEMOTION:
            if self.selecting_units and self.mouse_drag_start:
                # Update selection rectangle
                mouse_x, mouse_y = event.pos
                start_x, start_y = self.mouse_drag_start
                
                # Create selection rectangle
                min_x = min(start_x, mouse_x)
                min_y = min(start_y, mouse_y)
                width = abs(mouse_x - start_x)
                height = abs(mouse_y - start_y)
                
                self.selection_rect = pygame.Rect(min_x, min_y, width, height)
                
                # Select units within rectangle
                self.unit_manager.deselect_all()
                for unit in self.unit_manager.units:
                    if unit.owner == "player":
                        unit_screen_x, unit_screen_y = self.camera.world_to_screen(unit.x, unit.y)
                        unit_screen_rect = pygame.Rect(unit_screen_x, unit_screen_y, unit.size, unit.size)
                        if self.selection_rect.colliderect(unit_screen_rect):
                            self.unit_manager.select_unit(unit)
    
    def update(self, dt):
        # Update camera
        self.camera.update(dt)
        
        # Update resource manager
        self.resource_manager.update(dt)
        
        # Update unit manager
        self.unit_manager.update(dt, self.player_castle, self.enemy_castles)
        
        # Update castle defense system
        enemy_units = self.unit_manager.get_units_by_owner("enemy")
        self.player_castle.update_defense(dt, enemy_units)
        
        # Generate resources periodically
        self.resource_timer += dt
        if self.resource_timer >= self.resource_interval:
            self.resource_timer = 0
            # Add resources to player castle
            self.player_castle.add_resources('gold', 5)
            self.player_castle.add_resources('food', 3)
            self.player_castle.add_resources('wood', 2)
            self.player_castle.add_resources('stone', 1)
        
        # Spawn enemy units periodically (only if game is not over)
        if not self.game_over:
            self.enemy_spawn_timer += dt
            if self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.enemy_spawn_timer = 0
                self._spawn_enemy_units()
        
        # Simple combat system
        self._handle_combat()
        
        # Check for game over conditions
        self._check_game_over()
    
    def _handle_combat(self):
        # Simple combat between player and enemy units
        player_units = self.unit_manager.get_units_by_owner("player")
        enemy_units = self.unit_manager.get_units_by_owner("enemy")
        
        # Player units attack nearby enemies and enemy castles
        for player_unit in player_units:
            attacked = False
            # Attack enemy units first
            for enemy_unit in enemy_units:
                distance = ((player_unit.x - enemy_unit.x)**2 + (player_unit.y - enemy_unit.y)**2)**0.5
                if distance <= player_unit.attack_range:
                    player_unit.attack(enemy_unit)
                    attacked = True
                    break
            
            # If no enemy units in range, attack enemy castles
            if not attacked:
                for enemy_castle in self.enemy_castles:
                    if enemy_castle.is_alive():
                        # Calculate distance to castle center
                        castle_center_x = enemy_castle.x + enemy_castle.size // 2
                        castle_center_y = enemy_castle.y + enemy_castle.size // 2
                        distance = ((player_unit.x - castle_center_x)**2 + (player_unit.y - castle_center_y)**2)**0.5
                        if distance <= player_unit.attack_range:
                            player_unit.attack(enemy_castle)
                            break
        
        # Enemy units prioritize attacking player castle
        for enemy_unit in enemy_units:
            attacked = False
            # Attack player castle first if in range
            if self.player_castle.is_alive():
                castle_center_x = self.player_castle.x + self.player_castle.size // 2
                castle_center_y = self.player_castle.y + self.player_castle.size // 2
                distance = ((enemy_unit.x - castle_center_x)**2 + (enemy_unit.y - castle_center_y)**2)**0.5
                if distance <= enemy_unit.attack_range:
                    enemy_unit.attack(self.player_castle)
                    attacked = True
            
            # If castle not in range, attack player units
            if not attacked:
                for player_unit in player_units:
                    distance = ((enemy_unit.x - player_unit.x)**2 + (enemy_unit.y - player_unit.y)**2)**0.5
                    if distance <= enemy_unit.attack_range:
                        enemy_unit.attack(player_unit)
                        break
    
    def render(self):
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render game world
        self.game_map.render(self.screen, self.camera)
        
        # Render resources
        self.resource_manager.render(self.screen, self.camera)
        
        # Render castles
        self.player_castle.render(self.screen, self.camera)
        for castle in self.enemy_castles:
            castle.render(self.screen, self.camera)
        
        # Render units
        self.unit_manager.render(self.screen, self.camera)
        
        # Render selection rectangle
        if self.selection_rect:
            pygame.draw.rect(self.screen, (255, 255, 255), self.selection_rect, 2)
        
        # Render HUD
        current_level = getattr(self.game_manager, 'current_level', 1)
        self.hud.render(self.screen, self.player_castle, self.unit_manager.selected_units, self.camera, current_level)
        
        # Render instructions and level info
        font = pygame.font.Font(None, 24)
        level_info = getattr(self.game_manager, 'current_level_info', None) or {'name': 'Unknown'}
        instructions = [
            f"Level {getattr(self.game_manager, 'current_level', 1)}: {level_info['name']}",
            "WASD/Arrow Keys: Move Camera",
            "Left Click: Select Units",
            "F Key: Move Units",
            "ESC: Return to Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            self.screen.blit(text, (10, 10 + i * 25))
        
        # Render game over messages
        if self.game_over:
            self._render_game_over_message()
    
    def _spawn_enemy_units(self):
        # Spawn enemy units from random enemy castles
        if self.enemy_castles:
            spawn_castle = random.choice(self.enemy_castles)
            
            # Choose random unit type (include musket at level 5+, cannon at level 6+, battalion at level 10+, giant at level 21+)
            unit_types = ['peasant', 'knight', 'archer', 'cavalry']
            current_level = getattr(self.game_manager, 'current_level', 1)
            if current_level >= 5:
                unit_types.append('musket')
            if current_level >= 6:
                unit_types.append('cannon')
            if current_level >= 10:
                unit_types.append('battalion')
            if current_level >= 21:
                unit_types.append('giant')
            unit_type = random.choice(unit_types)
            
            # Spawn 1-2 units near the castle
            num_units = random.randint(1, 2)
            for _ in range(num_units):
                # Random position around castle
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-50, 50)
                spawn_x = spawn_castle.x + offset_x
                spawn_y = spawn_castle.y + offset_y
                
                # Create and add enemy unit (apply difficulty scaling)
                enemy_unit = Unit(spawn_x, spawn_y, unit_type, "enemy")
                # Apply additional difficulty scaling
                enemy_unit.health = int(enemy_unit.health * self.enemy_multiplier)
                enemy_unit.max_health = int(enemy_unit.max_health * self.enemy_multiplier)
                enemy_unit.attack_damage = int(enemy_unit.attack_damage * self.enemy_multiplier)
                self.unit_manager.add_unit(enemy_unit)
                
                # Special handling for enemy battalions - spawn knights
                if unit_type == 'battalion':
                    enemy_unit.spawn_battalion_knights(self.unit_manager)
    
    def _check_game_over(self):
        if self.game_over:
            return
        
        # Check if player castle is destroyed
        if not self.player_castle.is_alive():
            self.game_over = True
            self.defeat = True
            print("DEFEAT! Your castle has been destroyed!")
        
        # Check if all enemy castles are destroyed
        alive_enemy_castles = [castle for castle in self.enemy_castles if castle.is_alive()]
        if not alive_enemy_castles:
            self.game_over = True
            self.victory = True
            print("VICTORY! All enemy castles have been destroyed!")
            # Unlock next level
            self.game_manager.level_completed()
        
        # Remove dead enemy castles from the list
        self.enemy_castles = [castle for castle in self.enemy_castles if castle.is_alive()]
    
    def _render_game_over_message(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Create game over message
        font = pygame.font.Font(None, 72)
        if self.victory:
            message = "VICTORY!"
            color = (0, 255, 0)
        else:
            message = "DEFEAT!"
            color = (255, 0, 0)
        
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)
        
        # Add instruction and level info
        small_font = pygame.font.Font(None, 36)
        instruction = small_font.render("Press ESC to return to menu", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(instruction, instruction_rect)
        
        # Show level completed message for victory
        if self.victory:
            level_font = pygame.font.Font(None, 24)
            level_text = level_font.render(f"Level {getattr(self.game_manager, 'current_level', 1)} Completed!", True, (0, 255, 0))
            level_rect = level_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 110))
            self.screen.blit(level_text, level_rect)