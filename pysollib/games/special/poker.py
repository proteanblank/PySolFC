#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
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
# ---------------------------------------------------------------------------##

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        InitialDealTalonStack, \
        InvisibleStack, \
        OpenTalonStack, \
        ReserveStack, \
        StackWrapper

# ************************************************************************
# * Poker Square
# ************************************************************************


class PokerSquare_RowStack(ReserveStack):
    def clickHandler(self, event):
        if not self.cards:
            self.game.s.talon.playMoveMove(1, self)
            return 1
        return ReserveStack.clickHandler(self, event)

    rightclickHandler = clickHandler


class PokerSquare(Game):
    Talon_Class = OpenTalonStack
    RowStack_Class = StackWrapper(PokerSquare_RowStack, max_move=0)
    Hint_Class = None

    WIN_SCORE = 100
    NUM_RESERVE = 0
    RESERVE_STACK = StackWrapper(ReserveStack, max_cards=5)
    UNSCORED = False

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # create texts 1)
        ta = "ss"
        x, y = l.XM, l.YM + 2*l.YS
        if self.preview <= 1 and not self.UNSCORED:
            t = MfxCanvasText(self.canvas, x, y, anchor="nw",
                              font=self.app.getFont("canvas_default"),
                              text=_('''\
Royal Flush
Straight Flush
4 of a Kind
Full House
Flush
Straight
3 of a Kind
Two Pair
One Pair'''))
            self.texts.list.append(t)
            bb = t.bbox()
            x = bb[1][0] + l.CW * 1.3
            h = bb[1][1] - bb[0][1]
            if h >= 2*l.YS:
                ta = "e"
                t.move(0, -l.YS)
                y = y - l.YS
            t = MfxCanvasText(self.canvas, x, y, anchor="nw",
                              font=self.app.getFont("canvas_default"),
                              text="100\n75\n50\n25\n20\n15\n10\n5\n2")
            self.texts.list.append(t)
            x = t.bbox()[1][0] + l.CW * .6
            self.texts.misc = MfxCanvasText(
                self.canvas, x, y, anchor="nw",
                font=self.app.getFont("canvas_default"),
                text="0\n"*8+"0")
            x = self.texts.misc.bbox()[1][0] + 32

        # set window
        if not self.UNSCORED:
            w = max(2 * l.XS, x, ((self.NUM_RESERVE + 1) * l.XS) + (4 * l.XM))
            self.setSize(l.XM + w + 5 * l.XS + 50, l.YM + 5 * l.YS + 30)
        else:
            w = l.XM
            self.setSize(l.XM + w + 5 * l.XS + 100, l.YM + 5 * l.YS)

        # create stacks
        for i in range(5):
            for j in range(5):
                x, y = l.XM + w + j*l.XS, l.YM + i*l.YS
                s.rows.append(self.RowStack_Class(x, y, self))
        x, y = l.XM, l.YM
        if self.UNSCORED:
            x += (4 * l.YS)
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, anchor=ta)
        s.internals.append(InvisibleStack(self))    # for _swapPairMove()

        for i in range(self.NUM_RESERVE):
            x, y = ((i + 1) * l.XS) + (2 * l.XM), l.YM
            s.reserves.append(self.RESERVE_STACK(x, y, self))

        # create texts 2)
        if self.preview <= 1:
            for i in (4, 9, 14, 19, 24):
                tx, ty, ta, tf = l.getTextAttr(s.rows[i], anchor="e")
                t = MfxCanvasText(self.canvas, tx+8, ty,
                                  anchor=ta,
                                  font=self.app.getFont("canvas_default"))
                self.texts.list.append(t)
            for i in range(20, 25):
                tx, ty, ta, tf = l.getTextAttr(s.rows[i], anchor="ss")
                t = MfxCanvasText(self.canvas, tx, ty, anchor=ta,
                                  font=self.app.getFont("canvas_default"))
                self.texts.list.append(t)
            self.texts.score = MfxCanvasText(
                self.canvas, l.XM, 5*l.YS, anchor="sw",
                font=self.app.getFont("canvas_large"))

        # define hands for scoring
        r = s.rows
        self.poker_hands = [
            r[0:5],  r[5:10], r[10:15], r[15:20], r[20:25],
            (r[0], r[0+5], r[0+10], r[0+15], r[0+20]),
            (r[1], r[1+5], r[1+10], r[1+15], r[1+20]),
            (r[2], r[2+5], r[2+10], r[2+15], r[2+20]),
            (r[3], r[3+5], r[3+10], r[3+15], r[3+20]),
            (r[4], r[4+5], r[4+10], r[4+15], r[4+20]),
        ]
        self.poker_hands = list(map(tuple, self.poker_hands))

        # define stack-groups
        l.defaultStackGroups()
        return l

    #
    # game overrides
    #

    def startGame(self):
        self.moveMove(27 - (5 * self.NUM_RESERVE), self.s.talon,
                      self.s.internals[0], frames=0)
        self.s.talon.fillStack()

    def isBoardFull(self):
        for i in range(25):
            if len(self.s.rows[i].cards) == 0:
                return False
        return True

    def isGameWon(self):
        if self.isBoardFull():
            return self.getGameScore() >= self.WIN_SCORE

        return False

    def getAutoStacks(self, event=None):
        return ((), (), ())

    #
    # scoring
    #

    def updateText(self):
        if self.preview > 1:
            return
        score = 0
        count = [0] * 9
        for i in range(10):
            type, value = self.getHandScore(self.poker_hands[i])
            if 0 <= type <= 8:
                count[type] += 1
            self.texts.list[i+2].config(text=str(value))
            score += value
        t = '\n'.join(map(str, count))
        self.texts.misc.config(text=t)
        #
        t = ""
        if score >= self.WIN_SCORE:
            t = _("WON\n\n")
        if not self.isBoardFull():
            t += _("Points: %d") % score
        else:
            t += _("Total: %d") % score
        self.texts.score.config(text=t)

    def parseGameInfo(self):
        return _("Points: %d") % self.getGameScore()

    def parseStackInfo(self, stack):
        if stack not in self.s.rows:
            return ""
        stackhands = []
        for hand in self.poker_hands:
            if stack in hand:
                stackhands.append(hand)
        row = (stack.id % 5) + 1
        column = (stack.id // 5) + 1
        return (_("Row: %d, Score %d, Column: %d, Score %d") %
                (row, self.getHandScore(stackhands[0])[1], column,
                 self.getHandScore(stackhands[1])[1]))

    def getGameScore(self):
        score = 0
        for hand in self.poker_hands:
            type, value = self.getHandScore(hand)
            score = score + value
        return score

    def getHandScore(self, hand):
        same_rank = [0] * 13
        same_suit = [0] * 4
        ranks = []
        for s in hand:
            if s.cards:
                rank, suit = s.cards[0].rank, s.cards[0].suit
                same_rank[rank] = same_rank[rank] + 1
                same_suit[suit] = same_suit[suit] + 1
                ranks.append(rank)
        #
        straight = 0
        if same_rank.count(1) == 5:
            d = max(ranks) - min(ranks)
            if d == 4:
                straight = 1                # normal straight
            elif d == 12 and same_rank[-4:].count(1) == 4:
                straight = 2                # straight with Ace ranked high
        #
        if max(same_suit) == 5:
            if straight:
                if straight == 2:
                    return 0, 100           # Royal Flush
                return 1, 75                # Straight Flush
            return 4, 20                    # Flush
        #
        if straight:
            return 5, 15                    # Straight
        #
        if max(same_rank) >= 2:
            same_rank.sort()
            if same_rank[-1] == 4:
                return 2, 50                # Four of a Kind
            if same_rank[-1] == 3:
                if same_rank[-2] == 2:
                    return 3, 25            # Full House
                return 6, 10                # Three of a Kind
            if same_rank[-2] == 2:
                return 7, 5                 # Two Pairs
            return 8, 2                     # Pair
        #
        return -1, 0


# ************************************************************************
# * Poker Shuffle
# ************************************************************************

class PokerShuffle_RowStack(ReserveStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        assert len(to_stack.cards) == 1
        self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)


class PokerShuffle(PokerSquare):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(
        PokerShuffle_RowStack, max_accept=1, max_cards=2)

    WIN_SCORE = 200

    def createGame(self):
        PokerSquare.createGame(self)
        if self.s.talon.texts.ncards:
            self.s.talon.texts.ncards.text_format = "%D"

    def startGame(self):
        self.moveMove(27, self.s.talon, self.s.internals[0], frames=0)
        self._startAndDealRow()


# ************************************************************************
# * Poker Square (Waste)
# * Poker Square (1 Reserve)
# * Poker Square (2 Reserves)
# ************************************************************************

class PokerSquareWaste(PokerSquare):
    NUM_RESERVE = 1
    RESERVE_STACK = StackWrapper(ReserveStack, max_cards=5, max_move=0)


class PokerSquare1Reserve(PokerSquare):
    NUM_RESERVE = 1


class PokerSquare2Reserves(PokerSquare):
    NUM_RESERVE = 2


# ************************************************************************
# * Maverick
# ************************************************************************

class Maverick(PokerShuffle):
    UNSCORED = True

    def createGame(self):
        PokerShuffle.createGame(self)
        r = self.s.rows
        self.poker_hands = [r[0:5], r[5:10], r[10:15], r[15:20], r[20:25]]

    def updateText(self):
        if self.preview > 1:
            return

        for i in range(5):
            type, value = self.getHandScore(self.poker_hands[i])
            self.texts.list[i].config(text=self.getNameByScore(value))

    def getNameByScore(self, score):
        scores = {0: "Nothing",
                  2: "One Pair",
                  5: "Two Pair",
                  10: "3 of a Kind",
                  15: "Straight",
                  20: "Flush",
                  25: "Full House",
                  50: "4 of a Kind",
                  75: "Straight Flush",
                  100: "Royal Flush"}
        return scores[score]

    def parseGameInfo(self):
        return ''

    def parseStackInfo(self, stack):
        if stack not in self.s.rows:
            return ""
        stackhand = None
        for hand in self.poker_hands:
            if stack in hand:
                stackhand = hand
        row = (stack.id % 5) + 1
        column = (stack.id // 5) + 1
        return (_("Row: %d, Column: %d, Current hand: %s") %
                (row, column,
                 self.getNameByScore(self.getHandScore(stackhand)[1])))

    def isGameWon(self):
        for i in range(5):
            type, value = self.getHandScore(self.poker_hands[i])
            if value < 15:
                return False
        return True


# register the game
registerGame(GameInfo(139, PokerSquare, "Poker Square",
                      GI.GT_POKER_TYPE | GI.GT_SCORE, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 25}))
registerGame(GameInfo(140, PokerShuffle, "Poker Shuffle",
                      GI.GT_POKER_TYPE | GI.GT_SCORE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_SKILL,
                      si={"ncards": 25}))
registerGame(GameInfo(797, PokerSquareWaste, "Poker Square (Waste)",
                      GI.GT_POKER_TYPE | GI.GT_SCORE, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 30}, rules_filename="pokersquare.html"))
registerGame(GameInfo(798, PokerSquare1Reserve, "Poker Square (1 Reserve)",
                      GI.GT_POKER_TYPE | GI.GT_SCORE, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 30}, rules_filename="pokersquare.html"))
registerGame(GameInfo(799, PokerSquare2Reserves, "Poker Square (2 Reserves)",
                      GI.GT_POKER_TYPE | GI.GT_SCORE, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 35}, rules_filename="pokersquare.html"))
registerGame(GameInfo(817, Maverick, "Maverick",
                      GI.GT_POKER_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 25}))
