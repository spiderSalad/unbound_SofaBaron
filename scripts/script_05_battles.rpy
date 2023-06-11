init 1 python:

    cfg, utils, audio = renpy.store.cfg, renpy.store.utils, renpy.store.audio
    state, game, flavor = renpy.store.state, renpy.store.game, renpy.store.flavor


label combat_test_scenario_1:

    python:
        cfg, utils, state, game = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.game
        audio, flavor = renpy.store.audio, renpy.store.flavor
        pc, CombAct, CombatAction, Item, Weapon = state.pc, game.CombAct, game.CombatAction, game.Item, game.Weapon
        Entity, NPCFighter = game.Entity, game.NPCFighter
        crew, opps = None, None

        temp_names = {
            NPCFighter.FT_BRAWLER: ("Guard", "Hitter"),
            NPCFighter.FT_SHOOTER: ("Soldier", "Shooter"),
            NPCFighter.FT_WILDCARD: ("Droog", "Mook"),
            NPCFighter.FT_FTPC: ("Traitor", "Assassin"),
            NPCFighter.FT_ESCORT: ("VIP", "Noncombatant")
        }

        # state.arena.register_combatants(pc_team=[ally1, ally2, ally3], enemy_team=[enemy1, enemy2, enemy3, enemy4])
        del crew, opps
        crew, opps = state.staffing.roster_test_1(3, pc_team=True), state.staffing.roster_test_1(4)
        for i, ent in enumerate(crew):
            if '#' in ent.name:
                ent.name = "bud{}-{}".format(i+1, temp_names[ent.ftype][0])
        for i, ent in enumerate(opps):
            if '#' in ent.name:
                ent.name = "nme{}-{}".format(i+1, temp_names[ent.ftype][1])
        state.set_hunger(0)

    call combat_encounter.battle_setup(crew, opps) from combat_test_1_begin

    return


label pulse_combat_encounter:

    $ num_encounters = 0
    while state.enc_opp_sets:
        $ opps, enc_num = state.enc_opp_sets.pop(), num_encounters + 1
        $ opps_who, opps_team = opps
        $ num_encounters += 1
        $ print("\n\nHEY", state.current_party, opps_team)
        call combat_encounter.battle_setup(state.current_party, opps_team) from encounter_pulse_battle_1

    return

