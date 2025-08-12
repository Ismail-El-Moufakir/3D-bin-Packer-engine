# 3D Bin Packing – Layer-by-Layer Greedy Algorithm (Python)

## Overview
This project implements a **layer-by-layer 3D bin packing algorithm** in Python using a **greedy heuristic**.  
Instead of placing items anywhere in 3D space, it fills bins **one horizontal layer at a time**, maximizing available surface usage before stacking to the next layer.

## Features
- **Greedy + Layering**: Sorts items by priority and fills each layer before moving upward.
- **Full orientation support**: Items are rotated to find the best fit in the current layer.
- **Collision detection**: Ensures no overlaps in each layer or across layers.
- **Free space splitting**: After each placement, available space is updated for the current layer.
- **Item attributes**: Supports `stackable`, `fragile`, and `group_id` for grouping logic.

## How It Works
1. **Sort items** by priority (e.g., order, weight).
2. **Start from the base layer** at `z = 0`.
3. **Fill the current layer** using available free rectangles in 2D (width × length).
4. **When no item fits** in the current layer:
   - Raise the layer height to the top of the tallest item in that layer.
   - Begin a new layer.
5. Repeat until all items are packed or no space remains.

## Requirements
- Python 3.9+
- `numpy`
- `plotly` *(optional, for visualization)*

Install dependencies:
```bash
pip install numpy plotly
