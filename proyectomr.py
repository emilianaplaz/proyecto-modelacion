import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import heapq

# Funciones predefinidas
grid_size = (6, 6)
javier_start = (4, 4)
andreina_start = (2, 3)
establishments = {"The Darkness": (0, 4), "La Pasión": (4, 1), "Mi Rolita": (0, 2)}

normal_time_javier = 4
normal_time_andreina = 6
bad_sidewalk_time_javier = 6
bad_sidewalk_time_andreina = 8
commercial_time_javier = 8
commercial_time_andreina = 10

bad_sidewalks = [(2, i) for i in range(6)] + [(3, i) for i in range(6)] + [(4, i) for i in range(6)]
commercial_blocks = [(i, 1) for i in range(6)]


def walking_time(block, person):
    if block in bad_sidewalks:
        return bad_sidewalk_time_javier if person == "Javier" else bad_sidewalk_time_andreina
    elif block in commercial_blocks:
        return commercial_time_javier if person == "Javier" else commercial_time_andreina
    else:
        return normal_time_javier if person == "Javier" else normal_time_andreina


def shortest_path(start, end, person):
    pq = [(0, start)]
    distances = {start: 0}
    previous = {start: None}

    while pq:
        current_distance, current_block = heapq.heappop(pq)

        if current_block == end:
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current_block[0] + dx, current_block[1] + dy)
            if 0 <= neighbor[0] < grid_size[0] and 0 <= neighbor[1] < grid_size[1]:
                distance = current_distance + walking_time(neighbor, person)
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_block
                    heapq.heappush(pq, (distance, neighbor))

    path = []
    while end:
        path.append(end)
        end = previous[end]

    return path[::-1], distances[path[0]]


def calculate_trajectories(destination):
    javier_path, javier_time = shortest_path(javier_start, establishments[destination], "Javier")
    andreina_path, andreina_time = shortest_path(andreina_start, establishments[destination], "Andreína")

    if javier_time > andreina_time:
        return javier_path, javier_time, andreina_path, andreina_time, "Andreína", javier_time - andreina_time
    elif andreina_time > javier_time:
        return javier_path, javier_time, andreina_path, andreina_time, "Javier", andreina_time - javier_time
    else:
        return javier_path, javier_time, andreina_path, andreina_time, None, 0


def draw_graph(javier_path, andreina_path):
    G = nx.grid_2d_graph(*grid_size)
    pos = {(x, y): (y, -x) for x, y in G.nodes()}  # Orientar correctamente el grafo

    fig = Figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111)

    # Dibujar el grafo base
    nx.draw(G, pos, ax=ax, with_labels=False, node_size=300, node_color="lightgray", edge_color="gray")

    # Etiquetar nodos con sus coordenadas
    for node, (x, y) in pos.items():
        ax.text(x, y, f"{node}", fontsize=8, ha="center", va="center", color="black")

    # Etiquetar las calles y carreras
    for x in range(grid_size[0]):
        ax.text(-1, -x, f"Calle {50 + x}", fontsize=10, ha="center", va="center", color="blue")

    for y in range(grid_size[1]):
        ax.text(y, 1, f"Cra {10 + y}", fontsize=10, ha="center", va="center", color="blue")

    # Etiquetar establecimientos
    for name, coords in establishments.items():
        x, y = pos[coords]
        ax.text(x, y - 0.3, name, fontsize=10, ha="center", va="center", color="green")

    # Etiquetar las casas de Andreina y Javier debajo de los nodos
    ax.text(pos[(2, 3)][0], pos[(2, 3)][1] - 0.3, "Casa Andreina", fontsize=10, ha="center", va="center", color="purple")
    ax.text(pos[(4, 4)][0], pos[(4, 4)][1] - 0.3, "Casa Javier", fontsize=10, ha="center", va="center", color="purple")

    # Resaltar caminos de Javier y Andreina
    nx.draw_networkx_nodes(G, pos, nodelist=javier_path, ax=ax, node_color="blue")
    nx.draw_networkx_nodes(G, pos, nodelist=andreina_path, ax=ax, node_color="red")

    return fig


# Interfaz gráfica
def calculate_route():
    destination = destination_var.get()
    if not destination:
        result_label.config(text="Selecciona un destino.")
        return

    javier_path, javier_time, andreina_path, andreina_time, early_person, early_time = calculate_trajectories(destination)

    result_text = f"Ruta de Javier: {javier_path}\n"
    result_text += f"Tiempo de Javier: {javier_time} minutos\n"
    result_text += f"Ruta de Andreina: {andreina_path}\n"
    result_text += f"Tiempo de Andreina: {andreina_time} minutos\n"
    if early_person:
        result_text += f"{early_person} debe salir {early_time} minutos antes."
    else:
        result_text += "Ambos deben salir al mismo tiempo."

    result_label.config(text=result_text)

    # Dibujar el grafo
    fig = draw_graph(javier_path, andreina_path)
    canvas.figure = fig
    canvas.draw()


# Crear ventana principal
root = tk.Tk()
root.title("Cálculo de Rutas")

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Widgets
ttk.Label(main_frame, text="Selecciona un destino:").grid(row=0, column=0, sticky=tk.W)
destination_var = tk.StringVar()
destination_menu = ttk.Combobox(main_frame, textvariable=destination_var)
destination_menu['values'] = list(establishments.keys())
destination_menu.grid(row=0, column=1, sticky=(tk.W, tk.E))

calculate_button = ttk.Button(main_frame, text="Calcular Ruta", command=calculate_route)
calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

result_label = ttk.Label(main_frame, text="", justify="left", padding="10")
result_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Área para el grafo
fig = Figure(figsize=(8, 8), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)

root.mainloop()







