# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://konachan.com/"""

from . import booru


class KonachanExtractor(booru.MoebooruPageMixin, booru.BooruExtractor):
    """Base class for konachan extractors"""
    category = "konachan"

    def __init__(self, match):
        super().__init__(match)
        self.api_url = "https://konachan.{tld}/post.json".format(
            tld=match.group("tld"))


class KonachanTagExtractor(booru.TagMixin, KonachanExtractor):
    """Extractor for images from konachan.com based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)"]
    test = [
        ("http://konachan.com/post?tags=patata", {
            "content": "838cfb815e31f48160855435655ddf7bfc4ecb8d",
        }),
        ("http://konachan.net/post?tags=patata", None),
    ]


class KonachanPoolExtractor(booru.PoolMixin, KonachanExtractor):
    """Extractor for image-pools from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/pool/show/(?P<pool>\d+)"]
    test = [
        ("http://konachan.com/pool/show/95", {
            "content": "cf0546e38a93c2c510a478f8744e60687b7a8426",
        }),
        ("http://konachan.net/pool/show/95", None),
    ]


class KonachanPostExtractor(booru.PostMixin, KonachanExtractor):
    """Extractor for single images from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post/show/(?P<post>\d+)"]
    test = [
        ("http://konachan.com/post/show/205189", {
            "content": "674e75a753df82f5ad80803f575818b8e46e4b65",
        }),
        ("http://konachan.net/post/show/205189", None),
    ]


class KonachanPopularExtractor(booru.MoebooruPopularMixin, KonachanExtractor):
    """Extractor for popular images from konachan.com"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.(?P<tld>com|net)"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?"]
    test = [
        ("https://konachan.com/post/popular_by_month?month=11&year=2010", {
            "count": 20,
        }),
        ("https://konachan.com/post/popular_recent", None),
        ("https://konachan.net/post/popular_recent", None),
    ]

    def __init__(self, match):
        super().__init__(match)
        self.api_url = (
            "https://konachan.{tld}/post/popular_{scale}.json".format(
                tld=match.group("tld"), scale=self.scale))
