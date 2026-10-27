import itertools
import networkx as nx

INF = 10 ** 9

def read_graph(path):
    with open(path, encoding="utf-8") as f:
        tokens = f.read().split()
        it = iter(tokens)
        p = int(next(it))
        q = int(next(it))
        weights = {}
        for _ in range(p):
            name = next(it)
            k = int(next(it))
            weights[name] = k
        G = nx.DiGraph()
        G.add_nodes_from(weights)
        for _ in range(q):
            u, v = next(it), next(it)
            t = int(next(it))          # ← целое время
            orient = int(next(it))
            G.add_edge(u, v, weight=t)
            if orient == 0:            # двусторонняя улица
                G.add_edge(v, u, weight=t)
    return G, weights

# ---------- 2. Матрица кратчайших путей (все пары) ----------
def all_pairs(G, nodes):
    dist = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
    D = {}
    for u in nodes:
        D[u] = {}
        for v in nodes:
            val = dist[u].get(v, INF)
            D[u][v] = int(val) if val < INF else INF
    return D

# ---------- 3. p-медиана: точный перебор ----------
def p_median(D, weights, punct):
    nodes = list(weights)
    best_S, best_F = None, INF
    for S in itertools.combinations(nodes, punct):
        F = 0
        for v in nodes:
            F += weights[v] * min(D[s][v] for s in S)
        if F < best_F:
            best_F, best_S = F, S
    return best_S, best_F

# ---------- 4. p-центр: точный перебор ----------
def p_center(D, weights, punct):
    nodes = list(weights)
    best_S, best_R = None, INF
    for S in itertools.combinations(nodes, punct):
        R = 0
        for v in nodes:
            R = max(R, min(D[s][v] for s in S))
        if R < best_R:
            best_R, best_S = R, S
    return best_S, best_R

# ---------- 5. Жадное дополнение (если punct большое) ----------
def p_median_greedy(D, weights, punct):
    nodes = list(weights)
    S = []
    while len(S) < punct:
        best_v, best_F = None, INF
        for v in nodes:
            if v in S:
                continue
            cand = S + [v]
            F = sum(weights[u] * min(D[s][u] for s in cand) for u in nodes)
            if F < best_F:
                best_F, best_v = F, v
        if best_v is None:
            break
        S.append(best_v)
    F = sum(weights[u] * min(D[s][u] for s in S) for u in nodes)
    return tuple(S), F

# ---------- 6. Восстановление маршрутов до ближайшего пункта ----------
def routes_to_service(D, G, weights, S):
    if not S:
        return {v: (None, INF) for v in weights}
    
    res = {}
    for v in weights:
        s = min(S, key=lambda x: D[x][v])
        if v == s:
            res[v] = ([v], 0)
        else:
            try:
                path = nx.shortest_path(G, s, v, weight="weight")
                length = int(nx.shortest_path_length(G, s, v, weight="weight"))
            except nx.NetworkXNoPath:
                path, length = None, INF
            res[v] = (path, length)
    return res

# ---------- 7. Печать блока маршрутов для заданного punct ----------
def print_routes(D, G, weights, S, punct, criterion="median"):
    label = "p-медиана" if criterion == "median" else "p-центр"
    print(f"\nМаршруты до ближайшего пункта "
          f"({label}, punct={punct}, S = {S}):")
    routes = routes_to_service(D, G, weights, S)
    # Сначала — сами пункты, потом остальные по алфавиту
    order = list(S) + sorted(v for v in weights if v not in S)
    total_k = 0
    total_time = 0
    for v in order:
        path, length = routes[v]
        k = weights[v]
        total_k += k
        total_time += k * length
        if path is None:
            print(f"  {v} (k={k}) -> нет пути  ({length})")
        else:
            print(f"  {v} (k={k}) -> {path}  ({length})")
    print(f"  ---")
    print(f"  Сумма весов k_v          : {total_k}")
    print(f"  Суммарное время F = Σk·d : {total_time}")
    if total_k:
        print(f"  Среднее время на вызов   : {total_time / total_k:.1f}")

