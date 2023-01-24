init 1 python in game:

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
            return tack(attacker, action_order, ao_index, considered_targets)

        @staticmethod
        def npc_defend(defender, attacker, atk_action):
            # choose a response to the incoming attack
            base_def, target = defender.base_combat_stat, attacker
            valid_skills = [{"name": base_def, "value": getattr(defender, base_def)}]
            for skill in defender.special_skills:
                if FightBrain.validate_action(skill, True, defender.engaged, defender.current_pos == attacker.current_pos):
                    valid_skills.append({"name": skill, "value": defender.special_skills[skill]})
            best_skill = max(valid_skills, key=lambda pair: pair["value"])
            bsk_name, bsk_value = best_skill["name"], best_skill["value"]
            if str(bsk_name).lower() == 'physical':  # Physical attribute is a special case.
                if defender.ftype == NPCFighter.FT_BRAWLER and attacker.current_pos == defender.current_pos:
                    atype = CAction.MELEE_ATTACK
                elif defender.ftype == NPCFighter.FT_SHOOTER:
                    atype = CAction.DODGE if defender.engaged else CAction.RANGED_ATTACK
                else:
                    atype = CAction.DODGE
                if atype == CAction.DODGE:
                    target = None
            elif bsk_name in CAction.DODGE_VARIANTS:
                atype = CAction.DODGE
                target = None
            elif bsk_name in (CAction.MELEE_ACTIONS + CAction.ANYWHERE_ACTIONS):
                atype = CAction.MELEE_ATTACK
            elif bsk_name in CAction.RANGED_ACTIONS:
                atype = CAction.RANGED_ATTACK
            else:
                atype = None
            if atype == CAction.DODGE and CAction.attack_is_gunshot(attacker, atk_action):
                if cfg.POWER_CELERITY_TWITCH in defender.passive_powers:
                    bsk_name = cfg.POWER_CELERITY_TWITCH
                else:
                    bsk_value = max(1, int(bsk_value) - cfg.BULLET_DODGE_PENALTY)
            return CAction(atype, target, user=defender, defending=True, pool=bsk_value, subtype=bsk_name)

        @staticmethod
        def brawler_attack(attacker, action_order, ao_index, atk_targets):
            # Attack a target in melee range (same current_pos), or close to a target at range.
            high_priority, low_priority = [], []
            for enemy in atk_targets:
                if enemy.current_pos == attacker.current_pos:
                    high_priority.append(enemy)
                else:
                    low_priority.append(enemy)
            if len(high_priority) > 0:
                target = utils.get_random_list_elem(high_priority)[0]  # Target chosen randomly from preferred category
                ranked_attacks = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_melee=True)
                atk_label, atk_pool = ranked_attacks[0]
                return CAction(CAction.MELEE_ATTACK, target, user=attacker, pool=atk_pool, subtype=atk_label)
            else:
                target = utils.get_random_list_elem(low_priority)[0]
                atk_label, atk_pool = cfg.NPCAT_PHYS, attacker.physical
                if cfg.SK_ATHL in attacker.special_skills and attacker.special_skills[cfg.SK_ATHL] >= attacker.physical:
                    atk_label, atk_pool = cfg.SK_ATHL, attacker.special_skills[cfg.SK_ATHL]
                return CAction(CAction.MELEE_ENGAGE, target, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def shooter_attack(attacker, action_order, ao_index, atk_targets):
            # Shoot at a target if not engaged, otherwise melee attack a target.
            can_shoot = not attacker.engaged
            atype = CAction.RANGED_ATTACK if can_shoot else CAction.MELEE_ATTACK
            if can_shoot:
                target = utils.get_random_list_elem(atk_targets)[0]
                # atk_label, atk_pool = ranked_attacks[0]
            else:
                melee_targets = [t for t in atk_targets if t.current_pos == attacker.current_pos]
                target = utils.get_random_list_elem(melee_targets)[0]
            ranked_attacks = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_melee=not can_shoot, must_be_ranged=can_shoot)
            atk_label, atk_pool = ranked_attacks[0]
            return CAction(atype, target, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def wildcard_attack(attacker, action_order, ao_index, atk_targets):
            # If engaged or lacking ranged attacks, act like a Brawler. Otherwise pick random target and attack.
            if attacker.engaged:
                return FightBrain.brawler_attack(attacker, action_order, ao_index, atk_targets)
            ranged_atk_options = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_ranged=True)
            if len(ranged_atk_options) < 1:
                return FightBrain.brawler_attack(attacker, action_order, ao_idnex, atk_targets)
            target = utils.get_random_list_elem(atk_targets)[0]
            use_melee = target.current_pos == attacker.current_pos
            atype = CAction.MELEE_ATTACK if use_melee else CAction.RANGED_ATTACK
            ranked_attacks = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_melee=use_melee)
            atk_label, atk_pool = ranked_attacks[0]
            return CAction(atype, target, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def pc_hunter_attack(attacker, action_order, ao_index, atk_targets):
            pc = renpy.store.state.pc
            atk_pc_m, atk_pc_r = FightBrain.can_attack_target(attacker, pc)
            if not atk_pc_m and not atk_pc_r:
                return FightBrain.wildcard_attack(attacker, action_order, ao_index, atk_targets)
            ranked_attacks = FightBrain.get_ranked_usable_combat_skills(attacker)
            atk_label, atk_pool = ranked_attacks[0]
            if atk_label in CAction.MELEE_ACTIONS or atk_label in CAction.ANYWHERE_ACTIONS:
                atype = CAction.MELEE_ATTACK
            else:
                atype = CAction.RANGED_ATTACK
            return CAction(atype, pc, user=attacker, pool=atk_pool, subtype=atk_label)

        @staticmethod
        def noncombatant_action(user, action_order, ao_index, atk_targets):
            # For now, just do nothing. Maybe special attacks later.
            return CAction(CAction.NO_ACTION, None, user=user)

        @staticmethod
        def get_ranked_usable_combat_skills(user, must_be_ranged=False, must_be_melee=False):
            bc_stat = (user.base_combat_stat, getattr(user, user.base_combat_stat))
            available_attacks = list(user.special_skills.items())
            if must_be_ranged:
                usable = [atk for atk in available_attacks if atk[0] in (CAction.RANGED_ACTIONS + CAction.ANYWHERE_ACTIONS)]
            elif must_be_melee:
                usable = [atk for atk in available_attacks if atk[0] in (CAction.MELEE_ACTIONS + CAction.ANYWHERE_ACTIONS)]
            else:
                usable = [atk for atk in available_attacks]
            usable.append(bc_stat)
            ranked_attacks = sorted(usable, key=lambda atk_opt: atk_opt[1])
            return ranked_attacks

        @staticmethod
        def can_attack_target(attacker, target):
            can_attack_melee, can_attack_ranged = True, True
            if attacker.current_pos != target.current_pos:
                can_attack_melee = False
            if attacker.engaged:
                can_attack_ranged = False
            if not can_attack_melee and not can_attack_ranged:
                return False, False
            if can_attack_melee:
                melee_skills = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_melee=True)
                if len(melee_skills) < 1:
                    can_attack_melee = False
            if can_attack_ranged:
                ranged_skills = FightBrain.get_ranked_usable_combat_skills(attacker, must_be_ranged=True)
                if len(ranged_skills) < 1:
                    can_attack_ranged = False
            return can_attack_melee, can_attack_ranged

        @staticmethod
        def filter_considered_targets(enemy_targets, all_targets, attacker):
            considering = enemy_targets
            # Consider allies for attacks if in rage frenzy.
            if attacker.get_se_ttl(Entity.SE_BERSERK):
                considering = all_targets
            # Ignore obfuscated targets unless we can sense them.
            obfuscated, visible = [], []
            for ct in considering:
                if ct.get_se_ttl(Entity.SE_OBFUSCATED) or ct.get_se_ttl(Entity.SE_OBFUSCATED_TECH):
                    obfuscated.append(ct)
                else:
                    visible.append(ct)
            for ob in obfuscated:
                if renpy.store.state.can_sense_unseen(ob, attacker):
                    visible.append(ct)
            del considering, obfuscated
            considering = visible
            # Additional tests here.
            return considering

        @staticmethod
        def validate_action(action, defending, engaged, at_range):
            if not defending and action == cfg.SK_ATHL:
                return False
            if engaged and action in CAction.RANGED_ACTIONS:
                return False
            elif (not engaged or at_range) and action in cfg.MELEE_ATTACK:
                return False
            return True
