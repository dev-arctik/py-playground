# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.color("red")
    pen.speed(0)
    pen.hideturtle()

    # Quadrant 1: top-right
    for i in range(0, 21):
        x = 0
        y = (10 - (0.5 * i)) * 25
        x1 = 0.5 * i * 25
        y1 = 0
        pen.penup()
        pen.goto(x, y)
        pen.pendown()
        pen.goto(x1, y1)
        if i % 3 == 0:
            await asyncio.sleep(0)

    # Quadrant 2: bottom-right
    for i in range(0, 21):
        x = 0
        y = (10 - (0.5 * i)) * 25
        x1 = 0.5 * i * 25
        y1 = 0
        pen.penup()
        pen.goto(x1, -y1)
        pen.pendown()
        pen.goto(x, -y)
        if i % 3 == 0:
            await asyncio.sleep(0)

    # Quadrant 3: bottom-left
    for i in range(0, 21):
        y = 0
        x = -(10 - (0.5 * i)) * 25
        y1 = -0.5 * i * 25
        x1 = 0
        pen.penup()
        pen.goto(x, y)
        pen.pendown()
        pen.goto(x1, y1)
        if i % 3 == 0:
            await asyncio.sleep(0)

    # Quadrant 4: top-left
    for i in range(0, 21):
        x = 0
        y = (10 - (0.5 * i)) * 25
        x1 = 0.5 * i * 25
        y1 = 0
        pen.penup()
        pen.goto(-x, y)
        pen.pendown()
        pen.goto(-x1, y1)
        if i % 3 == 0:
            await asyncio.sleep(0)


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
