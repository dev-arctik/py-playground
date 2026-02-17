# Original repo: dev-arctik/Sierpinski-s-Triangle
import pygame
import random
import asyncio


async def main():
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Sierpinski Triangle")

    white = (255, 255, 255)

    # Three vertices of the triangle
    a = [250, 20]
    b = [20, 480]
    c = [480, 480]

    # Random starting point for the chaos game
    x = [random.randrange(20, 480), random.randrange(20, 480)]

    def layout():
        """Draw the three vertices."""
        pygame.draw.circle(win, white, a, 2)
        pygame.draw.circle(win, white, b, 2)
        pygame.draw.circle(win, white, c, 2)

    def draw_point():
        """Chaos game: pick a random vertex and move halfway toward it."""
        pnt = random.choice(['a', 'b', 'c'])
        if pnt == 'a':
            x[0] = (x[0] + a[0]) // 2
            x[1] = (x[1] + a[1]) // 2
        elif pnt == 'b':
            x[0] = (x[0] + b[0]) // 2
            x[1] = (x[1] + b[1]) // 2
        elif pnt == 'c':
            x[0] = (x[0] + c[0]) // 2
            x[1] = (x[1] + c[1]) // 2
        pygame.draw.circle(win, white, x, 2)

    # Draw vertices once at the start
    layout()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Space bar exits (preserved from original)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Batch 200 points per frame for performance (original drew 1 per iteration)
        for _ in range(200):
            draw_point()

        pygame.display.update()

        # 60 FPS — original had no delay, this yields to the browser event loop
        await asyncio.sleep(1 / 60)


# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
