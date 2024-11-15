def component_says_hello():
    """ Always write docstrings """
    return "Hello"

if __name__ == "__main__":
    # This is so that you can run it locally with python src/example.py 
    print("Running locally")
    print(component_says_hello())
