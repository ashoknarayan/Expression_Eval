import pygame
import sys
import math

# --- Expression Tree Node ---
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.eval_result = None  # For storing evaluated value during evaluation
        self.color = None  # To store node color during traversal

# --- Operator precedence ---
precedence = {
    '^': 4,
    '*': 3,
    '/': 3,
    '+': 2,
    '-': 2,
    '(': 1
}

def is_operator(c):
    return c in precedence

def infix_to_postfix(expression):
    output = []
    stack = []
    tokens = tokenize(expression)
    for token in tokens:
        if is_number(token):
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())
    return output

def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        if expr[i] in precedence or expr[i] in '()':
            tokens.append(expr[i])
            i += 1
        else:
            num = ''
            dot_count = 0
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError("Invalid number format")
                num += expr[i]
                i += 1
            tokens.append(num)
    return tokens

def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

def build_tree(postfix):
    stack = []
    for token in postfix:
        if is_number(token):
            stack.append(Node(token))
        else:
            node = Node(token)
            right = stack.pop()
            left = stack.pop()
            node.left = left
            node.right = right
            stack.append(node)
    return stack[0] if stack else None

def inorder(node):
    if node is None:
        return ''
    if is_operator(node.val):
        return '(' + inorder(node.left) + node.val + inorder(node.right) + ')'
    else:
        return node.val

def preorder(node):
    if node is None:
        return ''
    return node.val + ' ' + preorder(node.left) + preorder(node.right)

def postorder(node):
    if node is None:
        return ''
    return postorder(node.left) + postorder(node.right) + node.val + ' '

def evaluate(node):
    if node is None:
        return 0
    if not is_operator(node.val):
        val = float(node.val)
        node.eval_result = val
        return val
    left_val = evaluate(node.left)
    right_val = evaluate(node.right)
    if node.val == '+':
        node.eval_result = left_val + right_val
    elif node.val == '-':
        node.eval_result = left_val - right_val
    elif node.val == '*':
        node.eval_result = left_val * right_val
    elif node.val == '/':
        node.eval_result = left_val / right_val
    elif node.val == '^':
        node.eval_result = left_val ** right_val
    else:
        raise ValueError("Unknown operator " + node.val)
    return node.eval_result

pygame.init()
WIDTH, HEIGHT = 1000, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Expression Tree Visualizer")

FONT = pygame.font.SysFont('Consolas', 20)
BIG_FONT = pygame.font.SysFont('Consolas', 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NODE_COLOR = (100, 149, 237)
HIGHLIGHT_COLOR = (255, 0, 0)  # Changed to red for traversal animation
EDGE_COLOR = (50, 50, 50)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HIGHLIGHT = (150, 150, 250)

# Node display settings base values
BASE_NODE_RADIUS = 25
BASE_VERTICAL_SPACING = 80
BASE_HORIZONTAL_SPACING = 40

def calculate_positions(root, x, y, positions, level=0):
    if root is None:
        return
    h_space = BASE_HORIZONTAL_SPACING * (2 ** (3 - level))
    calculate_positions(root.left, x - h_space, y + BASE_VERTICAL_SPACING, positions, level + 1)
    positions[root] = (x, y)
    calculate_positions(root.right, x + h_space, y + BASE_VERTICAL_SPACING, positions, level + 1)

def draw_edges(root, positions, offset, scale):
    if root is None:
        return
    if root.left:
        start = scale_pos(positions[root], offset, scale)
        end = scale_pos(positions[root.left], offset, scale)
        pygame.draw.line(SCREEN, EDGE_COLOR, start, end, max(1, int(2*scale)))
        draw_edges(root.left, positions, offset, scale)
    if root.right:
        start = scale_pos(positions[root], offset, scale)
        end = scale_pos(positions[root.right], offset, scale)
        pygame.draw.line(SCREEN, EDGE_COLOR, start, end, max(1, int(2*scale)))
        draw_edges(root.right, positions, offset, scale)

def draw_nodes(root, positions, offset, scale):
    if root is None:
        return
    color = root.color if root.color else NODE_COLOR
    x, y = scale_pos(positions[root], offset, scale)
    radius = max(10, int(BASE_NODE_RADIUS * scale))
    pygame.draw.circle(SCREEN, color, (int(x), int(y)), radius)
    pygame.draw.circle(SCREEN, BLACK, (int(x), int(y)), radius, 2)
    text = FONT.render(str(root.val), True, BLACK)
    text_rect = text.get_rect(center=(int(x), int(y)))
    SCREEN.blit(text, text_rect)
    draw_nodes(root.left, positions, offset, scale)
    draw_nodes(root.right, positions, offset, scale)

def scale_pos(pos, offset, scale):
    return (pos[0] * scale + offset[0], pos[1] * scale + offset[1])

def traverse_with_highlight(root, order_type):
    order = []
    def preorder_collect(node):
        if node:
            order.append(node)
            preorder_collect(node.left)
            preorder_collect(node.right)
    def inorder_collect(node):
        if node:
            inorder_collect(node.left)
            order.append(node)
            inorder_collect(node.right)
    def postorder_collect(node):
        if node:
            postorder_collect(node.left)
            postorder_collect(node.right)
            order.append(node)

    if order_type == 'prefix':
        preorder_collect(root)
    elif order_type == 'infix':
        inorder_collect(root)
    elif order_type == 'postfix':
        postorder_collect(root)
    else:
        return []
    return order

def reset_node_colors(root):
    if root:
        root.color = None
        reset_node_colors(root.left)
        reset_node_colors(root.right)

# --- Button class ---
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover = False

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius=6)
        pygame.draw.rect(SCREEN, BLACK, self.rect, 2, border_radius=6)
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        SCREEN.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color = BUTTON_HIGHLIGHT
            self.hover = True
        else:
            self.color = BUTTON_COLOR
            self.hover = False

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

