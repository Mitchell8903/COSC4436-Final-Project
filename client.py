import socket

PORT = 5050
FORMAT = 'utf-8'
SERVER = input("Enter server IP: ")
ADDR = (SERVER, PORT)

def place_ships():
    board = []
    for x in range(10):
        board.append(['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'])
    size = [5,4,3,3,2] 

    a = 0
    while a < 5: 
        print()
        print_board(board)
        print("\nShip %s is size %s" % (str(a + 1), size[a]))
        try:
            x = int(input("Enter the x coordinate of ship %s (0 - 9): " % str(a + 1)))
            y = int(input("Enter the y coordinate of ship %s (0 - 9): " % str(a + 1)))
            direction = input("Enter which direction you wish to place the ship (n/w/s/e)").lower()
        except Exception as e:
            print("Invalid input")
            continue
        
        #swapped x and y here because the they were coming out backwards
        valid = check_place(board, size[a], direction, y, x, a) #pass size of ship, direction from start, x, y

        if valid:
            print("Ship %s placed successfully" % str(a + 1))
            #print board after each placement
            a += 1
        else:
            print("Ship %s could not be placed. Please try a different location and/or orientation" % str(a + 1))
    return board
     

     
#helper to print board
def print_board(board):
    print("  0 1 2 3 4 5 6 7 8 9")
    for x in range(10):
        print(str(x) + " " + " ".join(board[x]))

#converts 10x10 2D array to String to send over socket easier
def flatten_board(board):
    flattened = ""
    for x in range(10):
        for y in range(10):
            flattened = flattened + board[y][x]
    return flattened

def check_place(board, size, direction, x, y, a):
    if direction not in ["n", "w", "s", "e"]:
        print("Invalid direction")
        return False

    symbols = ['A', 'B', 'C', 'D', 'E']

    if direction == 'n':
        if x - size < 0:
            return False
        for z in range(size):
            if board[x-z][y] != '.':
                return False
        for z in range(size):
            board[x-z][y] = symbols[a]

    if direction == 's':
        if x + size > 10:
            return False
        for z in range(size):
            if board[x+z][y] != '.':
                return False
        for z in range(size):
            board[x+z][y] = symbols[a]

    if direction == 'w':
        if y - size < 0:
            return False
        for z in range(size):
            if board[x][y-z] != '.':
                return False
        for z in range(size):
            board[x][y-z] = symbols[a]

    if direction == 'e':
        if y + size > 10:
            return False
        for z in range(size):
            if board[x][y + z] != '.':
                return False
        for z in range(size):
            board[x][y + z] = symbols[a]

    return True



if __name__ == "__main__":

    #connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    #get board
    board = place_ships()

    #send board
    client.sendall(flatten_board(board).encode(FORMAT))