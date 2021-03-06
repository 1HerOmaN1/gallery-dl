# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://rule34.paheal.net/"""

from .common import SharedConfigExtractor, Message
from .. import text


class PahealExtractor(SharedConfigExtractor):
    """Base class for paheal extractors"""
    basecategory = "booru"
    category = "paheal"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    archive_fmt = "{id}"
    root = "http://rule34.paheal.net"

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, self.get_metadata()

        for data in self.get_posts():
            url = data["file_url"]
            for key in ("id", "width", "height"):
                data[key] = text.parse_int(data[key])
            data["tags"] = text.unquote(data["tags"])
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_metadata(self):
        """Return general metadata"""
        return {}

    def get_posts(self):
        """Return an iterable containing data of all relevant posts"""


class PahealTagExtractor(PahealExtractor):
    """Extractor for images from rule34.paheal.net by search-tags"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{tags}"]
    pattern = [r"(?:https?://)?(?:rule34|rule63|cosplay)\.paheal\.net"
               r"/post/list/([^/?&#]+)"]
    test = [("https://rule34.paheal.net/post/list/k-on/1", {
        "url": "c33de1a1470ab29e24ba7a39f53dbf77984be383",
        "keyword": "dcba36cfeedf53387aa9656675307fb9141901f1",
    })]
    per_page = 70

    def __init__(self, match):
        PahealExtractor.__init__(self)
        self.tags = text.unquote(match.group(1))

    def get_metadata(self):
        return {"tags": self.tags}

    def get_posts(self):
        pnum = 1
        while True:
            url = "{}/post/list/{}/{}".format(self.root, self.tags, pnum)
            page = self.request(url).text

            for post in text.extract_iter(
                    page, '<img id="thumb_', '>Image Only<'):
                yield self._extract_data(post)

            if ">Next<" not in page:
                return
            pnum += 1

    @staticmethod
    def _extract_data(post):
        pid , pos = text.extract(post, '', '"')
        data, pos = text.extract(post, 'title="', '"', pos)
        md5 , pos = text.extract(post, '/_thumbs/', '/', pos)
        url , pos = text.extract(post, '<a href="', '"', pos)

        tags, dimensions, size, _ = data.split(" // ")
        width, _, height = dimensions.partition("x")

        return {
            "id": pid, "md5": md5, "tags": tags, "file_url": url,
            "width": width, "height": height,
            "size": text.parse_bytes(size[:-1]),
        }


class PahealPostExtractor(PahealExtractor):
    """Extractor for single images from rule34.paheal.net"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:rule34|rule63|cosplay)\.paheal\.net"
               r"/post/view/(\d+)"]
    test = [("http://rule34.paheal.net/post/view/481609", {
        "url": "2d6c0e28dc2ba3fdd75c807aab297bb973588858",
        "keyword": "da03f47df6878b519717a0ffcfd24e1ec7890987",
        "content": "7b924bcf150b352ac75c9d281d061e174c851a11",
    })]

    def __init__(self, match):
        PahealExtractor.__init__(self)
        self.post_id = match.group(1)

    def get_posts(self):
        url = "{}/post/view/{}".format(self.root, self.post_id)
        page = self.request(url).text

        tags  , pos = text.extract(page, ": ", "<")
        md5   , pos = text.extract(page, "/_thumbs/", "/", pos)
        url   , pos = text.extract(page, "id='main_image' src='", "'", pos)
        width , pos = text.extract(page, "data-width='", "'", pos)
        height, pos = text.extract(page, "data-height='", "'", pos)

        return ({
            "id": self.post_id, "md5": md5, "tags": tags, "file_url": url,
            "width": width, "height": height, "size": 0,
        },)
