################################################################################
## CHANGED (custom) screens
################################################################################


screen tl_corner_hud(*args):
    frame id "calendar" align (0.0, 0.0) xysize (250, 40) background Frame("gui/frame.png"):
        padding (7, 5)
        margin (5, 0)
        xfill False
        yfill False

        $ state = renpy.store.state
        # $ p_night, p_hours = state.clock.posted_night, state.clock.posted_hours
        $ p_night, p_hours = state.clock.night, state.clock.hours

        text "Night [p_night]:  [p_hours] hours left" id "nightcounter" text_align 0.5 align (0.5, 0.5) size 18


screen dev_panel(*args):
    frame id "call_stack_readout" align (0.0, 0.06) xysize (500, 180) background Frame("gui/frame.png"):
        padding (7, 5)
        margin (5, 0)
        xfill False
        yfill False

        $ state = renpy.store.state
        $ stack_string, pc = state.get_call_stack_str(), state.pc
        side "c l":
            viewport id "call_stack_list" draggable True mousewheel True:# scrollbars "vertical":
                frame padding (7, 0) background None:
                    text "[stack_string]" text_align 0.0 align (0.1, 0.1) size 16
            vbar value YScrollValue("call_stack_list")

    frame id "second_dev_readout" align (0.0, 0.3) xysize (800, 250) background Frame("gui/frame.png"):
        margin (5, 0)
        padding (7, 5)
        xfill False
        yfill False
        python:
            state, ro_text_main, ao_r, rosters_r = renpy.store.state, "", "", ""
            rr_listcomp_1, rr_listcomp_2 = [], []

            # ent_format = lambda ent: " {}   {}".format(">" if state.arena.get_up_next() is ent else " ", ent)
            def ent_format(ent, show_stats=False):
                if ent.dead:
                    key = "X"
                elif state.arena.get_up_next() is ent:
                    key = ">"
                else:
                    key = "  "
                status_l, status_r, eng = " [ {} ] ".format(ent.current_pos), "", "[e]" if ent.engaged_by else ""
                grap = "[g<]" if ent.grappled_by else "[g>]" if ent.grappling_with else ""
                atkd = f'{ent.times_attacked_this_turn}x<-'
                if show_stats:
                    if ent.dead:
                        status_r = "  (dead)"
                    else:
                        spf, agg, clear, total = ent.hp.spf_damage, ent.hp.agg_damage, ent.hp.undamaged, ent.hp.total
                        # status_r = "  ({} spf + {} agg/{} hp)  [ {} ]{}".format(
                            # spf, agg, total, ent.current_pos, eng
                        # )
                        status_r = f'  (hp: {ent.hp})   {eng}{grap}{atkd}'
                return " {0}{1}   {2: <8}{3}".format(key, status_l, utils.truncate_string(str(ent), leng=17), status_r)

            pc_append = "  (pc={}/{}".format(pc.pronoun_set.PN_SHE_HE_THEY, pc.pronoun_set.PN_HER_HIM_THEM)
            pc_append += ", scream={})".format(utils.truncate_string(pc.scream, leng=20, reverse=True))
            pc_append += "\nUsed discipline this turn: {}".format("Yes" if state.used_disc_this_turn else "No")
            if not hasattr(state, "arena") or not state.arena:
                ro_text_main = "Battle engine not initialized.{}".format(pc_append)
            elif state.arena.battle_end:
                ro_text_main = "Battle engine initialized & g2g.{}".format(pc_append)
            else:
                ro_text_main = "Ongoing battle: R{}, T{}{}\n".format(state.arena.round+1, state.arena.ao_index+1, pc_append)
                ro_text_main += "round order:  " + ",  ".join(state.arena.round_order)
                ao_r = "act order:\n\n" + "\n".join([ent_format(ent) for ent in state.arena.action_order])
                pc_team, enemies = state.arena.pc_team, state.arena.enemies
                rosters_r = "Team Rosters:\n\n"
                rr_listcomp_1 = [(ent_format(ent, True), ent) for ent in pc_team]
                rosters_r += "PC Team:\n" + "\n".join([el[0] for el in rr_listcomp_1]) + "\n"
                rr_listcomp_2 = [(ent_format(ent, True), ent) for ent in enemies]
                rosters_r += "Enemies:\n" + "\n".join([el[0] for el in rr_listcomp_2]) + "\n"
                ro_text_main += "..."
        side "c l":
            viewport id "battle_readout_list" draggable True mousewheel True yinitial 1.0:
                frame padding (7, 0) background None:
                    vbox spacing 15:
                        text "[ro_text_main]" text_align 0.0 align (0.1, 0.1) size 16
                        hbox spacing 20:
                            #text "[rosters_r]" text_align 0.0 yalign 0.0 size 16
                            vbox spacing 5:
                                text "PC Team:" size 16
                                for ent_tup in rr_listcomp_1:
                                    use hovertext(repr(ent_tup[1]), _style="small", tooltip=ent_tup[1].summarize())
                                text "Enemies:" size 16
                                for ent_tup in rr_listcomp_2:
                                    use hovertext(repr(ent_tup[1]), _style="small", tooltip=ent_tup[1].summarize())
                            text "[ao_r]" text_align 0.0 yalign 0.0 size 16
            vbar value YScrollValue("battle_readout_list")


