# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A 2D medieval-themed strategy game built with Python and Pygame. The game features scrollable maps, resource management, unit recruitment, and real-time combat. Players control kingdoms, build castles, manage resources, and lead armies in tactical battles.

## Development Commands

### Running the Game
```bash
python main.py
```

### Testing
```bash
python test_game.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### State Management System
The game uses a state-based architecture managed by `GameManager`:
- `MenuState`: Main menu and game start
- `GameState`: Active gameplay with world, units, and UI
- `BaseState`: Abstract base class for all game states

### Core Systems

#### World System (`game/world/`)
- `GameMap`: Procedurally generated terrain with tile-based rendering
- `Camera`: Viewport management for scrolling around the world
- `Castle`: Player and enemy strongholds with upgradeable levels

#### Entity System (`game/entities/`)
- `Unit`: All movable game pieces (peasants, knights, archers, catapults)
- `UnitManager`: Handles selection, movement, combat, and AI
- `Resource`: Collectible resources (gold, wood, stone, food)
- `ResourceManager`: Resource collection and management

#### UI System (`game/ui/`)
- `HUD`: Game interface showing resources, unit info, and controls
- Image assets stored in `game/ui/images/`

### Unit Types and Balance
- **Peasant**: Basic cheap unit (25 HP, 5 damage, 16 range)
- **Knight**: Heavy melee unit (80 HP, 20 damage, 20 range)
- **Archer**: Ranged unit (40 HP, 15 damage, 80 range)
- **Cavalry**: Fast mounted unit (65 HP, 18 damage, 24 range, 120 speed)
- **Catapult**: Siege weapon (60 HP, 40 damage, 120 range)

Enemy units are automatically weakened (30% less health, 20% less damage, 10% slower) for game balance.

### Resource System
- **Gold**: Primary currency for all units and upgrades
- **Wood**: Required for archers and siege weapons
- **Stone**: Needed for castle upgrades and heavy units
- **Food**: Sustains army units

## Code Conventions

### File Structure
- Game logic organized in modules: `entities/`, `world/`, `states/`, `ui/`
- Each module has `__init__.py` for proper Python packaging
- Unit images stored as JPEG files in `ui/images/`

### Rendering Pipeline
1. `GameMap.render()` - Draw terrain tiles with camera culling
2. `UnitManager.render()` - Draw all units with effects
3. `HUD.render()` - Draw UI overlays

### Combat System
- Range-based combat with cooldowns
- Health bars appear when units are damaged
- Visual effects include combat flashes and movement trails
- Enemy AI targets nearest player units or castle

### Camera System
- World-to-screen coordinate conversion
- Visibility culling for performance
- Smooth scrolling with WASD/arrow keys