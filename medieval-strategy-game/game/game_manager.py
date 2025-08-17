import pygame
from .states.menu_state import MenuState
from .states.game_state import GameState

class GameManager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize states
        self.states = {
            "menu": MenuState(self),
            "game": GameState(self)
        }
        
        # Start with menu state
        self.current_state = self.states["menu"]
        self.current_state.enter()
        
        # Level system
        self.current_level = 1
        self.current_level_info = None
    
    def change_state(self, state_name):
        if state_name in self.states:
            self.current_state.exit()
            self.current_state = self.states[state_name]
            self.current_state.enter()
    
    def handle_event(self, event):
        self.current_state.handle_event(event)
    
    def update(self, dt):
        self.current_state.update(dt)
    
    def render(self):
        self.current_state.render()
    
    def start_level(self, level_num, level_info):
        """Start a specific level with given difficulty parameters"""
        self.current_level = level_num
        self.current_level_info = level_info
        # Recreate game state with new difficulty
        self.states["game"] = GameState(self)
    
    def level_completed(self):
        """Called when a level is completed successfully"""
        # Unlock next level in menu state
        menu_state = self.states["menu"]
        menu_state.unlock_next_level()
        # Return to menu
        self.change_state("menu")