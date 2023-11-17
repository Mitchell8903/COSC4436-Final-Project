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
            self.shots_made.append(['O','O','O','O','O','O','O','O','O','O'])

    #initilaizes ships and sets status to ready
    def ready_up(self, ships):
        self.ships = ships
        self.ready = True

    #Returns 0 for miss, 1 for hit and 2 for hit and sunk battleship
    def attack(self, opp, x, y):
        if (opp.ships[y][x] in ['A', 'B', 'C', 'D', 'E']):
            self.shots_made[y][x] = 'H' #mark as hit for player
            opp.ships[y][x] = 'X' #mark hit on opponents ship
            opp.ship_health[opp.ships[y][x]] -= 1 #update ships health
            if (opp.ship_health[opp.ships[y][x]] == 0):
                return 2
            return 1
        else:
            self.shots_made[y][x] = 'M' #mark as hit for player
            return 0

    #returns true if still has ships alive
    def is_alive(self):
        for ship in self.ship_health:
            if ship > 0:
                return True
        return False

    #sends a string to client
    def send_message(message):
        sock.send(message.encode(FORMAT))



def unflatten_board(flattened_board):
    i = 0
    board = []
    for x in range(10):
        board.append(list(flattened_board[i:i+10]))
        i += 10
    return board



#called after new connection, returns player object with ships configured
def handle_initial_connection(player: Player):
    #wait to receive ship placement from client
    ships = player.sock.recv(256).decode(FORMAT)
    #set players status to ready and initalize those ships
    player.ready_up(unflatten_board(ships))



if __name__ == "__main__":

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] server is starting... (%s)" % SERVER)
    server.listen()

    #wait for player 1 to join
    sock, addr = server.accept()
    player1 = Player(sock, addr) 
    print("Player 1 Connected [%s]" % addr[0])
    #begin ship placement for player 1
    thread1 = threading.Thread(target=handle_initial_connection, args=(player1,))
    thread1.start()

    #wait for player 2 to join
    sock, addr = server.accept()
    player2 = Player(sock, addr) 
    print("Player 2 Connected [%s]" % addr[0])
    #begin ship placement for player 1
    thread2 = threading.Thread(target=handle_initial_connection, args=(player2,))
    thread2.start()

    #wait for both players to finish placing ships
    while (not (player1.ready and player2.ready)):
        pass

    #ACTUAL GAME LOGIC BEGINS HERE
    print("Begin Game Here")
    print(player1.ships)
    print(player2.ships)
    input()
     


