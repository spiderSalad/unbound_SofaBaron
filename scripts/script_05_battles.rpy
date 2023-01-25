label combat_test_scenario_1:

    python:
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game
        pc, CAction, Weapon = state.pc, game.CAction, game.Weapon

        if not hasattr(state, "arena") or not state.arena:
            state.arena = game.BattleArena()

        # Fighters are brawlers by default.
        fighter1 = game.NPCFighter(name="Ally1", physical=5)
        fighter2 = game.NPCFighter(name="Ally2", ftype=game.NPCFighter.FT_SHOOTER, physical=4)
        fighter3 = game.NPCFighter(name="Enemy1", physical=7)
        fighter4 = game.NPCFighter(name="Enemy2", ftype=game.NPCFighter.FT_FTPC, physical=6)
        fighter5 = game.NPCFighter(name="Enemy3", ftype=game.NPCFighter.FT_WILDCARD, physical=4)

    label .start:

        python:
            state.arena.reset()
            state.arena.register_combatants(pc_team=[fighter1, fighter2], enemy_team=[fighter3, fighter4, fighter5])
            state.arena.set_position((fighter2, -2))
            state.arena.start()

        "Battle commencing..."

    label .exec_turn:

        python:
            # Whose turn is it anyway?
            up_next = state.arena.get_up_next()
            # TODO: Add validating logic here, possible integrate into class
            atk_action, def_action = state.arena.get_next_contest()
            no_contest = False
            if atk_action is None and def_action is None:
                no_contest = True

        if no_contest and state.arena.battle_end:
            "Battle concluded!"
            jump .end
        elif no_contest and not state.arena.get_up_next():
            "Next round..."
            # jump .exec_turn
        elif no_contest:
            jump .player_attack_menu
        elif def_action is None:
            jump .player_defense_menu
        else:
            $ atk_pool, def_pool = "pool{}".format(atk_action.pool), "pool{}".format(def_action.pool)
            call roll_control(atk_pool, def_pool, npc_only=True) from combat_gen_npc_vs_npc_test
            $ roll_result = _return
            $ report = state.arena.process_new_result(roll_result, atk_action, def_action)
            "[report]"

        jump .exec_turn

    label .player_attack_menu:

        python:
            at_range, close_enough = [], []
            for enemy in state.arena.enemies:
                if enemy.current_pos == pc.current_pos:
                    close_enough.append(enemy)
                else:
                    at_range.append(enemy)
            can_attack_ranged = not pc.engaged and state.pc_has_ranged_attack()
            can_throw = can_attack_ranged and (pc.held.throwable or pc.sidearm.throwable)

        menu:
            "What will you do?"

            "Rush 'em!" if at_range and not pc.engaged:
                python:
                    target = utils.get_random_list_elem(at_range)[0]
                    pa_pool = "strength+athletics/dexterity+athletics"
                    pc_atk = CAction(CAction.MELEE_ENGAGE, target, user=pc, pool=pa_pool)
                "you rush toward an enemy over yonder"

            # TODO: Blink should be usable here as a MELEE_ENGAGE + MELEE_ATTACK in one move.

            # TODO: Soaring Leap should help here.

            "Melee Attack" if close_enough:
                python:
                    target = utils.get_random_list_elem(close_enough)[0]
                    using_deadly_weapon, using_heavy_weapon = True, True  # TODO: add something for this
                    using_feral_weapons, using_vicissitude_weapon = False, False
                    if using_deadly_weapon:
                        dmg_type = cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                        pa_pool = "strength+combat" if using_heavy_weapon else "dexterity+combat"
                    elif using_feral_weapons:
                        dmg_type = cfg.DMG_AGG if target.mortal else cfg.DMG_FULL_SPF
                        pa_pool = "dexterity+combat/strength+combat" if using_vicissitude_weapon else "strength+combat"
                    elif using_vicissitude_weapon:
                        dmg_type = cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                        pa_pool = "dexterity+combat/strength+combat"
                    else:
                        dmg_type = cfg.DMG_SPF
                        pa_pool = "strength+combat"
                    pc_atk = CAction(CAction.MELEE_ATTACK, target, user=pc, pool=pa_pool)
                "you attack a random target in melee"

            "Shoot at them" if at_range and can_attack_ranged:
                $ target = utils.get_random_list_elem(at_range)[0]
                $ pa_pool, dmg_type = "dexterity+firearms", cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                $ pc_atk = CAction(CAction.RANGED_ATTACK, target, user=pc, pool=pa_pool)
                "you draw your gun and fire at a random enemy"

            "Throw something!" if at_range and can_throw:
                python:
                    target = utils.get_random_list_elem(at_range)[0]
                    pa_pool, dmg_type = "dexterity+athletics", cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                    pc_atk = CAction(
                        CAction.RANGED_ATTACK, target, user=pc, pool=pa_pool,
                        use_held_weapon=pc.held.throwable, use_sidearm=pc.sidearm.throwable
                    )
                "you throw something, like maybe a knife"

            "Pass turn":
                "Reckless haste will get you killed..."
                jump .pass_turn_submenu

            "Run":
                "run awaaaaaaaaaaaayyyyy"
                jump .end

    label .pc_attack_post:

        $ npc_def_action = target.defend(pc, pc_atk)
        $ def_pool = "pool{}".format(npc_def_action.pool)
        call roll_control(pa_pool, def_pool) from combat_gen_pc_attack_test1
        $ roll_result = _return
        $ report = state.arena.process_new_result(roll_result, pc_atk, npc_def_action)

        "[report]"

        jump .exec_turn

    label .pass_turn_submenu:

        menu:
            "...but so will inaction. Better decide quickly."

            "I do nothing. (Passes the turn.)":
                $ pc_atk, roll_result = CAction(CAction.NO_ACTION, None, user=pc), None
                "You bide your time and wait for a better opportunity to present itself."

            "I want to fall back into the shadows." if pc.current_pos > -2:
                $ pc_atk = CAction(CAction.FALL_BACK, None, user=pc)
                $ roll_result = None
                beast "Planning something special?"

            "No, I can't let myself hesitate.":
                jump .player_attack_menu

        $ report = state.arena.process_new_result(roll_result, pc_atk, None)

        # "[report]"

        jump .exec_turn

    label .player_defense_menu:

        python:
            atk_pool, attacker = "pool{}".format(atk_action.pool), atk_action.user
            can_counter_melee = attacker.current_pos == pc.current_pos
            can_counter_ranged = not pc.engaged and state.pc_has_ranged_attack()
            can_throw = can_counter_ranged and (pc.held.throwable or pc.sidearm.throwable)

        menu:
            # TODO: specify attack type/weapon, for narrative use later and for user benefit
            "You're being attacked by [attacker.name]! Oh shit what you gonna do?!"

            "Dodge  (Dexterity + Athletics)":  # Only defense that's always available.
                python:
                    pd_pool, rr_dodge = "dexterity+athletics", "dodge"
                    if CAction.attack_is_gunshot(attacker, atk_action):
                        if pc.has_disc_power(cfg.POWER_CELERITY_TWITCH, cfg.DISC_CELERITY):
                            rr_dodge = "celerity-dodge"
                            print("Bullet-time! Gunshot dodging penalty waived.")
                        else:
                            pd_pool += "+-{}".format(cfg.BULLET_DODGE_PENALTY)
                    pc_def = CAction(CAction.DODGE, None, user=pc, defending=True, pool=pd_pool)
                "you attempt to dodge"
                # jump .pc_defend_post

            "Counterattack!\n(Dexterity + Combat / Strength + Combat)" if can_counter_melee:
                $ pd_pool = "dexterity+combat/strength+combat"
                $ pc_def = CAction(CAction.MELEE_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool)
                "you attempt a counterattack"
                # jump .pc_defend_post

            "Return fire!  (Dexterity + Firearms)" if can_counter_ranged:
                $ pd_pool = "dexterity+firearms"
                $ pc_def = CAction(CAction.RANGED_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool)
                "you bust back"
                # jump .pc_defend_post

            "Throw something!" if can_throw:
                python:
                    pd_pool = "dexterity+athletics"
                    pc_def = CAction(
                        CAction.RANGED_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool,
                        use_held_weapon=pc.held.throwable, use_sidearm=pc.sidearm.throwable
                    )

    label .pc_defend_post:

        call roll_control(atk_pool, pd_pool, npc_attacker=True) from combat_gen_pc_defense_test2
        $ roll_result = _return
        $ report = state.arena.process_new_result(roll_result, atk_action, pc_def)

        "[report]"

        jump .exec_turn

    label .end:

        "Returning...?"

    return