async def main():
    clock = pygame.time.Clock()

    input_expr = "3 + 4 * (2 - 1)"  # default expression
    input_active = False
    user_text = ""

    root = None
    traversal_order = []
    current_step = -1
    traversal_type = 'infix'  # default infix
    animating = False
    animation_speed = 500  # milliseconds per step
    last_step_time = 0

    offset_x, offset_y = 0, 0  # for dragging
    dragging = False
    drag_start = (0, 0)
    offset_start = (0, 0)
    scale = 1.0  # zoom scale
    min_scale, max_scale = 0.3, 3.0

    # Buttons
    buttons = [
        Button((20, 590, 120, 40), "Infix"),
        Button((160, 590, 120, 40), "Prefix"),
        Button((300, 590, 120, 40), "Postfix"),
    ]

    running = True
    while running:
        SCREEN.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                global WIDTH, HEIGHT
                WIDTH, HEIGHT = event.w, event.h
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if 20 <= event.pos[0] <= 480 and 540 <= event.pos[1] <= 570:
                    input_active = True
                else:
                    input_active = False

                for b in buttons:
                    if b.is_clicked(event.pos) and not animating:
                        traversal_type = b.text.lower()
                        if root:
                            reset_node_colors(root)
                            traversal_order = traverse_with_highlight(root, traversal_type)
                            current_step = 0
                            animating = True
                            last_step_time = pygame.time.get_ticks()

                if event.button == 1:
                    dragging = True
                    drag_start = event.pos
                    offset_start = (offset_x, offset_y)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            if event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - drag_start[0]
                dy = event.pos[1] - drag_start[1]
                offset_x = offset_start[0] + dx
                offset_y = offset_start[1] + dy

            if event.type == pygame.MOUSEWHEEL:
                old_scale = scale
                if event.y > 0:
                    scale *= 1.1
                else:
                    scale /= 1.1
                scale = max(min_scale, min(max_scale, scale))
                mx, my = mouse_pos
                offset_x = mx - (mx - offset_x) * (scale / old_scale)
                offset_y = my - (my - offset_y) * (scale / old_scale)

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    try:
                        postfix = infix_to_postfix(user_text)
                        root = build_tree(postfix)
                        traversal_order = traverse_with_highlight(root, traversal_type)
                        current_step = -1
                        animating = False
                        reset_node_colors(root)
                        input_expr = user_text
                    except Exception as e:
                        print("Error parsing:", e)
                    user_text = ""
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        # Animation logic for node highlighting
        if animating and root and traversal_order:
            current_time = pygame.time.get_ticks()
            if current_time - last_step_time >= animation_speed:
                if current_step < len(traversal_order):
                    node = traversal_order[current_step]
                    node.color = HIGHLIGHT_COLOR
                    current_step += 1
                    last_step_time = current_time
                else:
                    animating = False
                    reset_node_colors(root)
                    current_step = -1

        # Draw input box
        pygame.draw.rect(SCREEN, (200, 200, 200), (20, 540, 460, 30))
        text_surface = FONT.render(user_text if input_active else input_expr, True, BLACK)
        SCREEN.blit(text_surface, (25, 545))

        # Draw buttons
        for b in buttons:
            b.check_hover(mouse_pos)
            b.draw()

        if root:
            positions = {}
            calculate_positions(root, 0, 0, positions)

            draw_edges(root, positions, (offset_x + WIDTH // 2, offset_y + 150), scale)
            draw_nodes(root, positions, (offset_x + WIDTH // 2, offset_y + 150), scale)

            # Info texts on top
            info_text = f"Traversal: {traversal_type.capitalize()} (Click buttons to change)"
            SCREEN.blit(FONT.render(info_text, True, BLACK), (20, 20))
            instructions = "Enter expression & press Enter | Drag to move | Mouse wheel to zoom"
            SCREEN.blit(FONT.render(instructions, True, BLACK), (20, 50))

            inorder_str = inorder(root)
            preorder_str = preorder(root).strip()
            postorder_str = postorder(root).strip()
            try:
                eval_val = evaluate(root)
                eval_str = f"Value = {eval_val}"
            except:
                eval_str = "Evaluation error"

            # Draw output above input box (moved higher)
            SCREEN.blit(FONT.render("Infix: " + inorder_str, True, BLACK), (20, 440))
            SCREEN.blit(FONT.render("Prefix: " + preorder_str, True, BLACK), (20, 465))
            SCREEN.blit(FONT.render("Postfix: " + postorder_str, True, BLACK), (20, 490))
            SCREEN.blit(BIG_FONT.render(eval_str, True, (0, 120, 0)), (600, 545))

        else:
            SCREEN.blit(FONT.render("Enter an expression and press Enter", True, BLACK), (20, 440))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

    pygame.quit()
    sys.exit()

import asyncio
import platform

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
