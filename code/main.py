import time
from client import ClientSocket
from argparse import ArgumentParser
import numpy as np
# H V W 0 1 2

# initiaize the game state as an np array of 3 elements
GAME_STATE = np.zeros((1, 1, 3))

# initiaize the game state
START_HME = (0, 0)
US = 0
CURRENT_POSITION = (0, 0)
# colonne is coordinate on x axis
# ligne is coordinate on y axis
# H is the number of humans on the cell x,y
# V is the number of vampires on the cell x,y
# W is the number of werewolves on the cell x,y
# GAME_STATE is a matrix of size given by the server (set message)
# GAME_STATE ( colonne,ligne,Espece )
# GAME_STATE[0][0] is the top left cell
# GAME_STATE[colonne][ligne] is the cell at coordinates colonne,ligne
# GAME_STATE[colonne][ligne] = (H, V, W) is the tuple of the number of humans, vampires and werewolves on the cell colonne,ligne

# UPDATE_GAME_STATE(message) is a function that updates the GAME_STATE matrix according to the message received from the server
# COMPUTE_NEcolonneT_MOVE(GAME_STATE) is a function that computes the next move given the GAME_STATE matrix and give nb_moves and moves
# nb_moves is the number of moves
# moves is a list of moves
# moves[i] is a tuple (colonne,ligne,H,V,W) where colonne,ligne are the coordinates of the cell to move to and H,V,W are the number of humans, vampires and werewolves to move to the cell colonne,ligne


'''

'''


def play_game(strategy=None, args=None):
    client_socket = ClientSocket(args.ip, args.port)
    client_socket.send_nme("IANIS")
    # set message
    message = client_socket.get_message()
    UPDATE_GAME_STATE(message)
    # hum message
    message = client_socket.get_message()
    UPDATE_GAME_STATE(message)
    # hme message
    message = client_socket.get_message()
    UPDATE_GAME_STATE(message)
    # map message
    message = client_socket.get_message()
    UPDATE_GAME_STATE(message)

    # start of the game
    while True:
        message = client_socket.get_message()
        time_message_received = time.time()
        UPDATE_GAME_STATE(message)
        if message[0] == "upd":
            nb_moves, moves = COMPUTE_NEXT_MOVE(GAME_STATE)
            client_socket.send_mov(nb_moves, moves)


def UPDATE_GAME_STATE(message):
    global GAME_STATE
    global START_HME
    global US
    global CURRENT_POSITION

    if message[0] == "set":
        message = message[1]
        GAME_STATE = np.full((message[0], message[1], 3), 0)

    elif message[0] == "hum":
        pass

    elif message[0] == "hme":
        message = message[1]
        START_HME = (message[0], message[1])

        CURRENT_POSITION = START_HME

    elif message[0] == "map" or message[0] == "upd":
        temp = message[0]
        message = message[1]
        for N in message:
            colonne = N[0]
            ligne = N[1]
            H = N[2]  # empty if 0 human otherwise
            V = N[3]
            W = N[4]
            GAME_STATE[ligne][colonne][0] = H
            GAME_STATE[ligne][colonne][1] = V
            GAME_STATE[ligne][colonne][2] = W

        if temp == "map":
            US = 1 if GAME_STATE[START_HME[1],
                                 START_HME[0], 1] > 0 else 2  # vampire ou werewolf

    elif message[0] == "end":
        START_HME = (0, 0)
        GAME_STATE = np.zeros((1, 1, 3))

    elif message[0] == "bye":
        # close connection
        # TODO
        pass

    # elif message[0] == "mov":
    #     # we can perform the move
    #     N = message[1]
    #     message = message[2:]
    #     for i in range(N):