label devtests:

    label .dt_combat_a1:
        python:
            Supply, Weapon, Inventory = game.Supply, game.Weapon, game.Inventory
            pc = state.pc

        menu:
            "Which test build?"

            "Brujah Brawler":
                "..."
                python:
                    state.apply_test_build("Star Athlete", cfg.CLAN_BRUJAH, cfg.PT_ALLEYCAT, cfg.DISC_POTENCE)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_FATALITY)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_PROWESS)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_RAGE)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_TWITCH)

            "Ravnos Trickster (not implemented yet)":
                "I said NOT IMPLEMENTED YET genius"
                jump .dt_combat_a1

            "Ventrue Gangster":
                "..."
                python:
                    state.apply_test_build("Veteran", cfg.CLAN_VENTRUE, cfg.PT_ALLEYCAT, cfg.DISC_CELERITY)
                    knife = Weapon(Supply.IT_WEAPON, "Butterfly Knife", tier=1, dmg_bonus=1, concealable=True)
                    gun = Weapon(Supply.IT_FIREARM, "Glock 19", tier=2, dmg_bonus=2)  # glock 19 uses 9mm ammo
                    state.give_item(knife, gun, equip_it=True)
                    pc.inventory.equip(gun, Inventory.EQ_WEAPON_ALT)
                    pc.disciplines.unlock_power(cfg.DISC_FORTITUDE, cfg.POWER_FORTITUDE_HP)
                    pc.disciplines.unlock_power(cfg.DISC_FORTITUDE, cfg.POWER_FORTITUDE_TOUGH)
                    pc.disciplines.unlock_power(cfg.DISC_DOMINATE, cfg.POWER_DOMINATE_COMPEL)
                    pc.disciplines.unlock_power(cfg.DISC_CELERITY, cfg.POWER_CELERITY_TWITCH)

            "Nurse Ratchet":
                "..."
                python:
                    state.apply_test_build("Nursing Student", cfg.CLAN_NOSFERATU, cfg.PT_BAGGER, cfg.DISC_OBFUSCATE)
                    scalpel = Weapon(Supply.IT_WEAPON, "\"Scalpel\"", tier=3, dmg_bonus=3)
                    state.give_item(scalpel, equip_it=True)
                    pc.disciplines.set_discipline_level(cfg.DISC_ANIMALISM, 0)
                    pc.disciplines.set_discipline_level(cfg.DISC_OBFUSCATE, 2)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_FADE)
                    pc.disciplines.unlock_power(cfg.DISC_OBFUSCATE, cfg.POWER_OBFUSCATE_STEALTH)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_SUPERJUMP)
                    pc.disciplines.unlock_power(cfg.DISC_POTENCE, cfg.POWER_POTENCE_PROWESS)


    label .dt_combat_a2:

        "fook"

        call combat_test_scenario_1 from sortie_test_2_direct

        "feck"

        jump .dt_combat_a2