label combat_encounter:

    label .battle_setup(crew, opps):

        python:
            pc, CombAct, CombatAction, Item, Weapon = state.pc, game.CombAct, game.CombatAction, game.Item, game.Weapon
            Entity, NPCFighter = game.Entity, game.NPCFighter

            if not hasattr(state, "arena") or not state.arena:
                state.arena = game.BattleArena()

            state.arena.reset()
            state.arena.register_combatants(pc_team=crew, enemy_team=opps)  # TODO: update this to take optional starting positions
            # state.arena.set_position((ally2, -2))
            state.arena.start()
            chained_action = None

        "Battle commencing..."

    label .turn_loop_start:

        python:
            if not chained_action:
                utils.log("Standard turn progression (whose turn is it anyway?)")
            else:
                utils.log("Chain action by {} ({})".format(chained_action.user, chained_action.action_type))
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
                call .handle_post_action(report=state.arena.process_new_result(None, None, None)) from no_contest_pnr
                $ chained_action = _return
            else:
                jump .player_attack_menu
        elif def_action is None:
            if atk_action.target and atk_action.target.is_pc:
                jump .player_defense_menu
            $ roll_result = None
            if atk_action.action_type == CombAct.DISENGAGE:
                call roll_control(atk_action.pool, "diff1", active_a=None) from combat_uncontested_disengage
                $ roll_result = _return
            $ non_action = CombatAction(CombAct.NO_ACTION, None, user=None)
            call .handle_post_action(report=state.arena.process_new_result(roll_result, atk_action, non_action))
            $ chained_action = _return
        elif chained_action:
            call roll_control(atk_action.pool, def_action.pool, active_a=atk_action, response_a=def_action) from combat_chain_atk
            $ roll_result = _return
            call .handle_post_action(report=state.arena.process_new_result(roll_result, atk_action, def_action)) from chain_pnr
            $ chained_action = _return
        else:
            $ atk_pool, def_pool = "pool{}".format(atk_action.pool), "pool{}".format(def_action.pool)
            call roll_control(atk_pool, def_pool, active_a=atk_action, response_a=def_action) from combat_npc_vs_npc
            $ roll_result = _return
            call .handle_post_action(report=state.arena.process_new_result(roll_result, atk_action, def_action)) from npc_vs_npc_pnr
            $ chained_action = _return

        jump .turn_loop_start

    label .handle_post_action(report=None):  # Prints out report from previous action and checks if there's another on the "stack".

        if report is None:
            return None
        python:
            report_type, report_readout, follow_up_action, obits = type(report), None, None, []
            if report_type not in (list, tuple):
                report = (report,)
            for i, item in enumerate(report):
                if type(item) is str and not report_readout:
                    report_readout = item
                elif isinstance(item, game.CombAct):
                    follow_up_action = item
                elif isinstance(item, (game.NPCFighter, game.PlayerChar)):
                    if item.dead:
                        obits.append(flavor.prompt_combat_death(item, pc_hunger=state.pc.hunger))
            death_numero, sanity_loop_limit = 0, 10

        if report_readout and str(report_readout).startswith(game.CombatLog.REF_HEADER):
            $ report_readout = report_readout[len(game.CombatLog.REF_HEADER):]
            "{size=28}[report_readout]{/size}"
        elif report_readout:
            "[report_readout]"
        while death_numero < len(obits) and death_numero < sanity_loop_limit:
            $ obituary = obits[death_numero]
            $ death_numero += 1
            "[obituary]"

        return follow_up_action

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
            can_attack_ranged = not pc.engaged_by and state.pc_has_ranged_attack()
            can_throw = can_attack_ranged and (pc.held.throwable or pc.sidearm.throwable)
            can_use_disc = not state.used_disc_this_turn
            can_use_2p_disc = can_use_disc and pc.can_rouse()
            pc_cornered, grap_pns = state.arena.is_cornered(pc) or pc.grappled_by, None
            grapple_prompt, grapple_confirm_txt = "Grab someone close by (grapple)", "You square yourself up to grab the nearest enemy..."
            if pc.grappled_by:
                at_range, close_enough, pc_cornered = [], pc.grappled_by, True
                can_attack_ranged, can_throw = False, False
                grapple_prompt, grapple_confirm_txt = "Get this motherfucker off me!", "You can't let yourself be manhandled like this."
            elif pc.grappling_with:
                grap_pns = pc.grappling_with[0].pronoun_set
                if len(pc.grappling_with) > 1:
                    grap_pns = cfg.PN_GROUP
                grapple_prompt = f'I\'ve got {grap_pns.PN_HER_HIM_THEM}, now to...'
                grapple_confirm_txt =  "So many possibilities, so little time."
            mend_prompt = "I should mend my wounds."
            if pc.crippled or pc.hp.agg_damage > 1:
                mend_prompt = "I'm in bad shape. I need to mend my wounds while I still can."
            disengage_default_prompt = "I need to back up, find a better vantage point."
            if pc.engaged_by:
                disengage_default_prompt = "I need to back out of this mess and reorient myself."
            state.menu_label_backref = f'{cfg.COMBAT_LABEL_MAIN}.player_attack_menu'
        menu:
            "What will you do?"

            "Rush 'em!" if at_range and not pc.engaged_by:
                "you rush toward an enemy over yonder"
                call .pc_attack_special_rush(None) from pc_rush_default
                $ pc_atk = _return

            # TODO: Soaring Leap should help here.
            "Soaring leap!" if at_range and pc.has_disc_power(cfg.POWER_POTENCE_SUPERJUMP):
                "soaring leap rush still in testing"
                call .pc_attack_special_rush(cfg.POWER_POTENCE_SUPERJUMP) from pc_rush_soaring_leap
                $ pc_atk = _return

            "Blink!" if at_range and can_use_2p_disc and pc.has_disc_power(cfg.POWER_CELERITY_BLINK):
                "blink rush/attack not implemented yet"
                call .pc_attack_special_rush(cfg.POWER_CELERITY_BLINK) from pc_rush_blink
                $ pc_atk = _return

            "Melee Attack" if close_enough and not pc.grappled_by:
                python:
                    target = utils.get_random_list_elem(close_enough) #[0]
                    using_deadly_weapon, using_heavy_weapon = True, True  # TODO: add something for this
                    using_feral_weapons, using_vicissitude_weapon = False, False
                    if using_deadly_weapon:
                        pa_pool = "strength+combat" if using_heavy_weapon else "dexterity+combat"
                    elif using_feral_weapons:
                        pa_pool = "dexterity+combat/strength+combat" if using_vicissitude_weapon else "strength+combat"
                    elif using_vicissitude_weapon:
                        pa_pool = "dexterity+combat/strength+combat"
                    else:
                        pa_pool = "strength+combat"
                    pc_atk = CombatAction(CombAct.MELEE_ATTACK, target, user=pc, pool=pa_pool)
                "you attack a random target in melee"

            "[grapple_prompt]" if close_enough:
                $ pain_check = not pc.grappled_by
                # call .combat_pain_points(crippled_check=pain_check, shocked_check=pain_check) from combat_pc_attack_menu_grapple_1
                # if not _return:
                #     jump expression state.menu_label_backref
                "[grapple_confirm_txt]"
                call .grapple_submenu from player_basic_grapple
                $ grapple_choice = _return
                if grapple_choice is None:
                    jump expression state.menu_label_backref
                python:
                    targets = pc.engaged_by if pc.engaged_by else close_enough
                    target, pa_pool = utils.get_random_list_elem(targets), "strength+combat"
                    if grapple_choice in (CombAct.GRAPPLE_BITE, CombAct.GRAPPLE_BITE_PLUS) and target not in pc.grappling_with:
                        pa_pool = f'{pa_pool}+-{abs(cfg.BITE_ATTACK_PENALTY)}'
                    print(f'grapple_choice = {grapple_choice}')
                    pc_atk = CombatAction(CombAct.MELEE_ATTACK, target, user=pc, pool=pa_pool, grapple_type=grapple_choice)
                    # TODO: grapple defenses, breaking off on dodge?

            "Shoot at them" if at_range and can_attack_ranged:
                $ target = utils.get_random_list_elem(at_range) #[0]
                $ pa_pool = "dexterity+firearms"
                $ pc_atk = CombatAction(CombAct.RANGED_ATTACK, target, user=pc, pool=pa_pool)
                "you draw your gun and fire at a random enemy"

            "Throw something!" if at_range and can_throw:
                python:
                    target = utils.get_random_list_elem(at_range) #[0]
                    pa_pool = "dexterity+athletics"
                    throw_sidearm = not pc.held.throwable and pc.sidearm.throwable
                    pc_atk = CombatAction(
                        CombAct.RANGED_ATTACK, target, user=pc, pool=pa_pool,
                        use_sidearm=throw_sidearm
                    )
                "you throw something, like maybe a knife"

            "[mend_prompt]" if pc.hp.spf_damage > 0 and not state.mended_this_turn and pc.can_rouse():
                call mend.superficial from combat_menu_mend_spf
                $ state.mended_this_turn = True
                jump expression state.menu_label_backref

            "[disengage_default_prompt]" if not pc_cornered:
                "you try and slink back into the shadows"
                call .pc_attack_special_disengage(None) from pc_disengage_default
                $ pc_atk = _return

            "I can Soaring Leap back to a better position." if not pc_cornered and pc.has_disc_power(cfg.POWER_POTENCE_SUPERJUMP):
                "jump back"
                call .pc_attack_special_disengage(cfg.POWER_POTENCE_SUPERJUMP) from pc_disengage_soaring_leap
                $ pc_atk = _return

            "Blink backwards!" if not pc_cornered and can_use_2p_disc and pc.has_disc_power(cfg.POWER_CELERITY_BLINK):
                "blink disengage"
                call .pc_attack_special_disengage(cfg.POWER_CELERITY_BLINK) from pc_disengage_blink
                $ pc_atk = _return

            "Pass turn" if not pc.grappled_by:
                "Reckless haste will get you killed..."
                if cfg.DEV_MODE and devtest.DEV_COMBAT_AUTO_PASS:
                    $ pc_atk, roll_result = CombatAction(CombAct.NO_ACTION, None, user=pc), None
                    jump .auto_pass
                jump .pass_turn_submenu

            "Run" if not pc.grappled_by:
                # TODO: test for escaping
                if True:
                    "run awaaaaaaaaaaaayyyyy"
                    $ state.arena.post_battle_cleanup(block_healing=True)
                else:
                    "But you can't get away, can you?"
                jump .end

        jump .pc_attack_post

    label .pc_attack_special_rush(rush_power_used=None):
        python:
            target = utils.get_random_list_elem(at_range) #[0]
            pa_pool = "strength+athletics/dexterity+athletics"
            pc_atk = CombatAction(CombAct.MELEE_ENGAGE, target, user=pc, pool=pa_pool)
            pc_atk.unarmed_power_used = utils.unique_append(pc_atk.unarmed_power_used, rush_power_used, sep=", ")
            free_blink = cfg.DEV_MODE and (cfg.FREE_BLINK or cfg.FREE_DISCIPLINES)

        if rush_power_used == cfg.POWER_CELERITY_BLINK and not free_blink:
            call roll_control.rouse_check() from pc_rush_blink_rouse

        return pc_atk

    label .pc_attack_special_disengage(disengage_power_used=None):
        python:
            target = pc.engaged_by[-1] if pc.engaged_by else None
            pa_pool = "wits+clandestine/dexterity+athletics"
            pc_atk = CombatAction(CombAct.DISENGAGE, target, user=pc, pool=pa_pool)
            pc_atk.unarmed_power_used = utils.unique_append(pc_atk.unarmed_power_used, disengage_power_used, sep=", ")
            free_blink = cfg.DEV_MODE and (cfg.FREE_BLINK or cfg.FREE_DISCIPLINES)

        if disengage_power_used == cfg.POWER_CELERITY_BLINK and not free_blink:
            call roll_control.rouse_check() from pc_disengage_blink_rouse

        return pc_atk

    label .pc_attack_post(atk_override=None):

        python:
            state.menu_label_backref = None
            npc_def = target.defend(pc, pc_atk) if target else CombatAction(CombAct.NO_ACTION, None, user=None)
            def_pool = "pool{}".format(npc_def.pool) if npc_def and npc_def.pool else None
        # call roll_control(pa_pool, def_pool, active_a=pc_atk, response_a=npc_def) from combat_pc_atk
        call roll_control(pc_atk.pool, def_pool, active_a=pc_atk, response_a=npc_def) from combat_pc_atk_v2
        $ roll_result = _return
        $ print(f'pc_atk.grapple_action_type = {pc_atk.grapple_action_type}')
        call .handle_post_action(report=state.arena.process_new_result(roll_result, pc_atk, npc_def)) from pc_atk_pnr
        $ chained_action = _return

        jump .turn_loop_start

    label .pass_turn_submenu:  # Only jump here.

        menu:
            "...but so will inaction. Better decide quickly."

            "I do nothing. (Passes the turn.)":
                $ pc_atk, roll_result = CombatAction(CombAct.NO_ACTION, None, user=pc), None
                "You bide your time and wait for a better opportunity to present itself."

            "I want to fall back into the shadows." if pc.current_pos > -2:
                $ pc_atk, roll_result = CombatAction(CombAct.DISENGAGE, None, user=pc), None
                beast "Planning something special?"

            "No, I can't let myself hesitate.":
                jump .player_attack_menu

        label .auto_pass:

        call .handle_post_action(report=state.arena.process_new_result(roll_result, pc_atk, None)) from pc_pass_turn_pnr
        $ chained_action = _return

        jump .turn_loop_start

    label .combat_pain_points(crippled_check=True, shocked_check=True):
        if crippled_check and pc.crippled:
            "The moment the idea enters your mind, sharp spasms of pain run through your limbs as if in contemptuous response."

            "Your body is too broken to try anything like that. You'll need to mend yourself first."
            return False
        if shocked_check and pc.shocked:
            "Ringing ears, blurred vision... Whatever idea you just had isn't going to work while you're like this."
            return False
        return True

    label .grapple_submenu:

        python:
            would_combat_feed = pc.grappling_with and (pc.hunger > 0 or pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX)
            pc_grappled = pc.grappled_by and len(pc.grappled_by)
            megasuck = pc.has_disc_power(cfg.POWER_POTENCE_MEGASUCK, cfg.DISC_POTENCE)
            if not grap_pns:
                if pc.grappling_with and len(pc.grappling_with) > 1:
                    grap_pns = cfg.PN_GROUP
                elif pc.grappling_with:
                    grap_pns = pc.grappling_with[0].pronoun_set
                else:
                    grap_pns = cfg.PN_PERSON

        menu:
            "...and?"

            "Break [grap_pns.PN_HER_HIM_THEM]." if not pc_grappled and pc.grappling_with:
                $ grapple_choice = CombAct.GRAPPLE_DMG

            "Break free!" if pc_grappled:
                $ grapple_choice = CombAct.GRAPPLE_ESCAPE

            "Make [grap_pns.PN_HER_HIM_THEM] regret putting [grap_pns.PN_HER_HIS_THEIR] hands on me." if pc_grappled:
                $ grapple_choice = CombAct.GRAPPLE_ESCAPE_DMG

            "Bite":  # Bite attacks can be used when grappling or grappled, tentatively.
                $ grapple_choice = CombAct.GRAPPLE_BITE

            "Bite... then drain [grap_pns.PN_HER_HIM_THEM] like a fucking slurpie!" if pc.grappling_with and megasuck:
                $ grapple_choice = CombAct.GRAPPLE_BITE_PLUS

            "Drink." if not pc_grappled and would_combat_feed:
                $ grapple_choice = CombAct.GRAPPLE_DRINK

            "Drain [grap_pns.PN_HER_HIM_THEM] like a fucking smoothie!" if not pc_grappled and would_combat_feed and megasuck:
                $ grapple_choice = CombAct.GRAPPLE_DRINK_PLUS

            "Just hold [grap_pns.PN_HER_HIM_THEM] in place." if not pc_grappled:
                $ grapple_choice = CombAct.GRAPPLE_HOLD

            "On second thought...":
                $ grapple_choice = None

        return grapple_choice

    label .player_defense_menu:

        python:
            atk_pool, attacker = "pool{}".format(atk_action.pool), atk_action.user
            can_use_melee_counter = attacker.current_pos == pc.current_pos
            can_use_ranged_counter = not pc.engaged_by and state.pc_has_ranged_attack()
            alt_ranged_counter = not pc.engaged_by and state.pc_has_ranged_attack(check_alt=True)
            can_throw = alt_ranged_counter and (pc.held.throwable or pc.sidearm.throwable)
            pns = attacker.pronoun_set
            if atk_action.action_type in (CombAct.MELEE_ENGAGE, CombAct.MELEE_ATTACK):
                shoot_prompt = "Shoot {}.  (Dexterity + Firearms)".format(pns.PN_HER_HIM_THEM)
                sideshoot_prompt = "Try to draw my sidearm and shoot!  (Dexterity/Wits + Firearms)"
            else:
                shoot_prompt = "Return fire!  (Dexterity + Firearms)"
                sideshoot_prompt = "Try to draw my sidearm and return fire!  (Dexterity/Wits + Firearms)"
            can_use_disc = not state.used_disc_this_turn
            can_use_2p_disc = can_use_disc and pc.can_rouse()
            can_flit = state.StatusFX.has_buff(pc, Entity.SE_FLEETY) and not state.fleet_dodge_this_turn #in pc.status_effects
            can_weave = state.StatusFX.has_buff(pc, Entity.SE_WEAVING) and atk_action.action_type in (CombAct.RANGED_ATTACK,)
            weaving_prompt = "Dance out of the way. Bullets can't touch me unless I let them."
            if can_weave and atk_action.weapon_used and atk_action.weapon_used.item_type != Item.IT_FIREARM:
                weaving_prompt = "Nonchalantly dance out of the way."
            state.menu_label_backref = f'{cfg.COMBAT_LABEL_MAIN}.player_defense_menu'
            defend_prompt = flavor.prompt_combat_defense(atk_action)
            counter_attack_prompt, no_action_prompt = "Counter-attack!", "Just take it."
            if atk_action.action_type in (CombAct.DISENGAGE, CombAct.FALL_BACK, CombAct.ESCAPE_ATTEMPT):
                counter_attack_prompt = f'Catch {pns.PN_HER_HIM_THEM}!'
                no_action_prompt = f'Just let {pns.PN_HER_HIM_THEM} go.'

        menu:
            # TODO: specify attack type/weapon, for narrative use later and for user benefit
            "[defend_prompt]"

            "[no_action_prompt]" if cfg.DEV_MODE and devtest.DEV_FACETANK:
                $ pd_pool = "pool1"
                $ pc_def = CombatAction(CombAct.NO_ACTION, None, user=pc, defending=True, pool=None)

            "Dodge  (Dexterity + Athletics)":  # Only defense that's always available.
                "you attempt to dodge"
                call .pc_defend_special_dodge(None) from pc_dodge_default
                $ pc_def = _return
                $ print(f'\nbasic dodge | pc_def.pool = {pc_def.pool}')

            "Flit out of the way with supernatural speed  (Dexterity + Athletics + Celerity)" if can_flit:
                "you get to flitting and fleeting"
                # $ state.fleet_dodge_this_turn = True
                call .pc_defend_special_dodge(cfg.POWER_CELERITY_SPEED) from pc_dodge_fleetness
                $ pc_def = _return
                $ print(f'\nfleet dodge | pc_def.pool = {pc_def.pool}')

            "[weaving_prompt]" if can_weave:
                "there is no spoon, neo"
                call .pc_defend_special_dodge(cfg.POWER_CELERITY_MATRIX_DODGE) from pc_dodge_weaving
                $ pc_def = _return
                $ print(f'\nweaving dodge | pc_def.pool = {pc_def.pool}')

            "Blink out of the way!" if can_use_2p_disc and pc.has_disc_power(cfg.POWER_CELERITY_BLINK):
                "blink evade/escape not implemented yet"
                call .pc_defend_special_dodge(cfg.POWER_CELERITY_BLINK) from pc_dodge_blink
                $ pc_def = _return
                $ print(f'\nblink dodge | pc_def.pool = {pc_def.pool}')

            "Soaring leap out of the way!" if pc.has_disc_power(cfg.POWER_POTENCE_SUPERJUMP):
                "soaring leap evade/escape not implemented yet"
                call .pc_defend_special_dodge(cfg.POWER_POTENCE_SUPERJUMP) from pc_dodge_soaring_leap
                $ pc_def = _return
                $ print(f'\nsoaring leap dodge | pc_def.pool = {pc_def.pool}')

            "[counter_attack_prompt]\n(Dexterity + Combat / Strength + Combat)" if can_use_melee_counter:
                python:
                    pd_pool = "dexterity+combat/strength+combat"
                    pc_gat = CombAct.GRAPPLE_DMG if atk_action.user in pc.grappling_with else None
                    pc_def = CombatAction(CombAct.MELEE_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool, grapple_type=pc_gat)
                "you attempt a counterattack"
                # jump .pc_defend_post

            # TODO: later, add version of these for Arms of Ahriman.
            "Grab [pns.PN_HER_HIM_THEM]! (Grapple)" if can_use_melee_counter and not pc.grappled_by and attacker not in pc.grappling_with:
                # call .combat_pain_points from combat_pc_defend_menu_grapple_1
                # if not _return:
                #     jump expression state.menu_label_backref
                python:
                    pd_pool = "strength+combat"
                    pc_def = CombatAction(
                        CombAct.MELEE_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool,
                        grapple_type=CombAct.GRAPPLE_HOLD, lethality=0
                    )
                "you try to grab your attacker"

            "But while [pns.PN_SHES_HES_THEYRE] in my grip, I can..." if atk_action.user in pc.grappling_with:
                # call .combat_pain_points from combat_pc_defend_menu_grapple_2
                # if not _return:
                #     jump expression state.menu_label_backref
                "defending grapple against grappled opponent"
                call .grapple_submenu from player_basic_grapple_2_defend
                $ grapple_choice = _return
                if grapple_choice is None:
                    jump expression state.menu_label_backref
                python:
                    target, pd_pool = atk_action.user, "strength+combat"
                    pc_def = CombatAction(CombAct.MELEE_ATTACK, target, user=pc, pool=pd_pool, grapple_type=grapple_choice)

            "Bite [pns.PN_HER_HIM_THEM]!" if can_use_melee_counter and not pc.grappled_by and attacker in pc.grappling_with:
                python:
                    pd_pool = f'strength+combat+-{cfg.BITE_ATTACK_PENALTY}'
                    pc_def = CombatAction(
                        CombAct.MELEE_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool, grapple_type=CombAct.GRAPPLE_BITE
                    )
                "as your attacker tries to overpower you, you try to bite"

            "[shoot_prompt]" if can_use_ranged_counter:
                $ pd_pool = "dexterity+firearms"
                $ pc_def = CombatAction(CombAct.RANGED_ATTACK, atk_action.user, user=pc, defending=True, pool=pd_pool)
                "you bust back"
                # jump .pc_defend_post

            "[sideshoot_prompt]" if alt_ranged_counter and pc.sidearm.item_type == Item.IT_FIREARM:
                python:
                    pd_pool = "dexterity+firearms/wits+firearms"
                    pc_def = CombatAction(
                        CombAct.RANGED_ATTACK, atk_action.user, user=pc, defending=True,
                        pool=pd_pool, use_sidearm=True
                    )

            "Throw something!" if can_throw:
                python:
                    pd_pool = "dexterity+athletics"
                    throw_sidearm = not pc.held.throwable and pc.sidearm.throwable
                    pc_def = CombatAction(
                        CombAct.RANGED_ATTACK, atk_action.user, user=pc, defending=True,
                        pool=pd_pool, use_sidearm=throw_sidearm
                    )

        jump .pc_defend_post

    label .pc_defend_special_dodge(dodge_power_used=None):
        python:
            pd_pool, rr_dodge = "dexterity+athletics", "dodge"
            if CombatAction.attack_is_gunshot(attacker, atk_action):
                if pc.has_disc_power(cfg.POWER_CELERITY_TWITCH, cfg.DISC_CELERITY):
                    rr_dodge = "celerity-dodge"
                    utils.log(f'Bullet-time! Gunshot dodging penalty waived for {pc}.')
                else:
                    pd_pool += f'+-{cfg.BULLET_DODGE_PENALTY}'
            pc_def = CombatAction(CombAct.DODGE, None, user=pc, defending=True, pool=pd_pool)
            print(f'pc_def pool just after creation: {pc_def.pool}')
            pc_def.unarmed_power_used = utils.unique_append(pc_def.unarmed_power_used, dodge_power_used, sep=", ")
            free_blink = cfg.DEV_MODE and (cfg.FREE_BLINK or cfg.FREE_DISCIPLINES)
            # Break grapple on Blink?

        if not free_blink:
            if dodge_power_used == cfg.POWER_CELERITY_BLINK:
                call roll_control.rouse_check() from pc_dodge_blink_rouse
            elif dodge_power_used == cfg.POWER_CELERITY_MATRIX_DODGE and not state.StatusFX.has_buff(pc, Entity.SE_WEAVING):
                $ state.statusfx.weaving(pc)
                call roll_control.rouse_check() from pc_dodge_weaving_rouse

        return pc_def

    label .pc_defend_post:

        $ state.menu_label_backref = None
        # call roll_control(atk_pool, pd_pool, active_a=atk_action, response_a=pc_def) from combat_pc_def
        call roll_control(atk_pool, pc_def.pool, active_a=atk_action, response_a=pc_def) from combat_pc_def_v2
        $ roll_result = _return
        call .handle_post_action(report=state.arena.process_new_result(roll_result, atk_action, pc_def)) from pc_def_pnr
        $ chained_action = _return

        jump .turn_loop_start

    label .end:

        "Returning...? (post-battle marker a01)"

    return


label battle_aftermath(*args):

    ""

    return


#
