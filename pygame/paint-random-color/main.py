# Original repo: dev-arctik/Paint-Canvas
import pygame
import random
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((800, 550))
    pygame.display.set_caption("Paint with random colors")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw random-colored circles at mouse position while left button held
        if pygame.mouse.get_pressed()[0]:
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]
            color = (random.randrange(226), random.randrange(226), random.randrange(226))
            pygame.draw.circle(win, color, (x, y), 8)

        # Update every frame (moved outside if block so display stays responsive)
        pygame.display.update()

        # Original had no delay — cap at 60 FPS to prevent 100% CPU
        await asyncio.sleep(1 / 60)


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
