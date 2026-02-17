# Original repo: dev-arctik/Paint-Canvas
import pygame
import random
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((675, 600))
    pygame.display.set_caption("Strips of shades of RGB")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Red strip (left to right, top third) — original had 5ms per rect
        for x in range(226):
            pygame.draw.rect(win, (x, 0, 0), (3 * x, 0, 3, 200))
            if x % 10 == 0:
                pygame.display.update()
                await asyncio.sleep(0.02)
        pygame.display.update()

        # Green strip (right to left, middle third — reversed direction)
        for x in range(225, -1, -1):
            pygame.draw.rect(win, (0, x, 0), (3 * x, 200, 3, 200))
            if x % 10 == 0:
                pygame.display.update()
                await asyncio.sleep(0.02)
        pygame.display.update()

        # Blue strip (left to right, bottom third)
        for x in range(226):
            pygame.draw.rect(win, (0, 0, x), (3 * x, 400, 3, 200))
            if x % 10 == 0:
                pygame.display.update()
                await asyncio.sleep(0.02)
        pygame.display.update()

        # Hold completed strips before clearing and repainting
        await asyncio.sleep(1.5)
        win.fill((0, 0, 0))


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
