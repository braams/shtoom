## Web prefererence rendering for shtoom.


from nevow import rend
from nevow import tags as T
from nevow import loaders
from nevow import entities
from nevow import inevow
from nevow import flat
from nevow import static

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


class Reloader(rend.Page):
    def locateChild(self, ctx, segments):
        from shtoom.ui.webui import prefs
        reload(prefs)
        return prefs.PreferencesPage(self.original), segments

