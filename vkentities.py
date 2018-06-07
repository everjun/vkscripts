from entities import Searcher, User
from datetime import datetime
import re
import requests

ACCESS_TOKEN = "0dd424870dd424870dd424874d0db735a000dd40dd4248756dfe8774b08dea0b79e4954"


class VKUser(User):
    """docstring for VKUser"""

    def __init__(self, id=None, screen_name=None, *args):
        super(VKUser, self).__init__(*args)
        self.id = id if isinstance(id, int) else None
        self.screen_name = screen_name


    def get_friends(self):
        if not self.id: self._get_user_full_info()
        response = requests.get('https://api.vk.com/method/friends.get?access_token=%s&user_id=%i&v=5.52' % 
                                    (ACCESS_TOKEN, self.id))
        response = response.json()
        
        if "response" in response:
            items = response["response"]["items"]
            result = []
            for item in items:
                result.append(VKUser(id=item))
            return result
        else:
            return []
        return []


    def _get_user_full_info(self):
        response = None
        if self.id:
            response = requests.get('https://api.vk.com/method/users.get?access_token=%s&user_ids=%i&fields=screen_name&v=5.52' % 
                                    (ACCESS_TOKEN, self.id))
        elif self.screen_name:
            response = requests.get('https://api.vk.com/method/users.get?access_token=%s&user_ids=%s&fields=screen_name&v=5.52' %
                                    (ACCESS_TOKEN, self.screen_name))
        if response:
            user = response.json()["response"]
            user = user[0] if user else None
            if user:
                self.id = user["id"]
                self.screen_name = user.get("screen_name", None)
                self._last_name = user["last_name"]
                self._first_name = user["first_name"]


    def _get_last_name(self):
        if not self._last_name:
            self._get_user_full_info()
        return self._last_name


    def _get_first_name(self):
        if not self._first_name:
            self._get_user_full_info()
        return self._first_name

    last_name = property(_get_last_name)
    first_name = property(_get_first_name)


    def __str__(self):
        return '%s %s (http://vk.com/id%i)' % (self.first_name,
                                               self.last_name,
                                               self.id)


    def __eq__(self, other):
        if other:
            if not self.id:
                self._get_user_full_info()
            if not other.id:
                other._get_user_full_info()
            return self.id == other.id




class VKSearcher(Searcher):
    """docstring for VKSearcher"""
    def get_chain_for(self, l1, l2):
        st = datetime.now()
        parser = VKLinkParser()
        u1 = parser.parse_link(l1)
        u2 = parser.parse_link(l2)
        if u1 and u2:
            u1 = VKUser(screen_name=u1)
            u2 = VKUser(screen_name=u2)
            list1 = [([], u1)]
            list2 = [([], u2)]
            middle_list = []

            i = 0
            finded = []
            while not finded and i < 10:
                for i1, user1 in list1:
                    l = i1 + [user1]
                    friends = user1.get_friends()
                    u = i1[-1] if i1 else None
                    if u in friends:
                        friends.remove(u)
                    middle_list += [(l, f) for f in friends]
                    for friend in friends:
                        for i2, user2 in list2:

                            if user2 == friend:
                                finded = i1
                                finded.append(user1)
                                finded.append(user2)
                                finded += i2[::-1]
                                break
                        if finded: break
                    if finded: break
                if finded: break
                i += 1
                list1 = middle_list
                middle_list = []
                for i2, user2 in list2:
                    l = i2 + [user2]
                    friends = user2.get_friends()
                    u = i2[-1] if i2 else None
                    if u in friends:
                        friends.remove(u)
                    middle_list += [(l, f) for f in friends]
                    for friend in friends:
                        for i1, user1 in list1:
                            if user1 == friend:
                                finded = i1
                                finded.append(user1)
                                finded.append(user2)
                                finded += i2[::-1]
                                break
                        if finded: break
                    if finded: break
                list2 = middle_list
                middle_list = []
                i += 1
        print((datetime.now() - st).seconds)
        return finded
    


class VKLinkParser:
    """docstring for VKLinkParser"""

    vklink_regexp = r'https{0,1}://(m[.]){0,1}vk[.]com/.*'
    screen_name_regexp = r'/[^/]*$'

    def parse_link(self, link):
        if re.match(self.vklink_regexp, link):
            result = re.search(self.screen_name_regexp, link)
            result = result.group(0)[1:]
            return result
        else:
            return None
        
        
