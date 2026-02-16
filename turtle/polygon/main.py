# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.pensize(1)
    pen.color("black")
    pen.penup()
    pen.setpos(0, -275)
    pen.pendown()
    pen.speed(0)
    pen.hideturtle()

    # tracer moved to setup — original had it inside inner loop (redundant)
    pen.getscreen().tracer(100, 0)

    # Capped from range(3, 2000) to range(3, 51) for browser performance
    for j in range(3, 51):
        a = 360 / j
        for i in range(j):
            pen.forward(75)
            pen.left(a)

        if j % 2 == 0:
            await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
