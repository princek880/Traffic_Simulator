# Traffic Simulation Network

Pygame-based traffic routing simulation demonstrating capacity-constrained network flows. Vehicles route from Source nodes to Sink nodes across Junctions and Roads using centralized shortest-path calculations.

## Architecture
* **Road**: Capacity-limited queues moving vehicles between nodes. Validates admission based on current load and queue sizes.
* **Junction**: Routing pass-through element utilizing centralized next-hop lookup. Adheres to processing rate intervals to simulate junction delay.
* **Source**: Spawns vehicles at defined intervals based on configured rate.
* **Sink**: Terminates vehicle paths. Absorbs network traffic.
* **CentralizedRouting**: Dijkstra-based shortest path calculator updating route weights.
* **GUIBuilder**: Pygame interface managing network construction and simulation rendering.

## Requirements
* Python 3.x
* Pygame

## Execution
```bash
pip install pygame
python main.py
```

## UI Controls
### Build Mode (Default)
* **Space**: Toggle Build Mode (`NODE` / `ROAD`).
* **Left Click (Empty space)**: Place Node (`NODE` mode).
* **Left Click (Node to Node)**: Draw Road (`ROAD` mode).
* **Right Click (Node)**: Cycle Node Type (Junction -> Source -> Sink).
* **Up / Down Arrows**: Adjust global Source spawn rate.
* **Left / Right Arrows**: Adjust global Road capacity.
* **S**: Start Simulation.

### Simulation Mode
Displays real-time vehicle movement. Moving vehicles are colored solid circles. Queued vehicles stack with black outlines behind junctions.
