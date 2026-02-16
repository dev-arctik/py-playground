# Original repo: dev-arctik/Python-Turtle
import turtle
import math
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.speed(0)
    pen.getscreen().tracer(100, 0)

    # Capped from infinite while True to 5000 iterations
    for i in range(1, 5001):
        pen.forward(math.sqrt(i))
        pen.left(math.pi * i * math.e)

        if i % 200 == 0:
            await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
