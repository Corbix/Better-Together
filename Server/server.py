import socket, pickle, random
from _thread import *
from game import Game

server = (ip, port) = ("localhost", 2911)

buffer = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(server)
except socket.error as errMsg:
    str(errMsg)

s.listen(1)
print("Waiting for connections")

games = {}

def aiMove(gameId): # work in progress
    for i in range(len(games[gameId].ai)):
        if games[gameId].ai[i]:
            direction = random.randrange(1,11)

            #games[gameId].play(i,(x, y, width, height, list([(24*frame,64,24,32) for frame in range(3)])[1])
            #game.aiMove(gameId, i, (x,y)))


            if direction == 1 and games[gameId].players[i].y + games[gameId].players[i].velocity > 0:
                games[gameId].players[i].y -= games[gameId].players[i].velocity

            if direction == 2 and games[gameId].players[i].x + games[gameId].players[i].velocity > 0:
                games[gameId].players[i].x -= games[gameId].players[i].velocity

            if direction == 3 and games[gameId].players[i].y + games[gameId].players[i].height - games[gameId].players[i].velocity < games[gameId].players[i].maxHeight:
                games[gameId].players[i].y += games[gameId].players[i].velocity

            if direction == 4 and games[gameId].players[i].x + games[gameId].players[i].width - games[gameId].players[i].velocity < games[gameId].players[i].maxWidth:
                games[gameId].players[i].x += games[gameId].players[i].velocity

            games[gameId].players[i].player = (games[gameId].players[i].x, games[gameId].players[i].y, games[gameId].players[i].width, games[gameId].players[i].height)


def clientThread(connection, playerNumber, gameId):

    # Send player object
    connection.send(pickle.dumps(games[gameId].players[playerNumber]))
    reply = []
    while True:
        try:
            # Get player move
            data = pickle.loads(connection.recv(buffer))
            if not data: break

            # Reply others move
            games[gameId].players[playerNumber] = data
            #aiMove(gameId) # work in progress
            for i in range(len(games[gameId].players)):
                if i != playerNumber:
                    reply.append(games[gameId].players[i])

                #print("Received: ", data)
                #print("Sending : ", reply)

            connection.sendall(pickle.dumps(reply))
            reply = []

        except: break

    print("Lost connection", address)
    games[gameId].ai[playerNumber] = True

    if False not in games[gameId].ai:
        try:
            del games[gameId]
            print("Closing Game", gameId)

        except:
            pass

    connection.close()


while True:
    connection, address = s.accept()
    print("Connected to:", address)

    found = False

    # Search for a game to join
    for game in games:
        if not found:
            for aiControlled in range(len(games[game].ai)):
                if games[game].ai[aiControlled]:
                    found = True
                    playerNumber = aiControlled
                    gameId = game

                    print("Joining game", gameId)

                    games[gameId].ai[playerNumber] = False
                    break

    # Reopen a game
    if not found:
        if games:
            recentlyClosed = None
            maxGameId = max(games.keys())
            gameFound = False
            for recentlyClosed in range(1, maxGameId+1):
                if recentlyClosed-1 not in games:
                    gameFound = True
                    gameId = recentlyClosed-1
                    break

            # Create a new game
            if not gameFound:
                gameId = maxGameId + 1
        else:
            gameId = 0

        print("Creating a new game.", gameId)

        games[gameId] = Game(gameId)
        playerNumber = 0
        games[gameId].ai[0] = False

    start_new_thread(clientThread, (connection, playerNumber, gameId))
