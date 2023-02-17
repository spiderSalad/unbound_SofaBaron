label combat_test_scenario_1:

    python:
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game
        pc, CAction, Entity, Item, Weapon = state.pc, game.CAction, game.Entity, game.Item, game.Weapon

        if not hasattr(state, "arena") or not state.arena:
            state.arena = game.BattleArena()

        npc_brawler, npc_shooter = game.NPCFighter.FT_BRAWLER, game.NPCFighter.FT_SHOOTER
        npc_wildcard, npc_ftpc = game.NPCFighter.FT_WILDCARD, game.NPCFighter.FT_FTPC

        # Fighters are brawlers by default.
        ally1 = game.NPCFighter(name="Ally1", physical=5)
        ally2 = game.NPCFighter(name="Ally2", ftype=npc_shooter, physical=4)
        ally2.npc_weapon = utils.get_random_list_elem(state.loot_tables[Item.IT_FIREARM].items) #[0]
        enemy1 = game.NPCFighter(name="Enemy1", physical=7)
        enemy1.npc_weapon = utils.get_random_list_elem(state.loot_tables[Item.IT_WEAPON].items) #[0]
        enemy2 = game.NPCFighter(name="Enemy2", ftype=npc_ftpc, physical=6, turns=2)
        enemy2.npc_weapon = state.loot_tables[Item.IT_FIREARM].items[0]
        enemy3 = game.NPCFighter(name="Enemy3", ftype=npc_wildcard, physical=4, turns=3)
        e3_wep = utils.get_random_list_elem(state.loot_tables[Item.IT_WEAPON].items) #[0]
        e3_gun = utils.get_random_list_elem(state.loot_tables[Item.IT_FIREARM].items) #[0]
        enemy3.inventory = Inventory(e3_wep, e3_gun)
        e4_kwargs = {cfg.SK_ATHL: 4}
        enemy4 = game.NPCFighter(name="Enemy4", ctype=cfg.CT_VAMPIRE, physical=8, **e4_kwargs)


    label .start:

        python:
            state.arena.reset()
            state.arena.register_combatants(pc_team=[ally1, ally2], enemy_team=[enemy1, enemy2, enemy3, enemy4])
            state.arena.set_position((ally2, -2))
            state.arena.start()
            state.set_hunger(0)
            chained_action = None

        "Battle commencing..."

    label .exec_turn:

        python:
            if not chained_action:
                print("Standard turn progression (whose turn is it anyway?)")
                # upp_next = state.arena.get_upp_next()
                # TODO: Add validating logic here, possible integrate into class
            else:
                print("We have a chain action: {}".format(chained_action))
            atk_action, def_action = state.arena.get_next_contest(chained_action)
            no_contest = False
            if atk_action is None and def_action is None:
                no_contest = True

        if no_contest and state.arena.battle_end:
            "Battle concluded!"
            jump .end
        elif no_contest and not state.arena.get_up_next():
            "Next round..."
        elif not state.arena.get_up_next():
            $ raise ValueError("Shouldn't reach here; if the queue is empty there shouldn't be a contest.")
        elif no_contest:
            $ up_next = state.arena.get_up_next()
            if up_next and up_next.dead:
                call .action_chain(report=state.arena.process_new_result(None, None, None)) from no_contest_pnr
                $ chained_action = _return
            else:
                jump .player_attack_menu
        elif def_action is None:
            jump .player_defense_menu
        elif chained_action:
            call roll_control(
                atk_action.pool, def_action.pool, active_a=atk_action, response_a=def_action, pc_defending=False
            ) from combat_chain_atk
            $ roll_result = _return
            call .action_chain(report=state.arena.process_new_result(roll_result, atk_action, def_action)) from chain_pnr
            $ chained_action = _return
        else:
            $ atk_pool, def_pool = "pool{}".format(atk_action.pool), "pool{}".format(def_action.pool)
            call roll_control(atk_pool, def_pool, active_a=atk_action, response_a=def_action, pc_defending=None) from combat_npc_vs_npc
            $ roll_result = _return
            call .action_chain(report=state.arena.process_new_result(roll_result, atk_action, def_action)) from npc_vs_npc_pnr
            $ chained_action = _return

        jump .exec_turn

    label .action_chain(report=None):  # Prints out report from previous action and checks if there's another on the "stack".

        if report is None:
            return None
        $ report_type = type(report)
        if report_type in (list, tuple):
            $ report_str, interject_action = report
        elif report_type is str:
            $ report_str, interject_action = report, None
        else:
            $ report_str, interject_action = None, report
        $ print("report_str = {}\ninterject_action = {}".format(report_str, interject_action))
        if report_str:
            "[report_str]"
        return interject_action

    label .player_attack_menu:

        python:
            at_range, close_enough = [], []
            for enemy in state.arena.enemies:
                if enemy.dead or enemy.appears_dead:
                    continue
                if enemy.current_pos == pc.current_pos:
                    close_enough.append(enemy)
                else:
                    at_range.append(enemy)
            can_attack_ranged = not pc.engaged and state.pc_has_ranged_attack()
            can_throw = can_attack_ranged and (pc.held.throwable or pc.sidearm.throwable)
            can_use_disc = not state.used_disc_this_turn
            can_use_2p_disc = can_use_disc and pc.can_rouse()
            mend_prompt = "I should mend my wounds."
            if pc.crippled:
                mend_prompt = "I'm in bad shape. I need to mend my wounds while I still can."
            state.menu_label_backref = "combat_test_scenario_1.player_attack_menu"

        menu:
            "What will you do?"

            "Rush 'em!" if at_range and not pc.engaged:
                "you rush toward an enemy over yonder"
                call .pc_attack_special_rush(None) from pc_rush_default
                $ pc_atk = _return

            # TODO: Soaring Leap should help here.
            "Soaring leap!" if at_range and pc.has_disc_power(cfg.POWER_POTENCE_SUPERJUMP):
                "soaring leap rush still in testing"
                call .pc_attack_special_rush(cfg.POWER_POTENCE_SUPERJUMP) from pc_rush_soaring_leap
                $ pc_atk = _return

            # TODO: Blink should be usable here as a MELEE_ENGAGE + MELEE_ATTACK in one move.
            "Blink!" if at_range and can_use_2p_disc and pc.has_disc_power(cfg.POWER_CELERITY_BLINK):
                "blink rush/attack not implemented yet"
                call .pc_attack_special_rush(cfg.POWER_CELERITY_BLINK) from pc_rush_blink
                $ pc_atk = _return

            "Melee Attack" if close_enough:
                python:
                    target = utils.get_random_list_elem(close_enough) #[0]
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
                $ target = utils.get_random_list_elem(at_range) #[0]
                $ pa_pool, dmg_type = "dexterity+firearms", cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                $ pc_atk = CAction(CAction.RANGED_ATTACK, target, user=pc, pool=pa_pool)
                # TODO: get rid of these dmg_type variables and other shit that's not being used
                "you draw your gun and fire at a random enemy"

            "Throw something!" if at_range and can_throw:
                python:
                    target = utils.get_random_list_elem(at_range) #[0]
                    pa_pool, dmg_type = "dexterity+athletics", cfg.DMG_AGG if target.mortal else cfg.DMG_SPF
                    throw_sidearm = not pc.held.throwable and pc.sidearm.throwable
                    pc_atk = CAction(
                        CAction.RANGED_ATTACK, target, user=pc, pool=pa_pool,
                        use_sidearm=throw_sidearm
                    )
                "you throw something, like maybe a knife"

            "[mend_prompt]" if pc.hp.spf_damage > 0 and not state.mended_this_turn and pc.can_rouse():
                call mend.superficial from combat_menu_mend_spf
                $ state.mended_this_turn = True
                jump expression state.menu_label_backref

            "Pass turn":
                "Reckless haste will get you killed..."
                jump .pass_turn_submenu

            "Run":
                "run awaaaaaaaaaaaayyyyy"
                jump .end

            "test option jaaaaaaaaaa":
                "oooooooooooo"

        jump .pc_attack_post

    label .pc_attack_special_rush(rush_power_used=None):
        python:
            target = utils.get_random_list_elem(at_range) #[0]
            pa_pool = "strength+athletics/dexterity+athletics"
            pc_atk = CAction(CAction.MELEE_ENGAGE, target, user=pc, pool=pa_pool)
            pc_atk.unarmed_power_used = utils.unique_append(pc_atk.unarmed_power_used, rush_power_used, sep=", ")
            print("Rushing with power = {}".format(rush_power_used))

        return pc_atk

    label .pc_attack_special_test_ex2:

        pass

    label .pc_attack_post(atk_override=None):

        python:
            state.menu_label_backref = None
            npc_def = target.defend(pc, pc_atk)
            def_pool = "pool{}".format(npc_def.pool)
        call roll_control(pa_pool, def_pool, active_a=pc_atk, response_a=npc_def) from combat_pc_atk
        $ roll_result = _return
        call .action_chain(report=state.arena.process_new_result(roll_result, pc_atk, npc_def)) from pc_atk_pnr
        $ chained_action = _return

        jump .exec_turn

    label .pass_turn_submenu:

        menu:
            "...but so will inaction. Better decide quickly."

            "I do nothing. (Passes the turn.)":
                $ pc_atk, roll_result = CAction(CAction.NO_ACTION, None, user=pc), None
                "You bide your time and wait for a better opportunity to present itself."

            "I want to fall back into the shadows." if pc.current_pos > -2:
                $ pc_atk, roll_result = CAction(CAction.FALL_BACK, None, user=pc), None
                beast "Planning something special?"

            "No, I can't let myself hesitate.":
                jump .player_attack_menu

        call .action_chain(report=state.arena.process_new_result(roll_result, pc_atk, None)) from pc_pass_turn_pnr
        $ chained_action = _return

        jump .exec_turn

    label .player_defense_menu:

        python:
            atk_pool, attacker = "pool{}".format(atk_action.pool), atk_action.user
            can_use_melee_counter = attacker.current_pos == pc.current_pos
            can_use_ranged_counter = not pc.engaged and state.pc_has_ranged_attack()
            alt_ranged_counter = not pc.engaged and state.pc_has_ranged_attack(check_alt=True)
            can_throw = alt_ranged_counter and (pc.held.throwable or pc.sidearm.throwable)
            sideshoot_prompt = "Try to draw my sidearm and return fire!  (Dexterity/Wits + Firearms)"
            can_use_disc = not state.used_disc_this_turn
            can_use_2p_disc = can_use_disc and pc.can_rouse()
            can_flit = Entity.SE_FLEETY in pc.status_effects and not state.fleet_dodge_this_turn
            state.menu_label_backref = "combat_test_scenario_1.player_defense_menu"
            defend_prompt = game.Flavorizer.prompt_combat_defense(atk_action)

        menu:
            # TODO: specify attack type/weapon, for narrative use later and for user benefit
            "[defend_prompt]"

            "Dodge  (Dexterity + Athletics)":  # Only defense that's always available.
                "you attempt to dodge"
                call .pc_defend_special_dodge(None) from pc_dodge_default
                $ pc_def = _return

            "Flit out of the way with supernatural speed  (Dexterity + Athletics + Celerity)" if can_flit:
                "you get to flitting and fleeting"
                # $ state.fleet_dodge_this_turn = True
                call .pc_defend_special_dodge(cfg.POWER_CELERITY_SPEED) from pc_dodge_fleetness

            # TODO: Blink should be usable here as an automatic DODGE with movement to different rank?
            "Blink out of the way!" if can_use_2p_disc and pc.has_disc_power(cfg.POWER_CELERITY_BLINK):
                "blink evade/escape not implemented yet"
                call .pc_defend_special_dodge(cfg.POWER_CELERITY_BLINK) from pc_dodge_blink
                $ pc_def = _return

            # TODO: Soaring Leap should be usable here as a boosted DODGE with movement to different rank
            "Soaring leap out of the way!" if pc.has_disc_power(cfg.POWER_POTENCE_SUPERJUMP):
                "soaring leap evade/escape not implemented yet"
                call .pc_defend_special_dodge(cfg.POWER_POTENCE_SUPERJUMP) from pc_dodge_soaring_leap
                $ pc_def = _return

            "Counterattack!\n(Dexterity + Combat / Strength + Combat)" if can_use_melee_counter:
                $ pd_pool = "dexterity+combat/strength+combat"
                $ pc_def = CAction(CAction.MELEE_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool)
                "you attempt a counterattack"
                # jump .pc_defend_post

            "Return fire!  (Dexterity + Firearms)" if can_use_ranged_counter:
                $ pd_pool = "dexterity+firearms"
                $ pc_def = CAction(CAction.RANGED_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool)
                "you bust back"
                # jump .pc_defend_post

            "[sideshoot_prompt]" if alt_ranged_counter and pc.sidearm.item_type == Item.IT_FIREARM:
                python:
                    pd_pool = "dexterity+firearms/wits+firearms"
                    pc_def = CAction(
                        CAction.RANGED_ATTACK, atk_action.user, user=pc, defending=True,
                        pool=pd_pool, use_sidearm=True
                    )

            "Throw something!" if can_throw:
                python:
                    pd_pool = "dexterity+athletics"
                    throw_sidearm = not pc.held.throwable and pc.sidearm.throwable
                    pc_def = CAction(
                        CAction.RANGED_ATTACK, atk_action.user, user=pc, defending=True,
                        pool=pd_pool, use_sidearm=throw_sidearm
                    )

            "test option":
                "dafuq 3024343"
                jump expression state.menu_label_backref

        jump .pc_defend_post

    label .pc_defend_special_dodge(dodge_power_used=None):
        python:
            pd_pool, rr_dodge = "dexterity+athletics", "dodge"
            if CAction.attack_is_gunshot(attacker, atk_action):
                if pc.has_disc_power(cfg.POWER_CELERITY_TWITCH, cfg.DISC_CELERITY):
                    rr_dodge = "celerity-dodge"
                    utils.log("Bullet-time! Gunshot dodging penalty waived.")
                else:
                    pd_pool += "+-{}".format(cfg.BULLET_DODGE_PENALTY)
            pc_def = CAction(CAction.DODGE, None, user=pc, defending=True, pool=pd_pool)
            pc_def.unarmed_power_used = utils.unique_append(pc_def.unarmed_power_used, dodge_power_used, sep=", ")
            print("Dodging with power = {}".format(dodge_power_used))

        return pc_def

    label .pc_defend_post:

        $ state.menu_label_backref = None
        call roll_control(atk_pool, pd_pool, active_a=atk_action, response_a=pc_def, pc_defending=True) from combat_pc_def
        $ roll_result = _return
        call .action_chain(report=state.arena.process_new_result(roll_result, atk_action, pc_def)) from pc_def_pnr
        $ chained_action = _return

        jump .exec_turn

    label .end:

        "Returning...?"

    return


label devtests:

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
                    knife = Weapon(Item.IT_WEAPON, "Butterfly Knife", tier=1, dmg_bonus=1, concealable=True)
                    gun = Weapon(Item.IT_FIREARM, "Glock 19", tier=2, dmg_bonus=2)  # glock 19 uses 9mm ammo
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
                    scalpel = Weapon(Item.IT_WEAPON, "\"Scalpel\"", tier=3, dmg_bonus=3)
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
