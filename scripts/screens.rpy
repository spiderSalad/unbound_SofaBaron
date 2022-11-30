################################################################################
## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who"

        text what id "what"

    # CHANGED: sidebar, components, and transform below
    frame id "calendar" align (0.0, 0.0) xysize (100, 40) background Frame("gui/frame.png"):
        padding (7, 5)
        xfill False
        yfill False

        $ global day

        text "Night [renpy.store.state.night]" id "nightcounter" text_align 0.5 align(0.5, 0.5) size 18

    window id "sidebar" align (1.0, 0.0) ysize 224 background Frame("gui/frame.png"):
        padding (10, 15, 10, 0)
        xfill False
        vbox spacing 10:
            yfill True
            imagebutton id "charSheetButton":
                yalign 0.0
                auto "gui/button/charsheet_%s.png" at sidebar_button_image
                action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexScoresPage", dissolve)]

            imagebutton id "charPowersButton":
                yalign 0.0
                auto "gui/button/powers_button_new_%s.png" at sidebar_button_image
                action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexPowersPage", dissolve)]

            imagebutton id "charStatusButton":
                yalign 0.0
                auto "gui/button/charstatus_button_%s.png" at sidebar_button_image
                action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexStatusPage", dissolve)]

            imagebutton id "caseFilesButton":
                yalign 0.0
                auto "gui/button/casefiles_button_%s.png" at sidebar_button_image
                action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexCasefilesPage", dissolve)]

            imagebutton id "infoButton":
                yalign 0.0
                auto "gui/button/info_button_%s.png" at sidebar_button_image
                action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexInfoPage", dissolve)]

    key "z" action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexScoresPage", dissolve)]
    key "x" action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexPowersPage", dissolve)]
    key "c" action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexStatusPage", dissolve)]
    key "b" action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexCasefilesPage", dissolve)]
    key "n" action [Play("sound", audio.gui_heartbeat), ToggleScreen("codexInfoPage", dissolve)]

    ## If there's a side image, display it above the text. Do not display on the
    ## phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


transform sidebar_button_image:
    zoom 0.5
    size (60, 60)


## Make the namebox available for styling through the Character object.
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos

    adjust_spacing False

## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## https://www.renpy.org/doc/html/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## https://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.button_text_properties("choice_button")


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    ## Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            textbutton _("Back") action Rollback()
            textbutton _("History") action ShowMenu('history')
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Save") action ShowMenu('save')
            textbutton _("Q.Save") action QuickSave()
            textbutton _("Q.Load") action QuickLoad()
            textbutton _("Prefs") action ShowMenu('preferences')


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_button is default
style quick_button_text is button_text

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.button_text_properties("quick_button")


################################################################################
## Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("Start") action Start()

        else:

            textbutton _("History") action ShowMenu("history")

            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")

        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:

            textbutton _("End Replay") action EndReplay(confirm=True)

        elif not main_menu:

            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):

            ## The quit button is banned on iOS and unnecessary on Android and
            ## Web.
            textbutton _("Quit") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.button_text_properties("navigation_button")


## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## https://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    ## This ensures that any other menu screen is replaced.
    tag menu

    add gui.main_menu_background

    ## This empty frame darkens the main menu.
    frame:
        style "main_menu_frame"

    ## The use statement includes another screen inside this one. The actual
    ## contents of the main menu are in the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When
## this screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu(title, scroll=None, yinitial=0.0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            ## Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial

                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True

                        side_yfill True

                        transclude

                else:

                    transclude

    use navigation

    textbutton _("Return"):
        style "return_button"

        action Return()

    label title

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        $ credz_json = renpy.store.utils.get_credits_json()
        $ sorted_credits = renpy.store.utils.sort_credits(credz_json)

        vbox:

            label "[config.name!t]"
            text _("Version [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]")

        vbox first_spacing 30 spacing 30:
            python:
                # global sortedCredits
                atagOpen1 = "{a="
                atagOpen2 = "}"
                atagClose = "{/a}"
            label "\nContributing Creators:"
            for ctype in sorted_credits:
                vbox first_spacing 20 spacing 10:
                    label "{t}s ({c}):".format(t = ctype.replace("_", " ").capitalize(), c = len(sorted_credits[ctype]))
                    for cred in sorted_credits[ctype]:
                        label "{cname}".format(cname = cred["name"])
                        vbox spacing 5:
                            for wk in cred["works"]:
                                hbox spacing 20:
                                    text "{}".format(wk["name"]) align(0.0, 0.5)
                                    textbutton "(License)" action OpenURL(wk["licenseUrl"]) align (0.0, 0.5)
                            if "website" in cred and cred["website"]:
                                textbutton "(Website Link)" action OpenURL(cred["website"]) xalign 0.2
                            for soc in cred["socials"]:
                                textbutton "{sms}: ({hdl})".format(sms=soc["site"], hdl=soc["handle"]) action OpenURL(soc["url"])


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save https://
## www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"

                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                textbutton _("<") action FilePagePrevious()

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto")

                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick")

                ## range(1, 10) gives the numbers from 1 to 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                textbutton _(">") action FilePageNext()


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5

