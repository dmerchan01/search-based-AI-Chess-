import numpy as np
import os


class RobotMoveWriter:
    """
        Class to handle chess to mm conversion and file generation 
        for robot moves.
    """

    # Constructor
    def __init__(self):
        """
            Initializes the RobotMoveWriter object.
            Parameters:
                - self: RobotMoveWriter instance
            Returns:
                - None
        """

        # Path to read/write files
        self.path_base = r"X:\EpsonRC70\Projects\chess_arm_robot"

        # High Z values
        self.z_tablero = 143.0  # High Z for main board
        self.z_externo = 118.0  # High Z for external areas (to save the captured pieces)

        # This are the corner points in mm coordinates (you can calibrate them however you want)
        self.p_a1 = np.array([228.5, 839.5])
        self.p_h1 = np.array([-41.0, 850.0])
        self.p_a8 = np.array([220.0, 572.0])
        self.p_h8 = np.array([-49.5, 580.5])

        # This are the corner points for the captured white pieces areas (you can calibrate them however you want) 
        self.p_i1 = np.array([411.0, 854.0])
        self.p_j1 = np.array([365.0, 844.0])
        self.p_i8 = np.array([411.0, 556.0])
        self.p_j8 = np.array([365.0, 561.0])

        # This are the corner points for the captured black pieces areas (you can calibrate them however you want)
        self.p_l1 = np.array([-172.0, 859.0])
        self.p_m1 = np.array([-222.0, 851.0])
        self.p_l8 = np.array([-172.0, 574.5])
        self.p_m8 = np.array([-222.0, 575.0])

        # This are the points for the queens to use in promotion (you can calibrate them however you want)
        self.p_k1 = np.array([464.0, 846.0])
        self.p_k8 = np.array([464.0, 555.0])
        self.p_n1 = np.array([-269.0, 857.0])
        self.p_n8 = np.array([-269.0, 577.0])

        # Type of movement to filename mapping
        self.nombres = {
            0: "move.txt",
            1: "capture.txt",
            2: "promotion.txt",
            3: "capture_promotion.txt"
        }

    # Bilinear interpolation method
    def bilinear_interpolation(self, c1, c2, c3, c4, u, v):
        """
            Bilinear interpolation to get mm coordinates.
            Parameters:
                - self: RobotMoveWriter instance
                - c1, c2, c3, c4: corner points as numpy arrays
                - u, v: normalized coordinates (0 to 1)
            Returns:
                - numpy array: interpolated point
        """

        return (c1 * (1 - u) * (1 - v) +
                c2 * u * (1 - v) +
                c3 * (1 - u) * v +
                c4 * u * v)

    # Linear interpolation method
    def linear_interpolation(self, p_start, p_end, v):
        """
            Linear interpolation to get mm coordinates.
            Parameters:
                - self: RobotMoveWriter instance
                - p_start, p_end: start and end points as numpy arrays
                - v: normalized coordinate (0 to 1)
            Returns:
                - numpy array: interpolated point
        """
        return p_start * (1 - v) + p_end * v

    # Chess to mm conversion method
    def chess_to_mm(self, square):
        """
            Converts chess square notation to mm coordinates.
            Parameters:
                - self: RobotMoveWriter instance
                - square: chess square in algebraic notation (e.g., 'e4')
            Returns:
                - numpy array: mm coordinates [x, y, z]
        """

        square = square.lower().strip() # Normalize input
        col_char = square[0]            # Column character
        row_num = int(square[1])        # Row number

        # Normalized v coordinate
        v = (row_num - 1) / 7.0

        # If the address is within the main board
        if 'a' <= col_char <= 'h':
            col_idx = ord(col_char) - ord('a')
            u = col_idx / 7.0
            xy = self.bilinear_interpolation(
                self.p_a1, self.p_h1, self.p_a8, self.p_h8, u, v
            )
            return np.array([xy[0], xy[1], self.z_tablero])

        # If the address is outside the main board (captrured white pieces)
        elif col_char in ['i', 'j']:
            col_idx = ord(col_char) - ord('i')
            u = col_idx / 1.0
            xy = self.bilinear_interpolation(
                self.p_i1, self.p_j1, self.p_i8, self.p_j8, u, v
            )
            return np.array([xy[0], xy[1], self.z_externo])

        # If the address is outside the main board (captrured black pieces)
        elif col_char in ['l', 'm']:
            col_idx = ord(col_char) - ord('l')
            u = col_idx / 1.0
            xy = self.bilinear_interpolation(
                self.p_l1, self.p_m1, self.p_l8, self.p_m8, u, v
            )
            return np.array([xy[0], xy[1], self.z_externo])

        # If the address is for promotion queens (white)
        elif col_char == 'k':
            xy = self.linear_interpolation(self.p_k1, self.p_k8, v)
            return np.array([xy[0], xy[1], self.z_externo])

        # If the address is for promotion queens (black)
        elif col_char == 'n':
            xy = self.linear_interpolation(self.p_n1, self.p_n8, v)
            return np.array([xy[0], xy[1], self.z_externo])

        # If the column is not recognized
        else:
            raise ValueError(f"Column '{col_char}' not recognized.")

    # Method to generate robot move file
    def generate_robot_file(self, movements_chain, movements_type):
        """
            Generates a robot move file from a chain of chess moves.
            Parameters:
                - self: RobotMoveWriter instance
                - movements_chain: string of chess squares (e.g., 'e2e4g8f6')
                - movements_type: type of movement (0: move, 1: capture,
                                  2: promotion, 3: capture + promotion)
            Returns:
                - None
        """

        # Ensure base path exists
        if not os.path.exists(self.path_base):
            try:
                os.makedirs(self.path_base)
            except:
                print(f"Error: The file couldnt be crerated {self.path_base}")
                return

        # Validate movement type
        if movements_type not in self.nombres:
            print("Error: Invalid movement type.")
            return

        # Prepare file path
        file_name = self.nombres[movements_type]
        complete_path = os.path.join(self.path_base, file_name)
        point_list = []

        # Convert each square to mm coordinates
        for i in range(0, len(movements_chain), 2):
            cell = movements_chain[i:i+2]
            point = self.chess_to_mm(cell)
            point_list.append(
                f"{point[0]:.2f},{point[1]:.2f},{point[2]:.2f}"
            )

        # Write to file
        try:
            with open(complete_path, "w") as f:
                f.write("\n".join(point_list))
            print(f"--- File created: {file_name} ---")
        # Catch file writing errors
        except Exception as e:
            print(f"Error writting the file: {e}")
