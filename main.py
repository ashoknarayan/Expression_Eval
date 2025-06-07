import pygame
import sys
import math
import asyncio
import platform

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

def evaluate(node, eval_order=None):
    if node is None:
        return 0
    # Postorder: evaluate left, then right, then current node
    if node.left:
        evaluate(node.left, eval_order)
    if node.right:
        evaluate(node.right, eval_order)
    if not is_operator(node.val):
        val = float(node.val)
        node.eval_result = val
        if eval_order is not None:
            eval_order.append(node)
        return val
    left_val = node.left.eval_result
    right_val = node.right.eval_result
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
    if eval_order is not None:
        eval_order.append(node)
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
HIGHLIGHT_COLOR = (255, 0, 0)  # For traversal animation
EVAL_COLOR = (0, 255, 0)  # Green for evaluation animation
EDGE_COLOR = (50, 50, 50)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HIGHLIGHT = (150, 150, 250)
SHADOW_COLOR = (70, 70, 70)

# Gradient background colors
GRADIENT_TOP = (220, 240, 255)
GRADIENT_BOTTOM = (255, 255, 255)

# Node display settings base values
BASE_NODE_RADIUS = 25
BASE_VERTICAL_SPACING = 80
BASE_HORIZONTAL_SPACING = 40

def draw_gradient_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * ratio)
        g = int(GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * ratio)
        b = int(GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * ratio)
        pygame.draw.line(SCREEN, (r, g, b), (0, y), (WIDTH, y))

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