style page_label_text:
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.button_text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.button_text_properties("slot_button")


## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    use game_menu(_("Preferences"), scroll="viewport"):

        vbox:

            hbox:
                box_wrap True

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("Skip")
                    textbutton _("Unseen Text") action Preference("skip", "toggle")
                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                vbox:

                    label _("Text Speed")

                    bar value Preference("text speed")

                    label _("Auto-Forward Time")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("Music Volume")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("Sound Volume")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("Voice Volume")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.button_text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.button_text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.button_text_properties("slider_button")

style slider_vbox:
    xsize 675


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


## This determines what tags are allowed to be displayed on the history screen.

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 23

            hbox:

                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
                textbutton _("Mouse") action SetScreenVariable("device", "mouse")

                if GamepadExists():
                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")

    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")

    hbox:
        label _("Escape")
        text _("Accesses the game menu.")

    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")

    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")

    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")

    hbox:
        label "H"
        text _("Hides the user interface.")

    hbox:
        label "S"
        text _("Takes a screenshot.")

    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")

    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")

    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")

    hbox:
        label _("Mouse Wheel Up\nClick Rollback Side")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")

    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")

    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")


    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")

    hbox:
        label _("Start, Guide")
        text _("Accesses the game menu.")

    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.button_text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    text_align 1.0


################################################################################
## CHANGED (custom) screens
################################################################################


screen ligma():
    tag ligma
    modal False
    window id "ligma_balls"


# Generates textbutton with tooltip
screen hovertext(txt, toolTip = None, _style = "medium", _xalign = 0.0):
    textbutton "[txt]" xalign _xalign:
        if _style == "medium":
            text_style "codex_hoverable_text"
        elif _style == "big":
            text_style "codex_hoverable_text_big"
        else:
            text_style "codex_hoverable_text_small"
        action NullAction()
        hovered ShowTransient("hovertip", None, str(toolTip))
        unhovered Hide("hovertip", None)


# Widget showing dots indicating ability scores
screen dotchain(name, score, dotcolor=renpy.store.cfg.DEFAULT_DOT_COLOR, format="bar", dfsize=None, altname=None, toolTip=None):
    python:
        cfg = renpy.store.cfg
        global scoreWords

        if not dfsize:
            style.frame["dots"].xysize = (gui.dot_frame_width, gui.dot_frame_height)
        else:
            style.frame["dots_vert"].xysize = dfsize
        scoreWord = cfg.SCORE_WORDS[int(score)] if renpy.store.utils.has_int(score) and int(score) >= 0 and int(score) < 6 else "zero"

    frame padding (5, 0) background None:
        if not dfsize:
            style style.frame["dots"]
        else:
            style style.frame["dots_vert"]

        if format == "bar":
            hbox xfill True yalign 0.5:
                use hovertext(str(name), toolTip, "big")
                image "gui/shapes/dots_[dotcolor]_[scoreWord].png" zoom 0.7 xalign 1.0
        elif format == "stack":
            vbox xfill True yalign 0.5 spacing 2:
                use hovertext(str(name), toolTip, "small", 0.5)
                image "gui/shapes/dots_[dotcolor]_[scoreWord].png" zoom 0.5 xalign 0.5
        elif format == "merit":
            vbox xfill True yfill True yalign 0.5 spacing 2:
                $ sendstr = "{name}\n({sz}{altname}{esz})".format(name = name, altname = altname, sz = "{size=11}", esz = "{/size}")
                use hovertext(sendstr, toolTip, _xalign = 0.5)
                image "gui/shapes/dots_[dotcolor]_[scoreWord].png" zoom 0.4 align (0.5, 1.0)
        else:
            $ raise ValueError("[Error]: That's not a known dotchain display format.")


