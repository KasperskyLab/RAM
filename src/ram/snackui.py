#!/usr/bin/python

import snack


ACTION_NONE = 0
ACTION_SET = 1
ACTION_INC = 2
ACTION_DEC = 3


more_hotkeys = {
    "+":        ord('+'),
    "-":        ord('-'),
    "LEFT":     0x8000 + 4,
    "RIGHT":    0x8000 + 5,
}


for n in more_hotkeys.keys():
    more_hotkeys[more_hotkeys[n]] = n

snack.hotkeys.update(more_hotkeys)


TEXT_WIDTH=72
EDIT_WIDTH=52

FLEX_DOWN=12
FLEX_UP=0


def _SnackWindow(screen, header, text, items):
    form = snack.GridForm(screen, header, 1, items + 1)
    if text:
        tbox = snack.TextboxReflowed(
            width=TEXT_WIDTH, text=text,
            maxHeight=screen.height - 12,
            flexDown=32, flexUp=0
        )
        form.add(tbox, 0, 0, padding=(0, 0, 0, 1))

    return form


def _ButtonsWindow(screen, header, text, buttons):
    form = _SnackWindow(screen, header, text, 1)

    btns = snack.ButtonBar(screen, buttons)
    form.add(btns, 0, 1, growx = 1)

    return btns.buttonPressed(form.runOnce())


def _EntryWindow(screen, header, text, entries, buttons):
    btns = snack.ButtonBar(screen, buttons)
    form = _SnackWindow(screen, header, text, 2)

    entries = [e if isinstance(e, tuple) else (e, "") for e in entries]

    entryList = []
    for label, entry in entries:
        if label.startswith('_'):
            _label = snack.Label(label[1:])
            _entry = snack.Entry(EDIT_WIDTH, entry, password=True)
        elif label.startswith('='):
            _label = snack.Label(label[1:])
            _entry = snack.Entry(EDIT_WIDTH, entry)
            _entry.setFlags(snack.FLAG_DISABLED, snack.FLAGS_SET)
        else:
            _label = snack.Label(label[0:])
            _entry = snack.Entry(EDIT_WIDTH, entry)
        entryList.append((_label, _entry))

    grid = snack.Grid(2, len(entryList))
    for index, (label, entry) in enumerate(entryList):
        grid.setField(label, 0, index, padding=(0, 0, 1, 0), anchorLeft=1)
        grid.setField(entry, 1, index, anchorLeft=1)

    form.add(grid, 0, 1, padding=(0, 0, 0, 1))
    form.add(btns, 0, 2, growx=1)

    if buttons[1:]:
        form.addHotKey('ESC')
    result = form.runOnce()
    values = [entry.value() for label, entry in entryList]

    if result == 'F12':
        return values
    elif (btns.buttonPressed(result) == buttons[0].lower()):
        return values
    else:
        raise KeyboardInterrupt()


import os
import sys

import ram.options


_errpt = ram.options['errpt']