screen bl_corner_panel(*args):
    frame id "contextual_action_bar" align (0.0, 0.64) xysize (400, 280) background Frame("gui/frame.png"):
        at fadein_basic
        padding (10, 15)
        margin (5, 0)
        python:
            state, Inventory = renpy.store.state, renpy.store.game.Inventory
            pc, qb_key = state.pc, ""
            equipped = pc.inventory.equipped
            surge_tooltip = "Risk Hunger to transcend the limitations of the human body and mind.\n\n(+2 dice to next roll)"
            sw_tooltip = "(You can only switch weapons on your turn.)"
            bs_action, surge_prompt = None, "Can't Rouse..."
            sw_action, item_action = Function(state.switch_weapons, reload_menu=state.in_combat), None
            dp_action = None
            if not state.blood_surge_active and state.blood_surge_enabled and pc.can_rouse():
                surge_prompt = "Rouse the Blood?"
                bs_action = Function(state.blood_surge, audio.heartbeat_faster_2)
            elif state.blood_surge_active:
                surge_prompt = "Blood Roused!"
            elif pc.hunger >= cfg.HUNGER_MAX:
                surge_prompt = "Can't. Rouse. Must. Feed."
        side "c l":
            viewport id "contextual_actions_list" draggable True mousewheel True yinitial 1.0:# scrollbars "vertical":
                vbox spacing 5 align (0.5, 0.5) yfill False box_reverse True:
                    use hovertext("{}".format(surge_prompt), tooltip=surge_tooltip, _action=bs_action, activated=state.blood_surge_active)
                    for item_slot in equipped:  # Add quickbar later
                        $ item, qb_key, sw_tt = equipped[item_slot] if equipped[item_slot] else None, "", None
                        # $ print("we have item {} at slot {}".format(item if item else None, item_slot))
                        if item and item_slot in [Inventory.EQ_CONSUMABLE_1, Inventory.EQ_CONSUMABLE_2]:
                            $ qb_key = " (x{})".format(equipped[item_slot].quantity)
                            $ sw_tt = item.desc if state.is_their_turn(pc) else sw_tooltip
                        elif item_slot in [Inventory.EQ_WEAPON, Inventory.EQ_WEAPON_ALT]:
                            python:
                                item_action, item_desc = sw_action, item.desc if item else "(Empty-handed)"
                                qb_key = "{b}At hand{/b}: " if item_slot == Inventory.EQ_WEAPON else "At side: "
                                sw_tt = item_desc if state.is_their_turn(pc) else sw_tooltip
                        if item:
                            use hovertext("{}{}".format(qb_key, item), tooltip=sw_tt, _action=item_action)
                    for disc in pc.disciplines.get_unlocked():
                        for pow_level in pc.disciplines.pc_powers[disc]:
                            python:
                                power, used_disc_this_turn = pc.disciplines.pc_powers[disc][pow_level], state.used_disc_this_turn
                                relevance, active = state.context_relevant(power)
                                activ_str = " (Active!)" if active else ""
                            if power and (relevance or active):
                                python:
                                    can_activate = (not active or power in cfg.REF_DISC_POWER_TOGGLABLES)
                                    is_freebie = power in cfg.REF_DISC_POWER_FREEBIES
                                    can_pay_blood = pc.can_rouse() or is_freebie
                                    on_cooldown = used_disc_this_turn and not is_freebie
                                    can_use = can_activate and can_pay_blood and not on_cooldown
                                    # print(" |-- {}: can_activate = {}, is_freebie = {}, can_pay_blood = {}, on_cooldown = {}, can_use = {}".format(
                                    #     power, can_activate, is_freebie, can_pay_blood, on_cooldown, can_use
                                    # ))
                                    dp_action = None if not can_use else Function(state.statusfx.use_disc_power, power)
                                use hovertext("{} ({}){}".format(power, disc, activ_str), tooltip="da powah", _action=dp_action, usable=can_use, activated=active)
                            elif power and relevance is not None:
                                use hovertext("{} ({})".format(power, disc), tooltip="da powah", _action=None, usable=False)  # TODO: change colors
                            elif power and cfg.DEV_MODE:  # Powers that are neither relevant nor usable are not displayed.
                                $ t_power, t_disc = utils.renpy_tag_wrap(power, "s"), utils.renpy_tag_wrap(disc, "s")
                                use hovertext("{} ({})".format(t_power, t_disc), tooltip="da powah", _action=None, usable=False)

            vbar value YScrollValue("contextual_actions_list")


