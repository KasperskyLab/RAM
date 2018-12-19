#!/usr/bin/python

import os
from collections import OrderedDict


class TabSeparatedFile(object):
    def __init__(self, filename, num_of_entries):
        self.filename = filename
        self.nentries = num_of_entries

    def __iter__(self):
        for line in open(self.filename):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line += "\t" * self.nentries
            nsplit = self.nentries-1 if self.nentries else 0
            yield [line] + [item.strip() for item in line.split("\t", nsplit)[:self.nentries]]


def ParseCountryFile(zoneinfo):
    for line, code, country in TabSeparatedFile(os.path.join(zoneinfo, 'iso3166.tab'), 2):
        if code and country:
            yield code, country
        else:
            raise ValueError("Country file at %s has invalid line: %s" % (zoneinfo, line))


def ParseZoneFile(zoneinfo):
    for line, code, coords, tz, comments in TabSeparatedFile(os.path.join(zoneinfo, 'zone.tab'), 4):
        if code and coords and tz:
            yield code, coords, tz, comments
        else:
            raise ValueError("Zone file at %s has invalid line: %s" % (zoneinfo, line))


def IsValidTimezone(zoneinfo, tz):
    filename = os.path.join(zoneinfo, tz)
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            if 'TZif' == f.read(4):
                return True
    return False


def GetSpecialTimezones(zoneinfo):
    area = 'Etc'
    areazones = OrderedDict()
    for filename in sorted(os.listdir(os.path.join(zoneinfo, area))):
        tz = os.path.join(area, filename)
        if IsValidTimezone(zoneinfo, tz):
            areazones[tz] = tz
    return OrderedDict({"Special area (Etc)": areazones}) if areazones else OrderedDict()


def GetCountryTimezones(zoneinfo):
    timezones = OrderedDict()
    # regular timezones
    code_country = dict(ParseCountryFile(zoneinfo))
    for code, coords, tz, comments in ParseZoneFile(zoneinfo):
        if not IsValidTimezone(zoneinfo, tz):
            raise ValueError("Invalid time zone file '%s'" % tz)
        country = code_country[code]
        prompt = comments if comments else tz
        timezones.setdefault(country, OrderedDict())[tz] = prompt
    return timezones


def GetAvailableTimezones(zoneinfo):
    timezones = GetSpecialTimezones(zoneinfo)
    countrytz = GetCountryTimezones(zoneinfo)
    for country in sorted(countrytz):
        timezones[country] = countrytz[country]
    return timezones


