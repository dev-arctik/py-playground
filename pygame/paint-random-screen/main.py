# Original repo: dev-arctik/Paint-Canvas
import pygame
import random
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((800, 560))
    pygame.display.set_caption("Paint screen with random colors")

    w = 20
    h = 20

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with random-colored rectangles row by row
        for y in range(0, 560, h):
            for x in range(0, 800, w):
                color = (random.randrange(226), random.randrange(226), random.randrange(226))
                pygame.draw.rect(win, color, (x, y, w, h))

            # Update per row with delay — original had 8ms per rect (40 rects/row = ~320ms)
            # Using ~50ms per row gives a visible progressive painting effect
            pygame.display.update()
            await asyncio.sleep(0.05)

        # Hold the completed screen for a moment before clearing
        await asyncio.sleep(1)
        win.fill((0, 0, 0))


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
