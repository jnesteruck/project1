import time, sys

def slowPrint(string, speed):
    for char in string:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def fastPrint(string, speed):
    i = 0
    while i < len(string):
        ct = 0
        sys.stdout.write(string[i])
        sys.stdout.flush()
        i += 1
        ct += 1
        while ct < speed:
            if i < len(string):
                sys.stdout.write(string[i])
                sys.stdout.flush()
            else:
                break
            ct += 1
            i += 1
        time.sleep(0.01)
    print()


