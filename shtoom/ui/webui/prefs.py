## Web prefererence rendering for shtoom.


from nevow import rend
from nevow import tags as T
from nevow import loaders
from nevow import entities
from nevow import inevow
from nevow import flat
from nevow import static
from nevow.url import here
from formless import annotate, webform, iformless

from shtoom import Options

import os

## The stylesheet which is used for all pages.
stylesheet = T.style(type="text/css")["""
@import "css";

body { margin: 0px; font-family: "gill sans" sans-serif; background-color: #f5f5f5; }
h1 { background-color: #dddddd; font-size: large; }
h2 { font-size: medium; }
h1,h2,form,table { padding: 7px; margin: 0px; }
form { background-color: #f5f5f5; }
p { margin: 5px; }
label { margin-left: 5px; cursor: pointer; }

#message {
    margin-bottom: 0.25em;
    padding: 0.25em;
    color: green;
    background-color: #efefef; }

.tab {
    background-color: #f5f5f5; }

.tab-selected {
    background-color: #ccccee;
    text-decoration: underline; }

.tab,.tab-selected {
    cursor: pointer;
    display: inline-block;
    padding: 15px;
    padding-top: 4px;
    padding-bottom: 4px; }

img { border: 0px; }

.header-line {
    white-space: nowrap;
    padding-top: 4px; }

.mode-switch { float: right; }

table { width: 100%; }
th { text-align: left; }
"""]

## A list of preference panes we are interested in viewing on the Advanced page.
interesting = ["identity", "proxy", "register"]


def switcher(ctx, *args):
    """Take any number of (interface, (badgeName, headerText), body) tuples, and return html which
    will render a tabbed widget. There will be a series of tabs, which will each show a badge and some
    header text. Each tab has a body which will be shown when that tab is selected.

    interface: If the avatar cannot be adapted to the given interface, that tab will not be shown.
    badgeName: The name of an image in the /images/ directory which will be rendered
        inside of the tab.
    headerText: The text which will be rendered inside of the tab.
    body: The stan which will be shown when this tab is selected.
    """
    headers, bodies = zip(*args)
    currentView = ctx.arg('currentView', headers[0][1])
    if currentView:
        for (i, (badge, description)) in enumerate(headers):
            if description == currentView:
                currentIndex = i
                break
        else:
            raise Exception("Bad view: %s" % currentView)
    else:
        currentIndex = 0

    def genheaders():
        for i, head in enumerate(headers):
            badge, description = head
            if currentView == description:
                klas = 'tab-selected'
            else:
                klas = 'tab'

            yield T.a(href=here.add('currentView', description))[
                T.span(_class="%s" % klas)[
                    T.img(src="/images/%s.png" % badge, style="margin-right: 5px;"), description]]

    yield T.div(_class="header-line")[ genheaders() ]

    def genbodies():
        style = None
        for i, body in enumerate(bodies):
            def remember(ctx, data):
                ctx.remember([('replace', ['currentView', headers[i][1]], {})], inevow.IViewParameters)
                return ctx.tag

            if currentView != headers[i][1]:
                continue

            yield T.div(id="switch_%s" % i, style=style, render=remember)[
                body ]

    yield T.div(style="margin-top: 4px")[ genbodies() ]


def noDefault(ctx, data):
    return ""
flat.registerFlattener(noDefault, Options._NoDefaultOption)