screen ingame_sidebar_menu(*args):
    frame id "sidebar" align (1.0, 0.0) ysize 224 background Frame("gui/frame.png"):
        padding (10, 15, 10, 0)
        margin (5, 0)
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


transform sidebar_button_image:
    zoom 0.5
    size (60, 60)


transform fadein_basic:
    alpha 0.0
    linear 1.0 alpha 1.0


transform fadeout_basic:
    alpha 1.0
    linear 1.0 alpha 0.0


# Generates textbutton with tooltip, action optional
screen hovertext(txt, tooltip=None, _style="medium", _xalign=0.0, _action=None, usable=True, activated=False, ttsize=None):
    $ tt_width, tt_height = ttsize if ttsize else (600, None)
    # $ print(f'tt_width = {tt_width}, tt_height = {tt_height}')
    textbutton "[txt]" xalign _xalign:
        if _style == "medium":
            text_style "codex_hoverable_text"
        elif _style == "big":
            text_style "codex_hoverable_text_big"
        else:
            text_style "codex_hoverable_text_small"
        selected activated
        sensitive usable or activated
        action If(_action is None, true=NullAction(), false=_action) #daction #_action or NullAction()
        hovered ShowTransient("hovertip", None, str(tooltip), tt_width=tt_width, tt_height=tt_height)
        unhovered Hide("hovertip", None)


# Widget showing dots indicating ability scores
screen dotchain(name, score, dcolor=store.cfg.DEF_DOT_COLOR, format="bar", dfsize=None, altname=None, tooltip=None, _action=None):
    python:
        cfg = store.cfg
        if not dfsize:
            dfsize = (gui.dot_frame_width, gui.dot_frame_height)
        score_word = cfg.SCORE_WORDS[int(score)] if renpy.store.utils.has_int(score) and int(score) >= 0 and int(score) < 6 else "zero"

    frame padding (5, 0) xysize dfsize background None:
        if format == "bar":
            hbox xfill True yalign 0.5:
                use hovertext(str(name), tooltip, "big", _action=_action)
                image "gui/shapes/dots_[dcolor]_[score_word].png" zoom 0.7 xalign 1.0 yalign 0.5
        elif format == "stack":
            vbox xfill True yalign 0.1 spacing 2:
                use hovertext(str(name), tooltip, "small", 0.5, _action=_action)
                image "gui/shapes/dots_[dcolor]_[score_word].png" zoom 0.6 xalign 0.5
        elif format == "merit":
            vbox xfill True yfill True yalign 0.5 spacing 2:
                $ sendstr = "{name}\n({sz}{altname}{esz})".format(name=name, altname=altname, sz="{size=11}", esz="{/size}")
                use hovertext(sendstr, tooltip, _xalign = 0.5, _action=_action)
                image "gui/shapes/dots_[dcolor]_[score_word].png" zoom 0.4 align (0.5, 1.0)
        elif format == "header":
            hbox xfill True yalign 0.5:
                use hovertext(str(name), tooltip, "big", _action=_action)
                image "gui/shapes/dots_[dcolor]_[score_word].png" zoom 1.0 align (1.0, 0.5)
        else:
            $ raise ValueError("\"{}\" is not a known dotchain display format.".format(format))


# A tracker box with one of three states: clear, superficial damage, or aggravated damage
screen trackerbox(name, damage, count):
    frame background None xysize (24, 24) padding (0, 0) xalign 0.0 yalign 0.5:
        image "gui/shapes/[name]_[damage].png" zoom 0.1 xalign 0.0 yalign 0.5


# Builds box trackers, i.e. health and willpower
screen trackerline(name, total, clearboxes, spfdamage, bonus=0, bonus_name=""):
    hbox spacing 0 xfill False:
        for count in range(total + bonus):
            $ box_name = "{}{}".format(name, bonus_name) if bonus > 0 and count >= total else name

            if count < clearboxes:
                use trackerbox(box_name, "clear", count)
            elif count < (clearboxes + spfdamage):
                use trackerbox(box_name, "superficial", count)
            else:
                use trackerbox(box_name, "aggravated", count)


