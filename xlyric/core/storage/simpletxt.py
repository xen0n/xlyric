#!/usr/bin/env python
# -*- coding: utf-8 -*-
# xlyric / 核心 / 存储 / 简单文本文件
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

import itertools
import re

from ..lyric import (Lyric, Stanza, StanzaRef, LyricLine, )

STANZA_SEP_RE = re.compile(r'\n{2,}')
TAG_PART_RE = re.compile(r'\s{2,}\((?P<part>[^)]+)\)$')
STANZA_LABEL_CHARS = frozenset('!@#$%^&*')


class SimpleTXTParser(object):
    def parse(self, s):
        lyric_obj = Lyric()
        state = {'part': None, 'labeled_stanzas': {}, }

        stanzas = STANZA_SEP_RE.split(s.strip())
        stanza_objs, labeled_stanzas = [], {}
        for stanza in stanzas:
            stanza_lines = [l.strip() for l in stanza.split('\n')]
            stanza_obj, state = self.parse_stanza(
                    stanza_lines,
                    state,
                    lyric_obj,
                    )
            stanza_objs.append(stanza_obj)

        lyric_obj.stanzas = stanza_objs
        return lyric_obj

    def parse_stanza(self, lines, state, lyric_obj):
        if len(lines) == 1:
            return self.parse_stanza_repetition(lines, state, lyric_obj)

        return self.parse_stanza_simple(lines, state, lyric_obj)

    def parse_line_tag(self, orig_line, state):
        part_match = TAG_PART_RE.search(orig_line)
        if part_match is None:
            return state['part'], orig_line, state

        part_name = part_match.group('part')
        state['part'] = part_name
        return part_name, orig_line[:part_match.start()], state

    def iter_stanza_simple(self, lines, state):
        assert len(lines) % 2 == 0

        orig_lines, xlat_lines = lines[::2], lines[1::2]

        for orig_line, xlat_line in itertools.izip(orig_lines, xlat_lines):
            part, orig_line_processed, state = self.parse_line_tag(
                    orig_line,
                    state,
                    )

            yield LyricLine(
                    orig=orig_line_processed,
                    xlat=xlat_line,
                    part=part,
                    )

    def parse_stanza_simple(self, lines, state, lyric_obj):
        assert len(lines) > 0

        # 本节是否有标记
        stanza_label = lines[0] if lines[0] in STANZA_LABEL_CHARS else None

        simple_lines = lines[0 if stanza_label is None else 1:]
        parsed_lines = list(self.iter_stanza_simple(simple_lines, state))

        stanza_obj = Stanza(parsed_lines, stanza_label, lyric_obj)
        if stanza_label is not None:
            state['labeled_stanzas'][stanza_label] = stanza_obj

        return stanza_obj, state

    def parse_stanza_repetition(self, lines, state, lyric_obj):
        assert len(lines) == 1 and lines[0] in STANZA_LABEL_CHARS

        ref = lines[0]
        # 正确更新当前 part 状态
        # 当前 part 就是被引用 stanza 最后一行的 part
        state['part'] = state['labeled_stanzas'][ref].lines[-1].part

        return StanzaRef(ref, lyric_obj), state


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
