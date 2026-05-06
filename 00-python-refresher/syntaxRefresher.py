class Animal:
    def __init__(self, able_to_walk: bool, able_to_swim: bool, able_to_speak: bool, name: str, age: int) -> None:
        self.able_to_walk = able_to_walk
        self.able_to_swim = able_to_swim
        self.able_to_speak = able_to_speak
        self.name = name
        self.age = age

    def set_able_to_walk(self, value: bool) -> None:
        self.able_to_walk = value


class Dog(Animal):
    def __init__(self, breed: str, can_walk: bool, name: str, age: int) -> None:
        self.breed = breed
        super().__init__(can_walk, True, False, name, age)

    def bark(self) -> None:
        print("Woof")


my_dog = Dog("Labrador", True, "Noris", 19)

print(my_dog.name)
my_dog.bark()
