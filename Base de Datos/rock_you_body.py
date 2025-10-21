import sys
from rich import print
from time import sleep

def typewriter(text, delay=0.05):
    for char in text:
        print(char, end="", flush=True)  # imprime sin salto de línea
        sleep(delay)
    print()  # salto de línea al terminar

def printLyrics():
    lines = [
        ("[I wanna da-]", 0.06),   #1
        ("I wanna dance in the lights", 0.05), #2
        ("I wanna ro-", 0.07),     #3
        ("I wanna rock your body", 0.08), #4
        ("I wanna go", 0.08),      #5
        ("I wanna go for a ride", 0.068), #6
        ("Hop in the music and", 0.07),   #7
        ("Rock your body", 0.08),  #8
        ("(Rock that body)", 0.069), #9
        ("come on, come on", 0.035), #10
        ("Rock that body", 0.08),   #11
        ("(Rock your body)", 0.053), #12
        ("Rock that body", 0.049), #13
        ("come on, come on", 0.035), #14
        ("Rock that body", 0.08),   #15
    ]

    for line, delay in lines:
        typewriter(line, delay)

printLyrics()
