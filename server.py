import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'


class Player:

    #constructer
    def __init__(self, sock, addr):
        self.sock = sock
        self.address = addr
        self.ship_health = {'A':5, 'B':4, 'C':3, 'D':3, 'E':2}
        self.ready = False
        self.ships = []
        self.shots_made = []
        for i in range(10):
            self.shots_made.append(['.','.','.','.','.','.','.','.','.','.'])

    #initilaizes ships and sets status to ready
    def ready_up(self, ships):
        self.ships = ships
        self.ready = True

    #Returns 0 for miss, 1 for hit and 2 for hit and sunk battleship
    def attack(self, opp, x, y):
        if (opp.ships[y][x] in ['A', 'B', 'C', 'D', 'E']):
            self.shots_made[y][x] = 'H' #mark as hit for player
            opp.ship_health[opp.ships[y][x]] -= 1 #update ships health
            if (opp.ship_health[opp.ships[y][x]] == 0):
                opp.ships[y][x] = 'X' #mark hit on opponents ship
                return 2
            opp.ships[y][x] = 'X' #mark hit on opponents ship
            return 1
        else:
            self.shots_made[y][x] = 'M' #mark as hit for player
            return 0

    #returns true if still has ships alive
    def is_alive(self):
        for ship in self.ship_health:
            if self.ship_health[ship] > 0:
                return True
        return False

    #sends a string to client
    def send_message(self,message):
        self.sock.send(message.encode(FORMAT))



def unflatten_board(flattened_board):
    i = 0
    board = []
    for x in range(10):
        board.append(list(flattened_board[i:i+10]))
        i += 10
    return board

def flatten_board(board):
    flattened = ""
    for x in range(10):
        for y in range(10):
            flattened = flattened + board[y][x]
    return flattened

#called after new connection, returns player object with ships configured
def handle_initial_connection(player: Player):
    player.send_message("bship")
    #wait to receive ship placement from client
    ships = player.sock.recv(256).decode(FORMAT)
    #set players status to ready and initalize those ships
    player.ready_up(unflatten_board(ships))



if __name__ == "__main__":

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] server is starting... (%s)" % SERVER)
    server.listen()
    print("Waiting for clients to connect...")

    #wait for player 1 to join
    sock1, addr1 = server.accept()
    player1 = Player(sock1, addr1) 
    print("Player 1 Connected [%s]" % addr1[0])
    #begin ship placement for player 1
    thread1 = threading.Thread(target=handle_initial_connection, args=(player1,))
    thread1.start()

    #wait for player 2 to join
    sock2, addr2 = server.accept()
    player2 = Player(sock2, addr2) 
    print("Player 2 Connected [%s]" % addr2[0])
    #begin ship placement for player 1
    thread2 = threading.Thread(target=handle_initial_connection, args=(player2,))
    thread2.start()

    #wait for both players to finish placing ships
    while (not (player1.ready and player2.ready)):
        pass

    #ACTUAL GAME LOGIC BEGINS HERE
    print("Begin Game Here")
    #print(player1.ships)
    #print(player2.ships)
    
    isPlayer1 = True
    while (player1.is_alive() and player2.is_alive()):
        #get current player
        currentPlayer = player1 if isPlayer1 else player2
        altPlayer = player2 if isPlayer1 else player1
        #request action from client, then send board data
        print('requesting action from %s' % {True:'Player 1', False:'Player 2'}[isPlayer1])
        currentPlayer.send_message('A')
        currentPlayer.send_message(flatten_board(currentPlayer.shots_made)+flatten_board(currentPlayer.ships))
        #get coordinates
        print('waiting for response...')
        attack_coord = currentPlayer.sock.recv(2).decode(FORMAT)
        #update boards
        print('response recieved, updating boards')
        status = currentPlayer.attack(altPlayer,int(attack_coord[0]),int(attack_coord[1]))
        if (status == 0):
            currentPlayer.send_message("Miss!")
        if (status == 1):
            currentPlayer.send_message("Hit!")
        if (status == 2):
            currentPlayer.send_message("Hit! You sunk a ship!")
        #get next player
        isPlayer1 = not isPlayer1

    #end it all
    player1.send_message('E')
    player2.send_message('E')

    if (player1.is_alive()):
        player1.send_message("You win!")
        player2.send_message("You lose!")
    else:
        player1.send_message("You lose!")
        player2.send_message("You win!")

