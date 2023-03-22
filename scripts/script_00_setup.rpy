init 1 python:

    import random

label init_setup:

    scene bg city main_menu

    python:  # Default game variables initialized here.
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game
        audio, flavor = renpy.store.audio, renpy.store.flavor
        # FlavorPack = game.FlavorPack
        Weapon = game.Weapon

        state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)
        state.pc.inventory = game.Inventory(owner_name=state.pc.name)
        state.statusfx, state.staffing = state.StatusFX(pc=state.pc), game.TempAgency()
        # state.give_item(game.Item(game.Item.IT_MONEY, "Cash", key="Money", tier=0, num=15, desc="Cash on hand."))
        state.give_item(state.get_random_cash())
        state.clock = state.GameClock(1, 9)
        state.diceroller_creation_count = 0

    if cfg.DEV_MODE and cfg.DEV_TESTING_COMBAT:
        $ state.blood_surge_enabled = True
        show screen bl_corner_panel
        jump devtests.dt_combat_a1
    elif cfg.DEV_MODE and cfg.DEV_WHATEVER:
        $ print("lakjsdfldksjfldskfjalsdkfjkl")
    elif cfg.DEV_MODE and cfg.DEV_TESTING_HUNT_FLAVOR:
        $ state.blood_surge_enabled = True
        show screen bl_corner_panel
        jump devtests.dt_hunting_b1

    jump intro


init 1 python in state:

    cfg, utils, game = renpy.store.cfg, renpy.store.utils, renpy.store.game

    pt_flavor_pack = None


label say_script(text_pack):

    $ say_lines = text_pack if type(text_pack) in (list, tuple) else [text_pack]
    while len(say_lines) > 0:
        $ next_line = say_lines.pop(0)
        if type(next_line) in (list, tuple):
            $ speaker, speech = next_line
        elif type(next_line) in (dict,):
            $ speaker = next_line["speaker"] if "speaker" in next_line else narrator
            $ speech = next_line["speech"] if "speech" in next_line else "..."
        # elif utils.percent_chance(30):
        #     $ speaker, speech = james, next_line
        else:
            $ speaker, speech = narrator, next_line

        speaker "[speech]"

    return


label devtests:

    label .dt_hunting_b1:
        python:
            pc = state.pc

        menu:
            "Which hunting test build?"

            "Brujah Alley Cat":
                "..."
                python:
                    state.apply_test_build("Veteran", cfg.CLAN_BRUJAH, cfg.PT_ALLEYCAT, cfg.DISC_CELERITY)

            "Nosferatu Bagger":
                "..."
                python:
                    state.apply_test_build("Nursing Student", cfg.CLAN_NOSFERATU, cfg.PT_BAGGER, cfg.DISC_OBFUSCATE)

            "Ravnos Farmer":
                "..."
                python:
                    state.apply_test_build("Grad Student", cfg.CLAN_RAVNOS, cfg.PT_FARMER, cfg.DISC_ANIMALISM)

            "Ventrue Siren":
                "..."
                python:
                    state.apply_test_build("Influencer", cfg.CLAN_VENTRUE, cfg.PT_SIREN, cfg.DISC_PRESENCE)

    label .dt_hunting_b2:

        "feeeeeek"

        call expression "hunt_" + str(pc.predator_type).replace(" ", "_").lower() pass (None) from hunting_test_base1

        "feckkkkk"

        $ outcome, time_spent = _return

        jump .dt_hunting_b2

    #

    label .dt_combat_a1:
        python:
            Item, Weapon, Inventory = game.Item, game.Weapon, game.Inventory
            pc = state.pc

        menu:
            "Which test build?"

            "Brujah Brawler":
                "..."
                python:
                    state.apply_test_build("Star Athlete", cfg.CLAN_BRUJAH, cfg.PT_ALLEYCAT, cfg.DISC_POTENCE)
                    # potence 3, celerity 1
                    pc.disciplines.set_discipline_level(cfg.DISC_CELERITY, 3)
                    pc.disciplines.set_discipline_level(cfg.DISC_PRESENCE, 3)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_FATALITY)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_PROWESS)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_RAGE)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_TWITCH)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_SPEED)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_BLINK)
                    pc.disciplines.unlock_power(cfg.DISC_PRESENCE, cfg.POWER_PRESENCE_AWE)
                    pc.disciplines.unlock_power(cfg.DISC_PRESENCE, cfg.POWER_PRESENCE_DAUNT)
                    pc.disciplines.unlock_power(cfg.DISC_PRESENCE, cfg.POWER_PRESENCE_SCARYFACE)
                    #

            "Ravnos Trickster (not implemented yet)":
                "I said NOT IMPLEMENTED YET genius"
                jump .dt_combat_a1

            "Ventrue Gangster":
                "..."
                python:
                    state.apply_test_build("Veteran", cfg.CLAN_VENTRUE, cfg.PT_ALLEYCAT, cfg.DISC_CELERITY)
                    # knife = Weapon(Item.IT_WEAPON, "Butterfly Knife", tier=1, dmg_bonus=1, concealable=True)
                    knife = state.gift_weapon(key="butterfly1")
                    gun = state.gift_gun(key="glock19")
                    state.give_item(knife, gun, equip_it=True)
                    pc.inventory.equip(gun, Inventory.EQ_WEAPON_ALT)
                    # celerity 1, fortitude 2, dominate 1
                    pc.disciplines.unlock_power(cfg.DISC_FORTITUDE, cfg.POWER_FORTITUDE_HP)
                    pc.disciplines.unlock_power(cfg.DISC_FORTITUDE, cfg.POWER_FORTITUDE_TOUGH)
                    pc.disciplines.unlock_power(cfg.DISC_DOMINATE, cfg.POWER_DOMINATE_COMPEL)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_TWITCH)

            "Nurse Ratchet":
                "..."
                python:
                    state.apply_test_build("Nursing Student", cfg.CLAN_NOSFERATU, cfg.PT_BAGGER, cfg.DISC_OBFUSCATE)
                    scalpel = state.gift_weapon(key="realscalpel")
                    state.give_item(scalpel, equip_it=True)
                    pc.disciplines.set_discipline_level(cfg.DISC_ANIMALISM, 0)
                    pc.disciplines.set_discipline_level(cfg.DISC_OBFUSCATE, 4)
                    pc.disciplines.set_discipline_level(cfg.DISC_POTENCE, 3)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_FADE)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_STEALTH)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_LAUGHINGMAN)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_VANISH)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_SUPERJUMP)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_PROWESS)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_MEGASUCK)


    label .dt_combat_a2:

        "fook"

        call combat_test_scenario_1 from sortie_test_2_direct

        "feck"

        jump .dt_combat_a2


#
