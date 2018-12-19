#!/usr/bin/python


class Results(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, _results):
        raise NotImplementedError()


class DumbResults(Results):
    def __init__(self, **kwargs):
        pass

    def __call__(self, _results):
        return iter(())


class Service(object):
    defaults = dict()
    _results = Results()

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def _service(self, *args, **kwargs):
        return self(*args, **kwargs)

    def _iterate(self, *args, **kwargs):
        _options = dict(self.defaults, **kwargs)
        _results = self._results(**_options)
        return _results(self._service(*args, **kwargs))


# ----


class ListResults(Results):
    def __init__(self, **kwargs):
        pass

    def __call__(self, _results):
        if _results is None:
            _results = ()

        return iter(map(str, _results))


class LineResults(Results):
    def __init__(self, **kwargs):
        self.strip = kwargs.pop('strip', False)

    def __call__(self, _results):
        if _results is None:
            _results = ""

        for body, line in enumerate(_results.splitlines()):
            yield line.strip() if self.strip else line.rstrip()


class DictResults(Results):
    def __init__(self, **kwargs):
        self.names = kwargs.pop('names', True)
        self.width = kwargs.pop('width', 0)

    def __call__(self, _results):
        _width = (
            self.width if self.width else
            max(len(_) for _ in _results) if _results else
            0
        )

        for key in sorted(_results):
            if self.names:
                yield "%-*.*s %s" % (_width, _width, key, _results[key])
            else:
                yield "%s" % (_results[key])


class ReprResults(Results):
    def __init__(self, **kwargs):
        pass

    def __call__(self, _results):
        if _results is None:
            _results = ""

        return iter(str(_results).splitlines())


class IterResults(Results):
    def __init__(self, **kwargs):
        pass

    def __call__(self, _results):
        if _results is None:
            _results = ()

        for _ in _results:
            yield str(_)