class PreferencesPage(rend.Page):
    def render_message(self, ctx, _):
        msg = ctx.arg('message')
        if msg is not None:
            return T.div(id="message")[msg]
        return ''

    def render_switcher(self, ctx, allOptions):
        def genSwitchers():
            for opt in allOptions:
                name = opt.getName()
                print name
                if name in interesting:
                    yield ((name, opt.getDescription()), T.invisible(render=self.render_option, data=opt))

        return switcher(ctx, *list(genSwitchers()))

    def render_option(self, ctx, opt):
        optType = type(opt)

        special = {Options.OptionGroup : self.render_optionGroup}
        if optType in special:
            return special[optType]

        bodyRenderer = {
            Options.ChoiceOption: self.render_choiceOption,
            Options.StringOption: self.render_stringOption,
            Options.BooleanOption: self.render_booleanOption,
            Options.NumberOption: self.render_numberOption,
            Options.PasswordOption: self.render_passwordOption
        }.get(optType, "Option type unknown: %s" % (optType, ))

        name = opt.getName()
        desc = opt.getDescription()
        return T.div[T.label(name=name)[T.strong[name], " ", desc], T.div[bodyRenderer]]

    def render_optionGroup(self, ctx, optGroup):
        return T.form(action=("configure_", optGroup.getName()))[
            T.fieldset[
                [T.invisible(render=self.render_option, data=o) for o in optGroup],
                T.input(type="submit")]]

    def render_choiceOption(self, ctx, choice):
        return T.select(name=choice.getName())[[
            T.option(value=x)[x] for x in choice.getChoices()]]

    def render_stringOption(self, ctx, string):
        return T.input(type="string", name=string.getName(), value=string.getValue())

    def render_booleanOption(self, ctx, boolean):
        if boolean.getValue():
            checked = "checked"
        else:
            checked = None
        return (
            T.input(type="checkbox", name=boolean.getName(), checked=checked),
            T.input(type="hidden", name=boolean.getName(), value="off"))

    render_numberOption = render_stringOption

    def render_passwordOption(self, ctx, password):
        return T.input(type="password", name=password.getName())

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Shtoom Settings"],
        stylesheet],
    T.body[
        T.h1[
            T.span(_class="mode-switch")[
                T.a(href="/")[T.span(_class="tab")["Basic"]],
                T.a(href="/advanced/")[T.span(_class="tab-selected")["Advanced"]]],
                "Shtoom Configuration"],
        render_switcher,
        render_message]])

    def childFactory(self, ctx, name):
        if name.startswith('configure_'):
            options = self.original._groupdict[name[len('configure_'):]]
            return Configure((self.original, options))


class Configure(rend.Page):
    def renderHTTP(self, ctx):
        all, mine = self.original
        for O in mine:
            name = O.getName()
            value = ctx.arg(name)
            if value == 'on':
                value = True
            if value == 'off':
                value = False
            if value is not None:
                O.setValue(value)
            else:
                print "VALUE FOR OPTION IS NONE:", name

        all.saveOptsFile()
        inevow.IRequest(ctx).redirect('/?message=Options+Set.')
        return '<html><body>Options set. <a href="/">Go back.</a></body></html>'



def getConfigurationChoices(ctx, data):
    rcd = os.path.expanduser('~/.shtoomrc.d')
    if not os.path.exists(rcd):
        os.mkdir(rcd)
    rv = os.listdir(rcd)
    rv = [x for x in rv if not x.startswith('.')]
    if not rv: return ['No current configurations']
    return rv


class IWizardConfiguration(annotate.TypedInterface):
    currentConfiguration = annotate.Choice(getConfigurationChoices)


labelClick = "document.getElementById(window.event.target.parentNode.getAttribute('for')).click(); true"


