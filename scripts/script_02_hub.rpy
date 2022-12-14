label haven:

    label .hub_entry:

        python:
            cfg, state = renpy.store.cfg, renpy.store.state
            pc = state.pc

        stop sound
        scene bg haven basic

        if not state.clan_chosen:
            $ state.outside_haven = False
            jump clan_choice

        if pc.frenzied_bc_hunger:
            jump hunger_frenzy

        # Standard haven hub menu

        if state.outside_haven and state.daybreak:
            "You make it back to your haven just in time, collapsing on the floor in a dead heap."
            $ state.outside_haven = False
            call new_night from hub_entry_sunrise_nick_of_time
        elif state.outside_haven:
            "You make your way back to your haven. Here you can safely rest. For now, anyway."
            $ state.outside_haven = False
        elif state.daybreak:
            call new_night from hub_entry_sunrise_indoors


    label .hub_main:

        python:
            can_hunt = (pc.hunger > cfg.HUNGER_MIN) or (pc.humanity < cfg.KILLHUNT_HUMANITY_MAX and pc.hunger > cfg.HUNGER_MIN_KILL)
            must_hunt = pc.hunger >= cfg.HUNGER_MAX
            relax_menu_text = "I think I'll just take it easy for the rest of the night."
            relax_text = "relaxing with your favorite streaming service."  # TODO: make this dependent on background
            if state.hunted_tonight:
                hunt_phrase = "I'm {i}still{/i} hungry. I want to try another hunt."
            elif state.tried_hunt_tonight:
                hunt_phrase = "I still need to hunt. Last one didn't go so well, but I {i}have{/i} to try again."
            else:
                hunt_phrase = "I need to hunt."

            should_shelter = True if state.clock.hours < 4 else False
            must_shelter = True if state.clock.hours < 2 else False
            can_hunt = (can_hunt and not must_shelter)
            other_activities = not must_hunt and not must_shelter
            if must_shelter and must_hunt:
                relax_menu_text = "I'm so hungry I can barely think, but it's almost sunrise. Going out now is certain death."
            elif must_shelter and pc.hunger > cfg.HUNGER_MAX_CALM:
                relax_menu_text = "I need to feed, but I need to not burn to death even more."
            elif must_shelter:
                relax_menu_text = "It's almost sunrise. Time to turn in for the day."
            elif pc.hunger > cfg.HUNGER_MAX_CALM:
                relax_menu_text = "I think I'd better stay in for the rest of the night."

        menu:
            "What do you want to do?"

            "[hunt_phrase]" if can_hunt:
                $ state.outside_haven = True

                scene bg domain basic

                call expression "hunt_" + str(pc.predator_type).replace(" ", "_").lower() pass (None) from main_hub_hunt

            "Stagnation and complacency are a Kindred's most insidious enemies. What can I do to improve?" if other_activities:
                "get swole son"
                call pass_time(1) from training_test1

            "Enemies closing in. Need to counterattack before I'm cornered." if other_activities:
                "sortie"
                call pass_time(2) from sortie_test1

            # TODO: Option for mending here

            "[relax_menu_text]" if must_shelter or not must_hunt:
                if pc.hunger > 2:
                    $ relax_text = "doing your best to ignore the Hunger."
                    $ spf_will_mend = min(pc.attrs[cfg.AT_COM], pc.attrs[cfg.AT_RES])
                else:
                    $ spf_will_mend = max(pc.attrs[cfg.AT_COM], pc.attrs[cfg.AT_RES])
                if not must_hunt:
                    "You spend the remainder of the night in calm repose, [relax_text]"
                    $ pc.will.mend(cfg.DMG_FULL_SPF, min(spf_will_mend, state.clock.hours))
                else:
                    "You spend what remains of the night on the edge of madness. When the daysleep takes you it's a mercy."

                call pass_time(None, in_shelter=True)

        jump post_activity_main


label post_activity_main:

    # $ state.clock.update()

    "(Post-activity evaluation)"

    label .eval:

        if state.daybreak and state.outside_haven:
            call sun_threat from post_activity_exposed_1
            call new_night from post_activity_exposed_2
        elif state.daybreak:
            call new_night from post_activity_safe

        if not state.outside_haven:
            jump haven.hub_entry

        "(add options other than return to haven here, which have to come with their own time evaluations)"

        python:
            sun_risk = False
            hours_left = state.clock.hours
            if hours_left > 6:
                pae_menu_phrase = "The night is still young."
            elif hours_left > 3:
                pae_menu_phrase = "You probably have enough time to squeeze in one more errand and make it back to your haven."
            elif hours_left > 1:
                pae_menu_phrase = "You still have time to make it back to your haven."
            elif hours_left > 0:
                sun_risk = True
                hours_token = cfg.SCORE_WORDS[hours_left]
                pae_menu_phrase = "Just {} hour{} left until ".format(hours_token, "s" if hours_left != 1 else "")
                pae_menu_phrase += "sunrise. Should you risk it, or try to find temporary shelter nearby?"
            else:
                raise ValueError("Pass_time isn't working properly if we get here!")

        "You look to the sky, and check your watch."

    label .outside_haven_hub_menu:

        menu:
            "[pae_menu_phrase]"

            "I'll head back to my haven.":

                if state.clock.hours < 2:
                    "(test to see if you make it back in time goes here)"  # TODO: add test results
                    call pass_time(1, in_shelter=True) from pae_temp_1a # TODO: temporary, replace this
                else:
                    call pass_time(1, in_shelter=True) from pae_temp_1b # TODO: temporary? replace this?

                jump haven.hub_entry

            "I think I'd better find someplace to sleep nearby." if sun_risk:
                label .hunker_down:

                    "Finding shelter out in the wilds of the city is a risky proposition. But it can't always be avoided."

                    call sun_threat.shelter_search(False, 1) from post_activity_hunker_down

                    $ sun_damage = _return

                    "(did they burn?) :: [sun_damage]"  # TODO: add test results here

                    call new_night from post_activity_hunker_down_post

            "(Do something else option #1)" if not sun_risk:
                "(not implemented)"
                call pass_time(2) from pae_temp_2

            "(Do something else option #2)" if not sun_risk:
                "(not implemented)"
                call pass_time(4) from pae_temp_3

    # jump haven.hub_entry
    # jump post_activity_main.outside_haven_hub_menu
    jump post_activity_main.eval
