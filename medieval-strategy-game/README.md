# Medieval Strategy Game

A 2D medieval-themed pixel-art strategy game built with Python and Pygame. Control a kingdom, build and upgrade castles, gather resources, recruit units, and lead armies in real-time battles.

## Features

- **Scrollable Campaign Map**: Navigate a large procedurally generated world
- **Castle Management**: Build and upgrade your castle with multiple levels
- **Resource System**: Gather gold, wood, stone, and food to fuel your kingdom
- **Unit Recruitment**: Train peasants, knights, archers, and catapults
- **Real-time Combat**: Engage in battles with enemy units and castles
- **Strategic Gameplay**: Manage resources, plan attacks, and defend your territory

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Controls

- **WASD/Arrow Keys**: Move camera around the map
- **Left Click**: Select units or interact with UI
- **Right clicky**: Move selected units
- **Shift + Left Click**: Add units to selection
- **ESC**: Return to main menu

## Game Mechanics

### Resources
- **Gold**: Primary currency for units and upgrades
- **Wood**: Used for archers and siege weapons
- **Stone**: Required for castle upgrades and heavy units
- **Food**: Needed to sustain your army

### Units
- **Peasant**: Basic unit, cheap and weak
- **Knight**: Heavy melee unit with high health
- **Archer**: Ranged unit with long attack range
- **Catapult**: Siege weapon with massive damage

### Castle Upgrades
- Each level increases health, garrison size, and unlocks new capabilities
- Higher level castles generate more resources over time
- Upgraded castles are harder for enemies to destroy

## Development

The game uses a modular architecture with separate systems for:
- Game states (menu, gameplay)
- World management (map, camera, castles)
- Entity systems (units, resources, buildings)
- User interface (HUD, menus)

## Future Enhancements

- Multiplayer support
- Campaign mode with story missions
- More unit types and castle upgrades
- Advanced AI for enemy kingdoms
- Save/load game functionality
- Sound effects and music