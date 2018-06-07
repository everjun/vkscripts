from entities import Searcher, User

import re
import requests
import asyncio
import aiohttp
from datetime import datetime

ACCESS_TOKEN = "0dd424870dd424870dd424874d0db735a000dd40dd4248756dfe8774b08dea0b79e4954"


class AVKUser(User):
    """docstring for VKUser"""

    def __init__(self, id=None, screen_name=None, *args):
        super(AVKUser, self).__init__(*args)
        self.id = id if isinstance(id, int) else None
        self.screen_name = screen_name


    async def get_friends(self):
        if not self.id: await self._get_user_full_info()
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.vk.com/method/friends.get?access_token=%s&user_id=%i&v=5.52' % 
                                    (ACCESS_TOKEN, self.id)) as response:
                response = await response.json()
                
                if "response" in response:
                    items = response["response"]["items"]
                    result = []
                    for item in items:
                        result.append(AVKUser(id=item))
                    return result
                else:
                    return []
                return []


    async def _get_user_full_info(self):
        response = None
        async with aiohttp.ClientSession() as session:
            method = 'https://api.vk.com/method/users.get?access_token=%s&user_ids=%s&fields=screen_name&v=5.52' % \
                                    (ACCESS_TOKEN, self.id if self.id else self.screen_name)
            if method:
                async with session.get(method) as response:
                    user = await response.json()
                    user = user["response"]
                    user = user[0] if user else None
                    if user:
                        self.id = user["id"]
                        self.screen_name = user.get("screen_name", None)
                        self._last_name = user["last_name"]
                        self._first_name = user["first_name"]


    def _get_user_full_info_sync(self):
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
            self._get_user_full_info_sync()
        return self._last_name


    def _get_first_name(self):
        if not self._first_name:
            self._get_user_full_info_sync()
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




class AVKSearcher(Searcher):
    """docstring for VKSearcher"""

    result_list = []

    async def _get_users_friends_and_check(self, list1, list2):
        middle_list = []
        for el1 in list1:
            friends = await el1[1].get_friends()
            lst = el1[0] + [el1[1]]
            for friend in friends:
                if el1[0] and friend != el1[0][-1] or not el1[0]:
                    for el2 in list2:
                        if self.result_list:
                            return
                        elif el2[1] == friend:
                            if self.result_list:
                                return
                            self.result_list += el1[0]
                            self.result_list.append(el1[1])
                            self.result_list.append(friend)
                            self.result_list += el2[0][::-1]
                        else:
                            middle_list.append((lst, friend))
        del list1[:]
        list1 += middle_list 



    def get_chain_for(self, l1, l2):
        st = datetime.now()
        parser = VKLinkParser()
        u1 = parser.parse_link(l1)
        u2 = parser.parse_link(l2)
        if u1 and u2:
            u1 = AVKUser(screen_name=u1)
            u2 = AVKUser(screen_name=u2)
            list1 = [([], u1)]
            list2 = [([], u2)]
            middle_list = []
            loop = asyncio.get_event_loop()
            
            while (not self.result_list):
                print("!")
                tasks = [
                    loop.create_task(self._get_users_friends_and_check(list1, list2)),
                    loop.create_task(self._get_users_friends_and_check(list2, list1))
                ]
                loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
            print((datetime.now() - st).seconds)
            return self.result_list

    


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
        
        