# Widget based on repbar, used for resonances
screen xpbar(value, max, name, color="#232323", _action=None, _tooltip=None):
    python:
        ratio = float(value) / float(max)
        if _action is None:
            _action = NullAction()

    frame style style.utility_frame:
        hbox spacing 10:
            textbutton "[name]" align (0.0, 0.5):  # size 18
                text_style style.codex_hoverable_text
                action _action
                hovered ShowTransient("hovertip", None, "{tt}".format(tt="tooltip tbd" if not _tooltip else _tooltip))
                unhovered Hide("hovertip", None)
            bar value StaticValue(value, max) xysize (160, 15):
                align (0.5, 0.5)
                xmaximum 160
                ymaximum 10
                left_bar color
                right_bar "#707070"
            text "[value]" yalign 0.5 size 20


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
screen buildGrid(nrows, ncols, num_items, _xspacing = 10, _yspacing = 10, _xpadding = 5, _ypadding = 5, _transpose = False):
    $ num_dummies = (nrows * ncols) - num_items
    frame style style.utility_frame padding (_xpadding, _ypadding) xalign 0.5:
        grid nrows ncols align (0.5, 0.5) xfill True yfill True:
            transpose _transpose
            xspacing _xspacing
            yspacing _yspacing

            transclude
            for count in range(num_dummies):
                null align (0.5, 0.5)


# Top row shown on all codex screens
screen codexTopRow():
    style_prefix "codex_panel"

    $ cfg, pc = renpy.store.cfg, renpy.store.state.pc
    frame id "top_status_row" background None xalign 0.5 padding (0, 0):
        hbox xsize gui.codex_inner_width xalign 0.5 spacing 15:
            frame id "pane_dossier" align (0.0, 0.0) xysize (510, 126):
                hbox xfill True yfill True:
                    python:
                        ptdesc = "\nPredator Type:"
                        ptname = "\n???" if not hasattr(pc, cfg.REF_PREDATOR_TYPE) else "\n" + str(pc.predator_type)
                        clan_string = "" if pc.clan == cfg.CLAN_NONE_CAITIFF else "Clan:"
                        right_text = "[pc.nickname]\n[pc.clan]\n11th {color=#cc0000}([pc.blood_potency]){/color}[ptname]"
                    text "Alias:\n[clan_string]\nGeneration:\nPredator Type:" text_align 0.0 size 18 xalign 0.0 line_spacing 7
                    text right_text text_align 1.0 size 18 xalign 1.0 line_spacing 7

            frame id "pane_soulstate" align (0.0, 0.0) xysize (192, 126):
                $ humanityPhrase = cfg.HUMANITY_BLURBS[pc.humanity - cfg.MIN_HUMANITY]
                $ hung_hum_index = max(0, int(pc.humanity) - cfg.MIN_HUMANITY - 1)
                $ hungerPhrase = cfg.HUNGER_BLURBS[pc.hunger][hung_hum_index]
                vbox spacing 2:
                    use dotchain("Humanity", pc.humanity - 3, dcolor="bright", format="stack", dfsize=(180, 60), tooltip=humanityPhrase)
                    use dotchain("Hunger", pc.hunger, format="stack", dfsize=(180, 60), tooltip=hungerPhrase)

            frame id "pane_public_relations" align (0.0, 0.0) xysize (376, 126):
                vbox yalign 0.5 spacing 15:
                    python:
                        mq_tooltip, mq_action = "It can't happen again. You wouldn't survive.", None
                        ntr_tooltip, ntr_action = "Make a name for yourself, but careful not to make too many waves...", None
                        if cfg.DEV_MODE:
                            mq_action = Function(state.masquerade_breach, base=10)
                    use xpbar(state.masquerade, cfg.VAL_MASQUERADE_MAX, "Masquerade", _tooltip=mq_tooltip, color="#ededed", _action=mq_action)
                    use xpbar(state.notoriety, cfg.VAL_NOTORIETY_MAX, "Notoriety", _tooltip=ntr_tooltip, color="#9306f4")

            frame id "pane_trackers" align (0.0, 0.0) xysize (465, 126) style style.codex_panel_frame:
                style_prefix "boxtracker"

                vbox spacing 0 align (1.0, 0.5) xfill True yfill True:
                    frame id "health_tracker" xsize 380 align(1.0, 0.4):
                        hbox:
                            text "Health" text_align 1.0 align (0.0, 0.5) style style.codex_panel_text
                            frame id "HPBoxes" xsize 280 align (1.0, 0.5):
                                $ bonus, total = pc.hp.bonus, pc.hp.boxes
                                $ spfd, aggd = pc.hp.spf_damage, pc.hp.agg_damage
                                $ clearHealth = (total + bonus) - (spfd + aggd)
                                use trackerline("Health", total, clearHealth, pc.hp.spf_damage, bonus=bonus, bonus_name="Fort")

                    frame id "willpower_tracker" xsize 380 align(1.0, 0.6):
                        hbox:
                            text "Willpower" text_align 1.0 align (0.0, 0.5) style style.codex_panel_text
                            frame id "WPBoxes" xsize 280 align (1.0, 0.5):
                                $ clearWillpower = pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)
                                use trackerline("Willpower", pc.will.boxes, clearWillpower, pc.will.spf_damage)

                    frame id "status_effect" xsize 380 align(1.0, 0.8):
                        $ pc_status = pc.status
                        hbox:
                            text "Status" text_align 1.0 xfill False xsize 50 align (0.0, 0.5) style style.codex_panel_text # codex_panel_button_text
                            frame id "status_text" xsize 280 align (1.0, 0.5):
                                text "[pc_status]" text_align 0.0 style style.codex_panel_text