def draw_nodes(root, positions, offset, scale, eval_node=None, eval_values=None):
    if root is None:
        return
    color = root.color if root.color else NODE_COLOR
    if root == eval_node:
        color = EVAL_COLOR
    x, y = scale_pos(positions[root], offset, scale)
    radius = max(10, int(BASE_NODE_RADIUS * scale))
    shadow_offset = max(2, int(5 * scale))
    
    # Draw shadow
    if is_operator(root.val):
        # Diamond shape for operators
        points = [
            (x, y - radius),  # Top
            (x + radius, y),  # Right
            (x, y + radius),  # Bottom
            (x - radius, y)   # Left
        ]
        shadow_points = [(px + shadow_offset, py + shadow_offset) for px, py in points]
        pygame.draw.polygon(SCREEN, SHADOW_COLOR, shadow_points)
        pygame.draw.polygon(SCREEN, color, points)
        pygame.draw.polygon(SCREEN, BLACK, points, 2)
    else:
        # Circle for numbers
        pygame.draw.circle(SCREEN, SHADOW_COLOR, (int(x + shadow_offset), int(y + shadow_offset)), radius)
        pygame.draw.circle(SCREEN, color, (int(x), int(y)), radius)
        pygame.draw.circle(SCREEN, BLACK, (int(x), int(y)), radius, 2)
    
    text = FONT.render(str(root.val), True, BLACK)
    text_rect = text.get_rect(center=(int(x), int(y)))
    SCREEN.blit(text, text_rect)
    
    # Display eval_result if this node is being evaluated
    if root == eval_node and eval_values and root.eval_result is not None:
        eval_text = FONT.render(f"= {root.eval_result}", True, BLACK)
        eval_rect = eval_text.get_rect(center=(int(x + radius + 40 * scale), int(y)))
        pygame.draw.rect(SCREEN, (200, 200, 200), eval_rect.inflate(10, 5))
        SCREEN.blit(eval_text, eval_rect)
    
    draw_nodes(root.left, positions, offset, scale, eval_node, eval_values)
    draw_nodes(root.right, positions, offset, scale, eval_node, eval_values)

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
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover = False

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius=6)
        pygame.draw.rect(SCREEN, BLACK, self.rect, 2, border_radius=6)
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        SCREEN.blit(text_surf, text_rect)

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

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
    global WIDTH, HEIGHT
    clock = pygame.time.Clock()

    input_expr = "Type Expression, Press Enter"  # default expression
    input_active = False
    user_text = ""

    root = None
    traversal_order = []
    current_step = -1
    traversal_type = 'infix'  # default infix
    animating = False
    animation_speed = 800  # milliseconds per step
    last_step_time = 0

    # Evaluation animation
    eval_order = []
    eval_step = -1
    evaluating = False
    eval_last_step_time = 0
    eval_values = {}  # Store eval results for display

    offset_x, offset_y = 0, 0  # for dragging
    dragging = False
    drag_start = (0, 0)
    offset_start = (0, 0)
    scale = 1.0  # zoom scale
    min_scale, max_scale = 0.3, 3.0

    # Buttons (positions will be updated dynamically)
    buttons = [
        Button(20, HEIGHT - 60, 120, 40, "Infix"),
        Button(160, HEIGHT - 60, 120, 40, "Prefix"),
        Button(300, HEIGHT - 60, 120, 40, "Postfix"),
        Button(440, HEIGHT - 60, 160, 40, "Step Evaluate"),
    ]

    # Input box position (will be updated dynamically)
    input_box_rect = pygame.Rect(20, HEIGHT - 110, 460, 30)

    running = True
    while running:
        draw_gradient_background()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                # Update positions of buttons and input box to stay at the bottom
                input_box_rect.y = HEIGHT - 110
                for button in buttons:
                    button.update_position(button.rect.x, HEIGHT - 60)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (input_box_rect.collidepoint(event.pos)):
                    input_active = True
                else:
                    input_active = False

                for b in buttons:
                    if b.is_clicked(event.pos):
                        if b.text == "Step Evaluate" and root and not evaluating and not animating:
                            eval_order = []
                            evaluate(root, eval_order)  # Compute evaluation order (postorder)
                            eval_step = 0
                            evaluating = True
                            eval_last_step_time = pygame.time.get_ticks()
                            eval_values = {node: node.eval_result for node in eval_order}
                        elif not animating and not evaluating:
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
                    # Check for '=' in the input
                    if '=' in user_text:
                        print("Error: '=' is not allowed in the expression")
                        user_text = ""  # Clear the input box
                        input_expr = "Please give a correct expression"  # Update default text
                    else:
                        try:
                            postfix = infix_to_postfix(user_text)
                            root = build_tree(postfix)
                            traversal_order = traverse_with_highlight(root, traversal_type)
                            current_step = -1
                            animating = False
                            evaluating = False
                            eval_step = -1
                            eval_order = []
                            eval_values = {}
                            reset_node_colors(root)
                            input_expr = user_text
                            user_text = ""
                        except Exception as e:
                            print("Error parsing:", e)
                            user_text = ""  # Clear the input box
                            input_expr = "Please give a correct expression"  # Update default text
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        # Animation logic for traversal
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

        # Animation logic for evaluation
        if evaluating and root and eval_order:
            current_time = pygame.time.get_ticks()
            if current_time - eval_last_step_time >= animation_speed:
                if eval_step < len(eval_order):
                    eval_step += 1
                    eval_last_step_time = current_time
                else:
                    evaluating = False
                    eval_step = -1

        # Draw input box
        pygame.draw.rect(SCREEN, (200, 200, 200), input_box_rect)
        text_surface = FONT.render(user_text if input_active else input_expr, True, BLACK)
        SCREEN.blit(text_surface, (input_box_rect.x + 5, input_box_rect.y + 5))

        # Draw buttons
        for b in buttons:
            b.check_hover(mouse_pos)
            b.draw()

        if root:
            positions = {}
            calculate_positions(root, 0, 0, positions)

            draw_edges(root, positions, (offset_x + WIDTH // 2, offset_y + 150), scale)
            eval_node = eval_order[eval_step] if 0 <= eval_step < len(eval_order) else None
            draw_nodes(root, positions, (offset_x + WIDTH // 2, offset_y + 150), scale, eval_node, eval_values)

            inorder_str = inorder(root)
            preorder_str = preorder(root).strip()
            postorder_str = postorder(root).strip()
            try:
                eval_val = evaluate(root)
                eval_str = f"Value = {eval_val}"
            except:
                eval_str = "Evaluation error"

            # Draw output above input box
            SCREEN.blit(FONT.render("Infix: " + inorder_str, True, BLACK), (20, HEIGHT - 210))
            SCREEN.blit(FONT.render("Prefix: " + preorder_str, True, BLACK), (20, HEIGHT - 185))
            SCREEN.blit(FONT.render("Postfix: " + postorder_str, True, BLACK), (20, HEIGHT - 160))
            SCREEN.blit(BIG_FONT.render(eval_str, True, (0, 120, 0)), (600, HEIGHT - 165))

        else:
            SCREEN.blit(FONT.render("Enter an expression and press Enter", True, BLACK), (20, HEIGHT - 210))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

    pygame.quit()
    sys.exit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
