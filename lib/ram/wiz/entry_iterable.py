#!/usr/bin/python

import ram.widgets


def RunDictEntry(
    header, text, title, values,
    format_fn=None, filter_fn=None,
    create_fn=None,
    modify_fn=None, switch_fn=None,
    itemExit=False
):
    values = values[:]

    modify_fn = modify_fn or switch_fn

    def __modify_fn(index):
        if not modify_fn:
            return

        _value = modify_fn(values[index])
        if not _value:
            del values[index]
        elif _value != values[index]:
            values[index] = _value

    def __switch_fn(index):
        if not switch_fn:
            return

        _value = switch_fn(values[index])
        if not _value:
            del values[index]
        elif _value != values[index]:
            values[index] = _value

    def __create_fn():
        value = None
        if create_fn:
            value = create_fn(values)

        if value:
            values.append(value)

    def __format_fn(index):
        return (
            format_fn(values[index]) if format_fn else
            values[index]
        )

    def __filter_fn(index):
        return (
            filter_fn(values[index]) if filter_fn else
            True
        )

    def __values_fn():
        return xrange(len(values))

    RunDictIndex(
        header,
        text=text,
        title=title,
        values_fn=__values_fn,
        format_fn=__format_fn,
        filter_fn=__filter_fn,
        create_fn=__create_fn,
        modify_fn=__modify_fn,
        switch_fn=__switch_fn,
        itemExit=itemExit,
    )

    return values


def RunListEntry(header, text, title, values, validate, itemExit=False):
    def DelListEntry(value, title):
        if not ram.widgets.AskViaButtons(
            "Remove %s" % title,
            "Would you like to remove `%s`?" % value
        ):
            return value

    def NewListEntry(validate, title):
        value, = ram.widgets.RunEntry(
            "Add %s" % title,
            "",
            [(title, "", validate)]
        )

        return value

    def __create_fn(values, validate=validate, title=title):
        return NewListEntry(validate, title)

    def __modify_fn(value, title=title):
        return DelListEntry(value, title)

    def __switch_fn(value, title=title):
        value, = ram.widgets.RunEntry(
            "Edit %s" % title,
            "",
            [(title, value, validate)]
        )

        return value


    return RunDictEntry(
        header,
        text,
        title,
        values,
        create_fn=__create_fn,
        modify_fn=__modify_fn,
        switch_fn=__switch_fn,
        itemExit=itemExit
    )


def RunDictIndex(
    header, text, title, values_fn,
    format_fn=None, filter_fn=None, header_fn=None,
    create_fn=None, modify_fn=None, switch_fn=None,
    handle_fn=None,
    timeout=None, watches=None,
    itemExit=False
):
    actions = {}

    modify_fn = modify_fn or switch_fn

    def __handle_fn(value, action):
        if handle_fn:
            return handle_fn(value)
        elif action == ram.widgets.ACTION_SET:
            if modify_fn:
                return modify_fn(value)
        else:
            if switch_fn:
                return switch_fn(value)

    def __format_fn(value):
        return format_fn(value) if format_fn else str(value)

    def __filter_fn(value):
        return filter_fn(value) if filter_fn else True

    def __mk_action(value):
        return lambda action, value=value: __handle_fn(value, action)

    def __mk_option(value):
        return (
            __format_fn(value),
            actions.setdefault(value, __mk_action(value))
        )

    def __create_fn(action):
        if action == ram.widgets.ACTION_SET:
            create_fn()

    def __gen_items():
        values = values_fn()

        _header = [
            (header_fn(), header_fn()),
            ("", ""),
        ] if header_fn else []

        _spacer = [
            ("", 0)
        ] if create_fn and values else []

        _create = [
            ("New ...", __create_fn),
        ] if create_fn else []

        options = [__mk_option(value) for value in values if __filter_fn(value)]

        return _header + options + _spacer + _create


    return ram.widgets.RunMenu(
        header,
        __gen_items,
        text=text,
        timeout=timeout,
        watches=watches,
        doAction=True,
        itemExit=itemExit,
    )