# A tracker box with one of three states: clear, superficial damage, and aggravated damage
screen trackerbox(name, damage, count):
    frame background None xysize (24, 24) padding (0, 0) xalign 0.0 yalign 0.5:
        image "gui/shapes/[name]_[damage].png" zoom 0.1 xalign 0.0 yalign 0.5


# Builds box trackers, i.e. health and willpower
screen trackerline(name, total, clearboxes, spfdamage, bonus = 0, bonusName = ""):
    hbox spacing 0 xfill False:
        for count in range(total + bonus):
            $ boxname = bonusName if bonus > 0 and count >= total else name

            if count < clearboxes:
                use trackerbox(boxname, "clear", count)
            elif count < (clearboxes + spfdamage):
                use trackerbox(boxname, "superficial", count)
            else:
                use trackerbox(boxname, "aggravated", count)


# Widget displaying opinion for a faction or character, from -100 to 100
screen repbar(trueValue, trueMax, valueAdjust, includeName = None):
    python:
        val = trueValue + valueAdjust
        maxval = trueMax # + valueAdjust
        ratio = float(val) / float(maxval)
        barColor = "#4545cc" if ratio > 0.5 else "#6f0000"

    frame style style.utility_frame:
        hbox spacing 10:
            if includeName:
                text "[includeName]" align (0.0, 0.5) size 15
            bar value StaticValue(val, maxval):
                align (0.5, 0.5)
                xmaximum 110
                ymaximum 20
                left_bar barColor
                right_bar "#707070"
                # left_bar Frame("gui/bar/sleek_bar_" + barColor + ".png") # "#cc0000"
            text "[trueValue]" yalign 0.5 size 20


# Screen that just builds grids
screen buildGrid(nrows, ncols, numItems, _xspacing = 10, _yspacing = 10, _xpadding = 5, _ypadding = 5, _transpose = False):
    $ numdummies = (nrows * ncols) - numItems
    frame style style.utility_frame padding (_xpadding, _ypadding) xalign 0.5:
        grid nrows ncols align (0.5, 0.5) xfill True yfill True:
            transpose _transpose
            xspacing _xspacing
            yspacing _yspacing

            transclude
            for count in range(numdummies):
                null align (0.5, 0.5)


# Top row shown on all codex screens
screen codexTopRow():
    style_prefix "codex_panel"

    $ cfg, pc = renpy.store.cfg, renpy.store.state.pc
    frame id "top_status_row" background None xalign 0.5 padding (0, 0):
        hbox xsize 860 xalign 0.5:
            frame id "pane_dossier" align (0.0, 0.0) xysize (250, 96):
                hbox xfill True:
                    python:
                        ptdesc = "\nPredator Type:"
                        ptname = "\n???" if not hasattr(pc, cfg.REF_PREDATOR_TYPE) else "\n" + str(pc.predator_type)
                    text "Alias:\nClan:\n[ptdesc]" text_align 0.0 size 12 xalign 0.0
                    text "[pc.nickname]\n[pc.clan] {color=#cc0000}([pc.blood_potency]){/color}[ptname]" text_align 1.0 size 12 xalign 1.0

            frame id "pane_soulstate" align (0.3, 0.0) xysize (172, 96):
                $ humanityPhrase = cfg.HUMANITY_BLURBS[pc.humanity - 4]
                $ hungerPhrase = cfg.HUNGER_BLURBS[pc.hunger][int(pc.humanity) - cfg.MIN_HUMANITY]
                vbox spacing 2:
                    use dotchain("Humanity", pc.humanity - 3, dotcolor = "bright", format = "stack", dfsize = (150, 40))
                    use dotchain("Hunger", pc.hunger, format = "stack", dfsize = (150, 40), toolTip = hungerPhrase)

            frame id "pane_trackers" align (1.0, 0.0) xysize (410, 96) style style.codex_panel_frame:
                style_prefix "boxtracker"

                vbox spacing 0 align (1.0, 0.5) xfill True yfill True:
                    frame id "healthTracker" xsize 380 align(1.0, 0.4):
                        hbox:
                            text "Health" text_align 1.0 align (0.0, 0.5) style style.codex_panel_text
                            frame id "HPBoxes" xsize 280 align (1.0, 0.5):
                                $ bonus = pc.hp.bonus
                                $ total = pc.hp.boxes
                                $ spfd = pc.hp.spf_damage
                                $ aggd = pc.hp.agg_damage
                                $ clearHealth = (total + bonus) - (spfd + aggd)
                                use trackerline("Health", total, clearHealth, pc.hp.spf_damage, bonus, "Fort")

                    frame id "willpowerTracker" xsize 380 align(1.0, 0.6):
                        hbox:
                            text "Willpower" text_align 1.0 align (0.0, 0.5) style style.codex_panel_text
                            frame id "WPBoxes" xsize 280 align (1.0, 0.5):
                                $ clearWillpower = pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)
                                use trackerline("Willpower", pc.will.boxes, clearWillpower, pc.will.spf_damage)