# Every codex panel uses this
screen codexBaseFrame(tabname):
    $ clan_token = str(state.pc.clan).lower() if state.pc.clan else None
    window id "codex_window_main" align (0.82, 0.0) xysize (gui.codex_base_width, 740) padding (5, 10):
        style_prefix "codex_panel"
        background Frame("gui/nvl.png", 5, 5, 5, 5)
        modal False

        if clan_token:
            image "gui/symbols/clan_bg_[clan_token]_red.png" align (0.5, 0.5) alpha 0.25 zoom 1.0
        vbox xfill True yfill True spacing 15:
            use codexTopRow()
            frame id "main_pane_container" xalign 0.5 xysize (gui.codex_inner_width, 580) padding (0, 0) background None:
                transclude
            use codex_tabs(tabname)


# Character sheet showing scores, i.e. attributes and skills
screen codexScoresPage(*args):
    tag codexPage
    modal False

    $ pc, cfg = renpy.store.state.pc, renpy.store.cfg

    use codexBaseFrame("scores"):  # TODO: re-implement tooltips, resize everything
        style_prefix "codex_panel"  # Current pane heights: 240 + 14 + 325 in baseframe of 580
        vbox spacing 14:
            frame id "pane_attributes" xalign 0.5 ysize 240:
                use buildGrid(gui.GRID_ROWS_ALLSCORES, gui.GRID_COLS_ATTRS, gui.GRID_ROWS_ALLSCORES * gui.GRID_COLS_ATTRS, _transpose = True):
                    for count, attr in enumerate(pc.attrs):
                        $ keydex = cfg.REF_ATTR_ORDER[count]
                        frame style style.utility_frame:
                            $ the_score = pc.attrs[keydex]
                            use dotchain(keydex, the_score, tooltip="{}".format(cfg.TOOLTIP_TABLE[attr]))
            frame id "pane_skills" xalign 0.5 ysize 325:
                use buildGrid(gui.GRID_ROWS_ALLSCORES, gui.GRID_COLS_SKILLS, gui.GRID_ROWS_ALLSCORES * gui.GRID_COLS_SKILLS, _transpose = True):
                    for count, skill in enumerate(pc.skills):
                        $ keydex = cfg.REF_SKILL_ORDER[count]
                        frame style style.utility_frame:
                            use dotchain(keydex, pc.skills[keydex], tooltip="{}".format(cfg.TOOLTIP_TABLE[skill]))


