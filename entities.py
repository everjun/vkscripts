class User:
    """Generic for User"""

    def __init__(self, last_name='', first_name=''):
        self._last_name = last_name
        self._first_name = first_name


    def get_friends(self):
        return []

        

class Searcher:

    def get_chain_for(self, string1, string2):
        return []
