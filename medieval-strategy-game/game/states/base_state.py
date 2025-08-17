from abc import ABC, abstractmethod
import pygame

class BaseState(ABC):
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.screen = game_manager.screen
        self.screen_width = game_manager.screen_width
        self.screen_height = game_manager.screen_height
    
    @abstractmethod
    def handle_event(self, event):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def render(self):
        pass
    
    def enter(self):
        pass
    
    def exit(self):
        pass