label haven:

    label .main:

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

        if state.outside_haven:
            "You make your way back to your haven. Here you can safely rest. For now, anyway."
            $ state.outside_haven = False

    label .post_main:

        $ can_hunt = (pc.hunger > cfg.HUNGER_MIN) or (pc.humanity < cfg.KILLHUNT_HUMANITY_MAX and pc.hunger > cfg.HUNGER_MIN_KILL)
        $ must_hunt = pc.hunger >= cfg.HUNGER_MAX
        $ hunt_phrase = "I'm {i}still{/i} hungry. I want to try another hunt." if state.hunted_tonight else "I need to hunt."
        $ relax_text = " relaxing with your favorite streaming service."  # TODO: make this dependent on background

        menu:
            "What do you want to do?"

            "[hunt_phrase]" if can_hunt:
                $ state.outside_haven = True
                call expression "hunt_" + str(pc.predator_type).replace(" ", "_").lower() pass (None) from main_hub_hunt

            "Stagnation and complacency are a Kindred's deadliest enemies. What can I do to improve?" if not must_hunt:
                "get swole son"
                call pass_time(1) from training_test1

            "Enemies closing in. Need to counterattack before I'm cornered." if not must_hunt:
                "sortie"
                call pass_time(2) from sortie_test1

            # TODO: Option for mending here

            "I think I'll just take it easy for the rest of the night." if not must_hunt:
                if pc.hunger > 2:
                    $ relax_test = " doing your best to ignore the Hunger."
                    $ spf_will_mend = min(pc.attrs[cfg.AT_COM], pc.attrs[cfg.AT_RES])
                else:
                    $ spf_will_mend = max(pc.attrs[cfg.AT_COM], pc.attrs[cfg.AT_RES])
                "You spend the remainder of the night in calm repose, [relax_text]"
                $ pc.will.mend(cfg.DMG_FULL_SPF, min(spf_will_mend, state.clock.hours))
                call pass_time(None, in_shelter=True)

        jump haven.main
