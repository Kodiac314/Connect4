# Connect 4 interface - play against no-cache DFS bot
# 9 APRIL 2026

"""
    Change here for human/bot
"""
PLAYER_1_BOT_MODE = False
PLAYER_2_BOT_MODE = True


from Connect4Solver import (
    Tile, Board, Idx, ROWS, COLS,
    smart_move, game_won, game_drawn, find_row
    )
import pygame
pygame.init()

# typedef
Display = None


"""
    Globals
"""
# Maximum screen dimensions (may be shrunk to fit board)
WIDTH, HEIGHT = 800, 600

# Game globals
board = [[0] * COLS for _ in range(ROWS)]
score = [0, 0, 0]
turn  = True

# Constants for Visual Display
RED      = (200, 50, 50)
YELLOW   = (200, 200, 50)
# WIDTH  : CHIPS=7*2*RADIUS, SPACER=6/2*R, 2*X_OFF=2*R -> 19*RADIUS
# HEIGHT : CHIPS=6*2*RADIUS, SPACER=5/2*R, Y_OFF=4*R -> 18.5*RADIUS
RADIUS   = int(min(WIDTH / 19, HEIGHT / 18.5))
SPACING  = 2.5 * RADIUS
X_OFFSET = 2 * RADIUS
Y_OFFSET = 4 *  RADIUS
BUFFER   = 1.5 * RADIUS

WIDTH = RADIUS * 19
HEIGHT = int(RADIUS * 18.5)
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4 vs bot")


# Animation globals
clicked_col     = 0
clicked_row     = 0
drop_y          = 0
max_drop_dist   = 0
new_chip_played = False
FALL_SPEED      = 1.5


"""
    Helper functions
"""
# a single RED or YELLOW circle at given coordinates
def draw_token(x: float, y: float) -> Display:
    pygame.draw.circle(dis, RED if turn==1 else YELLOW, (x, y), RADIUS)

# draws the board and pieces
def background() -> Display:
    dis.fill(0xffffff)
    pygame.draw.rect(dis, (15, 30, 133), (X_OFFSET - BUFFER, Y_OFFSET - BUFFER, 6*SPACING + 2*BUFFER, 5*SPACING + 2*BUFFER), border_radius=RADIUS)
    for y, row in enumerate(board):
        for x, sq in enumerate(row):
            color = RED if sq == 1 else YELLOW if sq == 2 else (200, 200, 200)
            pygame.draw.circle(dis, color, (x * SPACING + X_OFFSET, y * SPACING + Y_OFFSET), RADIUS)

# returns int 0-6 (or 10 if out of bounds) for which column user clicked on
def get_column() -> Idx:
    x, y = pygame.mouse.get_pos()
    col = -1
    if X_OFFSET - RADIUS <= x <= X_OFFSET + COLS*SPACING + RADIUS:
        col = (x - X_OFFSET + RADIUS) / SPACING
    return int(col)

def resetBoard():
    global board, turn
    print(f"Red has {score[1]} wins / YELLOW has {score[2]} wins / {score[0]} draws ")
    board = [[0] * COLS for _ in range(ROWS)]
    turn = sum(score) % 2 + 1


"""
    Game Loop
"""
def main():
    global dis, board, score, turn, clicked_col, clicked_row, new_chip_played
    
    pause        = False
    debug_mode   = True  # game paused after each move
    
    in_animation = False
    game_over    = False


    debug_mode = debug_mode and PLAYER_1_BOT_MODE and PLAYER_2_BOT_MODE
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                if event.key == pygame.K_SPACE:
                    pause = not pause

            """
                Mouse Clicked -> validate and drop chip
            """
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if in_animation:
                    continue
                
                if (turn==1 and PLAYER_1_BOT_MODE) or (turn==2 and PLAYER_2_BOT_MODE):
                    continue
                
                clicked_col = get_column()
                
                if clicked_col == -1 or board[0][clicked_col] != 0:
                    continue
                
                # Set the column clicked, animate the piece dropping down
                in_animation = True
                drop_y = RADIUS * 1.5
                clicked_row = find_row(board, clicked_col)
                max_drop_dist = Y_OFFSET + SPACING * clicked_row

        """
            Render the game
        """
        
        if pause:
            continue
        
        background()
        
        # Animate the chip falling
        if in_animation:
            drop_y += FALL_SPEED
            
            if drop_y > max_drop_dist:
                in_animation = False
                board[clicked_row][clicked_col] = turn
                turn = 3 - turn
                drop_y = max_drop_dist
                new_chip_played = True
            
            draw_token(X_OFFSET + SPACING * clicked_col, drop_y)
        
        # Check for game end
        elif new_chip_played:
            new_chip_played = False
            if debug_mode: pause = True
            
            if game_won(board, clicked_row, clicked_col, 3-turn):
                print("YELLOW" if turn==1 else "Red", "wins the game!")
                score[3-turn] += 1
                resetBoard()
            
            elif game_drawn(board):
                print("The game is a draw!")
                score[0] += 1
                resetBoard()
        
        elif (turn==1 and PLAYER_1_BOT_MODE) or (turn==2 and PLAYER_2_BOT_MODE):
            clicked_col = smart_move(board, turn)
            in_animation = True
            drop_y = RADIUS * 1.5
            clicked_row = find_row(board, clicked_col)
            max_drop_dist = Y_OFFSET + SPACING * clicked_row
        
        # Draw chip above board for next player's turn
        else:
            draw_token(X_OFFSET + SPACING * get_column(), RADIUS * 1.25)

        pygame.display.update()

    #pygame.display.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
