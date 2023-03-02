init 1 python in game:

    state = renpy.store.state

    class FightBrain:  # Shitty combat AI for NPCs
        @staticmethod
        def npc_attack(attacker, action_order, ao_index, enemy_targets, all_targets):
            ftype = attacker.ftype
            if ftype == NPCFighter.FT_BRAWLER:
                tack = FightBrain.brawler_attack
            elif ftype == NPCFighter.FT_SHOOTER:
                tack = FightBrain.shooter_attack
            elif ftype == NPCFighter.FT_WILDCARD:
                tack = FightBrain.wildcard_attack
            elif ftype == NPCFighter.FT_FTPC:
                tack = FightBrain.pc_hunter_attack
            else:
                tack = FightBrain.noncombatant_action
            considered_targets = FightBrain.filter_considered_targets(enemy_targets, all_targets, attacker)
            _tack = tack(attacker, action_order, ao_index, considered_targets)
            print("\nNPC ATTACK ({}/{}): {} --> {}\n".format(
                _tack.action_type, _tack.action_label,
                _tack.user.name if _tack.user else "Nobody",
                _tack.target.name if _tack.target else "Nobody"
            ))
            return _tack

        @staticmethod
        def npc_defend(defender, attacker, atk_action):  # TODO: here!
            # Reacting to a Disengage action isn't technically a defense.
            if atk_action.action_type == CAction.DISENGAGE:
                return FightBrain.npc_possible_pursuit(defender, attacker, atk_action)
            # Choose a response to the incoming attack.
            base_def, target = defender.base_combat_stat, attacker
            valid_skills = [(base_def, getattr(defender, base_def))]
            for skill in defender.special_skills:
                # if FightBrain.validate__action(skill, True, defender.engaged, defender.current_pos == attacker.current_pos):
                if FightBrain.validate_action(skill, defender, True, target):
                    valid_skills.append((skill, defender.special_skills[skill]))
            best_skill = max(valid_skills, key=lambda pair: pair[1])
            bsk_name, bsk_value = best_skill
            if utils.caseless_equal(bsk_name, 'physical'):  # Physical attribute is a special case.
                if defender.ftype == NPCFighter.FT_BRAWLER and attacker.current_pos == defender.current_pos:
                    def_atype = CAction.MELEE_ATTACK
                elif defender.ftype == NPCFighter.FT_SHOOTER:
                    def_atype = CAction.DODGE if defender.engaged else CAction.RANGED_ATTACK
                else:
                    def_atype = CAction.DODGE
                if def_atype == CAction.DODGE:
                    target = None
                    # Force use of Athletics to dodge if it's present along with Physical stat.
                    if cfg.SK_ATHL in defender.special_skills:
                        bsk_name, bsk_value = cfg.SK_ATHL, defender.special_skills[cfg.SK_ATHL]
            elif bsk_name in CAction.DODGE_VARIANTS:
                def_atype = CAction.DODGE
                target = None
            elif bsk_name in (CAction.MELEE_ACTIONS + CAction.ANYWHERE_ACTIONS):
                def_atype = CAction.MELEE_ATTACK
            elif bsk_name in CAction.RANGED_ACTIONS:
                def_atype = CAction.RANGED_ATTACK
            else:
                def_atype = None
            if def_atype == CAction.DODGE and CAction.attack_is_gunshot(attacker, atk_action):
                if cfg.POWER_CELERITY_TWITCH in defender.passive_powers:
                    bsk_name = cfg.POWER_CELERITY_TWITCH
                else:
                    bsk_value = max(1, int(bsk_value) - cfg.BULLET_DODGE_PENALTY)
            return CAction(def_atype, target, user=defender, defending=True, pool=bsk_value, subtype=bsk_name)

        @staticmethod
        def npc_possible_pursuit(pursuer, fleer, flight_action):
            ftype = pursuer.ftype
            if ftype == NPCFighter.FT_ESCORT or (ftype == NPCFighter.FT_FTPC and not fleer.is_pc):
                return CAction(CAction.NO_ACTION, None, user=pursuer)  # TODO: implement uncontested contests i.e. one side no-actions
            if flight_action.skip_contest:
                return CAction(CAction.NO_ACTION, None, user=pursuer)
            fleer_atk_m, fleer_atk_r = FightBrain.can_attack_target(pursuer, fleer)
            if not fleer_atk_m and not fleer_atk_r:
                return CAction(CAction.NO_ACTION, None, user=pursuer)
            other_engagements = False
            if pursuer.engaged and len(pursuer.engaged) > 1:
                other_engagements = True
            elif pursuer.engaged and pursuer.engaged[0] is not fleer:
                other_engagements = True
            pursuit_label, pursuit_pool = None, None
            threatened = FightBrain.feels_threatened(pursuer)
            # TODO: implement "threatened" above as mentioned elsewhere
            if ftype == NPCFighter.FT_BRAWLER or other_engagements:
                pursuit_type = CAction.MELEE_ATTACK if fleer_atk_m else CAction.NO_ACTION
            elif ftype == NPCFighter.FT_SHOOTER:
                if threatened or not fleer_atk_r:
                    return CAction(CAction.NO_ACTION, None, user=pursuer)
                pursuit_type = CAction.RANGED_ATTACK
            elif ftype in (NPCFighter.FT_WILDCARD, NPCFighter.FT_FTPC):
                pursuit_type = None
            else:
                raise ValueError("We shouldn't reach here; check if {} is a valid fighter archetype.".format(ftype))
            ranked_attacks = FightBrain.grucs_v2(pursuer, pursuit_type)
            pursuit_label, pursuit_pool = ranked_attacks[0]
            if not pursuit_type:
                if pursuit_label in (CAction.MELEE_ACTIONS + CAction.ANYWHERE_ACTIONS):
                    pursuit_type = CAction.MELEE_ATTACK
                else:
                    pursuit_type = CAction.RANGED_ATTACK
            return CAction(pursuit_type, fleer, user=pursuer, pool=pursuit_pool, subtype=pursuit_label)

        @staticmethod
        def brawler_attack(attacker, action_order, ao_index, atk_targets):
            # Attack a target in melee range (same current_pos), or attempt to close in on a target at range.
            high_priority, low_priority = [], []
            for enemy in atk_targets:
                if enemy.current_pos == attacker.current_pos:
                    high_priority.append(enemy)
                else:
                    low_priority.append(enemy)
            if len(high_priority) > 0:
                target = utils.get_random_list_elem(high_priority)  # Target chosen randomly from preferred category
                ranked_attacks = FightBrain.grucs_v2(attacker, CAction.MELEE_ATTACK)
                atk_label, atk_pool = ranked_attacks[0]
                print("BRAWLER attack choice (high priority): {}, {}".format(atk_label, atk_pool))
                return CAction(CAction.MELEE_ATTACK, target, user=attacker, pool=atk_pool, subtype=atk_label)
            else:
                target = utils.get_random_list_elem(low_priority)
                atk_label, atk_pool = cfg.NPCAT_PHYS, attacker.physical
                if cfg.SK_ATHL in attacker.special_skills:# and attacker.special_skills[cfg.SK_ATHL] >= attacker.physical:
                    atk_label, atk_pool = cfg.SK_ATHL, attacker.special_skills[cfg.SK_ATHL]
                return CAction(CAction.MELEE_ENGAGE, target, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def shooter_attack(attacker, action_order, ao_index, atk_targets):
            # Shoot at a target if not engaged, otherwise melee attack a target.
            r_held, r_sidearm = state.holding_ranged_weapon(attacker), state.holding_ranged_weapon(attacker, check_alt=True)
            can_shoot = not attacker.engaged and r_sidearm
            atype = CAction.RANGED_ATTACK if can_shoot else CAction.MELEE_ATTACK
            if can_shoot:
                target = utils.get_random_list_elem(atk_targets)
                ranked_attacks = FightBrain.grucs_v2(attacker, CAction.RANGED_ATTACK)
                atk_label, atk_pool = ranked_attacks[0]
                offhand=r_sidearm and not r_held
                return CAction(CAction.RANGED_ATTACK, target, user=attacker, pool=atk_pool, subtype=atk_label, use_sidearm=offhand)
            melee_action = next((True for act in CAction.MELEE_ACTIONS if act in attacker.special_skills), None)
            # TODO: change above to more precise list of valid melee attacks, right now it's all MELEE_ACTIONS
            threatened, cornered = FightBrain.feels_threatened(attacker), state.arena.is_cornered(attacker)
            # TODO: "threatened" should depend on enemy type (do they scrap or flee to range)
            # "cornered" is True if they're at the farthest rank for their side, i.e. 2 or -2.
            # In short, are they inclined to fight or forced to?
            if melee_action and (not threatened or cornered):
                melee_targets = [t for t in atk_targets if t.current_pos == attacker.current_pos]
                if len(melee_targets) < 1:
                    return None  # Shooters do not seek out melee targets like brawlers, but TODO come back to this.
                target = utils.get_random_list_elem(melee_targets)
                ranked_attacks = FightBrain.grucs_v2(attacker, CAction.MELEE_ATTACK)
                atk_label, atk_pool = ranked_attacks[0]
                offhand=r_held and not r_sidearm
                return CAction(CAction.MELEE_ATTACK, target, user=attacker, pool=atk_pool, subtype=atk_label, use_sidearm=offhand)
            if not cornered:
                return FightBrain.attempt_to_disengage(attacker, action_order, ao_index, atk_targets)
            return CAction(CAction.NO_ACTION, None, user=attacker)

        @staticmethod
        def attempt_to_disengage(fleer, action_order, ao_index, targets):
            # Most recent engager will be the "defender" against a disengage attempt.
            interloper = fleer.engaged[-1] if fleer.engaged else None
            ranked_ds = FightBrain.grucs_v2(fleer, CAction.DISENGAGE)
            diseng_label, diseng_pool = ranked_ds[0] if ranked_ds else (None, None)
            return CAction(CAction.DISENGAGE, interloper, user=fleer, pool=diseng_pool, subtype=diseng_label)

        @staticmethod
        def wildcard_attack(attacker, action_order, ao_index, atk_targets):
            # If engaged or lacking ranged attacks, act like a Brawler. Otherwise pick random target and attack.
            r_held, r_sidearm = state.holding_ranged_weapon(attacker), state.holding_ranged_weapon(attacker, check_alt=True)
            can_shoot = not attacker.engaged and r_sidearm
            if not can_shoot:
                return FightBrain.brawler_attack(attacker, action_order, ao_index, atk_targets)
            ranged_atk_options = FightBrain.grucs_v2(attacker, CAction.RANGED_ATTACK)
            if not ranged_atk_options or (not r_held and percent_chance(60)):  # Only 40% chance to use off-hand ranged weapon.
                return FightBrain.brawler_attack(attacker, action_order, ao_index, atk_targets)
            target = utils.get_random_list_elem(atk_targets)
            use_melee = target.current_pos == attacker.current_pos and utils.percent_chance(65)
            atype = CAction.MELEE_ATTACK if use_melee else CAction.RANGED_ATTACK
            ranked_attacks = FightBrain.grucs_v2(attacker, CAction.MELEE_ATTACK if use_melee else None)
            atk_label, atk_pool = ranked_attacks[0]
            use_sidearm = not use_melee and r_sidearm and not r_held
            return CAction(atype, target, user=attacker, pool=atk_pool, subtype=atk_label, use_sidearm=use_sidearm)

        @staticmethod
        def pc_hunter_attack(attacker, action_order, ao_index, atk_targets):
            pc = state.pc
            atk_pc_m, atk_pc_r = FightBrain.can_attack_target(attacker, pc)
            if not atk_pc_m and not atk_pc_r:  # If PC can't be targeted, do whatever.
                return FightBrain.wildcard_attack(attacker, action_order, ao_index, atk_targets)
            atk_action_type = None
            if not atk_pc_r:
                atk_action_type = CAction.MELEE_ATTACK
            elif not atk_pc_m:
                atk_action_type = CAction.RANGED_ATTACK
            # Pat Benatar; hit PC with best shot.
            ranked_attacks = FightBrain.grucs_v2(attacker, atk_action_type)
            atk_label, atk_pool = ranked_attacks[0]
            if atk_pc_m and (atk_label in CAction.MELEE_ACTIONS or atk_label in CAction.ANYWHERE_ACTIONS):
                atype = CAction.MELEE_ATTACK
            elif atk_pc_r and state.holding_ranged_weapon():
                atype = CAction.RANGED_ATTACK
            elif atk_pc_m:
                atype = CAction.MELEE_ATTACK
            else:
                atype = CAction.MELEE_ENGAGE
            return CAction(atype, pc, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def noncombatant_action(user, action_order, ao_index, atk_targets):
            # For now, just do nothing. Maybe special attacks later.
            return CAction(CAction.NO_ACTION, None, user=user)

        @staticmethod
        def feels_threatened(actor):
            return False

        @staticmethod
        def grucs_v2(user, action_type, anywhere_actions_only=False):
            ranking = FightBrain.get_r_ranked_usable_combat_skills_v2(user, action_type, anywhere_actions_only=anywhere_actions_only)
            print("\n >> RANKING for {}, action type is {}:".format(user.name, action_type))
            utils.log("get_r_ranked_usable_combat_skills_v2() returns:\n\n{}\n".format(
                '\n'.join(["{}: {}".format(rsk[0], rsk[1]) for rsk in ranking]) if ranking else "--empty action list--"
            ))
            return ranking

        @staticmethod
        def get_r_ranked_usable_combat_skills_v2(user, action_type, anywhere_actions_only=False):
            bc_stat = None
            if hasattr(user, "base_combat_stat"):
                bc_stat = (user.base_combat_stat, getattr(user, user.base_combat_stat))
            available_skills, possibly_usable = list(user.special_skills.items()), []
            if bc_stat:
                available_skills += (bc_stat,)
                print("avail skillz", available_skills)
            if not action_type:
                return sorted(available_skills + [bc_stat], key=lambda skill_opt: skill_opt[1])
            if anywhere_actions_only:
                possibly_usable = CAction.ANYWHERE_ACTIONS
            elif action_type == CAction.DODGE:
                possibly_usable = CAction.DODGE_VARIANTS
            elif action_type == CAction.RANGED_ATTACK:
                if not state.holding_ranged_weapon(user):
                    return None
                possibly_usable = CAction.RANGED_ACTIONS + CAction.ANYWHERE_ACTIONS
            elif action_type == CAction.MELEE_ATTACK:
                possibly_usable = CAction.MELEE_ACTIONS + CAction.ANYWHERE_ACTIONS
            elif action_type == CAction.MELEE_ENGAGE:
                possibly_usable = CAction.RUSH_VARIANTS
            elif action_type == CAction.DISENGAGE:
                possibly_usable = (CAction.DODGE_VARIANTS + CAction.RUSH_VARIANTS)
            else:
                raise ValueError("Unaccounted-for action type in skill rank method ({})!".format(action_type))
            usable, athletics_incl = [], False
            if possibly_usable:
                if action_type == CAction.MELEE_ATTACK:
                    print("grucs melee check, possibly_usable = ", possibly_usable)
                else:
                    print("gimme dat gruck gruck gruck", action_type)
                for avsk in available_skills:
                    avsk_name = avsk[0]
                    if avsk_name == cfg.SK_ATHL:
                        athletics_incl = True
                    if avsk_name in possibly_usable and avsk_name not in usable:
                        usable.append(avsk)
            # If NPC has Athletics skill, force its use.
            if usable and action_type in (CAction.DODGE, CAction.DISENGAGE) and athletics_incl:
                usable = [usk for usk in usable if usk[0] != bc_stat[0]]
            elif not usable or not len(usable):
                usable = [bc_stat]
            return sorted(usable, key=lambda skill_opt: skill_opt[1])

        # @staticmethod

        @staticmethod
        def can_attack_target(attacker, target):
            can_attack_melee, can_attack_ranged = True, True
            if attacker.current_pos != target.current_pos:
                can_attack_melee = False
            if attacker.engaged or not state.holding_ranged_weapon(attacker, check_alt=True):
                can_attack_ranged = False
            if not can_attack_melee and not can_attack_ranged:
                return False, False
            if can_attack_melee:
                melee_skills = FightBrain.grucs_v2(attacker, CAction.MELEE_ATTACK)
                if len(melee_skills) < 1:
                    can_attack_melee = False
            if can_attack_ranged:
                ranged_skills = FightBrain.grucs_v2(attacker, CAction.RANGED_ATTACK)
                if len(ranged_skills) < 1:
                    can_attack_ranged = False
            return can_attack_melee, can_attack_ranged

        @staticmethod
        def filter_considered_targets(enemy_targets, all_targets, attacker):
            considering = enemy_targets
            # Consider allies for attacks if in rage frenzy.
            if attacker.get_effect_ttl(Entity.SE_BERSERK):
                considering = all_targets
            # Ignore obfuscated targets unless we can sense them.
            obfuscated, visible, seem_dead = [], [], []
            for ct in considering:
                if ct.dead or (ct.appears_dead and True):  # TODO: detect feign death?
                    seem_dead.append(ct)
                    continue
                if ct.get_effect_ttl(Entity.SE_OBFU_MOBILE) or ct.get_effect_ttl(Entity.SE_OBFU_ROOTED):
                    if not attacker.detector_tech or ct.stealth_ignore_tech:
                        obfuscated.append(ct)
                    else:
                        visible.append(ct)
                else:
                    visible.append(ct)
            for ob in obfuscated:
                if renpy.store.state.can_sense_unseen(ob, attacker):
                    visible.append(ct)
            del considering, obfuscated, seem_dead
            considering = visible
            # Additional tests here.
            return considering

        @staticmethod
        # def validate__action(action, defending, engaged, at_range):
        def validate_action(action_skill, user, defending, target):
            print("IN VALID ACTION WE HAVE RECEIVED: {}, type {}".format(action_skill, type(action_skill)))
            at_range = user.current_pos != target.current_pos
            if not defending:
                if action_skill in CAction.DODGE_VARIANTS:
                    return False
            if action_skill in CAction.RANGED_ACTIONS:
                if user.engaged:
                    return False
                if user and not state.holding_ranged_weapon(user, check_alt=True):
                    return False
                return True
            elif (not user.engaged or at_range) and action_skill in CAction.MELEE_ACTIONS:
                return False
            return True
