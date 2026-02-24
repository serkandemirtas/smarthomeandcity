from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod 
    def update(self, message): pass # Everyone will implement this method in their own way

class Command(ABC):
    @abstractmethod
    def execute(self): pass # Base structure for commands