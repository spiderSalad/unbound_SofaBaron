init 1 python:

    import random

label init_setup:

    scene bg city main_menu

    python:  # Default game variables initialized here.
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game

        state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)
        state.pc.inventory = game.Inventory(owner_name=state.pc.name)
        state.statusfx = state.StatusFX(pc=state.pc)
        # state.give_item(game.Item(game.Item.IT_MONEY, "Cash", key="Money", tier=0, num=15, desc="Cash on hand."))
        state.give_item(state.get_random_cash())
        state.clock = state.GameClock(1, 9)
        state.staffing = game.TempAgency()
        state.diceroller_creation_count = 0

    if cfg.DEV_MODE:
        python:
            state.blood_surge_enabled = True

        show screen bl_corner_panel
        jump devtests.dt_combat_a1

    jump intro
