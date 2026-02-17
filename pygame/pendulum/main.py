# Original repo: dev-arctik/Pendulum
import pygame
import math
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Simple Pendulum")

    # Pendulum parameters
    m = 7        # bob radius (visual mass)
    l = 200      # rod length
    a = math.pi / 2   # initial angle (90 degrees)
    av = 0       # angular velocity
    aa = 0       # angular acceleration
    g = 0.009    # gravity constant (tuned for this simulation)
    x0 = 250     # pivot x
    y0 = 50      # pivot y

    def draw(x, y):
        """Draw the pivot, rod, and bob."""
        pygame.draw.circle(win, (250, 250, 250), (x0, y0), 2)
        pygame.draw.line(win, (250, 0, 0), (x0, y0), (x, y), 3)
        pygame.draw.circle(win, (250, 250, 0), (int(x), int(y)), m)

    running = True
    while running:
        win.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Physics: angular acceleration from gravity, damped angular velocity
        aa = -m * g * math.sin(a)
        av = av + aa
        av = av * 0.99  # damping factor
        a = a + av

        # Convert polar to cartesian
        x = x0 + (l * math.sin(a))
        y = y0 + (l * math.cos(a))

        draw(x, y)
        pygame.display.update()

        # Replaces pygame.time.delay(50) — preserves original 20 FPS
        await asyncio.sleep(0.05)


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
