# This is the main file which runs everything
from src.example import component_says_hello()

def main():
    """ Main entry point """
    component_result = component_says_hello()
    print(component_result)

if __name__ == "__main__":
    main()
