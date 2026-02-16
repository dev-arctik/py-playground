# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.speed(0)
    pen.color("green")
    pen.penup()
    pen.hideturtle()

    # tracer moved to setup — original had it inside the loop (redundant)
    pen.getscreen().tracer(1000, 0)

    x = 0
    y = 0

    # Reduced from 100000 to 20000 iterations for browser performance
    for n in range(20000):
        r = random.random() * 100

        pen.goto(85 * x, 57 * y - 275)
        pen.pendown()
        pen.dot()
        pen.penup()

        # Note: original code has a sequential update — y uses new x, not old x.
        # Standard IFS requires simultaneous update. Preserving original behavior.
        if r < 1:
            x = 0
            y = 0.16 * y
        elif r < 86:
            x = 0.85 * x + 0.04 * y
            y = -0.04 * x + 0.85 * y + 1.6
        elif r < 93:
            x = 0.20 * x - 0.26 * y
            y = 0.23 * x + 0.22 * y + 1.6
        else:
            x = -0.15 * x + 0.28 * y
            y = 0.26 * x + 0.24 * y + 0.44

        if n % 800 == 0:
            await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
