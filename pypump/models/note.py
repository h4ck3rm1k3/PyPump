##
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from datetime import datetime
from dateutil.parser import parse

from pypump.exception.ImmutableException import ImmutableException
from pypump.exception.PumpException import PumpException

from pypump.compatability import *

from pypump.models import (AbstractModel, Postable, Likeable, Shareable, 
                           Commentable, Deleteable)

@implement_to_string
class Note(AbstractModel, Postable, Likeable, Shareable, Commentable, Deleteable):
    
    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(
            username=self._pump.nickname
            )


    id = ""
    content = ""
    updated = None # last time this was updated
    published = None # When this was published
    deleted = False # has the note been deleted
    liked = False
    author = None

    _links = dict()

    def __init__(self, content, id=None, published=None, updated=None, 
                 links=None,  deleted=False, liked=False, author=None,
                 *args, **kwargs):

        super(Note, self).__init__(*args, **kwargs)

        self._links = links if links else dict()

        self.id = id if id else None
        self.content = content

        if published:
            self.published = published
        else:
            self.published = datetime.now()

        if updated:
            self.updated = updated
        else:
            self.updated = self.published

        self.deleted = deleted
        self.liked = liked
        self.author = self._pump.me if author is None else author


    def serialize(self):
        """ Convers the post to JSON """
        data = super(Note, self).serialize()
        data.update({
            "verb":"post",
            "object":{
                "objectType":self.objectType,
                "content":self.content,
            }
        })

        return data

    def __repr__(self):
        return "<{type} by {name}>".format(
            type=self.TYPE,
            name=self.author.webfinger
            )
   
    def __str__(self):
        return str(repr(self))

    @classmethod
    def unserialize(cls, data, obj=None):
        """ Goes from JSON -> Note object """
        cls.debug("unserialize({params})", params={"cls": cls, "data": data, "obj": obj})

        id = data.get("id", None)
        content = data.get("content", u"")

        links = dict()
        for i in ["likes", "replies", "shares"]:
            if data.get(i, None):
                if "pump_io" in data[i]:
                    links[i] = data[i]["pump_io"]["proxyURL"]
                else:
                    links[i] = data[i]["url"]

        updated=parse(data["updated"])
        published=parse(data["published"])
        liked = data["liked"] if "liked" in data else False
        deleted = parse(data["deleted"]) if "deleted" in data else False
        author = cls._pump.Person.unserialize(data["author"]) if "author" in data else None

        if obj is None:
            return cls(
                    id=id,
                    content=content,
                    to=(), # todo still.
                    cc=(), # todo: ^^
                    updated=updated,
                    published=published,
                    links=links,
                    liked=liked,
                    deleted=deleted,
                    author=author,
                    )
        else:
            obj.content = content
            obj.id = id
            obj.updated = updated
            obj.published = published
            obj._links = links
            obj.liked = liked
            obj.deleted = deleted
            obj.author = author if author else obj.author
            return obj
