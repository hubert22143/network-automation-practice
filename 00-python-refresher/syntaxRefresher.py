class Animal:
    def __init__(self, ableToWalk: bool, ableToSwim: bool , ableToSpeak: bool, name : str , age : int) -> None:
        self.ableToWalk = ableToWalk
        self.ableToSwim = ableToSwim
        self.ableToSpeak = ableToSpeak
        self.name = name
        self.age = age

    def setAbleToWalk(self,value: bool):
        self.ableToWalk = value

class Dog(Animal):
    def __init__(self, breed: str, can_walk: bool , name : str , age : int) -> None:
        self.breed = breed
        super().__init__(can_walk,True,False,name,age)


my_dog = Dog("Labrador" , True , "Noris" , 19)

print(my_dog.name)