#!/usr/bin/env python
# -*- coding: utf-8 -*-
# xlyric / 核心 / 歌词 / 包
#
# Copyright (C) 2015 Wang Xuerui
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import weakref


class Lyric(object):
    def __init__(self, stanzas=[]):
        self.stanzas = stanzas

    @property
    def stanzas(self):
        return self._stanzas

    @stanzas.setter
    def stanzas(self, val):
        self._stanzas = val
        self._stanza_label_idx = self._generate_label_index(val)

    def stanza_from_label(self, label):
        # 因为是 weakref.ref 引用, 所以要调用一次才能解出对象
        return self._stanza_label_idx[label]()

    def _generate_label_index(self, stanzas):
        return {
                stanza.label: weakref.ref(stanza)
                for stanza in stanzas
                if isinstance(stanza, Stanza)
                    and stanza.label is not None
                }

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        repr_stanzas = ', '.join(repr(stanza) for stanza in self.stanzas)
        return '<Lyric: stanzas=[{}]>'.format(repr_stanzas)


class BaseStanza(object):
    pass


class StanzaRef(BaseStanza):
    def __init__(self, label, lyric=None):
        self.label = label
        self.lyric = weakref.ref(lyric)

    @property
    def ref(self):
        return self.lyric().stanza_from_label(self.label)

    @property
    def lines(self):
        return self.ref.lines

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return "<StanzaRef: reference to {}>".format(repr(self.ref))


class Stanza(BaseStanza):
    def __init__(self, lines, label=None, lyric=None):
        self.lines = lines
        self.label = label
        self.lyric = weakref.ref(lyric)

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return '<Stanza: label={}, {} line(s)>'.format(
                'n/a' if self.label is None else "'{}'".format(self.label),
                len(self.lines),
                )


class LyricLine(object):
    def __init__(self, orig, xlat, part=None):
        self.orig = orig
        self.xlat = xlat
        self.part = part

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return "<LL: '{}' -> '{}' (part={})>".format(
                self.orig,
                self.xlat,
                self.part,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