# Character sheet tab showing discipline powers and maybe merits/Hardestadt loresheet if I get that far
screen codexPowersPage(*args):  # current pane heights: 120 + 14 + 445 = 579/580
    tag codexPage
    modal False
    python:
        cfg, pc = renpy.store.cfg, renpy.store.state.pc
        merits_and_flaws = [bg for bg in pc.backgrounds if bg[cfg.REF_TYPE] in (cfg.REF_BG_FLAW, cfg.REF_BG_MERIT)]
        resmax, r_action = cfg.VAL_RESONANCE_GUI_MAX, None
    use codexBaseFrame("powers"):
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_merits" xalign 0.5 ysize 120 padding (10, 10):
                # #$ leng = len(pc.merits)
                # if len(merits_and_flaws) > 0: # Shouldn't be more than 3
                #     hbox xfill True:
                #         for count in range(min(len(merits_and_flaws), cfg.MERIT_DISPLAY_MAX)):
                #             frame style style.utility_frame yfill True:
                #                 python:
                #                     m_f = merits_and_flaws[count]
                #                     dcolor = "red" if m_f[cfg.REF_TYPE] == cfg.REF_BG_FLAW else "red"
                #                     altname = m_f[cfg.REF_TYPE]
                #                     tooltip = m_f[cfg.REF_TOOLTIP] if cfg.REF_TOOLTIP in m_f else None
                #                 use dotchain(m_f[cfg.REF_BG_NAME], m_f[cfg.REF_DOTS], altname=altname, dcolor=dcolor, format="merit", tooltip=tooltip)
                # else:
                #     hbox xfill True yalign 0.5:
                #         text "Nothing special unlocked or discovered." text_align 0.5 xalign 0.5 yalign 0.5
                use buildGrid(3, 2, 6):
                    for reso in state.resonances:
                        python:
                            if cfg.DEV_MODE:
                                r_action = Function(state.feed_resonance, reso=reso, intensity=cfg.RINT_ACUTE)
                        use xpbar(state.resonances[reso], resmax, reso, color=cfg.VAL_RESON_COLORS[reso], _action=r_action)

            frame id "pane_disciplines" xalign 0.5 ysize 445 padding (0, 0):
                $ unlocked_ds = pc.disciplines.get_unlocked()
                # hbox xfill True:
                # NOTE: Viewport doesn't take a background property; it can't be substituted for a frame
                if len(unlocked_ds) > 4:
                    viewport scrollbars "horizontal" mousewheel "horizontal" draggable True:# child_size (300, None):
                        use codexPowersSubpage(unlocked_ds, len(unlocked_ds))
                else:
                    frame padding(0, 0) style style.utility_frame:
                        use codexPowersSubpage(unlocked_ds, len(unlocked_ds))


screen codexPowersSubpage(unlocked_ds, num_ds):
    $ total_scroll_width = (num_ds * 390) + ((num_ds - 1) * 0) + 20
    hbox spacing 1 xfill False xsize total_scroll_width:
        for ul_disc in unlocked_ds:
            frame style style.utility_frame xsize 396 yfill True padding(6, 0, 0, 0):#
                vbox spacing 7:
                    hbox ysize 60 spacing 0:
                        $ uldl, dt_toggle = str(ul_disc).lower(), ToggleScreen("powerSelectTree", None, dname=ul_disc)
                        image "gui/symbols/disc_bg_[uldl].png" align (0.0, 0.5) alpha 0.9 zoom 0.1
                        use dotchain(ul_disc, pc.disciplines.levels[ul_disc], tooltip="tooltip tbd", _action=dt_toggle, dfsize=(334, 60))
                    $ ul_disc_prefix = "POWER_{}".format(str(ul_disc).upper())
                    $ disc_powers = cfg.REF_DISC_POWER_TREES[ul_disc]
                    $ power_list = pc.disciplines.pc_powers[ul_disc]
                    for i, pkey in enumerate(power_list):
                        $ power = power_list[pkey] if power_list[pkey] else None
                        if power:
                            frame style style.utility_frame left_padding 5 xalign 0.0:
                                textbutton "{}. {}".format(i+1, power):
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
            frame id "pane_opinions" xalign 0.5 ysize 205 padding (10, 15):
                use buildGrid(gui.REP_GRID_ROWS, gui.REP_GRID_COLS, len(state.opinions), 10, 15):
                    for count, reputation in enumerate(state.opinions):
                        use repbar(state.opinions[reputation], cfg.REP_MAX, cfg.REP_VALUE_ADJUST, includeName=reputation)
            frame id "pane_backgrounds" xalign 0.5 ysize 360 padding (10, 10):
                #use buildGrid(gui.BG_GRID_ROWS, gui.BG_GRID_COLS, len(pc.backgrounds), 10, 10):
                use buildGrid(3, 3, len(pc.backgrounds), 10, 10):
                    for count, bg in enumerate(pc.backgrounds):
                        python:
                            dcolor = "dark" if bg[cfg.REF_TYPE] == cfg.REF_BG_FLAW else "red"
                            altname, flaw_text = None,  " Flaw" if bg[cfg.REF_TYPE] == cfg.REF_BG_FLAW else ""
                            if cfg.REF_SUBTYPE in bg:
                                altname = "{}{}".format(bg[cfg.REF_SUBTYPE], flaw_text)
                        if bg[cfg.REF_TYPE] == cfg.REF_BG_PAST:
                            use hovertext("Mortal past: {}".format(bg[cfg.REF_BG_NAME]), bg[cfg.REF_DESC], "big")
                        elif bg[cfg.REF_TYPE] == cfg.REF_PREDATOR_TYPE:
                            use hovertext("Predator Type: {}".format(bg[cfg.REF_BG_NAME]), bg[cfg.REF_DESC], "big")
                        elif bg[cfg.REF_TYPE] == cfg.REF_VENTRUE_PALATE:
                            $ vfp_desc = bg[cfg.REF_DESC] + " Feeding on anyone else requires an effort of will."
                            use hovertext("Ventrue \"palate\": {}".format(bg[cfg.REF_BG_NAME]), vfp_desc, "big")
                        else:
                            use dotchain(
                                bg[cfg.REF_BG_NAME], bg[cfg.REF_DOTS], altname=altname, dcolor=dcolor, format="merit",
                                tooltip=bg[cfg.REF_DESC]
                            )


