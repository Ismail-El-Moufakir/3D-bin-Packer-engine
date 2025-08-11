import plotly.graph_objects as go
import numpy as np

# ---------- Helpers ----------
def _safe_get(obj, key, default=None):
    # Works with objects (attrs) and dicts (keys)
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    return default

def _add_horizontal_layer(fig, W, D, z, name="Layer", opacity=0.35):
    X = np.array([[0, W],[0, W]])
    Y = np.array([[0, 0],[D, D]])
    Z = np.full((2, 2), float(z))

    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, "lightgray"], [1, "lightgray"]],
        opacity=opacity,
        showscale=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter3d(
        x=[0, W, W, 0, 0],
        y=[0, 0, D, D, 0],
        z=[z, z, z, z, z],
        mode="lines",
        line=dict(width=3),
        name=name,
        hoverinfo="skip"
    ))

PLOTLY_COLORS = [
    'cyan', 'blue', 'green', 'yellow', 'orange', 'red',
    'purple', 'magenta', 'teal', 'goldenrod'
]

def construct_box_vertices(placement):
    x, y, z = placement.position.x, placement.position.y, placement.position.z
    h, w, l = placement.dimensions.x, placement.dimensions.y, placement.dimensions.z  # height, width, length

    V = [
        (x,     y,     z),
        (x+l,   y,     z),
        (x+l,   y+w,   z),
        (x,     y+w,   z),
        (x,     y,     z+h),
        (x+l,   y,     z+h),
        (x+l,   y+w,   z+h),
        (x,     y+w,   z+h),
    ]

    faces = [
        (0,1,2), (0,2,3),  # bottom
        (4,5,6), (4,6,7),  # top
        (0,1,5), (0,5,4),  # front
        (2,3,7), (2,7,6),  # back
        (1,2,6), (1,6,5),  # right
        (4,7,3), (4,3,0),  # left
    ]
    return V, faces

EDGE_PAIRS = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7),
]

def add_box_with_edges(fig, V, faces, facecolor, name, edgecolor="black", edgewidth=3):
    X, Y, Z = zip(*V)
    i_faces, j_faces, k_faces = zip(*faces)

    fig.add_trace(go.Mesh3d(
        x=X, y=Y, z=Z,
        i=i_faces, j=j_faces, k=k_faces,
        color=facecolor,
        opacity=0.95,
        flatshading=True,
        lighting=dict(ambient=0.45, diffuse=0.9, specular=0.1, roughness=0.8),
        lightposition=dict(x=0.5, y=0.5, z=2),
        name=name,
        hovertemplate=f"{name}<extra></extra>",
        showscale=False
    ))

    xe, ye, ze = [], [], []
    for a, b in EDGE_PAIRS:
        xa, ya, za = V[a]
        xb, yb, zb = V[b]
        xe += [xa, xb, None]
        ye += [ya, yb, None]
        ze += [za, zb, None]

    fig.add_trace(go.Scatter3d(
        x=xe, y=ye, z=ze,
        mode="lines",
        line=dict(color=edgecolor, width=edgewidth),
        name=f"{name} edges",
        hoverinfo="skip",
        showlegend=False
    ))

