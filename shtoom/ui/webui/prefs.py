## Web prefererence rendering for shtoom.


from nevow import rend
from nevow import tags as T
from nevow import loaders
from nevow import entities
from nevow import inevow
from nevow import flat
from nevow import static
from formless import annotate, webform, iformless

from shtoom import Options

import os


def switcher(*args):
    """Take any number of (interface, (badgeName, headerText), body) tuples, and return html which
    will render a tabbed widget. There will be a series of tabs, which will each show a badge and some
    header text. Each tab has a body which will be shown when that tab is selected.

    interface: If the avatar cannot be adapted to the given interface, that tab will not be shown.
    badgeName: The name of an image in the /images/badges/ directory which will be rendered
        inside of the tab.
    headerText: The text which will be rendered inside of the tab.
    body: The stan which will be shown when this tab is selected.
    """
    def render(ctx, avatar):
        interfaces, headers, bodies = zip(*args)
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

        yield T.inlineJS("""
    var current = 'switch_%s';
    function switchIt(what) {
        document.getElementById(current).style.display = 'none';
        document.getElementById(what).style.display = 'block';
        document.getElementById(current + '_tab').className = 'tab';
        document.getElementById(what + '_tab').className = 'tab-selected';
        current = what;
    }""" % currentIndex)


        def genheaders():
            for i, head in enumerate(headers):
                if interfaces[i](avatar, None) is None:
                    ## This avatar does not have this interface. Don't render the tab.
                    continue
                badge, description = head
                if currentView == description:
                    klas = 'tab-selected'
                else:
                    klas = 'tab'
                
                yield entities.nbsp, entities.nbsp, entities.nbsp, entities.nbsp, 
                if badge is None:
                    image = ''
                else:
                    image = T.img(src="/images/%s.png" % badge, style="margin-right: 5px;")
                yield T.span(_class="%s" % klas, id="switch_%s_tab" % i, onclick="switchIt('switch_%s')" % i)[
                    image, description]

        yield T.div(style="white-space: nowrap;")[ genheaders() ]

        def genbodies():
            style = None
            for i, body in enumerate(bodies):
                if interfaces[i](avatar, None) is None:
                    ## This avatar does not have this interface. Don't render the tab.
                    continue

                def remember(ctx, data):
                    ctx.remember([('replace', ['currentView', headers[i][1]], {})], inevow.IViewParameters)
                    return ctx.tag

                if currentView != headers[i][1]:
                    style = 'display: none'
                else:
                    style = None

                yield T.div(id="switch_%s" % i, style=style, render=remember)[
                    body ]

        yield T.div(_class="switcher-body")[ genbodies() ]
    return render


