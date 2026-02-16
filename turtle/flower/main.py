# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio


async def main():
    pen = turtle.Turtle()
    pen.color("red")
    pen.speed(0)
    pen.up()
    pen.backward(100)
    pen.down()

    for i in range(36):
        pen.begin_fill()
        pen.forward(200)
        pen.left(170)
        pen.end_fill()
        await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
