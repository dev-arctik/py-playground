# Original repo: dev-arctik/Paint-board
import pygame
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Drawing square")

    x = 50
    y = 50
    width = 4
    height = 4
    vel = 5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Wrap around screen edges on all four sides
        if keys[pygame.K_LEFT]:
            x -= vel
            if x < 0:
                x = 500
        if keys[pygame.K_RIGHT]:
            x += vel
            if x > 500:
                x = 0
        if keys[pygame.K_UP]:
            y -= vel
            if y < 0:
                y = 500
        if keys[pygame.K_DOWN]:
            y += vel
            if y > 500:
                y = 0

        # Press 'c' to clear the canvas
        if keys[pygame.K_c]:
            win.fill((0, 0, 0))

        # No win.fill() per frame — rectangles persist as a drawing trail
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
