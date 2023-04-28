init 1 python:

    import random

label init_setup:

    scene bg city main_menu

    python:  # Default game variables initialized here.
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game
        audio, flavor = renpy.store.audio, renpy.store.flavor
        Weapon = game.Weapon

        state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)
        state.pc.inventory = game.Inventory(owner_name=str(state.pc))
        state.statusfx, state.staffing = state.StatusFX(pc=state.pc), game.TempAgency()
        # state.give_item(game.Item(game.Item.IT_MONEY, "Cash", key="Money", tier=0, num=15, desc="Cash on hand."))
        state.give_item(state.get_random_cash())
        state.clock = state.GameClock(1, 9)
        state.diceroller_creation_count = 0

    if cfg.DEV_MODE:
        call dev_tests from initial_setup_dev_check

    jump intro


label say_script(text_pack):

    $ say_lines = text_pack if type(text_pack) in (list, tuple) else [text_pack]
    while len(say_lines) > 0:
        $ next_line = say_lines.pop(0)
        if type(next_line) in (list, tuple):
            $ speaker, speech = next_line
        elif type(next_line) in (dict,):
            $ speaker = next_line["speaker"] if "speaker" in next_line else narrator
            $ speech = next_line["speech"] if "speech" in next_line else "..."
        else:
            $ speaker, speech = narrator, next_line

        speaker "[speech]"

    return


#
