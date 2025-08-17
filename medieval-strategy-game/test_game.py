#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    try:
        import pygame
        print("✓ Pygame imported successfully")
        
        from game.game_manager import GameManager
        print("✓ GameManager imported successfully")
        
        from game.states.menu_state import MenuState
        from game.states.game_state import GameState
        print("✓ Game states imported successfully")
        
        from game.world.map import GameMap
        from game.world.camera import Camera
        from game.world.castle import Castle
        print("✓ World components imported successfully")
        
        from game.entities.unit import Unit, UnitManager
        from game.entities.resource import Resource, ResourceManager
        print("✓ Entity components imported successfully")
        
        from game.ui.hud import HUD
        print("✓ UI components imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    try:
        # Test basic object creation
        from game.world.map import GameMap
        from game.world.camera import Camera
        from game.world.castle import Castle
        from game.entities.unit import Unit
        from game.entities.resource import Resource
        
        # Create test objects
        game_map = GameMap(10, 10)
        camera = Camera(800, 600, game_map.world_width, game_map.world_height)
        castle = Castle(100, 100, "player")
        unit = Unit(50, 50, "peasant", "player")
        cavalry = Unit(75, 75, "cavalry", "player")
        resource = Resource(200, 200, "gold")
        
        print("✓ Basic object creation successful")
        
        # Test some basic methods
        assert game_map.is_walkable(100, 100) in [True, False]
        assert castle.level == 1
        assert unit.is_alive() == True
        assert cavalry.is_alive() == True
        assert cavalry.unit_type == "cavalry"
        assert cavalry.speed == 120  # Cavalry should be fast
        assert resource.amount > 0
        
        print("✓ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Medieval Strategy Game...")
    print("=" * 40)
    
    if test_imports():
        print("\nTesting basic functionality...")
        if test_basic_functionality():
            print("\n✓ All tests passed! Game is ready to run.")
            print("\nTo play the game, run: python main.py")
        else:
            print("\n✗ Some functionality tests failed.")
    else:
        print("\n✗ Import tests failed. Please check dependencies.")
    
    print("=" * 40)