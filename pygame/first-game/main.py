# Original repo: dev-arctik/Python-Game
import pygame
import asyncio


# No-op audio stub — pygame.mixer may not work in the browser
class _NoSound:
    def play(self):
        pass


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 480))
    pygame.display.set_caption("First Game")

    # Load images after display init (browser requires set_mode first)
    walkRight = [pygame.image.load(f'assets/R{i}.png') for i in range(1, 10)]
    walkLeft = [pygame.image.load(f'assets/L{i}.png') for i in range(1, 10)]
    bg = pygame.image.load('assets/bg.jpg')
    char = pygame.image.load('assets/standing.png')

    # Enemy sprite sheets
    enemyWalkRight = [pygame.image.load(f'assets/R{i}E.png') for i in range(1, 12)]
    enemyWalkLeft = [pygame.image.load(f'assets/L{i}E.png') for i in range(1, 12)]

    # Audio disabled for browser — no-op stubs prevent NameError
    bulletSound = _NoSound()
    hitSound = _NoSound()

    score = 0

    class player(object):
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.vel = 5
            self.isJump = False
            self.left = False
            self.right = False
            self.walkCount = 0
            self.jumpCount = 10
            self.standing = True
            self.hitbox = (self.x + 17, self.y + 11, 29, 52)

        def draw(self, win):
            if self.walkCount + 1 >= 27:
                self.walkCount = 0

            if not self.standing:
                if self.left:
                    win.blit(walkLeft[self.walkCount // 3], (self.x, self.y))
                    self.walkCount += 1
                elif self.right:
                    win.blit(walkRight[self.walkCount // 3], (self.x, self.y))
                    self.walkCount += 1
            else:
                if self.right:
                    win.blit(walkRight[0], (self.x, self.y))
                else:
                    win.blit(walkLeft[0], (self.x, self.y))
            self.hitbox = (self.x + 17, self.y + 11, 29, 52)

        async def hit(self):
            """Async version — replaces blocking while loop (200 x 10ms = 2s pause)"""
            nonlocal score
            self.isJump = False
            self.jumpCount = 10
            self.x = 0
            self.y = 410
            self.walkCount = 0
            # Replaced SysFont('comicsans', 100) — no system fonts in browser
            font1 = pygame.font.Font(None, 100)
            text = font1.render('-5', 1, (255, 0, 0))
            win.blit(text, (250 - (text.get_width() / 2), 200))
            pygame.display.update()
            # Async delay replacing blocking: while i < 200: delay(10)
            for i in range(200):
                await asyncio.sleep(0.01)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
            return True

    class projectile(object):
        def __init__(self, x, y, radius, color, facing):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.facing = facing
            self.vel = 8 * facing

        def draw(self, win):
            pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    class enemy(object):
        def __init__(self, x, y, width, height, end):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.end = end
            self.path = [self.x, self.end]
            self.walkCount = 0
            self.vel = 3
            self.hitbox = (self.x + 17, self.y + 2, 31, 57)
            self.health = 10
            self.visible = True

        def draw(self, win):
            self.move()
            if self.visible:
                if self.walkCount + 1 >= 33:
                    self.walkCount = 0

                if self.vel > 0:
                    win.blit(enemyWalkRight[self.walkCount // 3], (self.x, self.y))
                    self.walkCount += 1
                else:
                    win.blit(enemyWalkLeft[self.walkCount // 3], (self.x, self.y))
                    self.walkCount += 1

                # Health bar (red background + green fill)
                pygame.draw.rect(win, (255, 0, 0), (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
                pygame.draw.rect(win, (0, 128, 0), (self.hitbox[0], self.hitbox[1] - 20, 50 - (5 * (10 - self.health)), 10))
                self.hitbox = (self.x + 17, self.y + 2, 31, 57)

        def move(self):
            if self.vel > 0:
                if self.x + self.vel < self.path[1]:
                    self.x += self.vel
                else:
                    self.vel = self.vel * -1
                    self.walkCount = 0
            else:
                if self.x - self.vel > self.path[0]:
                    self.x += self.vel
                else:
                    self.vel = self.vel * -1
                    self.walkCount = 0

        def hit(self):
            if self.health > 0:
                self.health -= 1
            else:
                self.visible = False

    def redrawGameWindow():
        win.blit(bg, (0, 0))
        text = font.render('Score: ' + str(score), 1, (0, 0, 0))
        win.blit(text, (350, 10))
        man.draw(win)
        goblin.draw(win)
        for bullet in bullets:
            bullet.draw(win)
        pygame.display.update()

    # Main loop setup
    # Replaced SysFont('comicsans', 30, True) — no system fonts in browser
    font = pygame.font.Font(None, 30)
    man = player(200, 410, 64, 64)
    goblin = enemy(100, 410, 64, 64, 450)
    shootLoop = 0
    bullets = []
    run = True

    while run:
        await asyncio.sleep(1 / 27)  # Replaces clock.tick(27) — 27 FPS

        # Player-enemy collision
        if goblin.visible:
            if man.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3] and man.hitbox[1] + man.hitbox[3] > goblin.hitbox[1]:
                if man.hitbox[0] + man.hitbox[2] > goblin.hitbox[0] and man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                    result = await man.hit()
                    if result is False:
                        run = False
                        break
                    score -= 5

        if shootLoop > 0:
            shootLoop += 1
        if shootLoop > 3:
            shootLoop = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Bullet collision + movement (iterate copy for safe removal)
        for bullet in bullets[:]:
            if goblin.visible:
                if bullet.y - bullet.radius < goblin.hitbox[1] + goblin.hitbox[3] and bullet.y + bullet.radius > goblin.hitbox[1]:
                    if bullet.x + bullet.radius > goblin.hitbox[0] and bullet.x - bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]:
                        hitSound.play()
                        goblin.hit()
                        score += 1
                        bullets.remove(bullet)
                        continue

            if 0 < bullet.x < 500:
                bullet.x += bullet.vel
            else:
                bullets.remove(bullet)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and shootLoop == 0:
            bulletSound.play()
            facing = -1 if man.left else 1
            if len(bullets) < 5:
                bullets.append(
                    projectile(round(man.x + man.width // 2), round(man.y + man.height // 2), 6, (0, 0, 0), facing)
                )
            shootLoop = 1

        if keys[pygame.K_LEFT] and man.x > man.vel:
            man.x -= man.vel
            man.left = True
            man.right = False
            man.standing = False
        elif keys[pygame.K_RIGHT] and man.x < 500 - man.width - man.vel:
            man.x += man.vel
            man.right = True
            man.left = False
            man.standing = False
        else:
            man.standing = True
            man.walkCount = 0

        if not man.isJump:
            if keys[pygame.K_UP]:
                man.isJump = True
                man.walkCount = 0
        else:
            if man.jumpCount >= -10:
                neg = 1 if man.jumpCount >= 0 else -1
                man.y -= (man.jumpCount ** 2) * 0.5 * neg
                man.jumpCount -= 1
            else:
                man.isJump = False
                man.jumpCount = 10

        redrawGameWindow()


# Dual-mode: browser (Pyodide has running loop) vs local
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
