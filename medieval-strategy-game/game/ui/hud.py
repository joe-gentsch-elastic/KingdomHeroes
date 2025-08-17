import pygame

class HUD:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # HUD dimensions
        self.hud_height = 100
        self.hud_rect = pygame.Rect(0, screen_height - self.hud_height, screen_width, self.hud_height)
        
        # Button dimensions
        self.button_width = 80
        self.button_height = 30
        self.button_margin = 10
        
        # Unit recruitment buttons
        self.recruit_buttons = {
            'peasant': pygame.Rect(10, screen_height - 90, self.button_width, self.button_height),
            'knight': pygame.Rect(100, screen_height - 90, self.button_width, self.button_height),
            'archer': pygame.Rect(190, screen_height - 90, self.button_width, self.button_height),
            'cavalry': pygame.Rect(280, screen_height - 90, self.button_width, self.button_height),
            'catapult': pygame.Rect(370, screen_height - 90, self.button_width, self.button_height),
            'musket': pygame.Rect(460, screen_height - 90, self.button_width, self.button_height),
            'cannon': pygame.Rect(550, screen_height - 90, self.button_width, self.button_height),
            'battalion': pygame.Rect(640, screen_height - 90, self.button_width, self.button_height),
            'dragoons': pygame.Rect(730, screen_height - 90, self.button_width, self.button_height),
            'commander': pygame.Rect(820, screen_height - 90, self.button_width, self.button_height),
            'giant': pygame.Rect(910, screen_height - 90, self.button_width, self.button_height)
        }
        
        # Commander control button
        self.command_button = pygame.Rect(screen_width - 250, screen_height - 50, 120, 30)
        
        # Castle upgrade button
        self.upgrade_button = pygame.Rect(screen_width - 120, screen_height - 90, 100, self.button_height)
        
        # Selected unit info area
        self.info_rect = pygame.Rect(400, screen_height - 90, 300, 80)
    
    def render(self, screen, castle, selected_units, camera, current_level=1):
        # Draw HUD background
        pygame.draw.rect(screen, (40, 40, 40), self.hud_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.hud_rect, 2)
        
        # Draw resources
        self._draw_resources(screen, castle)
        
        # Draw recruitment buttons
        self._draw_recruitment_buttons(screen, castle, current_level)
        
        # Draw upgrade button
        self._draw_upgrade_button(screen, castle)
        
        # Draw selected unit info
        self._draw_selected_unit_info(screen, selected_units)
        
        # Draw commander control button
        self._draw_command_button(screen, selected_units)
        
        # Draw minimap
        self._draw_minimap(screen, camera)
    
    def _draw_resources(self, screen, castle):
        y_offset = self.screen_height - 40
        resources = castle.resources
        
        # Draw resource icons and amounts
        resource_names = ['gold', 'wood', 'stone', 'food']
        colors = {
            'gold': (255, 215, 0),
            'wood': (139, 69, 19),
            'stone': (128, 128, 128),
            'food': (255, 140, 0)
        }
        
        for i, resource in enumerate(resource_names):
            x = 10 + i * 100
            color = colors[resource]
            amount = resources.get(resource, 0)
            
            # Draw resource icon (simple colored circle)
            pygame.draw.circle(screen, color, (x + 10, y_offset), 8)
            
            # Draw resource amount
            text = self.small_font.render(f"{amount}", True, (255, 255, 255))
            screen.blit(text, (x + 25, y_offset - 8))
    
    def _draw_recruitment_buttons(self, screen, castle, current_level=1):
        unit_costs = {
            'peasant': {'gold': 5, 'food': 0},
            'knight': {'gold': 25, 'food': 10, 'stone': 3},
            'archer': {'gold': 30, 'food': 10, 'wood': 3},
            'cavalry': {'gold': 35, 'food': 10, 'stone': 3},
            'catapult': {'gold': 80, 'food': 20, 'wood': 30, 'stone': 20},
            'musket': {'gold': 60, 'food': 25, 'wood': 15, 'stone': 10},
            'cannon': {'gold': 100, 'food': 0, 'wood': 40, 'stone': 50},
            'battalion': {'gold': 60, 'food': 35, 'wood': 25, 'stone': 5},
            'dragoons': {'gold': 150, 'food': 40, 'wood': 60, 'stone': 10},
            'commander': {'gold': 80, 'food': 20, 'wood': 5, 'stone': 5},
            'giant': {'gold': 200, 'food': 80, 'wood': 0, 'stone': 30}
        }
        
        for unit_type, button_rect in self.recruit_buttons.items():
            cost = unit_costs[unit_type]
            can_afford = castle.can_recruit_unit(cost)
            
            # Check if unit is unlocked (musket requires level 5, cannon requires level 6, battalion requires level 10, dragoons requires level 10, commander requires level 15, giant requires level 21)
            is_unlocked = True
            if unit_type == 'musket' and current_level < 5:
                is_unlocked = False
            elif unit_type == 'cannon' and current_level < 6:
                is_unlocked = False
            elif unit_type == 'battalion' and current_level < 10:
                is_unlocked = False
            elif unit_type == 'dragoons' and current_level < 10:
                is_unlocked = False
            elif unit_type == 'commander' and current_level < 15:
                is_unlocked = False
            elif unit_type == 'giant' and current_level < 21:
                is_unlocked = False
            
            # Button color based on affordability and unlock status
            if not is_unlocked:
                color = (50, 50, 50)  # Dark gray for locked
            elif can_afford:
                color = (0, 150, 0)  # Green for affordable
            else:
                color = (100, 100, 100)  # Gray for unaffordable
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
            
            # Button text
            if not is_unlocked:
                text = self.small_font.render("LOCKED", True, (150, 150, 150))
            else:
                text = self.small_font.render(unit_type.capitalize(), True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
    
    def _draw_upgrade_button(self, screen, castle):
        can_upgrade = castle.level < castle.max_level
        
        # Button color based on upgrade availability
        color = (150, 100, 0) if can_upgrade else (100, 100, 100)
        pygame.draw.rect(screen, color, self.upgrade_button)
        pygame.draw.rect(screen, (255, 255, 255), self.upgrade_button, 2)
        
        # Button text
        text = self.small_font.render("Upgrade", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.upgrade_button.center)
        screen.blit(text, text_rect)
        
        # Display upgrade cost underneath button
        if can_upgrade:
            upgrade_cost = castle.get_upgrade_cost()
            if upgrade_cost:
                cost_y = self.upgrade_button.bottom + 5
                cost_text = f"Cost: {upgrade_cost['gold']}G {upgrade_cost['wood']}W {upgrade_cost['stone']}S"
                cost_surface = self.small_font.render(cost_text, True, (255, 255, 255))
                cost_rect = cost_surface.get_rect(center=(self.upgrade_button.centerx, cost_y + 8))
                screen.blit(cost_surface, cost_rect)
    
    def _draw_command_button(self, screen, selected_units):
        # Check if any selected unit is a commander
        has_commander = any(getattr(unit, 'is_commander', False) for unit in selected_units)
        
        if has_commander:
            # Draw command button
            button_color = (150, 100, 0)  # Bronze color
            pygame.draw.rect(screen, button_color, self.command_button)
            pygame.draw.rect(screen, (255, 255, 255), self.command_button, 2)
            
            # Button text
            text = self.small_font.render("ATTACK!", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.command_button.center)
            screen.blit(text, text_rect)
    
    def _draw_selected_unit_info(self, screen, selected_units):
        if not selected_units:
            return
        
        # Draw info background
        pygame.draw.rect(screen, (60, 60, 60), self.info_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.info_rect, 2)
        
        if len(selected_units) == 1:
            # Single unit selected
            unit = selected_units[0]
            y = self.info_rect.y + 10
            
            # Unit type
            text = self.small_font.render(f"Type: {unit.unit_type.capitalize()}", True, (255, 255, 255))
            screen.blit(text, (self.info_rect.x + 10, y))
            
            # Health
            y += 20
            text = self.small_font.render(f"Health: {unit.health}/{unit.max_health}", True, (255, 255, 255))
            screen.blit(text, (self.info_rect.x + 10, y))
            
            # Damage
            y += 20
            text = self.small_font.render(f"Damage: {unit.attack_damage}", True, (255, 255, 255))
            screen.blit(text, (self.info_rect.x + 10, y))
        else:
            # Multiple units selected
            text = self.small_font.render(f"Selected: {len(selected_units)} units", True, (255, 255, 255))
            screen.blit(text, (self.info_rect.x + 10, self.info_rect.y + 10))
    
    def _draw_minimap(self, screen, camera):
        # Simple minimap in top-right corner
        minimap_size = 150
        minimap_x = self.screen_width - minimap_size - 10
        minimap_y = 10
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
        
        # Draw minimap background
        pygame.draw.rect(screen, (20, 20, 20), minimap_rect)
        pygame.draw.rect(screen, (255, 255, 255), minimap_rect, 2)
        
        # Draw camera viewport indicator
        if camera.world_width > 0 and camera.world_height > 0:
            view_x = int((camera.x / camera.world_width) * minimap_size)
            view_y = int((camera.y / camera.world_height) * minimap_size)
            view_w = int((camera.screen_width / camera.world_width) * minimap_size)
            view_h = int((camera.screen_height / camera.world_height) * minimap_size)
            
            view_rect = pygame.Rect(minimap_x + view_x, minimap_y + view_y, view_w, view_h)
            pygame.draw.rect(screen, (255, 255, 0), view_rect, 2)
    
    def handle_click(self, mouse_x, mouse_y, castle, unit_manager, current_level=1, enemy_castles=None, selected_units=None):
        # Check recruitment buttons
        unit_costs = {
            'peasant': {'gold': 5, 'food': 0},
            'knight': {'gold': 25, 'food': 10, 'stone': 3},
            'archer': {'gold': 30, 'food': 10, 'wood': 3},
            'cavalry': {'gold': 35, 'food': 10, 'stone': 3},
            'catapult': {'gold': 80, 'food': 20, 'wood': 30, 'stone': 20},
            'musket': {'gold': 60, 'food': 25, 'wood': 15, 'stone': 10},
            'cannon': {'gold': 100, 'food': 0, 'wood': 40, 'stone': 50},
            'battalion': {'gold': 60, 'food': 35, 'wood': 25, 'stone': 5},
            'dragoons': {'gold': 100, 'food': 40, 'wood': 0, 'stone': 0},
            'commander': {'gold': 80, 'food': 20, 'wood': 5, 'stone': 5},
            'giant': {'gold': 200, 'food': 80, 'wood': 0, 'stone': 30}
        }
        
        for unit_type, button_rect in self.recruit_buttons.items():
            if button_rect.collidepoint(mouse_x, mouse_y):
                # Check if unit is unlocked (musket requires level 5, cannon requires level 6, battalion requires level 10, dragoons requires level 10, commander requires level 15, giant requires level 21)
                is_unlocked = True
                if unit_type == 'musket' and current_level < 5:
                    is_unlocked = False
                elif unit_type == 'cannon' and current_level < 6:
                    is_unlocked = False
                elif unit_type == 'battalion' and current_level < 10:
                    is_unlocked = False
                elif unit_type == 'dragoons' and current_level < 10:
                    is_unlocked = False
                elif unit_type == 'commander' and current_level < 15:
                    is_unlocked = False
                elif unit_type == 'giant' and current_level < 18:
                    is_unlocked = False
                
                if is_unlocked:
                    cost = unit_costs[unit_type]
                    if castle.recruit_unit(unit_type, cost):
                        # Spawn unit near castle with upgrade bonuses
                        from ..entities.unit import Unit
                        unit = Unit(castle.x + castle.size + 20, castle.y + castle.size // 2, unit_type, "player", castle.upgrade_bonus)
                        unit_manager.add_unit(unit)
                        
                        # Special handling for battalion - spawn 6 elite knights
                        if unit_type == 'battalion':
                            unit.spawn_battalion_knights(unit_manager, castle.upgrade_bonus)
                        
                        # Special handling for dragoons - spawn 6 cavalry
                        if unit_type == 'dragoons':
                            unit.spawn_dragoon_cavalry(unit_manager, castle.upgrade_bonus)
                return True
        
        # Check upgrade button
        if self.upgrade_button.collidepoint(mouse_x, mouse_y):
            if castle.upgrade():
                # Apply upgrade bonuses to existing units
                unit_manager.apply_upgrade_bonus_to_existing_units(castle.upgrade_bonus)
            return True
        
        # Check command button
        if (self.command_button.collidepoint(mouse_x, mouse_y) and 
            selected_units and enemy_castles):
            # Find selected commanders
            commanders = [unit for unit in selected_units if getattr(unit, 'is_commander', False)]
            if commanders and enemy_castles:
                # Command attack on nearest enemy castle
                target_castle = min(enemy_castles, 
                                   key=lambda c: ((commanders[0].x - c.x)**2 + (commanders[0].y - c.y)**2)**0.5)
                for commander in commanders:
                    commander.start_command_attack(target_castle, unit_manager)
                return True
        
        return False