currentConfigFilename = os.path.expanduser('~/.shtoomrc.d/.currentConfigName')
class WizardConfiguration(rend.Page):
    __implements__ = IWizardConfiguration, rend.Page.__implements__

    def child_add_config(self, ctx):
        return ConfigurationWizard(self.original)

    def child_advanced(self, ctx):
        return PreferencesPage(self.original)

    child_images = static.File(os.path.join(os.path.dirname(__file__), 'images'))
    child_css = webform.defaultCSS

    def getCurrentConfig(self):
        if os.path.exists(currentConfigFilename):
            return open(currentConfigFilename).read().strip()
        return ''
    def setCurrentConfig(self, new):
        open(currentConfigFilename, 'w').write(new)
        rcname = os.path.expanduser('~/.shtoomrc')
        open(rcname, 'w').write(open(os.path.expanduser('~/.shtoomrc.d/%s' % new)).read())
        self.original.setValue('created_by_wizard', '')
        ## reload app options
        self.original.loadOptsFile()
        print "OPTS LOADED", open(rcname).read()
    currentConfiguration = property(getCurrentConfig, setCurrentConfig)

    def render_currentConfiguration(self, ctx, data):
        eml = self.original.getValue('email_address')
        if eml:
            ctx.fillSlots('current',
                ctx.onePattern('current'
                ).fillSlots('email', eml
                ).fillSlots('host', self.original.getValue('register_uri')))
        else:
            ctx.fillSlots('current', '')
        return ctx.tag

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Shtoom Configuration"],
        stylesheet],
    T.body[
        T.h1[
            T.span(_class="mode-switch")[
                T.a(href="/")[T.span(_class="tab-selected")["Basic"]],
                T.a(href="/advanced/")[T.span(_class="tab")["Advanced"]]],
                "Shtoom Configuration"],
        webform.renderForms(bindingNames=['currentConfiguration'])[
            T.form(pattern='freeform-form',
            action=T.slot('form-action'),
            enctype="multipart/form-data",
            method="POST",
            id=T.slot('form-id'))[
                T.slot('form-arguments'),
                T.span(pattern="binding")[
                    T.strong[T.slot('label')],
                    T.slot('input'),
                    webform.ChoiceRenderer.default_select.clone()(
                        style="margin-left: 15px", pattern="selector", onchange='submit();')]]],
        T.div(render=render_currentConfiguration)[
            T.slot('current')[
                T.table(pattern="current")[
                    T.tr[
                        T.th["Account"], T.th["Host"]],
                    T.tr[
                        T.td[T.slot('email')], T.td[T.slot('host')]]]]],
        T.h1["Add a Configuration"],
        T.form(action="add_config")[
            T.p[
                T.input(type="radio", name="config_type", id="divmod_radio", value="divmod"),
                T.label(_for="divmod_radio", onclick=labelClick)["Divmod account"]],
            T.p[
                T.input(type="radio", name="config_type", id="fwd_radio", value="fwd"),
                T.label(_for="fwd_radio", onclick=labelClick)["Free world dialup account"]],
            T.input(type="submit", name="configure", value="Create configuration")]]])


class IConfigurationWizard(annotate.TypedInterface):
    def divmod(self, req=annotate.Request(), name=annotate.String(label="Configuration Name"), username=annotate.String(), password=annotate.PasswordEntry()):
        """Divmod Account

        Add a configuration for a Divmod account.
        """
        pass
    divmod = annotate.autocallable(divmod, action="Create")

    def fwd(self, req=annotate.Request(), name=annotate.String(label="Configuration Name"), username=annotate.String(), password=annotate.PasswordEntry()):
        """Free World Dialup Account

        Add a configuration for a FWD account.
        """
        pass
    fwd = annotate.autocallable(fwd, action="Create")


class ConfigurationWizard(rend.Page):
    __implements__ = IConfigurationWizard, rend.Page.__implements__
    def render_configBody(self, ctx, data):
        return webform.renderForms(bindingNames=[ctx.arg('config_type')])

    def render_result(self, ctx, data):
        result = inevow.IHand(ctx, default=None)
        if result is not None:
            return result
        return ''

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Configuration Wizard"],
        stylesheet],
    T.body[
        T.span(render=render_result),
        T.h1["Add configuration"],
        render_configBody,
        T.form(action=".")[
            T.input(type="submit", name="cancel", value="Cancel")]]])

    def divmod(self, req, name, username, password):
        self.original.updateOptions(dict(
            username=username,
            email_address="%s@divmod.com" % (username, ),
            register_uri='sip:divmod.com:5060',
            register_user=username,
            register_authuser=username,
            register_authpasswd=password))
        self.pokeOptsFile(name)
        req.setComponent(iformless.IRedirectAfterPost, '/')

    def fwd(self, req, name, username, password):
        self.original.updateOptions(dict(username=username,
            email_address='%s@fwd.pulver.com' % (username, ),
            outbound_proxy_url='sip:fwdnat.pulver.com:5082',
            register_uri='sip:fwd.pulver.com:5060',
            register_authuser=username,
            register_user=username,
            register_authpasswd=password))
        self.pokeOptsFile(name)
        req.setComponent(iformless.IRedirectAfterPost, '/')

    def pokeOptsFile(self, name):
        self.original.saveOptsFile()
        self.original.loadOptsFile()
        self.original.setOptsFile('.shtoomrc.d/%s' % (name, ))
        self.original.saveOptsFile()
        self.original.setOptsFile('.shtoomrc')
        open(currentConfigFilename, 'w').write(name)


class Reloader(rend.Page):
    def locateChild(self, ctx, segments):
        from shtoom.ui.webui import prefs
        reload(prefs)
        return prefs.WizardConfiguration(self.original), segments