# ---------- 8. Демонстрация ----------
if __name__ == "__main__":
    G = nx.DiGraph()
    nodes_k = dict(A=1, B=2, C=3, D=2, E=1,
                   F=2, G=3, H=4, I=3, J=2,
                   K=3, L=4, M=5, N=4, O=3,
                   P=2, Q=3, R=4, S=3, T=2,
                   U=1, V=2, W=3, X=2, Y=1)
    G.add_nodes_from(nodes_k)
    edges = [
        ("A", "B", 10, 1), ("A", "C", 13, 0), ("A", "G", 19, 0),
        ("A", "F", 5, 0),  ("A", "H", 13, 0), ("A", "E", 13, 0),
        ("B", "H", 17, 1),
        ("C", "B", 21, 1), ("C", "D", 11, 1), ("C", "H", 18, 0),
        ("D", "H", 15, 0), ("D", "I", 15, 1), ("D", "E", 12, 1),
        ("E", "J", 10, 0), ("E", "O", 16, 0), ("E", "I", 23, 0),
        ("F", "K", 25, 0), ("F", "L", 14, 0), ("F", "G", 18, 0),
        ("G", "B", 24, 1), ("G", "H", 10, 0), ("G", "M", 13, 1),
        ("G", "L", 9, 0),
        ("H", "I", 27, 1), ("H", "M", 14, 1), ("H", "C", 18, 1),
        ("I", "J", 25, 1), ("I", "N", 21, 0),
        ("K", "L", 13, 1), ("K", "P", 22, 0),
        ("L", "M", 14, 0), ("L", "Q", 8, 1),
        ("M", "Q", 18, 1), ("M", "R", 14, 1), ("M", "S", 18, 1),
        ("M", "N", 5, 1),  ("M", "I", 13, 0),
        ("N", "I", 21, 0), ("N", "J", 22, 1), ("N", "T", 17, 1),
        ("N", "S", 12, 0),
        ("O", "J", 15, 0), ("O", "N", 13, 0), ("O", "T", 15, 1),
        ("P", "Q", 17, 0), ("P", "L", 13, 1), ("P", "U", 21, 0),
        ("Q", "V", 11, 1), ("Q", "R", 15, 0),
        ("R", "X", 17, 1), ("R", "S", 19, 0), ("R", "W", 18, 0),
        ("S", "T", 23, 1), ("S", "Y", 19, 1), ("S", "X", 14, 0),
        ("T", "Y", 21, 1),
        ("U", "Q", 24, 1), ("U", "V", 12, 1), ("U", "P", 21, 1),
        ("V", "R", 12, 0), ("V", "W", 16, 0),
        ("W", "X", 9, 1),  ("W", "R", 18, 0), ("W", "Y", 18, 0),
        ("X", "Y", 16, 0),
    ]
    for u, v, t, f in edges:
        G.add_edge(u, v, weight=t)
        if f == 0:
            G.add_edge(v, u, weight=t)

    nodes = list(nodes_k)
    D = all_pairs(G, nodes)

    # --- 8.1. Сводка по нескольким punct ---
    print("=" * 60)
    print(f"{'punct':>6} | {'p-медиана':^24} | {'p-центр':^24}")
    print("-" * 60)
    for punct in (1, 2, 3, 4):
        Sm, Fm = p_median(D, nodes_k, punct)
        Sc, Rc = p_center(D, nodes_k, punct)
        print(f"{punct:>6} | S={str(Sm):<12} F={Fm:<6} | "
              f"S={str(Sc):<12} R={Rc:<6}")
    print("=" * 60)
    # --- 8.2. Подробные маршруты для ЛЮБОГО punct ---
    # Меняйте punct здесь:
    punct_to_show = 4
    # (а) для p-медианы
    S_med, F_med = p_median(D, nodes_k, punct_to_show)
    print_routes(D, G, nodes_k, S_med, punct_to_show, criterion="median")
    # (б) для p-центра
    S_cen, R_cen = p_center(D, nodes_k, punct_to_show)
    print_routes(D, G, nodes_k, S_cen, punct_to_show, criterion="center")