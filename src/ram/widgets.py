#!/usr/bin/python

from ram.osutils import getenv

if getenv('RAMUSRIF') == 'shell':
    from ram.shellui import ShellUI as UI
else:
    from ram.snackui import SnackUI as UI

from ram.snackui import ACTION_NONE, ACTION_SET, ACTION_INC, ACTION_DEC


# basic widgets


def VoteText(header, text, buttons, watches=None, reflow=False):
    watches = watches or {}
    return UI().VoteText(header, text, buttons, watches, reflow)


def ActionChoice(header, text, options, watches=None, current=None, timeout=None):
    watches = watches or []
    for index, option in enumerate(options[:]):
        if type(option) == tuple:
            option, item = option
        else:
            option, item = option, option
        options[index] = (option, item)
    return UI().ActionChoice(header, text, options, watches, current, timeout)


def SingleChoice(header, text, options, watches=None, current=None, timeout=None):
    try:
        return ActionChoice(header, text, options, watches, current, timeout)[0]
    except KeyboardInterrupt:
        return current


def ShowError(header, text, buttonText=None):
    return UI().ShowError(header, text, buttonText)


def ShowMessage(header, text, buttonText=None):
    return UI().ShowMessage(header, text, buttonText)


def AskViaButtons(header, text, yesButtonText=None, noButtonText=None):
    return UI().AskViaButtons(header, text, yesButtonText, noButtonText)


def AskEntries(header, text, entries, allowCancel):
    return UI().AskEntries(header, text, entries, allowCancel)


def ShowProgress(header, text, process, length=100):
    return UI().ShowProgress(header, text, process, length)


# extra widgets


def RunMenu(
    header, entries, current=None,
    timeout=None, watches=None,
    text="", doAction=False,
    itemExit=False, itemOnly=False
):
    if not isinstance(itemExit, basestring):
        itemExit = "Continue ..." if itemExit else "Go back ..."

    def __options(entries=entries):
        options = entries() if callable(entries) else entries
        sepexit = [("", (itemExit,))] if options else []
        theexit = (sepexit + [(itemExit, itemExit)]) if not itemOnly else []
        return options + theexit

    def __watch_action(watch):
        action = watches[watch]
        if callable(action):
            for _ in watch:
                action(_)
        elif action:
            for _ in watch:
                pass

    options = __options()
    if current is not None:
        for option, item in options:
            if option == current:
                current = item
                break
    watches = watches if watches is not None else {}

    action = None
    while options:
        try:
            current, action = ActionChoice(
                header, text, options=options, current=current,
                timeout=timeout, watches=watches
            )
        except KeyboardInterrupt:
            if not itemOnly:
                return None
            else:
                action = None
        if not action:
            pass
        elif watches and action in watches:
            __watch_action(action)
        elif callable(current):
            ret = current(action) if doAction else current()
            if ret is not None:
                return ret
        elif current is None or current is itemExit:
            if not itemOnly:
                return None
        options = __options()
        watches = dict((watch, watches[watch]) for watch in watches if watch)


def RunEntry(header, text, entries, initContext=None, allowCancel=True, supplySaved=True, waitCorrect=False):
    titles, saved_values, validators = zip(*entries)
    titles = [title + ":" for title in titles]
    values = saved_values if supplySaved else ["" for _ in saved_values]
    while saved_values:
        items = zip(titles, values)

        try:
            values = AskEntries(header, text, items, allowCancel)
        except KeyboardInterrupt:
            return saved_values

        context = initContext and initContext(*values)

        parsed = []
        errors = []
        for title, value, validate in zip(titles, values, validators):
            if not validate:
                continue
            try:
                parsed += [validate(context, value) if context else validate(value)]
            except ValueError as err:
                errors += [(title.strip('_='), str(msg)) for msg in list(err) or [""]]

        invalid_msgs = ["%s %s" % (title, msg) for (title, msg) in errors if msg]
        if invalid_msgs:
            ShowError("Incorrect input", "\n".join(invalid_msgs), "Ok")

        if not errors:
            return values
        elif not waitCorrect:
            return saved_values


def RunList(entries):
    entries = entries() if callable(entries) else entries

    for entry in entries:
        entry()
