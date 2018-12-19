``files`` service
=================

Synopsis
--------

Получение списка конфигурационных файлов управляемых конфигурационных юнитом.

Usage
-----

Обязательным параметром для сервиса ``files`` является имя конфигурационного юнита.
Вызов сервиса возвращает полные пути конфигурационных файлов управляемых юнитом, которые фактически присутствуют в системе:

.. sourcecode:: console

    # ram files sslcert
    /etc/pki/tls/certs/product.crt
    /etc/pki/tls/private/product.key

При использовании python-интерфейса вызов сервиса возвращает список, элементами которого являются полные пути файлов:

.. sourcecode:: pycon

    >>> import ram
    >>> print ram.files('sslcert')
    ['/etc/pki/tls/certs/product.crt', '/etc/pki/tls/private/product.key']


Interface
---------

Для поддержки сервиса ``files`` в юните необходимо добавить одноименный текстовый файл.
В файле необходимо построчно указать маски имен файлов:

.. sourcecode:: pycon

    # cat `ram which smtpwiz files`
    /etc/pki/tls/certs/smtpd.crt
    /etc/pki/tls/private/smtpd.key
    /path/to/product/cert/*.pem


See also
--------

.. toctree::
    :maxdepth: 1

    watch
