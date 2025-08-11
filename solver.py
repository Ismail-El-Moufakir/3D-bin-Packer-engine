from models import *
from geometry import *
from collections import deque
from typing import List
from utils import *

class solver :
    def __init__(self, bins: List[Bin], items: List[Item]):
        self.bins = bins
        self.items = items
        self.placements = []
        self.Available_positions = {bin.id: deque([{"Pos": Vector3(0, 0, 0), "Dim": Vector3(bin.W, bin.L, bin.H)}]) for bin in bins}

    def solve(self):
       self.items = sorted(self.items, key = lambda x: (x.order,x.weight),reverse=True)
     
       for item in self.items:
          print(f"Packing item {item.id} with dimensions {item.dim.x}x{item.dim.y}x{item.dim.z} and weight {item.weight}")
          Placements = []

          # fit item in every bin and choose bin to pack object using a computed score
          for bin in self.bins:
              is_placed = False
              while self.Available_positions[bin.id]:
                print(f"Checking available position in Bin {bin.id}")
                available_plc = self.Available_positions[bin.id].popleft()
                print(f"Available position: {available_plc['Pos'].x}, {available_plc['Pos'].y}, {available_plc['Pos'].z} with dimensions {available_plc['Dim'].x}x{available_plc['Dim'].y}x{available_plc['Dim'].z}")
                can_fit, orientation = self.check_item_fit(item, available_plc)
                if can_fit:
                    print(f"Item {item.id} can fit in Bin {bin.id} at position {available_plc['Pos'].x}x{available_plc['Pos'].y}x{available_plc['Pos'].z} with orientation {orientation.x}x{orientation.y}x{orientation.z}")
                    item.dim = orientation
                    placement = Placement(item.id, bin.id, available_plc["Pos"], orientation)
                    score = self.evaluate_bin(bin, placement)
                    Placements.append((placement, score))
                    is_placed = True
                    break
                else:
                   continue
              if not is_placed:
                 Placements.append((None, None))
            # Select the best placement based on the score
          if Placements:
             # pick the MIN waste (previously max)
             best_placement = min(Placements, key=lambda x: x[1]['waste_volume'] if x[1] else float('inf'))
             if best_placement[0] is not None:
                 self.placements.append(best_placement[0])
                 for bin in self.bins:
                     self.update_available_places(bin.id)

    def evaluate_bin(self, bin: Bin, placement: Placement):
        # Check if the item can fit in the bin
       score = {"waste_volume": (bin.W * bin.L * bin.H) - (placement.dimensions.x * placement.dimensions.y * placement.dimensions.z)}
       return score

    def enumerate_orientations(self, item: Item):
       orientations = [
           Vector3(item.dim.x, item.dim.y, item.dim.z),
           Vector3(item.dim.x, item.dim.z, item.dim.y),
           Vector3(item.dim.y, item.dim.x, item.dim.z),
           Vector3(item.dim.y, item.dim.z, item.dim.x),
           Vector3(item.dim.z, item.dim.x, item.dim.y),
           Vector3(item.dim.z, item.dim.y, item.dim.x),
       ]
       return orientations

    def check_item_fit(self,item:Item,available:dict):
       orientations = self.enumerate_orientations(item)
       for orientation in orientations:
           if orientation.x <= available["Dim"].x and orientation.y <= available["Dim"].y and orientation.z <= available["Dim"].z:
               return True, orientation
       return False,None
    
    def Compute_Layers(self, bin_id: int):
       placed_in_bin = [plc for plc in self.placements if plc.bin_id == bin_id]
       bin = next((b for b in self.bins if b.id == bin_id), None)
       #checking possible packing layers
       ordered_placements = sorted(placed_in_bin, key=lambda x: x.position.z + x.dimensions.z)
       layers = {0:0}
       layer_idx = 1
       for placement in ordered_placements:
          if placement.position.z + placement.dimensions.z  not in layers.values():
             layers[layer_idx] = placement.position.z + placement.dimensions.z
             layer_idx += 1
       return layers

    def free_space_in_Layer(self, bin_id: int, layer: float):
        EPS = 1e-2

        placed_rects = []
        for plc in self.placements:
            if plc.bin_id != bin_id:
                continue
            if abs(plc.position.z - layer) > EPS:
                continue
            x = float(plc.position.x)
            y = float(plc.position.y)
            w = float(plc.dimensions.z)  # length along X
            d = float(plc.dimensions.y)  # width  along Y
            if w > EPS and d > EPS:
                placed_rects.append(Rect(x, y, w, d))

        foundations = list(self.get_foundations(bin_id, layer))  

        free_spaces = foundations[:]  
        for occ in placed_rects:
            new_spaces = []
            for space in free_spaces:
                parts = subtract_rect(space, occ)
                if parts:
                    for r in parts:
                        if r.w > EPS and r.h > EPS:
                            new_spaces.append(r)
            free_spaces = new_spaces

            if not free_spaces:
                return []

        if foundations:
            clipped = []
            for fs in free_spaces:
                for base in foundations:
                    inter = intersection(fs, base)
                    if inter and inter.w > EPS and inter.h > EPS:
                        clipped.append(inter)
            free_spaces = clipped

        free_spaces = self._prune_and_dedup_rects(free_spaces)

        return free_spaces

    def _prune_and_dedup_rects(self,rects, eps=1e-9):
        """Drop tiny slivers and deduplicate rectangles by rounded coords."""
        # Remove tiny
        rects = [r for r in rects if r.w > eps and r.h > eps]

        # Dedup by rounding (adjust decimals as you like)
        key = lambda r: (round(r.x, 6), round(r.y, 6), round(r.w, 6), round(r.h, 6))
        seen = set()
        out = []
        for r in rects:
            k = key(r)
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out

    def get_foundations(self,bin_id,layer):
       # look up bin by id (bin_id is not a list index)
       bin_obj = next((b for b in self.bins if b.id == bin_id), None)
       if layer == 0:
          return  [Rect(0, 0, bin_obj.W, bin_obj.L)]
       else:
          object_placed_in_layers = [plc for plc in self.placements if plc.bin_id == bin_id and plc.position.z + plc.dimensions.z == layer]
          if not object_placed_in_layers:
              return [Rect(0, 0, bin_obj.W, bin_obj.L)]
          else:
             res = []
             for plc in object_placed_in_layers:
                 res.append(Rect(plc.position.x, plc.position.y, plc.dimensions.x, plc.dimensions.y))
             return res

    def update_available_places(self,bin_id):
        self.Available_positions[bin_id].clear()
        layers = self.Compute_Layers(bin_id)
        # iterate over actual layer heights
        for layer in layers.values():
            free_spaces = self.free_space_in_Layer(bin_id, layer)
            # get bin height to set vertical capacity
            bin_obj = next((b for b in self.bins if b.id == bin_id), None)
            remaining_h = max(0, bin_obj.H - layer)
            for free in free_spaces:
                self.Available_positions[bin_id].append({"Pos": Vector3(free.x, free.y, layer), "Dim": Vector3(free.w, free.h, remaining_h)})
