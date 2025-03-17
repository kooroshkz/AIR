from typing import Any, Dict


class GlobalModelState:
    def __init__(self) -> None:
        # the attributes are being stored as a dictionary because I couldnt think of a better way to "Null" initialize them
        # also this kinda lets the object have a dynamic set of attributes
        # also makes for easier visualizations for the object, which will be
        # useful when building a more intuitive ui for them
        self.__attributes: Dict[str, Any] = {}

    def set_attr(self, name : str, val : Any):
        #set a variable which doesent already have a setter
        #risky because since keys are strings you may be setting a variable which was already set
        self.__attributes[name] = val
        print(f"\033[92;1m[LUIS]\033[0m {name} set to {val}")
        print(self.__attributes)

    def __bool__(self):
        # returns false if we currently dont have a model state
        # meaning that the biologist hasnt yet finalized what their final
        # pipeline stage will look like
        pass