# Every codex panel uses this
screen codexBaseFrame(tabname):
    window id "codex_window_main" align (0.5, 0.1) xysize (900, 500) padding (15, 10):
        style_prefix "codex_panel"
        background Frame("gui/nvl.png", 5, 5, 5, 5)
        modal False

        image "gui/clan_bg_ventrue.png" align (0.5, 0.5) zoom 1.0
        vbox xfill True yfill True spacing 0:
            use codexTopRow()
            frame id "main_pane_container" xalign 0.5 xysize (860, 300) padding (0, 0) background None:
                transclude
            use codex_tabs(tabname)


# Character sheet showing scores, i.e. attributes and skills
screen codexScoresPage(*args):
    tag codexPage
    modal False

    $ pc, cfg = renpy.store.state.pc, renpy.store.cfg

    use codexBaseFrame("scores"):  # TODO: re-implement tooltips, resize everything
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_attributes" xalign 0.5 ysize 130:
                use buildGrid(gui.GRID_ROWS_ALLSCORES, gui.GRID_COLS_ATTRS, gui.GRID_ROWS_ALLSCORES * gui.GRID_COLS_ATTRS, _transpose = True):
                    for count, attr in enumerate(pc.attrs):
                        $ keydex = cfg.REF_ATTR_ORDER[count]
                        frame style style.utility_frame:
                            $ the_score = pc.attrs[keydex]
                            use dotchain(keydex, the_score, toolTip="{at1}".format(at1="tooltip tbd"))# tooltipTable[keydex]))
            frame id "pane_skills" xalign 0.5 ysize 170:
                use buildGrid(gui.GRID_ROWS_ALLSCORES, gui.GRID_COLS_SKILLS, gui.GRID_ROWS_ALLSCORES * gui.GRID_COLS_SKILLS, _transpose = True):
                    for count, skill in enumerate(pc.skills):
                        $ keydex = cfg.REF_SKILL_ORDER[count]
                        frame style style.utility_frame:
                            use dotchain(keydex, pc.skills[keydex], toolTip="{st1}".format(st1="tooltip tbd"))#tooltipTable[keydex]))


# Character sheet tab showing discipline powers and maybe merits/Hardestadt loresheet if I get that far
screen codexPowersPage(*args):
    tag codexPage
    modal False
    $ cfg, pc = renpy.store.cfg, renpy.store.state.pc
    $ merits_and_flaws = [bg for bg in pc.backgrounds if bg[cfg.REF_TYPE] in (cfg.REF_BG_FLAW, cfg.REF_BG_MERIT)]
    use codexBaseFrame("powers"):
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_merits" xalign 0.5 ysize 80 padding (10, 10):
                #$ leng = len(pc.merits)
                if len(merits_and_flaws) > 0: # Shouldn't be more than 3
                    hbox xfill True:
                        for count in range(min(len(merits_and_flaws), cfg.MERIT_DISPLAY_MAX)):
                            frame style style.utility_frame yfill True:
                                python:
                                    m_f = merits_and_flaws[count]
                                    dcolor = "red" if m_f[cfg.REF_TYPE] == cfg.REF_BG_FLAW else "red"
                                    altname = m_f[cfg.REF_TYPE]
                                    toolTip = m_f[cfg.REF_TOOLTIP] if cfg.REF_TOOLTIP in m_f else None
                                use dotchain(m_f[cfg.REF_BG_NAME], m_f[cfg.REF_DOTS], altname=altname, dotcolor=dcolor, format="merit", toolTip=toolTip)
                else:
                    hbox xfill True yalign 0.5:
                        text "Nothing special unlocked or discovered." text_align 0.5 xalign 0.5 yalign 0.5
            frame id "pane_disciplines" xalign 0.5 ysize 220:  # TODO: left off here, and in new SuperpowerArsenal class
                $ unlocked_ds = pc.disciplines.get_unlocked()
                hbox xfill True:
                    for count, ul_disc in enumerate(unlocked_ds):
                        $ xalv = float(count) / float(len(unlocked_ds) - 1)
                        frame style style.utility_frame yfill True xalign xalv:  # TODO: adjust this scheme later for horizontal scrolling
                            vbox spacing 7:
                                use dotchain(ul_disc, pc.disciplines.levels[ul_disc], toolTip="tooltip tbd")
                                $ ul_disc_prefix = "POWER_{}".format(str(ul_disc).upper())
                                $ disc_powers = cfg.REF_DISC_POWER_TREES[ul_disc]# [getattr(cfg, pw) for pw in cfg.__dict__ if str(pw).startswith(ul_disc_prefix)]
                                # $ unlocked_powers = [pw for pw in disc_powers if pw in pc.powers]
                                $ power_list = pc.disciplines.pc_powers[ul_disc]
                                for pkey in power_list:
                                    $ power = power_list[pkey] if power_list[pkey] else None
                                    if power:
                                        frame style style.utility_frame left_padding 5 xalign 0.0:
                                            textbutton str(count + 1) + ". [power]":
                                                text_style style.codex_hoverable_text
                                                action NullAction()
                                                hovered ShowTransient("hovertip", None, "{tt}".format(tt="tooltip tbd"))
                                                unhovered Hide("hovertip", None)
                                            # text str(count + 1) + ". [power]" text_align 1.0 xfill True


