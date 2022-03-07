class Singleton:
    instances = {}

    def __new__(cls, classname, parents, arguments):
        new_class = type(classname, parents, arguments)
        if classname not in Singleton.instances:
            Singleton.instances[classname] = new_class()
        
        def __new__(cls, dirname:str = '.'):
            return Singleton.instances[classname]

        new_class.__new__ = __new__

        return new_class