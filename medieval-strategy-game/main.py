import pygame
import sys
from game.game_manager import GameManager

def main():
    pygame.init()
    
    # Game settings
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 60
    
    # Create display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Medieval Strategy Game")
    clock = pygame.time.Clock()
    
    # Initialize game manager
    game_manager = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)
        
        # Update game
        game_manager.update(dt)
        
        # Render game
        game_manager.render()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()