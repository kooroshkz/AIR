## What is src?
src contains all of the files(components) that the main.py can execute

## But what if I am working on SST or something else and I dont want to run main.py because it has someone elses code in it and I dont want to change it?
If you want to run the component you made locally you can just run the file in the directly here in src and add into the file the section:
```py
if __name__ = "__main__": etc...
```
and then 
```sh
python mycomponentthatisinrsc.py
```
## Should I make a new requirements.txt here?
No. Put all of the dependencies any of your components might have in the root directory requirements.txt.

## Can I create directories here?
Only if it would increase the readability of the src folder.
So if you have 3 or more files that are related you can move them to their own subfolder here. eg) you have sst.py which depends on conversion.py and speech.py so then you can move both of them to their own folder called sst

