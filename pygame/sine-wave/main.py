# Original repo: dev-arctik/Sine-Wave
import pygame
import math
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Sine Wave")

    # Phase offset — increments each frame to make the wave scroll
    offset = 0

    running = True
    while running:
        win.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw all points with a shifting phase so the wave moves
        for i in range(50):
            x = ((math.pi * i) / 180) * 700
            y = 75 * math.sin(x + offset) + 250
            pygame.draw.circle(win, (250, 250, 250), (int(x), int(y)), 5)

        pygame.display.update()
        offset += 0.1

        await asyncio.sleep(1 / 60)


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