# Shows character inventory and case notes, i.e. quest log
screen codexCasefilesPage(*args):
    tag codexPage
    modal False

    use codexBaseFrame("casefiles"):
        style_prefix "codex_panel"
        vbox spacing 14:
            frame id "pane_inventory" xalign 0.5 ysize 250:
                use buildGrid(4, 3, len(state.pc.inventory), 5, 10):
                    for count, item in enumerate(state.pc.inventory.items):
                        frame style style.utility_frame:
                            python:
                                color_str = game.Item.ITEM_COLOR_KEYS[item.item_type]
                                title = item
                                tooltip = item.desc
                                itype = item.item_type

                                if itype == game.Item.IT_MONEY:
                                    title = "{}: ${:.2f}".format(item, item.quantity)
                                elif itype == game.Item.IT_WEAPON or itype == game.Item.IT_FIREARM:
                                    if item.concealable:
                                        concealed = "You have your trusty forged CCW permit, just in case."
                                    else:
                                        concealed = "This is an open carry state, right?"
                                    lethal = " (Lethal)" if itype == game.Item.IT_FIREARM or item.lethality >= 2 else ""
                                    tooltip = "+{}{}\n\n{}\n\n{}".format(item.dmg_bonus, lethal, concealed, tooltip)

                            textbutton str(title) + " {color=[color_str]}(" + str(itype) + "){/color}":
                                text_style style.codex_hoverable_text
                                action NullAction()
                                hovered ShowTransient("hovertip", None, "{}".format(tooltip), tt_width=600)
                                unhovered Hide("hovertip", None)
            frame id "pane_case_log" xalign 0.5 ysize 315 padding (10, 10):
                text "This will basically be a quest log."


