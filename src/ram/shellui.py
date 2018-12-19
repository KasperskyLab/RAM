#!/usr/bin/python

import sys
import getpass

class ShellUI(object):
    def __init__(self, keep=False):
        pass

    def AskViaButtons(self, header, text, yesButtonText=None, noButtonText=None):
        raise NotImplementedError("AskViaButtons is not implemented for this widgets.")

    def AskEntries(self, header, text, entries, allowCancel):
        print >> sys.stderr, text
        answers = []
        for label, entry in entries:
            if label.startswith('_'):
                if sys.stdin.isatty():
                    answers.append(getpass.getpass("%s " % label[1:]))
                else:
                    answers.append(raw_input("%s " % label[1:]))
            elif label.startswith('='):
                print >> sys.stderr, "%s %s" % (label[1:], entry)
                answers.append(entry)
            else:
                answers.append(raw_input("%s " % label))
        return answers

    def ShowError(self, header, text, buttonText=None):
        print >> sys.stderr, text.strip()

    def ShowMessage(self, header, text, buttonText=None):
        print >> sys.stderr, text.strip()

    def VoteText(self, header, text, buttons=None, watches=None):
        raise NotImplementedError("ButtonChoice is not implemented for this widgets.")

    def ActionChoice(self, header, text, options, watches=None, current=None, timeout=None):
        raise NotImplementedError("ActionChoice is not implemented for this widgets.")

    def ShowProgress(self, header, text, process, length):
        raise NotImplementedError("ShowProgress is not implemented for this widgets.")
