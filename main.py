# This is the main file which runs everything
from src.example import componentSaysHello

def main():
    componentResult = componentSaysHello()
    print(componentResult)

if __name__ == "__main__":
    main()