# Glossary of VtM lore and game mechanics
screen codexInfoPage(*args):
    tag codexPage
    modal False

    use codexBaseFrame("info"):
        style_prefix "codex_panel"
        frame id "glossary" ysize 579 padding (10, 10):
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
screen powerSelectTree(dname, *args):
    tag codexPage
    modal False

    python:
        clan_token, dname_lower = str(state.pc.clan).lower() if state.pc.clan else None, str(dname).lower()
        d_powers_list, disc_level = state.get_power_choices(dname), state.pc.disciplines.levels[dname]
        access_token = state.pc.disciplines.access[dname]
        title_tt = cfg.TOOLTIP_TABLE[access_token]

    window id "powertree_main" align (0.82, 0.1) xysize (gui.codex_base_width, 700) padding (15, 10):
        style style.codex_panel_frame
        background Frame("gui/nvl.png", 5, 5, 5, 5)
        modal False

        image "gui/symbols/disc_bg_[dname_lower].png" align (0.5, 0.5) alpha 0.25 zoom 1.0
        fixed xysize (20, 20) align (0.95, 0.0):
            use hovertext("x", "Close", "big", _action=ToggleScreen("powerSelectTree", None))
        vbox spacing 2 xfill True:
            use dotchain("{} Powers  ({})".format(dname, access_token), disc_level, dfsize=(1000, 50), tooltip=title_tt)
            # truecenter for alignment was the source of error
            # truecenter is a transform object and passing it to align was invalid syntax, since align expects a tuple
            for i in range(1, 6):
                hbox spacing 5:
                    python:
                        sw, dcolor, tooltip = cfg.SCORE_WORDS[i], "dark", cfg.TOOLTIP_TABLE[cfg.TT_LOCKED]
                        p_chosen, previous_p_chosen, d_action = None, None, None
                        if i > 1:
                            previous_p_chosen = state.pc.disciplines.pc_powers[dname][cfg.SCORE_WORDS[i-1]]
                        if disc_level >= i:
                            dcolor = "red"
                            p_chosen = state.pc.disciplines.pc_powers[dname][sw]
                            if p_chosen:
                                tooltip = "Chosen power: {}".format(p_chosen)
                            elif previous_p_chosen or i == 1:
                                tooltip = cfg.TOOLTIP_TABLE[cfg.TT_POWER_AVAILABLE]
                            else:
                                tooltip = cfg.TOOLTIP_TABLE[cfg.TT_NEED_PREVIOUS]
                        elif disc_level == i - 1:
                            can_purchase, xp_next, tooltip_add, confirm_prompt = state.meet_next_level_reqs(dname, access_token)
                            if tooltip_add:
                                 # tooltip += " - {}".format(tooltip_add)
                                 tooltip = tooltip_add
                            if can_purchase:
                                disc_resonance = cfg.REF_DISC_BLURBS[dname][cfg.REF_RESONANCE]
                                d_action = Confirm(
                                    confirm_prompt, yes=[
                                        Function(state.buy_next_disc_level, dname, disc_resonance, xp_next),
                                        Play("sound", audio.mutation_jingle)
                                    ], no=None, confirm_selected=False
                                )
                    use dotchain("Level {}".format(i), i, dfsize=(250, 40), dcolor=dcolor, tooltip=tooltip, _action=d_action)
                    if p_chosen:
                        use hovertext(p_chosen, "tooltip tbd!")
                    elif disc_level >= i or i == 1:
                        python:
                            # pick = None
                            if disc_level >= i and (i == 1 or previous_p_chosen):
                                tooltip = "We could have this power..."
                        vbox spacing 5:
                            for power in d_powers_list[sw]:
                                python:
                                    pick, tooltip2 = None, tooltip
                                    amalg = pc.disciplines.amalgam_reqs_met(dname, power)[0]
                                    prereq = pc.disciplines.power_prereqs_met(dname, power)[0]
                                    if not amalg:
                                        req_disc_data = cfg.REF_DISC_AMALGAM_REQS[power]
                                        req_disc_msg = "{} level {}".format(req_disc_data[0], req_disc_data[1])
                                        tooltip2 = "{}\n\n({})".format(cfg.TOOLTIP_TABLE[cfg.TT_AMALGAM_LOCK], req_disc_msg)
                                    elif not prereq:
                                        req_power = cfg.REF_DISC_POWER_PREREQS[power]
                                        tooltip2 = "{}\n\n({})".format(cfg.TOOLTIP_TABLE[cfg.TT_PREREQ_LOCK], req_power)
                                    if disc_level >= i and (i == 1 or previous_p_chosen) and amalg and prereq:
                                        pick = Confirm("Unlock {}?".format(power), [
                                                Function(pc.disciplines.unlock_power, dname, power),
                                                Play("sound", audio.mutation_jingle)
                                            ], no=None, confirm_selected=False
                                        )
                                use hovertext("--> {}".format(power), tooltip=tooltip2, _action=pick)


# Used to display tooltips
screen hovertip(tip, tt_width=400, tt_height=200, *args):
    frame background Frame("gui/frame_original.png", Borders(5, 5, 5, 5)):  # TODO: make a different version of gui/frame.png for this with full opacity
        xmaximum tt_width
        ymaximum tt_height
        # ysize 80
        pos renpy.get_mouse_pos()
        padding (15, 30)
        text "[tip]" size 18 xfill True yfill True


# Should show at 3 hunger or more and intensify
screen hungerlay():
    tag hunger_overlay
    modal False

    if renpy.store.state.pc.hunger > renpy.store.cfg.HUNGER_MAX_CALM:
        $ score_word = renpy.store.cfg.SCORE_WORDS[int(renpy.store.state.pc.hunger)]
        image "gui/overlay/hunger_[score_word].png" align (0.5, 0.5) xysize (1920, 1080)
    else:
        image None


# Codex styles
style codex_panel_frame:
    modal False
    xsize gui.codex_inner_width
    padding (10, 5)
    background Frame("gui/frame.png", Borders(2, 2, 2, 2))

style codex_panel_viewport:
    modal False
    xsize gui.codex_inner_width
    padding (10, 5)

style codex_panel_text:
    size 16 # 16
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

# NOTE original as of 2023/02/17
# style codex_hoverable_text:
#     size 20
#     hover_color "#ffebeb"
#     insensitive_color "552323"
#     selected_color "#ee3737"
#     color "#ffbbbb"
#     text_align 0.5

style codex_hoverable_text:
    size 20
    hover_color "#ffebeb"
    selected_insensitive_color "ff0000" #552323
    insensitive_color "552323" #552323
    selected_color "#ee3737"
    idle_color "#ffbbbb"
    text_align 0.5

style codex_hoverable_text_small:
    size 16
    hover_color "#ffebeb"
    insensitive_color "552323"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.0

style codex_hoverable_text_big:
    size 24
    hover_color "#ffebeb"
    insensitive_color "552323"
    selected_color "#ee3737"
    color "#ffbbbb"
    text_align 0.0
