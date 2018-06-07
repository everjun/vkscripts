from avkentities import *


class Controller(object):
    """docstring for Controller"""

    def start_program(self):
        l1 = input("Enter first link please\n")
        l2 = input("Enter first link please\n")
        searcher = AVKSearcher()
        chain = searcher.get_chain_for(l1, l2)
        print("")
        print(' ->\n'.join(map(str, chain)))
        


if __name__ == '__main__':
    c = Controller()
    c.start_program()