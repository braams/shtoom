import twisted.python.components as tpc

# Interfaces

class IPageElement(tpc.Interface):
    "An element of a wizard page"
    help = ''

class IPage(tpc.Interface):
    "A single 'page' in a multi-page wizard"

class IWizard(tpc.Interface):
    "A wizard"
    def start():
        "Called to return the first page"

    def aborted():
        "Called if the user kills the window or aborts it in some other way"

    def completed():
        "Called when the user completes the wizard"

class IWizardDisplayer(tpc.Interface):
    "A user interface capable of displaying a wizard"

# Code

# XXX refactor to use the elements from shtoom.Options!

class PageElement:
    __implements__ = (IPageElement,)
    type = None

class Label(PageElement):
    type = 'Label'
    def __init__(self, name, text, html=None):
        self.name = name
        self.text = text
        self.html = html

class Choice(PageElement):
    type = 'Choice'
    def __init__(self, name, label, choices, default=None, help=None):
        self.name = name
        self.label = label
        self.choices = choices
        self.default = default
        self.help = help

class Text(PageElement):
    type = 'Text'
    def __init__(self, name, label, default='', help=None):
        self.name = name
        self.label = label
        self.default = default
        self.help = help

class Password(Text):
    type = 'Password'

class Boolean(PageElement):
    type = 'Boolean'
    def __init__(self, name, label, default=False, help=None):
        self.name = name
        self.label = label
        self.default = default
        self.help = help

class Tab(PageElement):
    type = 'Tab'
    def __init__(self, name, elements, help=None):
        self.name = name
        self.elements = elements
        self.help = help

class Page:
    __implements__ = (IPage,)
    def __init__(self, title, elements, actions):
        self.title = title
        self.elements = elements
        self.actions = actions

class Wizard:
    __implements__ = (IWizard,)

    def start(self):
        return None

    def aborted(self):
        pass

    def completed(self):
        pass