# Character sheet tab showing status, i.e. opinions, backgrounds, inventory
screen codexStatusPage(*args):
    tag codexPage
    modal False

    # $ global opinions

    use codexBaseFrame("status"):
        $ pc = state.pc
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_opinions" xalign 0.5 ysize 120 padding (10, 15):
                use buildGrid(gui.REP_GRID_ROWS, gui.REP_GRID_COLS, len(state.opinions), 10, 15):
                    for count, reputation in enumerate(state.opinions):
                        use repbar(state.opinions[reputation], cfg.REP_MAX, cfg.REP_VALUE_ADJUST, includeName=reputation)
            frame id "pane_backgrounds" xalign 0.5 ysize 180 padding (10, 10):
                use buildGrid(gui.BG_GRID_ROWS, gui.BG_GRID_COLS, len(pc.backgrounds), 10, 10):
                    for count, asset in enumerate(pc.backgrounds):
                        $ dcolor = "dark" if asset[cfg.REF_TYPE] == cfg.REF_BG_FLAW else "red"
                        $ altname = (asset[cfg.REF_BG_NAME] + " Flaw") if asset[cfg.REF_TYPE] == cfg.REF_BG_FLAW else (asset[cfg.REF_BG_NAME])
                        use dotchain(asset[cfg.REF_BG_NAME], asset[cfg.REF_DOTS], altname=altname, dotcolor=dcolor, format="merit")


# Shows character inventory and case notes, i.e. quest log
screen codexCasefilesPage(*args):
    tag codexPage
    modal False

    use codexBaseFrame("casefiles"):
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_inventory" xalign 0.5 ysize 130:
                use buildGrid(4, 3, len(state.pc.inventory), 5, 10):
                    for count, item in enumerate(state.pc.inventory):
                        frame style style.utility_frame:
                            python:
                                global itemTable
                                itemDetails = itemTable[item[KEY_NAME]]
                                colorstr = IT_COLOR_KEYS[itemDetails[KEY_ITEMTYPE]]

                                title = getItemProperty(item, KEY_VALUE)
                                toolTip = getItemProperty(item, KEY_TOOLTIP)
                                itype = getItemProperty(item, KEY_ITEMTYPE)

                                if itemDetails[KEY_ITEMTYPE] == IT_MONEY:
                                    title = "" + str(item[KEY_NAME]).capitalize() + ": ${:.2f}".format(item[KEY_VALUE])
                                elif itemDetails[KEY_ITEMTYPE] == IT_WEAPON or itemDetails[KEY_ITEMTYPE] == IT_FIREARM:
                                    concealed = "I have my trusty forged CCW permit, just in case." if itemDetails[ITEM_CONCEALED] else "This is an open carry state, right?"
                                    toolTip = "Damage Bonus: {db}\n\n{cncl}\n\n{btt}".format(db=itemDetails[DAMAGE_BONUS], cncl=concealed, btt=toolTip)

                            textbutton str(title) + " {color=[colorstr]}(" + str(itemDetails[KEY_ITEMTYPE]) + "){/color}":
                                text_style style.codex_hoverable_text
                                action NullAction()
                                hovered ShowTransient("hovertip", None, "{}".format(toolTip))
                                unhovered Hide("hovertip", None)
            frame id "pane_case_log" xalign 0.5 ysize 170 padding (10, 10):
                text "This will basically be a quest log."


