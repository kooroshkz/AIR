# AIR
Someone can change this description
## What to remember when writing code here?
1) All requirements that are needed to run some .py program has to be put in requirements.txt
2) Write test cases for the code that you develop(I can then verify the future integrity of the code with automated testing)
## Where do I write my code?
Write your code as a component in src folder. If you want the final program to use your component then integrate your src folder component to main.py by importing it in main.py.
- For more information read the README in src
## What is main.py?
It runs our whole and complete application. So the end user should be able to run everything in the end with just:
```sh
python main.py
```
## How do I write good code?
Write in snake_case, always include docstrings, etc 
- Just make sure that when you push the file the pylint process doesnt fail
- It only fails if the code that was pushed is not written well
## How to run main.py?
Install the requirements:
```sh
pip install -r requirements.txt
```
Then you can run the application:
```sh
python main.py
```
