import pygame
import random

# ----------------------------
# 1. Pygame Setup
# ----------------------------
pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Tic-Tac-Toe MCTS Visualization")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

FONT = pygame.font.SysFont("Arial", 14)

# ----------------------------
# 2. Node Class
# ----------------------------
class Node:
    def __init__(self, board, parent=None):
        self.board = board  # string of 9 chars
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.pos = (0,0)
        self.edge_prob = 0

# ----------------------------
# 3. Tic-Tac-Toe Logic
# ----------------------------
def next_player(board):
    return "X" if board.count("X") <= board.count("O") else "O"

def legal_moves(board):
    return [i for i, c in enumerate(board) if c == " "]

def make_move(board, pos, player):
    new_board = list(board)
    new_board[pos] = player
    return "".join(new_board)

# ----------------------------
# 4. MCTS Step
# ----------------------------
def mcts_step(node):
    moves = legal_moves(node.board)
    if not moves:
        return
    if random.random() < 0.5:
        move = random.choice(moves)
        player = next_player(node.board)
        new_board = make_move(node.board, move, player)
        child = Node(new_board, parent=node)
        child.visits = random.randint(1, 10)
        child.value = random.random()
        child.edge_prob = random.random()
        node.children.append(child)
        node.visits += child.visits
        node.value = (node.value + child.value)/2
    else:
        node.visits += random.randint(1,5)
        node.value += random.random()/10

# ----------------------------
# 5. Best Path
# ----------------------------
def best_path(node):
    path = [node]
    current = node
    while current.children:
        best_child = max(current.children, key=lambda c: c.visits)
        path.append(best_child)
        current = best_child
    return path

# ----------------------------
# 6. Layout Tree (Non-overlapping)
# ----------------------------
def layout_tree(node, x, y, x_min=50, x_max=1150, y_step=120):
    node.pos = (x, y)
    n = len(node.children)
    if n == 0:
        return
    spacing = (x_max - x_min) / n
    for i, child in enumerate(node.children):
        child_x_min = x_min + i*spacing
        child_x_max = x_min + (i+1)*spacing
        child_x = (child_x_min + child_x_max)/2
        child_y = y + y_step
        layout_tree(child, child_x, child_y, child_x_min, child_x_max, y_step)

# ----------------------------
# 7. Draw Node and Board
# ----------------------------
def draw_board(node, best_path_nodes):
    x, y = node.pos
    # Node circle
    radius = min(50, 20 + int(node.visits))  # cap radius
    color = (int(min(node.value,1)*255), 150, 50)
    pygame.draw.circle(screen, color, (int(x), int(y)), radius)
    pygame.draw.circle(screen, BLACK, (int(x), int(y)), radius, 2)
    
    # Mini 3x3 board
    size = 12
    offset = 18
    for i in range(3):
        for j in range(3):
            cell = node.board[i*3+j]
            rect = pygame.Rect(x-offset+j*size, y-offset+i*size, size, size)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if cell != " ":
                text = FONT.render(cell, True, BLACK)
                screen.blit(text, (rect.x+2, rect.y))
    
    # Visits and value inside node
    visit_text = FONT.render(f"V:{node.visits}", True, BLACK)
    val_text = FONT.render(f"Q:{node.value:.2f}", True, BLACK)
    screen.blit(visit_text, (x - radius + 2, y - radius + 2))
    screen.blit(val_text, (x - radius + 2, y + radius - 18))
    
    # Draw edges and recursively draw children
    for child in node.children:
        edge_color = RED if child in best_path_nodes else BLACK
        width = max(1, int(child.edge_prob*5))
        pygame.draw.line(screen, edge_color, (x, y), child.pos, width)
        draw_board(child, best_path_nodes)

# ----------------------------
# 8. Main Loop
# ----------------------------
root = Node("         ")  # empty board
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(WHITE)
    
    # Simulate several MCTS steps per frame
    nodes_to_expand = [root]
    for _ in range(10):
        node = random.choice(nodes_to_expand)
        mcts_step(node)
        nodes_to_expand += node.children
    
    # Layout tree
    layout_tree(root, WIDTH//2, 50)
    
    # Best path
    path_nodes = best_path(root)
    
    # Draw tree
    draw_board(root, path_nodes)
    
    pygame.display.flip()
    clock.tick(2)  # frames per second

pygame.quit()
