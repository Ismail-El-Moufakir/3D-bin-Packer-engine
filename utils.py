from models import *

def subtract_rect(rectA, rectB):
    ax, ay, aw, ah = rectA.x, rectA.y, rectA.w, rectA.h
    bx, by, bw, bh = rectB.x, rectB.y, rectB.w, rectB.h

    # Intersection
    ix1 = max(ax, bx)
    iy1 = max(ay, by)
    ix2 = min(ax + aw, bx + bw)
    iy2 = min(ay + ah, by + bh)

    result = []
    # No overlap
    if ix1 >= ix2 or iy1 >= iy2:
        return [rectA]

    # Top piece
    if ay < iy1:
        result.append(Rect(ax, ay, aw, iy1 - ay))
    # Bottom piece
    if iy2 < ay + ah:
        result.append(Rect(ax, iy2, aw, ay + ah - iy2))
    # Left piece
    if ax < ix1:
        result.append(Rect(ax, iy1, ix1 - ax, iy2 - iy1))
    # Right piece
    if ix2 < ax + aw:
        result.append(Rect(ix2, iy1, ax + aw - ix2, iy2 - iy1))

    return result


rect1 = Rect(0, 0, 5, 5)
rect2 = Rect(1, 5, 15, 15)
result = subtract_rect(rect1, rect2)
for r in result:
    print(f"Rect({r.x}, {r.y}, {r.w}, {r.h})")

def intersection(rectA, rectB):
    ax, ay, aw, ah = rectA.x, rectA.y, rectA.w, rectA.h
    bx, by, bw, bh = rectB.x, rectB.y, rectB.w, rectB.h

    # Find the intersection coordinates
    ix1 = max(ax, bx)
    iy1 = max(ay, by)
    ix2 = min(ax + aw, bx + bw)
    iy2 = min(ay + ah, by + bh)

    # If there is no intersection, return None
    if ix1 >= ix2 or iy1 >= iy2:
        return None

    # Return the intersecting rectangle
    return Rect(ix1, iy1, ix2 - ix1, iy2 - iy1)