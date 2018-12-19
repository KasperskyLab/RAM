``which`` service
=================

Synopsis
--------

Получение списка файлов в составе конфигурационного юнита.

Usage
-----

Обязательным параметром для сервиса ``which`` является имя конфигурационного юнита.
Если иные параметры не указаны, вызов сервиса ``which`` возвращает список всех файлов в составе конфигурационного юнита:

.. sourcecode:: console

    # ram which hostname
    /usr/lib/ram/hostname/about
    /path/to/the/unit/apply.collectd
    /usr/lib/ram/hostname/param
    /usr/lib/ram/hostname/query
    /usr/lib/ram/hostname/apply
    /usr/lib/ram/hostname/input
    /usr/lib/ram/hostname/store

В качестве опциональных аргументов можно указать имена файлов, по которым будет отфильтрован результат вызова.
Если файлов с указанными именами не существует в составе конфигурационного юнита, вывод будет пустым. Код возврата останется нулевым.

.. sourcecode:: console

    # ram which hostname input
    /usr/lib/ram/hostname/input
    # ram which hostname utils.py
    # ram which hostname input param utils.py
    /usr/lib/ram/hostname/input
    /usr/lib/ram/hostname/param

Допускается указание масок имен файлов {shell globs} в качестве имен файлов. Поведение вызова при этом остается неизменным:

.. sourcecode:: console

    # ram which hostname a*
    /usr/lib/ram/hostname/apply
    /path/to/the/unit/apply.collectd
    /usr/lib/ram/hostname/about
    # ram which hostname a* i* o*
    /usr/lib/ram/hostname/apply
    /path/to/the/unit/apply.collectd
    /usr/lib/ram/hostname/about
    /usr/lib/ram/hostname/input

При использовании python-интерфейса вызов сервиса возвращает словарь,
ключом в котором являются имена найденных файлов,
а значением их полные пути:

.. sourcecode:: pycon

    >>> import ram
    >>> import pprint
    >>> pprint.pprint(ram.which('hostname'))
    {'about': '/usr/lib/ram/hostname/about',
     'apply': '/usr/lib/ram/hostname/apply',
     'apply.collectd': '/path/to/the/unit/apply.collectd',
     'input': '/usr/lib/ram/hostname/input',
     'param': '/usr/lib/ram/hostname/param',
     'query': '/usr/lib/ram/hostname/query',
     'store': '/usr/lib/ram/hostname/store'}
    >>> pprint.pprint(ram.which('hostname', 'a*', 'i*', 'o*'))
    {'about': '/usr/lib/ram/hostname/about',
     'apply': '/usr/lib/ram/hostname/apply',
     'apply.collectd': '/path/to/the/unit/apply.collectd',
     'input': '/usr/lib/ram/hostname/input'}


See also
--------

.. toctree::
    :maxdepth: 1

    index
    files
        
