#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------#

# imports

# PySol imports
# from pysollib.mfxutil import KwStruct
# from pysollib.settings import TITLE

# Toolkit imports
# from tkconst import EVENT_HANDLED
# from tkwidget import MfxDialog

# ************************************************************************
# *
# ************************************************************************

solver_dialog = None


def create_solver_dialog(parent, game):
    pass


def connect_game_solver_dialog(game):
    pass


def raise_solver_dialog(game):
    pass


def unraise_solver_dialog():
    pass


def destroy_solver_dialog():
    global solver_dialog
    solver_dialog = None


def reset_solver_dialog():
    pass
