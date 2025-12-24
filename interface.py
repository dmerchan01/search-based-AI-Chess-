import tkinter as tk
import chess
import os

from engine.evaluation import Evaluator
from engine.search import NegamaxEngine

# Import the new file .py
from FuncionCrearPuntos import generar_archivo_robot

# Visual configuration
SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
LIGHT_COLOR = "#b58863"
DARK_COLOR = "#f0d9b5"

# Pieces Unicode
WHITE_PIECES = {
    chess.PAWN: "♙",
    chess.KNIGHT: "♘",
    chess.BISHOP: "♗",
    chess.ROOK: "♖",
    chess.QUEEN: "♕",
    chess.KING: "♔",
}
BLACK_PIECES = {
    chess.PAWN: "♟",
    chess.KNIGHT: "♞",
    chess.BISHOP: "♝",
    chess.ROOK: "♜",
    chess.QUEEN: "♛",
    chess.KING: "♚",
}


class ChessGUI:
    """
        Class to create a GUI for human vs computer chess game.
        Also synchronizes each move with external files for a robot:
        - initialMove.txt -> from-square (e.g., 'a1')
        - finalMove.txt   -> to-square   (e.g., 'a5')
        The game only continues when both files have been deleted.
    """
    # Path for robot files to write and delete
    ROBOT_DIR = r"X:\EpsonRC70\Projects\chess_arm_robot"

    # Constructor
    def __init__(self, root: tk.Tk):
        
        # Initialize root window
        self.root = root
        self.root.title("AI Chess - Human vs Computer")

        # Logical chess setup
        self.board = chess.Board()
        evaluator = Evaluator(mobility_weight=3)
        self.engine = NegamaxEngine(evaluator=evaluator, depth=3)

        # State of player selection
        self.selected_square = None  # Stores an index 0–63 or None

        # Flag to control if human is allowed to move
        self.can_human_move = True

        # Canvas to draw the board
        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        # Info label
        self.info_label = tk.Label(root, text="Turn: white (Human)")
        self.info_label.pack(pady=5)

        # Storage tables
        self.white_storage = [[None for _ in range(3)] for _ in range(8)]
        self.black_storage = [[None for _ in range(3)] for _ in range(8)]

        # Columns names
        self.white_storage_cols = ['i', 'j', 'k']
        self.black_storage_cols = ['l', 'm', 'n']

        # Current move filename being processed
        self.current_move_filename = None

        # Initial board draw
        self.draw_board()

    # Determine move kind 
    def get_move_kind(self, move: chess.Move) -> str:
        """
            Determine if the move is a normal move, capture, or promotion.
            Returns one of: "move", "capture", "promotion".
            Parameters:
                - move: chess.Move instance
            Returns:
                - str: kind of move
        """

        # Check move type
        is_capture = self.board.is_capture(move)
        is_promotion = move.promotion is not None

        # Return kind
        if is_capture and is_promotion:
            return "capture_promotion"
        if is_promotion:
            return "promotion"
        elif is_capture:
            return "capture"
        else:
            return "move"

    # Convert storage indices to square notation
    def storage_index_to_square(self, color: bool, col_idx: int, row_idx: int) -> str:
        """
            Convert storage indices to chess square notation.
            E.g., (0,0) -> 'i1', (2,7) -> 'k8'.
            Parameters:
                - color: chess.WHITE or chess.BLACK
                - col_idx: column index (0, 1, or 2)
                - row_idx: row index (0 to 7)
            Returns:
                - str: square notation (e.g., 'i1', 'k8')
        """

        # Determine column letter based on color
        cols = self.white_storage_cols if color == chess.WHITE else self.black_storage_cols
        
        # Build square notation
        col_letter = cols[col_idx]          
        row_number = row_idx + 1

        # Return square string            
        return f"{col_letter}{row_number}"
    
    # Get next storage square for captured piece
    def get_next_storage_square(self, captured_color: bool) -> str:
        """
            Return the next available storage square for a captured piece.
            Marks that square as occupied after returning it.
            Parameters: 
            - captured_color: color of the captured piece (chess.WHITE or chess.BLACK)
            Returns:    
            - str: square notation (e.g., 'i1', 'l3')
        """

        # Select appropriate storage
        if captured_color == chess.WHITE:
            storage = self.white_storage
        else:
            storage = self.black_storage

        # Find next free square in columns i/j/k or l/m/n
        for row in range(8):
            for col in range(2):
                if storage[row][col] is None:
                    storage[row][col] = "USED"   # Mark as occupied
                    return self.storage_index_to_square(captured_color, col, row)

        # If no free square found, raise error
        raise RuntimeError("There are no free storage squares available for captured pieces.")

    # Get next queen source square for promotion
    def get_next_queen_source_square(self, color: bool) -> str:
        """
            Return the next available queen source square for promotion.
            Marks that square as used after returning it.
            Parameters:
                - color: chess.WHITE or chess.BLACK
            Returns:
                - str: square notation (e.g., 'k1', 'n5')
        """

        # Select appropriate storage
        if color == chess.WHITE:
            storage = self.white_storage
        else:
            storage = self.black_storage

        # Find next free queen source square in column k or n
        col = 2  
        for row in range(8):
            if storage[row][col] != "USED":
                storage[row][col] = "USED"
                return self.storage_index_to_square(color, col, row)

        # If no free square found, raise error
        raise RuntimeError("No free queen source squares available for promotion.")

    # Encode robot move sequence 
    def encode_robot_sequence(self, move: chess.Move) -> str:
        """
            Encode the given move into a robot-readable sequence.
            Parameters:
                - move: chess.Move instance
            Returns:
                - str: encoded move sequence (e.g., 'a2a3', 'a5i1b6a5', 'a7j1k1a8', 'a5l1m1b6j1k1a8')
        """

        # Basic from/to squares
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)

        # Determine move type
        is_capture = self.board.is_capture(move)
        is_promotion = move.promotion is not None

        # Get moving piece color before the move
        moving_piece = self.board.piece_at(move.from_square)
        moving_color = moving_piece.color if moving_piece else chess.WHITE

        # Handle different move types
        if is_capture:
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece is None and self.board.is_en_passant(move):
                return from_sq + to_sq

        # Normal move cases and return it
        if not is_capture and not is_promotion:
            return from_sq + to_sq

        # Simple capture move cases and return it
        if is_capture and not is_promotion:
            captured_color = captured_piece.color
            captured_sq = to_sq
            captured_storage_sq = self.get_next_storage_square(captured_color)
            return captured_sq + captured_storage_sq + from_sq + to_sq

        # Store pawn and queen squares for promotion cases
        pawn_storage_sq = self.get_next_storage_square(moving_color)
        queen_source_sq = self.get_next_queen_source_square(moving_color)

        # Promotion move case without capture and return it
        if not is_capture and is_promotion:
            return from_sq + pawn_storage_sq + queen_source_sq + to_sq

        # Promotion move case with capture and return it
        if is_capture and is_promotion:
            captured_piece = self.board.piece_at(move.to_square)
            captured_color = captured_piece.color
            captured_sq = to_sq
            captured_storage_sq = self.get_next_storage_square(captured_color)
            return captured_sq + captured_storage_sq + from_sq + pawn_storage_sq + queen_source_sq + to_sq
            

        # General fallback
        return from_sq + to_sq

    # Helper method for robot sync
    def write_move_file(self, move: chess.Move):
        """
            Create <kind_move>.txt with the encoded move sequence for the robot.
            Parameters:
                - move: chess.Move instance
            Returns:    
                - None
        """

        # Determine move kind and filename
        kind = self.get_move_kind(move)

        # Determine filename based on move kind
        if kind == "move":
            type = 0
            fname = "move.txt"
        elif kind == "capture":
            type = 1
            fname = "capture.txt"
        elif kind == "promotion":
            type = 2
            fname = "promotion.txt"
        else:
            type = 3
            fname = "captured_promotion.txt"

        # Save current move filename
        self.current_move_filename = fname

        # Obtain encoded sequence
        sequence = self.encode_robot_sequence(move)

        generar_archivo_robot(sequence, type)

        # Debug print
        print(f"[File] {fname} = {sequence}")

    # Wait until both move files are deleted
    def wait_until_file_deleted(self, callback):
        """
            Wait until the current move file is deleted by the robot.
            Once deleted, call the provided callback function.
            Parameters:
                - callback: function to call once file is deleted
            Returns:
                - None
        """

        # Get current move filename
        fname = self.current_move_filename
        if not fname:
            callback()
            return

        fullpath = os.path.join(self.ROBOT_DIR, fname)
        exists = os.path.exists(fullpath)

        # Check if file still exists
        # exists = os.path.exists(fname)

        # If not exists, call callback; else, check again after delay
        if not exists:
            self.current_move_filename = None
            callback()
        else:
            self.root.after(200, lambda: self.wait_until_file_deleted(callback))

    # Callback after human move is processed
    def after_human_move_ready(self):
        """
            Called when the robot/external system has finished
            processing the human move (files deleted).
            Now it's time for the computer to move.
        """

        # Check for game over
        if self.board.is_game_over():
            self.show_result()
            return

        # Update info label
        self.info_label.config(text="Turn: black (Computer)")
        
        # Let the AI make its move
        self.computer_move()

    # Callback after AI move is processed
    def after_ai_move_ready(self):
        """
            Called when the robot/external system has finished
            processing the computer move (files deleted).
            Now it's time for the human to move again.
        """
        # Check for game over
        if self.board.is_game_over():
            self.show_result()
            return

        # Allow human to move again
        self.can_human_move = True
        self.info_label.config(text="Turn: white (Human)")

    # Board drawing method
    def draw_board(self):
        """
            Draw the chess board and pieces on the canvas.
            Parameters:
                - self: ChessGUI instance
            Returns:
                - None
        """

        # Clear the canvas
        self.canvas.delete("all")

        # Draw squares and pieces
        for rank in range(8):
            for file in range(8):

                # Calculate square coordinates
                x1 = file * SQUARE_SIZE
                y1 = (7 - rank) * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                # Determine square color
                color = LIGHT_COLOR if (file + rank) % 2 == 0 else DARK_COLOR
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Draw piece if present
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    if piece.color == chess.WHITE:
                        symbol = WHITE_PIECES[piece.piece_type]
                    else:
                        symbol = BLACK_PIECES[piece.piece_type]

                    # Draw the piece symbol
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=symbol,
                        font=("Arial", 32),
                    )

        # Highlight selected square
        if self.selected_square is not None:
            file = chess.square_file(self.selected_square)
            rank = chess.square_rank(self.selected_square)
            x1 = file * SQUARE_SIZE
            y1 = (7 - rank) * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="red", width=3
            )

    # User click handling
    def on_click(self, event):
        """
            Handle user clicks on the chess board.
            Parameters:
                - self: ChessGUI instance
                - event: Tkinter event instance
            Returns:
                - None
        """

        # Ignore clicks if game is over
        if self.board.is_game_over():
            return

        # If we are waiting for the robot, ignore clicks
        if not self.can_human_move:
            return

        # Only allow moving if it's white's turn (human)
        if self.board.turn != chess.WHITE:
            return

        # Calculate clicked square
        file = event.x // SQUARE_SIZE
        rank = 7 - (event.y // SQUARE_SIZE)

        # Check bounds
        if file < 0 or file > 7 or rank < 0 or rank > 7:
            return

        # Calculate the square index
        clicked_square = chess.square(file, rank)

        # Handle first and second clicks
        if self.selected_square is None:
            # First click: select piece
            piece = self.board.piece_at(clicked_square)
            if piece is None or piece.color != chess.WHITE:
                return
            self.selected_square = clicked_square
            self.draw_board()
        else:
            # Second click: attempt to move
            from_sq = self.selected_square
            to_sq = clicked_square
            move = chess.Move(from_sq, to_sq)

            # Check if move is legal, handle promotion
            if move not in self.board.legal_moves:
                promo_move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
                if promo_move in self.board.legal_moves:
                    move = promo_move
                else:
                    # Illegal move, deselect
                    self.selected_square = None
                    self.draw_board()
                    return

            # Make the move made by the human
            print(f"Move (Human): {move.uci()}")

            # Send move to robot first and wait before pushing
            self.can_human_move = False
            self.write_move_file(move)
            self.info_label.config(
                text="Human move sent (<kind_move>.txt). Waiting external execution..."
            )

            # Now push the move to the board
            self.board.push(move)
            self.selected_square = None
            self.draw_board()

            # Check for game over
            if self.board.is_game_over():
                self.show_result()
                return

            # Wait until files are deleted, then continue with computer move
            self.wait_until_file_deleted(self.after_human_move_ready)

    # AI move handling 
    def computer_move(self):
        """
            Let the computer (AI) make its move.
        """
        # Check for game over
        if self.board.is_game_over():
            return

        # Get AI move
        move = self.engine.choose_move(self.board)
        if move is None:
            self.show_result()
            return

        # Debug print
        print(f"Move (Computer): {move.uci()}")

        # Calculate SAN for display before pushing
        move_san = self.board.san(move)

        # Send move to robot first and wait before pushing
        self.can_human_move = False
        self.write_move_file(move)
        self.info_label.config(
            text=f"Black plays: {move_san}. Waiting external execution of AI move..."
        )

        # Now push the move to the board
        self.board.push(move)
        self.draw_board()

        # Check for game over
        if self.board.is_game_over():
            self.show_result()
            return

        # Wait until files are deleted, then allow human to move
        self.wait_until_file_deleted(self.after_ai_move_ready)


    # Show game result
    def show_result(self):
        """
            Display the result of the game.
            Parameters:
                - self: ChessGUI instance
            Returns:
                - None
        """

        # Get and display result
        result = self.board.result()

        # Display result message
        if result == "1-0":
            text = "Result: 1-0 (white wins)"
        elif result == "0-1":
            text = "Result: 0-1 (black wins)"
        else:
            text = "Result: 1/2-1/2 (draw)"
        self.info_label.config(text=text)