class SnackUI(object):
    __screen = None
    __stdout = []

    def __init__(self):
        with self:
            pass

    def __enter__(self):
        od = os.dup(sys.stdout.fileno())
        self.__stdout.append(od)

        try:
            if _errpt:
                raise OSError()
            nd = os.open('/dev/tty', os.O_WRONLY)
        except OSError:
            nd = os.dup(sys.stderr.fileno())

        os.dup2(nd, sys.stdout.fileno())
        os.close(nd)

        self.__screen = snack.SnackScreen()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__screen.finish()

        od = self.__stdout.pop()

        os.dup2(od, sys.stdout.fileno())
        os.close(od)

    def __GetWidgetBounds(self, ndelta=0, nlines=None, text=None):
        width = max(80, self.__screen.width) - 10
        height = max(25, self.__screen.height) - 8 - ndelta

        if not nlines and text:
            ulines = (line.decode('utf-8') for line in text.splitlines())
            nlines = sum((len(line) / width) + 1 for line in ulines)

        if height <= 0:
            raise ValueError("unable to create widget of required size")
        elif nlines is None or height < nlines:
            return width, height, True
        else:
            return width, nlines, False

    def AskEntries(self, header, text, entries, allowCancel):
        if not entries:
            raise ValueError("non-emtpy iterable required")
        buttonText = ['Ok', 'Cancel'] if allowCancel else ['Ok']
        with self:
            return _EntryWindow(self.__screen, header, text, entries, buttonText)

    def AskViaButtons(self, header, text, yesButtonText=None, noButtonText=None):
        if not yesButtonText:
            yesButtonText, noButtonText = 'Yes', 'No'
        elif not noButtonText:
            noButtonText = 'Cancel'
        with self:
            pressed = _ButtonsWindow(
                self.__screen,
                header, text,
                [yesButtonText, noButtonText],
            )
            return (pressed == yesButtonText.lower())

    def ShowMessage(self, header, text, buttonText=None):
        if not buttonText:
            buttonText = 'Ok'
        with self:
            _ButtonsWindow(
                self.__screen,
                header, text,
                [buttonText],
            )

    def ShowError(self, header, text, buttonText=None):
        self.ShowMessage(header, text, buttonText)

    def VoteText(self, header, text, buttons=None, watches=None, reflow=False):
        if not buttons:
            buttons = ['Ok']
        if watches is None:
            watches = {}
        with self:
            btnsbar = snack.ButtonBar(self.__screen, buttons)
            form = snack.GridForm(self.__screen, header, 1, 2)
            if text and reflow:
                textbox = snack.TextboxReflowed(width=TEXT_WIDTH, text=text, flexDown=FLEX_DOWN, flexUp=FLEX_UP)
                form.add(textbox, 0, 0, padding=(0, 0, 0, 1))
            elif text:
                width, height, scroll = self.__GetWidgetBounds(5, text=text)
                textbox = snack.Textbox(width, height, text=text, scroll=scroll, wrap=True)
                form.add(textbox, 0, 0, padding=(0, 0, 0, 1))
            form.add(btnsbar, 0, 1, padding=(0, 0, 0, 0))
            for watch in watches:
                form.form.watchFile(watch, 1)
            ret = form.runOnce()
            if btnsbar.buttonPressed(ret):
                return btnsbar.buttonPressed(ret)
            elif ret in watches:
                return watches[ret]
            else:
                return None

    def ActionChoice(self, header, text, options, watches=None, current=None, timeout=None):
        if watches is None:
            watches = []
        with self:
            text, text_width, text_height = snack.reflow(text, width=TEXT_WIDTH, flexDown=FLEX_DOWN, flexUp=FLEX_UP)
            width, height, scroll = self.__GetWidgetBounds(text_height, nlines=len(options))
            items_width = [len(option) for option, item in options]
            scrolled = 3 if scroll else 0
            width = min(TEXT_WIDTH, max(items_width) + scrolled if items_width else TEXT_WIDTH)
            listbox = snack.Listbox(height, scroll=scroll, width=width, returnExit=1)
            for option, item in options:
                listbox.append(option, item)
            if current is not None:
                try:
                    listbox.setCurrent(current)
                except KeyError:
                    pass
            form = snack.GridForm(self.__screen, header, 1, 2)
            if text:
                textbox = snack.Textbox(width=text_width, height=text_height, text=text)
                form.add(textbox, 0, 0, padding=(0, 0, 0, 1))
            form.add(listbox, 0, 1)
            for watch in watches:
                form.form.watchFile(watch, 1)
            if timeout is not None:
                form.form.setTimer(timeout)
            form.addHotKey('ESC')
            form.addHotKey('+')
            form.addHotKey('-')
            form.addHotKey('LEFT')
            form.addHotKey('RIGHT')
            ret = form.runOnce()
            if ret is listbox:
                return listbox.current(), ACTION_SET
            elif ret == 'TIMER':
                return listbox.current() if options else None, None
            elif ret in watches:
                return listbox.current() if options else None, watch
            elif ret == 'F12':
                return listbox.current() if options else None, ACTION_SET
            elif ret == 'ESC':
                raise KeyboardInterrupt()
            elif ret == '-' or ret == 'LEFT':
                return listbox.current() if options else None, ACTION_DEC
            elif ret == '+' or ret == 'RIGHT':
                return listbox.current() if options else None, ACTION_INC
            else:
                raise NotImplementedError("Unexpected return value from form.runOnce: %s" % ret)

    def ShowProgress(self, header, text, process, length):
        with self:
            form = _SnackWindow(self.__screen, header, text, 1)

            scale = snack.Scale(width=TEXT_WIDTH, total=100)
            form.add(scale, 0, 1)

            for complete in process:
                scale.set(complete * 100 / length)
                form.draw()
                self.__screen.refresh()
            self.__screen.popWindow()