def COMPUTE_NEXT_MOVE(GAME_STATE):
    global US  # keep track of our nature (W/V)
    nb_moves = 1
    moves = []
    us_coordinates = []
    possible_moves = []
    next_move = (0, 0)
    global CURRENT_POSITION  # keep track of our position
    # vampire (V) or a werewolf (W) can move only to an adjacent cell (up, down, left, right and diagonal)

    x = CURRENT_POSITION[0]  # x coordinate (i) 14
    y = CURRENT_POSITION[1]   # y coordinate (j) 28

    # if we are non on borders of the map we stock 8 possible positions
    if y > 0 and y < GAME_STATE.shape[0]-1 and x > 0 and x < GAME_STATE.shape[1]-1:
        possible_moves.append((x-1, y-1))
        possible_moves.append((x-1, y))
        possible_moves.append((x-1, y+1))
        possible_moves.append((x, y-1))
        possible_moves.append((x, y+1))
        possible_moves.append((x+1, y-1))
        possible_moves.append((x+1, y))
        possible_moves.append((x+1, y+1))

    # if we are on the top left corner we stock 3 possible positions
    elif y == 0 and x == 0:

        possible_moves.append((x, y+1))
        possible_moves.append((x+1, y))
        possible_moves.append((x+1, y+1))

    # if we are on the top right corner we stock 3 possible positions
    elif y == 0 and x == GAME_STATE.shape[1]-1:
        possible_moves.append((x, y-1))
        possible_moves.append((x+1, y-1))
        possible_moves.append((x+1, y))

    # if we are on the bottom left corner we stock 3 possible positions
    elif y == GAME_STATE.shape[0]-1 and x == 0:
        possible_moves.append((x-1, y))
        possible_moves.append((x-1, y+1))
        possible_moves.append((x, y+1))

    # if we are on the top border we stock 5 possible positions
    elif y == 0 and x > 0 and x < GAME_STATE.shape[1]-1:
        possible_moves.append((x, y-1))
        possible_moves.append((x, y+1))
        possible_moves.append((x+1, y-1))
        possible_moves.append((x+1, y))
        possible_moves.append((x+1, y+1))

    # if we are on the bottom border we stock 5 possible positions
    elif y == GAME_STATE.shape[0]-1 and x > 0 and x < GAME_STATE.shape[1]-1:
        possible_moves.append((x-1, y-1))
        possible_moves.append((x-1, y))
        possible_moves.append((x-1, y+1))
        possible_moves.append((x, y-1))
        possible_moves.append((x, y+1))

    # if we are on the left border we stock 5 possible positions
    elif y > 0 and y < GAME_STATE.shape[0]-1 and x == 0:
        possible_moves.append((x-1, y))
        possible_moves.append((x-1, y+1))
        possible_moves.append((x, y+1))
        possible_moves.append((x+1, y))
        possible_moves.append((x+1, y+1))

    # if we are on the right border we stock 5 possible positions
    elif y > 0 and y < GAME_STATE.shape[0]-1 and x == GAME_STATE.shape[1]-1:
        possible_moves.append((x-1, y-1))
        possible_moves.append((x-1, y))
        possible_moves.append((x, y-1))
        possible_moves.append((x+1, y-1))
        possible_moves.append((x+1, y))

    # bottom right corner
    if y == GAME_STATE.shape[0]-1 and x == GAME_STATE.shape[1]-1:
        possible_moves.append((x-1, y-1))
        possible_moves.append((x-1, y))
        possible_moves.append((x, y-1))

    # chooe a random move
    next_move = possible_moves[np.random.randint(0, len(possible_moves))]
    print(possible_moves)
    print(next_move)

    # moves = [next_move[0], next_move[1], GAME_STATE[x]
    #          [y][0], GAME_STATE[x][y][1], GAME_STATE[x][y][2]]

    moves = [[x, y, GAME_STATE[y]
              [x][1], next_move[0], next_move[1]]]
    CURRENT_POSITION = (next_move[0], next_move[1])
    return nb_moves, moves


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(dest='ip', default='localhost', type=str,
                        help='IP adress the connection should be made to.')
    parser.add_argument(dest='port', default='5555', type=int,
                        help='Chosen port for the connection.')

    args = parser.parse_args()
    play_game(None, args)
