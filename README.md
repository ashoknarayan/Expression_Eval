# Expression_Eval

## Overview
Expression_Eval is a Python-based application that allows users to input mathematical expressions and visualize their expression trees. It supports infix, prefix, and postfix traversals, step-by-step evaluation, and interactive features like dragging and zooming. The project uses Pygame for rendering and provides a user-friendly interface to explore expression trees.

## Features
- **Expression Parsing**: Converts infix mathematical expressions (e.g., `5 * (2 + 3) - 4 ^ 2`) into an expression tree.
- **Traversal Visualization**: Displays the tree with animated traversals:
  - Infix (left, root, right)
  - Prefix (root, left, right)
  - Postfix (left, right, root)
- **Step-by-Step Evaluation**: Animates the evaluation of the expression in postorder, showing intermediate results.
- **Interactive Interface**:
  - Drag the tree to reposition it.
  - Zoom in/out using the mouse wheel.
  - Input box to enter expressions.
  - Buttons to switch between traversal types and trigger evaluation.
- **Error Handling**:
  - Clears the input box and displays an error message for invalid expressions.
  - Prevents hanging by rejecting expressions with `=` (e.g., `4=4`).
- **Responsive Design**: Adjusts the UI dynamically when the window is resized, keeping buttons and input at the bottom-left corner.

## Screenshots
*(You can add screenshots here by taking images of the running application and uploading them to your GitHub repository. For example:)*
![Expression Tree Example](screenshots/example.png)

## Prerequisites
- Python 3.7 or higher
- Pygame library

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Expression_Eval.git
   cd Expression_Eval
   ```

2. **Install Dependencies**:
   Install Pygame using pip:
   ```bash
   pip install pygame
   ```

## Usage
1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Interact with the Application**:
   - **Enter an Expression**: Click the input box at the bottom-left, type a mathematical expression (e.g., `3 + 4 * (2 - 1)`), and press Enter.
   - **View the Tree**: The expression tree will be displayed with nodes as circles (numbers) or diamonds (operators).
   - **Traversal**: Click the "Infix", "Prefix", or "Postfix" buttons to animate the respective traversal.
   - **Evaluate**: Click "Step Evaluate" to see the step-by-step evaluation of the expression.
   - **Drag and Zoom**: Drag the tree with the mouse to move it, and use the mouse wheel to zoom in/out.
   - **Error Handling**: If the expression is invalid (e.g., `2 + + 3` or `4=4`), the input box will clear, and the placeholder text will change to "Please give a correct expression".

## Code Structure
- `main.py`: The main script containing the entire application logic, including expression parsing, tree building, visualization, and user interaction.
- (Add other files if you split the code into modules in the future.)

## Limitations
- Supports basic operators: `+`, `-`, `*`, `/`, `^` (exponentiation).
- Does not support advanced mathematical functions (e.g., `sin`, `log`).
- Expressions with `=` are not allowed and will trigger an error message.
- Requires a graphical environment to run (Pygame does not work in headless
