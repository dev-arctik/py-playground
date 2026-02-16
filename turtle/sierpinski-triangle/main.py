# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.pensize(0.5)
    pen.speed(0)
    pen.color("black")
    pen.hideturtle()

    # tracer moved to setup — original had it inside the loop (redundant)
    pen.getscreen().tracer(100, 0)

    # Triangle vertices
    x1, y1 = 0, 250      # top
    x2, y2 = -250, -250   # bottom-left
    x3, y3 = 250, -250    # bottom-right

    # Plot the three vertices
    for vx, vy in [(x1, y1), (x2, y2), (x3, y3)]:
        pen.penup()
        pen.setpos(vx, vy)
        pen.pendown()
        pen.dot()
        pen.penup()

    # Start from a random point
    x = random.randrange(-250, 250)
    y = random.randrange(-250, 250)
    pen.setpos(x, y)
    pen.pendown()
    pen.dot()
    pen.penup()

    # Chaos game — capped from 2e21 to 10000 iterations
    for i in range(10000):
        pnt = random.choice(["a", "b", "c"])

        if pnt == "a":
            x = (x + x1) / 2
            y = (y + y1) / 2
        elif pnt == "b":
            x = (x + x2) / 2
            y = (y + y2) / 2
        elif pnt == "c":
            x = (x + x3) / 2
            y = (y + y3) / 2

        pen.setpos(x, y)
        pen.pendown()
        pen.dot()
        pen.penup()

        if i % 400 == 0:
            await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
