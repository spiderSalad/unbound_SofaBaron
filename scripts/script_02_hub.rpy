label haven:

    label .main:

        python:
            cfg, state = renpy.store.cfg, renpy.store.state
            pc = state.pc

        stop sound
        scene bg haven basic

        if not state.clan_chosen:
            jump clan_choice

        # Standard haven hub menu

        "You make your way back to your haven. Here you can safely rest. For now, anyway."

    label .post_main:

        $ can_hunt = (pc.hunger > cfg.HUNGER_MIN) or (pc.humanity < cfg.KILL_HUNT_HUMANITY_THRESHOLD_INC and pc.hunger > cfg.HUNGER_MIN_KILL)

        menu:
            "What do you want to do?"

            "I need to hunt." if can_hunt:
                call expression "hunt_" + str(pc.predator_type).replace(" ", "_").lower() pass (None) from main_hub_hunt

            "Stagnation and complacency are a Kindred's deadliest enemies. What can I do to improve?":
                "get swole son"

            "Enemies closing in. Need to counterattack before I'm cornered.":
                "sortie"

        jump haven.main