# Glossary of VtM lore and game mechanics
screen codexInfoPage(*args):
    tag codexPage
    modal False

    use codexBaseFrame("info"):
        style_prefix "codex_panel"
        frame id "glossary" ysize 314 padding (10, 10):
            text "Glossary goes here, eventually"


# widget to switch between codex tabs
screen codex_tabs(*args):
    $ global codexTabList

    frame xalign 0.5 yalign 1.0 xysize (600, 40) style style.codex_panel_frame:
        hbox xfill True:
            textbutton "Abilities {size=11}(z){/size}" xalign 0.143:
                keysym "z"
                action ToggleScreen("codexScoresPage", None) # dissolve without quotes
            textbutton "Powers {size=11}(x){/size}" xalign 0.429:
                keysym "x"
                action ToggleScreen("codexPowersPage", None)
            textbutton "Status {size=11}(c){/size}" xalign 0.714:
                keysym "c"
                action ToggleScreen("codexStatusPage", None)
            textbutton "Case Files {size=11}(b){/size}" xalign 0.714:
                keysym "b"
                action ToggleScreen("codexCasefilesPage", None)
            textbutton "Codex {size=11}(n){/size}" xalign 0.714:
                keysym "n"
                action ToggleScreen("codexInfoPage", None)

# Player chooses discipline powers here.
screen disciplineTree(*args):
    tag codexPage

    window id "powertree_main" align (0.5, 0.1) xysize (900, 500) padding (15, 10):
        style style.codex_panel_frame
        background Frame("gui/nvl.png", 5, 5, 5, 5)
        modal False

        image "gui/ventrue_bg.png" align (0.5, 0.5) zoom 1.0
        vbox spacing 2 xfill True:
            text "Discipline Powers" align truecenter text_align 0.5

# Used to display tooltips
screen hovertip(tip, *args):
    frame background Frame("gui/frame.png", Borders(5, 5, 5, 5)):
        xmaximum 250
        ymaximum 160
        # ysize 80
        pos renpy.get_mouse_pos()
        padding (10, 10)
        text "[tip]" size 12 xfill True yfill True

# Should show at 3 hunger or more and intensify
screen hungerlay():
    tag hunger_overlay
    modal False

    if renpy.store.state.pc.hunger > renpy.store.cfg.HUNGER_MAX_CALM:
        $ scoreWord = renpy.store.cfg.SCORE_WORDS[int(renpy.store.state.pc.hunger)]
        image "gui/overlay/hunger_[scoreWord].png" align (0.5, 0.5) xysize (1920, 1080)
    else:
        image None


# Codex styles
style codex_panel_frame:
    modal False
    xsize 860
    padding (10, 5)
    background Frame("gui/frame.png", Borders(2, 2, 2, 2))

style codex_panel_text:
    size 16
    color "#ffbbbb"
    text_align 0.0
    line_spacing 3

style codex_panel_button_text:
    size 16
    hover_color "#ffebeb"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.5

style boxtracker_frame:
    background None
    ysize 24
    padding (0, 0)

style boxtracker_hbox:
    spacing 0
    xfill True

style utility_frame:
    background None
    align (0.5, 0.5)
    padding (0, 0)

style codex_hoverable_text:
    size 13
    hover_color "#ffebeb"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.5

style codex_hoverable_text_small:
    size 11
    hover_color "#ffebeb"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.0

style codex_hoverable_text_big:
    size 15
    hover_color "#ffebeb"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.0


################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## https://www.renpy.org/doc/html/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 45

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 150

                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    ## Right-click and escape answer "no".
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    text_align 0.5
    layout "subtitle"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.button_text_properties("confirm_button")


## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    ## glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL screen ##################################################################
##
## This screen is used for NVL-mode dialogue and menus.
##
## https://www.renpy.org/doc/html/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## Displays dialogue in either a vpgrid or the vbox.
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## Displays the menu, if given. The menu may be displayed incorrectly if
        ## config.narrator_menu is set to True.
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## This controls the maximum number of NVL-mode entries that can be displayed at
## once.
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    text_align gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    text_align gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    text_align gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.button_text_properties("nvl_button")



################################################################################
## Mobile Variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## Since a mouse may not be present, we replace the quick menu with a version
## that uses fewer and bigger buttons that are easier to touch.
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            textbutton _("Back") action Rollback()
            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")
            textbutton _("Menu") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
