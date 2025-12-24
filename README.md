# AI Chess with Robotic Arm Integration

This project presents the development of an automated chess system that integrates a classical Artificial Intelligence (AI) chess engine with a graphical user interface and a robotic arm for 
physical execution of chess moves. The system allows a human player to compete against the computer while each move is synchronized and executed by an industrial robotic arm EPSON.


---

## Project Overview

The system combines:
- A **classical AI chess engine** based on Negamax search with alpha-beta pruning.
- A **graphical user interface (GUI)** built with Tkinter for human interaction.
- A **file-based communication architecture** to transmit chess moves to a robotic arm.
- A **master–slave asynchronous control scheme**, ensuring synchronization between software and hardware.

Each move, whether performed by the human or the AI, is encoded and sent to the robot as a sequence of coordinates, enabling the physical manipulation of chess pieces on a real board.


---

## System Architecture

The project is structured into modular components:

- **Chess Logic & Rules**  
  Implemented using the `python-chess` library to manage board states, legal moves, game rules, and end-game conditions.

- **Search Engine (AI)**  
  A Negamax-based search engine with alpha-beta pruning evaluates and selects optimal moves using a heuristic evaluation function.

- **Evaluation Module**  
  Scores board positions based on material balance and mobility to guide the AI’s decision-making.

- **Graphical User Interface**  
  Built with Tkinter, allowing the user to interact with the chessboard through mouse clicks.

- **Robot Communication Layer**  
  Translates chess moves into robot-readable sequences using text files, enabling synchronized physical execution.


---


## Project Structure

- main.py               
- interface.py
- engine/evaluation.py  
- engine/search.py      
- engine/recorder.py    
- engine/robot_files.py
  

---


### Robotic Arm Integration

The robotic arm operates under an **asynchronous master–slave architecture**:
- The chess software acts as the **master**, generating movement commands.
- The robotic arm acts as the **slave**, executing moves based on generated text files.

The system waits for confirmation (file deletion) before allowing the next turn, ensuring full synchronization between the digital game and the physical execution.


---


### Features

- Human vs AI chess gameplay
- Classical AI using Negamax with alpha-beta pruning
- Real-time GUI interaction
- Physical execution of moves via robotic arm
- Support for captures and promotions
- Game recording in FEN and PGN formats


--- 


### Libraries Used

- **python-chess** – Chess rules, board representation, move generation  
  https://python-chess.readthedocs.io/en/latest/
- **Tkinter** – Graphical user interface  
  https://docs.python.org/3/library/tkinter.html
- **random** – Fallback random move selection  
  https://docs.python.org/3/library/random.html


---


### How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/dmerchan01/AI-chess.git
   ```
2. Create and activate a virtual environment (optional but recommended).
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