# ---------- Elegant 3D rect patches ----------
def _add_rect_patch3d(fig, x, y, w, d, z=0.0, name="Free space", color="rgba(0, 150, 255, 1.0)", opacity=0.25, show_label=True):
    """
    Draw a 2D rectangle at height z as a translucent filled quad + crisp outline.
    """
    # Small offset to avoid z-fighting with layer/box tops
    z = float(z) + 1e-6

    # Quad vertices (counter-clockwise)
    V = [
        (x,     y,     z),
        (x+w,   y,     z),
        (x+w,   y+d,   z),
        (x,     y+d,   z),
    ]
    Xi, Yi, Zi = zip(*V)

    # Filled patch (two triangles)
    fig.add_trace(go.Mesh3d(
        x=Xi, y=Yi, z=Zi,
        i=[0, 0], j=[1, 2], k=[2, 3],
        opacity=opacity,
        color=color,
        flatshading=True,
        hovertemplate=(
            f"{name}"
            + "<br>x: %{x:.2f}, y: %{y:.2f}, z: %{z:.2f}"
            + f"<br>w×d: {w:.2f} × {d:.2f}"
            + f"<br>area: {w*d:.2f}"
            + "<extra></extra>"
        ),
        name=name,
        showscale=False
    ))

    # Outline
    xs = [x, x+w, x+w, x, x]
    ys = [y, y,   y+d, y+d, y]
    zs = [z]*5
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines",
        line=dict(width=3),
        name=name,
        hoverinfo="skip",
        showlegend=False
    ))

    # Optional center label
    if show_label and name:
        cx, cy = x + w/2.0, y + d/2.0
        fig.add_trace(go.Scatter3d(
            x=[cx], y=[cy], z=[z],
            mode="text",
            text=[name],
            textposition="middle center",
            hoverinfo="skip",
            showlegend=False
        ))

def render_rects(fig, rects):
    """
    Render a list of free-space rectangles (objects or dicts).
    Expected fields: x, y, w, h (or d), optional z, name, color, opacity.
    """
    if not rects:
        return

    for i, rect in enumerate(rects):
        x = float(_safe_get(rect, "x", 0.0))
        y = float(_safe_get(rect, "y", 0.0))
        w = float(_safe_get(rect, "w", _safe_get(rect, "width", 0.0)))
        d = float(_safe_get(rect, "h", _safe_get(rect, "d", _safe_get(rect, "depth", 0.0))))
        z = float(_safe_get(rect, "z", 0.0))

        # Skip invalid rectangles gracefully
        if w <= 0 or d <= 0:
            continue

        name = _safe_get(rect, "name", f"Free {i}")
        color = _safe_get(rect, "color", PLOTLY_COLORS[i % len(PLOTLY_COLORS)])
        opacity = float(_safe_get(rect, "opacity", 0.25))

        _add_rect_patch3d(fig, x, y, w, d, z=z, name=name, color=color, opacity=opacity)

# ---------- Main renderer ----------
def render_bin(placements, bin_size=None, title="Bin", Layers=None, rects=None):
    fig = go.Figure()

    # Items
    for i, p in enumerate(placements):
        V, faces = construct_box_vertices(p)
        color = PLOTLY_COLORS[i % len(PLOTLY_COLORS)]
        add_box_with_edges(fig, V, faces, facecolor=color, name=f"Item {getattr(p, 'item_id', i)}")

    # Axes ranges / layers / free spaces
    if bin_size:
        W, D, H = bin_size
        xr, yr, zr = [0, W], [0, D], [0, H]

        if Layers:
            for idx, z in (Layers.items() if isinstance(Layers, dict) else enumerate(Layers)):
                if 0 <= z <= H:
                    _add_horizontal_layer(fig, W, D, z, name=f"Layer {idx}", opacity=0.35)

        if rects:
            render_rects(fig, rects)
    else:
        # Fallback ranges from placements
        max_x = max((p.position.x + p.dimensions.z) for p in placements) if placements else 1.0
        max_y = max((p.position.y + p.dimensions.y) for p in placements) if placements else 1.0
        max_z = max((p.position.z + p.dimensions.x) for p in placements) if placements else 1.0
        xr, yr, zr = [0, max_x], [0, max_y], [0, max_z]

        if rects:
            render_rects(fig, rects)

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis=dict(range=xr, title="X (width)", zeroline=False, showgrid=True),
            yaxis=dict(range=yr, title="Y (depth)", zeroline=False, showgrid=True),
            zaxis=dict(range=zr, title="Z (height)", zeroline=False, showgrid=True),
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.write_html("bin_render.html", auto_open=True)