def ALWAYS(data, default): return True


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
                yield (ALWAYS, (opt.getName(), opt.getDescription()), T.invisible(render=self.render_option, data=opt))

        return switcher(*list(genSwitchers()))

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
        return T.input(type="checkbox", name=boolean.getName(), checked=checked)

    render_numberOption = render_stringOption

    def render_passwordOption(self, ctx, password):
        return T.input(type="password", name=password.getName())

    child_images = static.File(os.path.join(os.path.dirname(__file__), 'images'))

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Shtoom Settings"]],
        T.style(type="text/css")["""
body {
    font-family: gill sans; 
    padding: 0px; }

#message {
    margin-bottom: 0.25em;
    padding: 0.25em;
    color: green;
    background-color: #efefef; }

.tab {
    background-color: #efefef; }

.tab-selected {
    background-color: #dddddd;
    text-decoration: underline; }

.tab,.tab-selected {
    cursor: pointer;
    display: inline-block;
    padding: 10px;
    padding-top: 4px;
    padding-bottom: 4px; }

.switcher-body { margin-top: -4px }
"""],
    T.body[
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
            if value is not None:
                O.setValue(value)
            else:
                print "VALUE FOR OPTION IS NONE:", name

        all.saveOptsFile()
        inevow.IRequest(ctx).redirect('/?message=Options+Set.')
        return '<html><body>Options set. <a href="/">Go back.</a></body></html>'


class IWizardConfiguration(annotate.TypedInterface):
    currentConfiguration = annotate.Choice(choicesAttribute='configurationChoices')


currentConfigFilename = os.path.expanduser('~/.shtoomrc.d/.currentConfigName')
class WizardConfiguration(rend.Page):
    __implements__ = IWizardConfiguration, rend.Page.__implements__

    def child_add_config(self, ctx):
        return ConfigurationWizard(self.original)

    child_css = webform.defaultCSS

    def getConfigurationChoices(self):
        print "get configuration choices"
        rcd = os.path.expanduser('~/.shtoomrc.d')
        if not os.path.exists(rcd):
            os.mkdir(rcd)
        rv = os.listdir(rcd)
        rv = [x for x in rv if not x.startswith('.')]
        if not rv: return ['No current configurations']
        return rv
    configurationChoices = property(getConfigurationChoices)

    def getCurrentConfig(self):
        if os.path.exists(currentConfigFilename):
            return open(currentConfigFilename).read().strip()
        return ''
    def setCurrentConfig(self, new):
        open(currentConfigFilename, 'w').write(new)
        open(os.path.expanduser('~/.shtoomrc'), 'w').write(open(os.path.expanduser('~/.shtoomrc.d/%s' % new)).read())
        ## reload app options
        self.original.loadOptsFile()
    currentConfiguration = property(getCurrentConfig, setCurrentConfig)

    def render_currentConfiguration(self, ctx, data):
        if not os.path.exists(currentConfigFilename):
            noConfig = True
        else:
            currentConfigFile = open(currentConfigFilename).read().strip()
            configFilename = os.path.expanduser('~/.shtoomrc.d/%s' % (currentConfigFile, ))
            if not os.path.exists(configFilename):
                noConfig = True
            else:
                noConfig = False

        if noConfig:
        #    import pdb; pdb.Pdb().set_trace()
            return "No current configurations. Please add one below."
        return T.h2[currentConfigFile]

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Shtoom Configuration"]],
        T.body[
            T.h1["Shtoom Configuration"],
            webform.renderForms()[
                T.form(pattern='freeform-form',
                action=T.slot('form-action'),
                enctype="multipart/form-data",
                method="POST",
                id=T.slot('form-id'))[
                    T.slot('form-arguments'),
                    T.span(pattern="binding")[
                        T.strong[T.slot('label')],
                        T.span(style="margin-left: 15px")[T.select(pattern='selector', onchange='submit();'), T.slot('input')]]]],
            render_currentConfiguration,
            T.h1["Add a Configuration"],
            T.form(action="add_config")[
                T.p[T.input(type="radio", name="config_type", value="divmod")["Divmod account"]],
                T.p[T.input(type="radio", name="config_type", value="fwd")["Free world dialup account"]],
                T.p[T.input(type="radio", name="config_type", value="manual")["Manual configuration"]],
                T.input(type="submit", name="configure", value="Create configuration")
                ]
            ]])


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

    def manual(self, req=annotate.Request(), name=annotate.String(label="Configuration Name"), username=annotate.String(), password=annotate.PasswordEntry()):
        """Manual
        
        Add a configuration manually.
        """
        pass
    manual = annotate.autocallable(manual, action="Create")


class ConfigurationWizard(rend.Page):
    __implements__ = IConfigurationWizard, rend.Page.__implements__
    def render_configBody(self, ctx, data):
        return webform.renderForms(bindingNames=[ctx.arg('config_type')])

    docFactory = loaders.stan(T.html[
    T.head[
        T.title["Configuration Wizard"],
        T.link(rel="stylesheet", type="text/css", href="css")],
    T.body[
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
        self.original.saveOptsFile()
        self.original.loadOptsFile()
        self.original.setOptsFile('.shtoomrc.d/%s' % (name, ))
        self.original.saveOptsFile()
        self.original.setOptsFile('.shtoomrc')
        open(currentConfigFilename, 'w').write(name)
        req.setComponent(iformless.IRedirectAfterPost, '/')

    def fwd(self, req, name, username, password):
        pass

    def manual(self, req, name, username, password):
        pass


class Reloader(rend.Page):
    def locateChild(self, ctx, segments):
        from shtoom.ui.webui import prefs
        reload(prefs)
        return prefs.WizardConfiguration(self.original), segments

