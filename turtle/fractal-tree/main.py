# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio


def tree(plist, l, a, n):
    """Recursive generator that draws a fractal tree using turtle cloning."""
    pen = []
    if l > 1.5:
        for p in plist:
            p.forward(l)
            q = p.clone()
            p.left(a)
            q.right(a)
            pen.append(p)
            pen.append(q)
        for x in tree(pen, l * n, a, n):
            yield None


async def main():
    p = turtle.Turtle()
    p.hideturtle()
    p.speed(0)
    p.getscreen().tracer(100, 0)
    p.left(90)
    p.penup()
    p.forward(-210)
    p.pendown()

    # Option A: keep tree() as regular generator, yield to browser in caller
    t = tree([p], 200, 65, 0.637)
    for i, x in enumerate(t):
        if i % 15 == 0:
            await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
