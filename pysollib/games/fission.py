#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.settings import TOOLKIT
from pysollib.stack import \
    InitialDealTalonStack, \
    OpenStack, \
    SS_FoundationStack, \
    Stack
from pysollib.util import ANY_SUIT


# ************************************************************************
# * Fission
# ************************************************************************


class Fission_Reserve(OpenStack):

    def acceptsCards(self, from_stack, cards):
        return (from_stack in self.game.s.foundations and
                (len(self.cards) == 0 or
                 self.cards[0].suit == cards[0].suit))

    getBottomImage = Stack._getReserveBottomImage


class Fission_Foundation(SS_FoundationStack):

    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 0:
            return False

        if (self.id >= 7 and
                len(self.game.s.foundations[self.id - 7].cards) > 0):
            return False

        if (self.id < len(self.game.s.foundations) - 7 and
                len(self.game.s.foundations[self.id + 7].cards) > 0):
            return False

        if self.cards[0].suit != cards[0].suit:
            return False

        return SS_FoundationStack.acceptsCards(self, from_stack, cards)

    def canMoveCards(self, cards):
        if self.id < len(self.game.s.foundations) - 7:
            if len(self.game.s.foundations[self.id + 7].cards) > 0:
                return False

        return SS_FoundationStack.canMoveCards(self, cards)

    getBottomImage = Stack._getNoneBottomImage

    def _position(self, card):
        # Foundations overlap vertically (half YS).  Ensure lower rows
        # (higher id) continue to paint above upper rows.
        # Similar to Mahjongg.
        SS_FoundationStack._position(self, card)
        col = self.id % 7
        fnds = self.game.s.foundations
        same_column = [fnds[col + 7 * k] for k in range(7)]
        before = [s for s in same_column if s.id < self.id and s.cards]
        after = [s for s in same_column if s.id > self.id and s.cards]
        if TOOLKIT == 'tk':
            if before:
                self.group.tkraise(before[-1].group)
            if after:
                self.group.lower(after[0].group)
        elif TOOLKIT == 'kivy':
            if before:
                self.group.tkraise(before[-1].group)
            if after:
                self.group.lower(after[0].group)
        elif TOOLKIT == 'gtk':
            # gtk raise/lower not wired; re-stack the whole column
            for k in range(7):
                s = fnds[col + 7 * k]
                if s.cards:
                    s.group.tkraise()


class Fission(Game):
    Hint_Class = None

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        x, y = l.XM, l.YM + 2 * l.YS

        # set window
        w = max(2 * l.XS, x)
        self.setSize(l.XM + w + 7 * l.XS, l.YM + 4 * l.YS)

        # create stacks
        for i in range(7):
            for j in range(7):
                x, y = l.XM + w + j * l.XS, l.YM + i * (l.YS // 2)
                s.foundations.append(Fission_Foundation(x, y, self,
                                                        ANY_SUIT, mod=13))
        x, y = l.XM, l.YM

        # set up spots for final cards
        for i in range(4):
            x, y = l.XM, l.YM + i * l.YS
            s.reserves.append(Fission_Reserve(x, y, self, max_accept=1,
                                              max_cards=13))

        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.s.talon.dealRowAvail(rows=self.s.reserves, frames=2)

    def fillStack(self, stack):
        if stack in self.s.foundations:
            movestacks = []
            checkstack = stack
            while checkstack is not None:
                checkstack = self.s.foundations[checkstack.id - 7]
                if len(checkstack.cards) > 0 and checkstack.id < stack.id:
                    movestacks.append(checkstack)
                else:
                    checkstack = None
            stacks = movestacks[:len(movestacks)//2]
            old_state = self.enterState(self.S_FILL)
            old_busy = self.busy
            self.busy = 1
            self.startDealSample()
            for src in stacks:
                self.moveMove(1, src, self.s.foundations[src.id + 7])
            self.stopSamples()
            self.busy = old_busy
            self.leaveState(old_state)

    def isGameWon(self):
        for f in self.s.foundations:
            if len(f.cards) == 0:
                continue

            if (f.id >= 7 and len(self.s.foundations[f.id - 7].cards) > 0):
                return False

            if (f.id < len(self.s.foundations) - 7 and
                    len(self.s.foundations[f.id + 7].cards) > 0):
                return False

        return Game.isGameWon(self)


# register the game
registerGame(GameInfo(987, Fission, "Fission",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_SKILL))
