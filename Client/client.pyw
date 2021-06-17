import pygame, socket, pickle, os

buffer = 2048

class Network:
    def __init__(self):
        self.server = (self.ip, self.port) = ("localhost", 2911)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = self.connect()

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.server)
            return pickle.loads(self.client.recv(buffer))
        except: pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(buffer))
        except socket.error as errMsg:
            print(errMsg)


size = (width, height) = (1280, 960)

window = pygame.display.set_mode(size)
pygame.display.set_caption("Better Together")

ship = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'ocean_e_new_ship_small.png')).convert(), (width//2, height)) #(825, 750)
water1 = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'water.png')).convert(), (width//4, height))
water2 = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'water.png')).convert(), (width//4, height))
aim = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'aim.png')).convert_alpha(), (80, 80))

def refresh(window, playerMe, playerOthers):
    window.blit(water1, (0, 0), (0, 0, width, height))
    window.blit(water2, (width-width//4, 0), (0, 0, width, height))
    window.blit(ship, (width//4, 0),(0, 0, width, height))
    for p in playerOthers:
        p.draw(window)

    playerMe.draw(window)

    font = pygame.font.SysFont(None, 64)

    window.blit(pygame.image.load(os.path.join('Images', 'wood plank.png')).convert_alpha(), (10,20))
    window.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (10,70))

    window.blit(font.render("{}".format(playerMe.inventoryWood), True, (0,0,0)), (60, 20))
    window.blit(font.render("{}".format(playerMe.inventoryCannon), True, (0,0,0)), (60, 70))

    #pygame.display.update()


if __name__ =="__main__":
    game = True
    server = Network()
    playerMe = server.getPlayer()
    framerate = pygame.time.Clock()
    infoCount = 0
    aimX = 300
    aimY = 320
    aimVelocity = 4
    cannonShoot = 60*2+1
    inventoryCannonWait = 0
    inventoryWoodWait = 0
    while game:
        framerate.tick(60)

        # refill inventory
        if playerMe.inventoryCannon <= 0:
            inventoryCannonWait += 1
            if inventoryCannonWait >= 60*60: # 1 minute
                playerMe.inventoryCannon = 9
                inventoryCannonWait = 0
        if playerMe.inventoryWood <= 0:
            inventoryWoodWait += 1
            if inventoryWoodWait >= 60*60: # 1 minute
                playerMe.inventoryWood = 9
                inventoryWoodWait = 0

        playerOthers = server.send(playerMe)


        refresh(window, playerMe, playerOthers)
        # cannon interaction
        if 420 <= playerMe.y <= 740 and (470 <= playerMe.x <= 550 or 760 <= playerMe.x <= 840):
            font = pygame.font.SysFont(None, 64)
            keys = pygame.key.get_pressed()

            if playerMe.inventoryCannon > 0:
                if keys[pygame.K_SPACE]:
                    if (keys[ord('w')] or keys[pygame.K_UP]) and aimY - aimVelocity > 0:
                        aimY -= aimVelocity
                        cannonShoot = 0

                    if (keys[ord('a')] or keys[pygame.K_LEFT]) and aimX - aimVelocity > 0:
                        aimX -= aimVelocity
                        cannonShoot = 0

                    if (keys[ord('s')] or keys[pygame.K_DOWN]) and aimY + aimVelocity < height:
                        aimY += aimVelocity
                        cannonShoot = 0

                    if (keys[ord('d')] or keys[pygame.K_RIGHT]) and aimX + aimVelocity < width:
                        aimX += aimVelocity
                        cannonShoot = 0

                    window.blit(aim, (aimX, aimY),(0, 0, width, height))
                else:
                    if cannonShoot <= 60*2: # 3 seconds
                        if cannonShoot == 60*2:
                            playerMe.inventoryCannon -= 1
                        cannonShoot += 1
                        window.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (aimX+20, aimY+20))

                    window.blit(font.render("Hold SPACE to use Cannon", True, (255,255,255)), (width//4-50, height-height//12))
                    playerMe.move()
            else:
                window.blit(font.render("No Ammo", True, (255,255,255)), (width//2-50, height-height//12))
                playerMe.move()
        else:
            playerMe.move()
            # move info
            if infoCount < 60*5: # 5 seconds
                infoCount += 1
                font = pygame.font.SysFont(None, 64)
                window.blit(font.render("Use WASD or Arrow Keys to MOVE", True, (255,255,255)), (width//4-50, height-height//12))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
                pygame.quit()
