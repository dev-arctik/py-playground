# Original repo: dev-arctik/Jumping-Square-
import pygame
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Jumping Square")  # Fixed from "First Game"

    x = 250
    y = 250
    width = 4
    height = 4
    vel = 5
    isJump = False
    jumpcount = 10

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Velocity wrapping is intentional — halves on left/top, doubles on right/bottom
        if keys[pygame.K_LEFT]:
            x -= vel
            if x < 0:
                x = 500
                vel = 0.5 * vel
        if keys[pygame.K_RIGHT]:
            x += vel
            if x > 500:
                x = 0
                vel = 2 * vel

        if not isJump:
            if keys[pygame.K_UP]:
                y -= vel
                if y < 0:
                    y = 500
                    vel = 0.5 * vel
            if keys[pygame.K_DOWN]:
                y += vel
                if y > 500:
                    y = 0
                    vel = 2 * vel
            if keys[pygame.K_SPACE]:
                isJump = True
        else:
            # Parabolic jump using squared jumpcount
            if jumpcount >= -10:
                neg = 1
                if jumpcount < 0:
                    neg = -1
                y -= (jumpcount ** 2) * 0.5 * neg
                jumpcount -= 1
            else:
                isJump = False
                jumpcount = 10

        win.fill((0, 0, 0))
        pygame.draw.rect(win, (255, 0, 0), (x, y, width, height))
        pygame.display.update()

        # Replaces pygame.time.delay(100) — preserves original 10 FPS
        await asyncio.sleep(0.1)


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
