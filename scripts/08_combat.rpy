init 1 python in game:

    import math
    state, audio = renpy.store.state, renpy.store.audio

    class CAction:
        NO_ACTION = "null_action"
        FALL_BACK = "fall_back"
        MELEE_ENGAGE = "melee_engage"
        MELEE_ATTACK = "melee_attack"
        RANGED_ATTACK = "ranged_attack"
        DODGE = "dodge"
        SPECIAL_ATTACK = "special_attack"
        ESCAPE_ATTEMPT = "tryna_escape"

        # Not necessarily attacks, but abilities that can be actively used in combat, not including
        # passive abilities that can affect combat.
        RANGED_ACTIONS = [  # Ranged only, cannot use if engaged
            cfg.SK_FIRE,
            cfg.POWER_ANIMALISM_SPEAK,
            cfg.POWER_OBFUSCATE_ILLUSION, cfg.POWER_OBFUSCATE_HALLUCINATION,
            cfg.POWER_POTENCE_RAGE,
            cfg.POWER_PROTEAN_DIRTNAP, cfg.POWER_PROTEAN_BOO_BLEH, cfg.POWER_PROTEAN_DRUID, cfg.POWER_PROTEAN_FINALFORM
        ]

        MELEE_ACTIONS = [  # Melee only, must be engaged to use
            cfg.SK_COMB,
            cfg.POWER_ANIMALISM_QUELL,
            cfg.POWER_DOMINATE_MESMERIZE,
            cfg.POWER_POTENCE_PROWESS, cfg.POWER_POTENCE_MEGASUCK,
            cfg.POWER_PROTEAN_REDEYE
        ]

        ANYWHERE_ACTIONS = [  # Usable at any distance, whether engaged or not
            cfg.SK_ATHL,
            cfg.POWER_CELERITY_SPEED, cfg.POWER_CELERITY_BLINK,
            cfg.POWER_DOMINATE_COMPEL,
            cfg.POWER_FORTITUDE_TOUGH, cfg.POWER_FORTITUDE_BANE,
            cfg.POWER_OBFUSCATE_VANISH,
            cfg.POWER_POTENCE_SUPERJUMP,
            cfg.POWER_PRESENCE_SCARYFACE,
            cfg.POWER_PROTEAN_TOOTH_N_CLAW, cfg.POWER_PROTEAN_MOLD_SELF
        ]

        DODGE_VARIANTS = [cfg.SK_ATHL, cfg.POWER_CELERITY_SPEED, cfg.POWER_OBFUSCATE_ILLUSION]

        SNEAK_VARIANTS = [cfg.SK_CLAN, cfg.DISC_OBFUSCATE] + cfg.REF_DISC_POWERS_SNEAKY

        DETECTION_VARIANTS = [cfg.POWER_AUSPEX_ESP]

        ESCAPE_VARIANTS = [
            cfg.SK_ATHL,
            cfg.POWER_CELERITY_SPEED, cfg.POWER_CELERITY_BLINK,
            cfg.POWER_OBFUSCATE_VANISH, cfg.POWER_OBFUSCATE_HALLUCINATION
        ]

        # For now, NPC combat discipline powers consist of all active combat discipline powers
        NPC_COMBAT_DISC_POWERS = RANGED_ACTIONS + MELEE_ACTIONS + ANYWHERE_ACTIONS + DODGE_VARIANTS + ESCAPE_VARIANTS
        NPC_COMBAT_DISC_POWERS = [p for p in NPC_COMBAT_DISC_POWERS if not str(p).startswith("SK_")]

        OUCH = [MELEE_ATTACK, RANGED_ATTACK, SPECIAL_ATTACK]
        NO_CONTEST = [NO_ACTION, FALL_BACK]

        def __init__(
            self, action_type, target:Entity, user=None, defending=False, pool=None, subtype=None, use_sidearm=False, lethality=None
        ):
            self.action_type = action_type  # Should be one of above types; subtype should be a discipline power or similar or None.
            self.pool, self.num_dice, self.alt_weapon_penalty = pool, None, None
            self.target, self.defending = target, defending
            self.user = user
            self.action_label = subtype
            self.weapon_used, self.skip_contest, self.lost_to_trump_card = None, False, False
            if use_sidearm:
                self.alt_weapon_penalty = True
                utils.log("Alt weapon penalty imposed on {} because use_sidearm ({}) set to True.".format(
                    self.user.name, self.user.sidearm if self.user and self.user.sidearm else "None?"
                ))
            self.unarmed_power_used, self.power_used = None, None
            if self.action_type is None and self.action_label is None:
                raise ValueError("At least one of 'action_type' and 'action_label' must be defined; they can't both be empty!")
            elif self.action_type is None:
                self.action_type = self.evaluate_type()
            # ---
            self.dmg_bonus, self.lethality = 0, 1
            self.dmg_bonus_labels = {}
            weapon, weapon_alt = None, None
            if self.user.is_pc:
                weapon, weapon_alt = self.user.held, self.user.sidearm
            else:
                if hasattr(self.user, "npc_weapon"):
                    weapon = self.user.npc_weapon
                if hasattr(self.user, "npc_weapon_alt"):
                    weapon_alt = self.user.npc_weapon

            if CAction.attack_weapon_match(weapon, self):
                self.weapon_used = weapon
            elif CAction.attack_weapon_match(weapon_alt, self):
                self.weapon_used = weapon_alt
                self.alt_weapon_penalty = True
                utils.log("Alt weapon penalty applied to attack type {} by {}, who has {} at hand and {} at side".format(
                    self.action_type, self.user.name, weapon.name, weapon_alt.name
                ))
            else:
                self.weapon_used = None

            self.dmg_bonus = 0
            self.armor_piercing = 0
            if hasattr(self.user, "npc_dmg_bonus") and self.user.npc_dmg_bonus:
                self.dmg_bonus, self.lethality = self.user.npc_dmg_bonus, self.user.npc_atk_lethality
            elif self.weapon_used:
                self.dmg_bonus, self.lethality = self.weapon_used.dmg_bonus, self.weapon_used.lethality
            # TODO: add checks for active buffs e.g. Fist of Caine.
            if lethality is not None:  # If lethality value is passed it overrides other sources.
                self.lethality = lethality
            # ---
            if self.action_type in [CAction.DODGE, CAction.MELEE_ENGAGE, CAction.NO_ACTION, CAction.FALL_BACK] or not self.target:
                self.dmg_type = cfg.DMG_NONE
            else:
                self.dmg_type = Weapon.get_damage_type(self.lethality, target.creature_type)

        def __repr__(self):
            return "< {} action, label {} >".format(self.action_type, self.action_label)

        def evaluate_type(self):
            print("\n\n\n EVALUATE TYPE CALLED IN ACTION\n\n\n")
            if self.defending and self.action_label in CAction.DODGE_VARIANTS:
                return CAction.DODGE
            elif self.action_label in CAction.RANGED_ACTIONS:
                return CAction.RANGED_ATTACK
            elif self.action_label in CAction.MELEE_ACTIONS:
                return CAction.MELEE_ATTACK
            elif self.action_label in CAction.ANYWHERE_ACTIONS:
                if self.target is None:
                    return CAction.ESCAPE_ATTEMPT if self.defending else CAction.SPECIAL_ATTACK
                if self.target.current_pos == self.user.current_pos:
                    return CAction.MELEE_ATTACK
                return CAction.RANGED_ATTACK
            print(
                "\n-- self.user = {}, self.user.current_pos = {}, self.defending = {},\n".format(
                    self.user.name, self.user.current_pos, self.defending
                ) + "-- self.action_label = {}, self.target = {}, self.target.current_pos = {}".format(
                    self.action_label, self.target.name, self.target.current_pos
                )
            )
            return CAction.NO_ACTION

        @staticmethod
        def attack_weapon_match(weapon, action):
            if not weapon or not action:
                return False
            if weapon.item_type == Item.IT_FIREARM:
                return action.action_type == CAction.RANGED_ATTACK
            if weapon.item_type == Item.IT_WEAPON:
                return action.action_type == CAction.MELEE_ATTACK or weapon.throwable
            return False

        @staticmethod
        def attack_is_gunshot(attacker, atk_action):
            if atk_action.action_type != CAction.RANGED_ATTACK:
                return False
            if attacker.ranged_attacks_use_gun or utils.caseless_in(cfg.SK_FIRE, atk_action.action_label):
                return True
            return False


    class ClashRecord:
        DEV_LOG_FLAGS = {
            CAction.MELEE_ENGAGE: "Rush",
            CAction.MELEE_ATTACK: "Melee",
            CAction.RANGED_ATTACK: "Ranged",
            CAction.DODGE: "Dodge",
            CAction.ESCAPE_ATTEMPT: "Flee",
            CAction.SPECIAL_ATTACK: "Special",
            CAction.FALL_BACK: "Slink Back",
            CAction.NO_ACTION: "No Action",

            cfg.DMG_SPF: "superf dmg",
            cfg.DMG_FULL_SPF: "unhalved dmg",
            cfg.DMG_AGG: "aggrav dmg",
            cfg.DMG_NONE: "(no damage)"
        }

        def __init__(self, pov_margin=None, dmg_type=None, dmg_bonus=None, target=None):
            self.pov_margin, self.target = pov_margin, target
            self.dmg_type, self.dmg_bonus = dmg_type, dmg_bonus
            self.log_str = ""
            self.actual_dmg_tup = None


    class CombatLog:
        def __init__(self, dfa=None, dfd=None, dbfa=None, dbfd=None, dtfa=None, dtfd=None):
            self.history = []
            self.attack_record = ClashRecord(pov_margin=dfa, dmg_bonus=dbfa, dmg_type=dtfa)
            self.defend_record = ClashRecord(pov_margin=dfd, dmg_bonus=dbfd, dmg_type=dtfd)

        def reset(self):
            del self.attack_record, self.defend_record
            self.attack_record, self.defend_record = None, None

        def set_clash_records(self, margin, atk_action, def_action, reset=False):  # Called after damage_step().
            if reset:
                self.reset()
            # if state.arena.attack_on_pc(atk_action):
            #     margin = margin * -1
            if margin >= 0:
                if not self.attack_record:
                    self.attack_record = ClashRecord()
                CombatLog.set_damage_flags(self.attack_record, margin, atk_action)
            if margin <= 0:
                if not self.defend_record:
                    self.defend_record = ClashRecord()
                CombatLog.set_damage_flags(self.defend_record, margin, def_action)

        @staticmethod
        def set_damage_flags(record: ClashRecord, margin, action):
            record.target = action.target
            record.dmg_bonus, record.dmg_type = action.dmg_bonus, action.dmg_type
            record.pov_margin = (abs(margin) if margin != 0 else 1) + record.dmg_bonus
            actual_dealt_dmg, unhalved_dmg, prevented_dmg, mitigated_dmg = 0, 0, 0, 0
            damaging_attack = True
            if record.dmg_type in [cfg.DMG_NONE, None]:
                damaging_attack = False
            if damaging_attack and record.actual_dmg_tup:
                actual_dealt_dmg, unhalved_dmg, prevented_dmg, mitigated_dmg = record.actual_dmg_tup

            if not damaging_attack:
                record.log_str = "non-damaging action"
            elif prevented_dmg > 0:
                record.log_str = "{} (-{}) {}".format(actual_dealt_dmg, prevented_dmg, ClashRecord.DEV_LOG_FLAGS[record.dmg_type])
            elif mitigated_dmg > 0:
                record.log_str = "{} {}//{} {}".format(
                    actual_dealt_dmg - mitigated_dmg, ClashRecord.DEV_LOG_FLAGS[cfg.DMG_AGG],
                    mitigated_dmg, ClashRecord.DEV_LOG_FLAGS[cfg.DMG_FULL_SPF]
                )
            else:
                record.log_str = "{} {}".format(unhalved_dmg, ClashRecord.DEV_LOG_FLAGS[record.dmg_type])

            weapon_str, power_str = "", ""
            if damaging_attack and action.weapon_used:
                weapon_str = "+{} via {}".format(record.dmg_bonus, action.weapon_used.name)
            elif damaging_attack and action.unarmed_power_used:
                if record.dmg_bonus > 0:
                    weapon_str = "+{} via {}".format(record.dmg_bonus, action.unarmed_power_used)
                else:
                    weapon_str = "via {}".format(action.unarmed_power_used)
            elif damaging_attack and record.dmg_bonus > 0:
                weapon_str = "+{} via no weapon?".format(record.dmg_bonus)
            elif damaging_attack:
                weapon_str = "unarmed"

            if damaging_attack and action.power_used:
                power_str = action.power_used
                weapon_str = "{}, {}".format(weapon_str, power_str)
            if weapon_str:
                weapon_str = "({})".format(weapon_str)
            record.log_str = "{} {}".format(weapon_str, record.log_str)

            if record.dmg_type == cfg.DMG_SPF:
                record.log_str += " =/=> {}".format(math.ceil(actual_dealt_dmg))

            return record

        def report(self, roll, atk_action, def_action):
            if atk_action.action_type in CAction.NO_CONTEST:
                rpt_template, pass_str = "{} takes no overt action, {}.", "passing the turn"
                if atk_action.action_type == CAction.FALL_BACK:
                    pass_str = "slinking back into the shadows"
                rpt_str = rpt_template.format(atk_action.user, pass_str)
                return rpt_str
            rpt_template = "{} ({}) => {} ({}) | margin of {} ({}/{} vs {}/{})\n{}{}"
            pc_defending = state.arena.attack_on_pc(atk_action)
            # if pc_defending:
            #     print('pc defending in report')
            #     r1, r2, r3, r4, r5 = roll.margin * -1, roll.opp_ws, atk_action.pool, roll.num_successes, roll.pool
            # else:
            r1, r2, r3, r4, r5 = roll.margin, roll.num_successes, roll.pool, roll.opp_ws, def_action.num_dice  # def_action.pool
            atype = ClashRecord.DEV_LOG_FLAGS[atk_action.action_type]
            dtype = ClashRecord.DEV_LOG_FLAGS[def_action.action_type]
            rep_atk_str, rep_def_str = "", ""
            if self.attack_record and self.attack_record.log_str and not atk_action.lost_to_trump_card:
                rep_atk_str = "atk: {}".format(self.attack_record.log_str)
            elif def_action.lost_to_trump_card:
                rep_atk_str = "atk: failed successfully"
            else:
                rep_atk_str = "atk: failed to connect"
            if self.defend_record and self.defend_record.log_str and not def_action.lost_to_trump_card:
                rep_def_str = "  /  def: {}".format(self.defend_record.log_str)
            elif atk_action.lost_to_trump_card:
                rep_def_str = "  /  def: failed, but got away anyway"
            else:
                rep_def_str = "  /  def: failed to defend"
            atkr_name = "{}[{}]".format(atk_action.user.name, str(atk_action.user.creature_type)[:2])
            defr_name = "{}[{}]".format(atk_action.target.name, str(atk_action.target.creature_type)[:2])
            rpt_str = rpt_template.format(atkr_name, atype, defr_name, dtype, r1, r2, r3, r4, r5, rep_atk_str, rep_def_str)
            self.history.append(rpt_str + '\n')
            # utils.log(rpt_str)
            return rpt_str


    class BattleArena:
        NUM_TURNS = 3
        PC_TEAM = "pc_team"
        ENEMY_TEAM = "enemies"

        def __init__(self, ambush=None, initiative_margin=0, **kwargs):
            self.battle_end = True
            self.round, self.actual_num_rounds, self.round_order = 0, 0, []
            self.initiative, self.ambush = None, ambush
            self.player_directive = None
            self.pc_team, self.enemies = [], []
            self.action_order, self.ao_index, self.ent_turns = [], 0, 1
            self.combat_log = CombatLog()
            #
            if not state.diceroller:
                state.diceroller = DiceRoller()
            self.reset(ambush=ambush, initiative_margin=initiative_margin, **kwargs)

        def reset(self, ambush=None, initiative_margin=0, **kwargs):
            self.battle_end, self.actual_num_rounds = True, BattleArena.NUM_TURNS
            if utils.percent_chance(5):
                self.actual_num_rounds += 1
            self.round = 0
            self.round_order = []
            if ambush == BattleArena.PC_TEAM or ambush == BattleArena.ENEMY_TEAM:
                self.initiative = ambush
            else:
                self.initiative = BattleArena.PC_TEAM if initiative_margin >= 0 else BattleArena.ENEMY_TEAM
            self.ambush = ambush
            switch, lag_team = False, BattleArena.ENEMY_TEAM if self.initiative == BattleArena.PC_TEAM else BattleArena.PC_TEAM
            for i in range(BattleArena.NUM_TURNS):
                self.round_order.append(lag_team if switch else self.initiative)
                switch = not switch
            utils.log("Round order: {}".format(self.round_order))
            self.player_directive = None
            self.pc_team, self.enemies = [], []
            self.action_order, self.ao_index = [], 0

        def register_combatants(self, pc_team, enemy_team):
            self.pc_team = pc_team
            self.pc_team.append(state.pc)
            self.enemies = enemy_team
            # Positions range from -2 to 2, with 0 at the center and -1/1 the usual starting positions.
            # Positions' only purpose is to determine who can hit who with what attack.
            for ent in self.pc_team:
                ent.current_pos = -1
                ent.engaged = []
            for ent in self.enemies:
                ent.current_pos = 1
                ent.engaged = []

        def set_position(self, char_pos_pair, *char_pos_pairs):
            char_pos_pair[0].current_pos = char_pos_pair[1]
            for pair in char_pos_pairs:
                pair[0].current_pos = pair[1]

        def start(self):
            state.in_combat = True
            self.battle_end = False
            self.eval_action_order()

        def get_init_order(self, roster):
            for combatant in roster:
                if combatant.is_pc:
                    pool = combatant.attrs[cfg.AT_DEX] + combatant.attrs[cfg.AT_WIT]
                else:
                    pool = combatant.physical + combatant.mental
                init_roll = state.diceroller.test(pool, 0, include_hunger=False)
                combatant.last_rolled_init = init_roll.margin
            ordered_roster = sorted(roster, key=lambda c: c.last_rolled_init)
            return ordered_roster

        def eval_action_order(self):
            if self.ambush is None:
                self.action_order = self.get_init_order(self.pc_team + self.enemies)
            else:
                self.action_order = self.get_init_order(self.round_order[0]) + self.get_init_order(self.round_order[1])

        def get_up_next(self):
            if self.ao_index >= len(self.action_order):
                return None
            return self.action_order[self.ao_index]

        def get_next_contest(self, preset_atk_action=None):
            if self.round >= self.actual_num_rounds:
                return self.battle_end_cleanup()
            if preset_atk_action:
                atk_action, up_next = preset_atk_action, preset_atk_action.user
            else:
                up_next = self.get_up_next()
                if not up_next:
                    return None, None
                if self.ent_turns <= 0:
                    self.ent_turns = up_next.turns if hasattr(up_next, "turns") else 1
                enemy_targets = self.pc_team if up_next in self.enemies else self.enemies
                opps = any([ct for ct in enemy_targets if not ct.dead and not ct.appears_dead])
                if not opps:
                    return self.battle_end_cleanup()
                if up_next.is_pc or up_next.dead:
                    return None, None
                all_targets = self.pc_team + self.enemies
                atk_action = up_next.attack(self.action_order, self.ao_index, enemy_targets, all_targets)
            if not atk_action.target or atk_action.target.is_pc:
                return atk_action, None
            def_action = atk_action.target.defend(up_next, atk_action)
            return atk_action, def_action

        def process_new_result(self, roll_result, atk_action, def_action):
            # margin_threshold = 0
            just_went = self.get_up_next()
            if roll_result is None:
                if just_went.dead:
                    self.increment()
                    return "{} is dead.".format(just_went.name)
                elif atk_action.action_type in CAction.NO_CONTEST:
                    self.increment()
                    return "..."
                raise ValueError("This should never be reached unless acting combatant is dead, and they don't seem to be.")

            if atk_action.action_type not in CAction.NO_CONTEST:
                if def_action.user.is_pc or (atk_action.target.is_pc and not atk_action.user.is_pc):
                    # margin_threshold = 1
                    pass
            follow_up_action = self.handle_clash(roll_result, atk_action, def_action)
            cl_report = self.combat_log.report(roll_result, atk_action, def_action)
            # rep_round, rep_ao_index = self.round + 1, self.ao_index
            if follow_up_action:
                return cl_report, follow_up_action
            if just_went.is_pc:
                state.mended_this_turn, state.used_disc_this_turn = False, False
                state.fleet_dodge_this_turn = False
            self.increment()
            return cl_report, None

        def increment(self):
            self.ent_turns -= 1
            up_next = self.get_up_next()
            if self.ent_turns > 0 and up_next and not up_next.dead:
                return
            self.ao_index += 1
            if self.ao_index >= len(self.action_order):
                self.ao_index = 0
                self.round += 1

        def handle_clash(self, roll_result, atk_action, def_action):
            atype, dtype = atk_action.action_type, def_action.action_type if def_action else None
            self.combat_log.reset()
            # track = cfg.TRACK_HP  # TODO: add conditions for mental attacks dealing willpower damage here

            print("\n\nAT HANDLE CLASSH MARGIN IS {} with attacker {} and defender {}\n\n".format(
                roll_result.margin, atk_action.user.name, def_action.user.name
            ))
            follow_up = None
            if atype == CAction.MELEE_ENGAGE:  # Melee Engage always behaves the same regardless of defense action.
                follow_up = self.handle_melee_engage(roll_result, atk_action, def_action)
            elif atype == CAction.RANGED_ATTACK:
                follow_up = self.handle_ranged_attack(roll_result, atk_action, def_action)
            elif atype == CAction.MELEE_ATTACK:
                follow_up = self.handle_melee_attack(roll_result, atk_action, def_action)
            elif atype == CAction.SPECIAL_ATTACK:
                follow_up = self.handle_special_attack(roll_result, atk_action, def_action)
            elif atype in CAction.NO_CONTEST:
                utils.log("No action! Or at least an action that doesn't invoke a contest.")
                follow_up = self.handle_non_contest(roll_result, atk_action)
            else:
                raise ValueError("\"{}\" is not a valid action type!".format(atype))
            self.play_clash_audio(roll_result.margin, atk_action, def_action)
            self.combat_log.set_clash_records(roll_result.margin, atk_action, def_action)
            return follow_up

        def handle_melee_engage(self, rolled, atk_action, def_action):
            # Move to the target's position and engage self unless it's a total failure, but only engage target on a win.
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            margin, fuiwin = rolled.margin, False
            if rolled.num_successes and rolled.outcome != V5DiceRoll.RESULT_BESTIAL_FAIL:
                atk_action.user.current_pos = atk_action.target.current_pos
                atk_action.user.engaged.append(atk_action.target)
                fuiwin = atk_action.skip_contest
            fuiwin = fuiwin and (rolled.num_successes or atk_action.user.has_disc_power(cfg.POWER_CELERITY_GRACE, cfg.DISC_CELERITY))
            # In a blink vs blink contest, the defender wins, i.e. "fuulose" trumps "fuiwin".
            fuulose = def_action.skip_contest and rolled.outcome not in (V5DiceRoll.RESULT_CRIT, V5DiceRoll.RESULT_MESSY_CRIT)
            fuulose = fuulose and bool(def_action.lifted_num_successes)
            if def_action.action_type == CAction.DODGE and fuulose:
                utils.log("Failed ranged attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            if margin >= 0 or fuiwin:
                atk_action.target.engaged.append(atk_action.user)
                if rolled.outcome in (V5DiceRoll.RESULT_MESSY_CRIT, V5DiceRoll.RESULT_CRIT) or fuiwin:
                    # A critical win on a rush (or any successes if using Blink) allows for a free extra melee attack.
                    # Weapon used is equipped, alt, or fists - in that priority order.
                    def_action.lost_to_trump_card = True
                    rush_attack = CAction(CAction.MELEE_ATTACK, atk_action.target, atk_action.user)
                    rush_attack.pool = "dexterity+combat/strength+combat"
                    return rush_attack
            elif def_action.action_type in CAction.OUCH:
                self.damage_step(margin, atk_action, def_action)
            else:
                utils.log("Failed melee engage against non-damaging attack.")
            # self.play_clash_audio(margin, atk_action_def_action)
            # self.combat_log.seet_clash_records(margin, atk_action, def_action)

        def handle_ranged_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            margin = rolled.margin
            # Blink dodgers can only be hit with a crit (and you still have to win), or if they totally fail.
            fuulose = def_action.skip_contest and rolled.outcome not in (V5DiceRoll.RESULT_CRIT, V5DiceRoll.RESULT_MESSY_CRIT)
            fuulose = fuulose and bool(def_action.lifted_num_successes)
            if def_action.action_type == CAction.DODGE and fuulose:
                utils.log("Failed ranged attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            if margin > 0:  # If a ranged attack lands nothing else matters.
                self.damage_step(margin, atk_action, def_action)
            else:  # If it fails, it may matter if the response is a ranged attack.
                if def_action.action_type == CAction.RANGED_ATTACK:
                    self.damage_step(margin, atk_action, def_action)
                elif def_action.action_type in CAction.OUCH and atk_action.user.current_pos == atk_action.target.current_pos:
                    self.damage_step(margin, atk_action, def_action)
                elif margin == 0:  # A tie with a ranged attack & non-damaging defense => win at margin 0.
                    self.damage_step(margin, atk_action, def_action, force_zero=True)
                else:
                    utils.log("Failed ranged attack with non-damaging response.")
            return None

        def handle_melee_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            margin = rolled.margin
            if atk_action.user.current_pos != atk_action.target.current_pos:
                utils.log("Melee attack launched against out-of-position target. This shouldn't ever be reached.")
                return
            # Blink dodgers can only be hit with a crit (and you still have to win), or if they totally fail.
            fuulose = def_action.skip_contest and rolled.outcome not in (V5DiceRoll.RESULT_CRIT, V5DiceRoll.RESULT_MESSY_CRIT)
            fuulose = fuulose and bool(def_action.lifted_num_successes)
            if def_action.action_type == CAction.DODGE and fuulose:
                utils.log("Failed melee attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            atk_action.user.engaged.append(atk_action.target)
            if margin > 0:  # Successful melee attack engages both user and target.
                atk_action.target.engaged.append(atk_action.user)
                self.damage_step(margin, atk_action, def_action)
            elif def_action.action_type in CAction.OUCH:
                self.damage_step(margin, atk_action, def_action)
            elif margin == 0:
                self.damage_step(margin, atk_action, def_action)
            else:
                utils.log("Failed melee attack with non-damaging response.")
            return None

        def handle_special_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            # margin = rolled.margin
            return None

        def handle_non_contest(self, rolled, atk_action):
            user = atk_action.user
            if atk_action.action_type == CAction.FALL_BACK:
                pos_mod = 1 if user in self.enemies else -1
                user.current_pos += pos_mod
            return None

        def play_clash_audio(self, margin, atk_action, def_action):
            win_sound, loss_sound, reaction_sound, extra_sound = audio.brawl_struggle, None, None, None
            attacker, defender = atk_action.user, def_action.user # TODO: standardize everywhere (def_action.user vs atk_action.target)
            attacker_scream, defender_scream = attacker.set_scream(), defender.set_scream()

            if margin >= 0 and ((not def_action.skip_contest) or atk_action.skip_contest):
                winning_action, losing_action = atk_action, def_action
                loser_scream = defender_scream
            else:
                winning_action, losing_action = def_action, atk_action
                loser_scream = attacker_scream
            win_weapon, loss_weapon = winning_action.weapon_used, losing_action.weapon_used
            print("SCREAMS -> attacker: {}, defender: {}, loser: {}".format(attacker_scream, defender_scream, loser_scream))

            if margin != 0:  # CLEAR WIN/LOSS
                win_sound = Weapon.get_fight_sound(winning_action, True)  # impact of winning weapon always plays
                if win_weapon and win_weapon.item_type == Item.IT_FIREARM:
                    extra_sound = Weapon.get_fight_sound(winning_action, None)  # gun reports always go off if winner uses gun
                    if loss_weapon and loss_weapon.item_type == Item.IT_FIREARM:
                        loss_sound = Weapon.get_fight_sound(losing_action, False)
                elif not win_weapon and winning_action.action_type in CAction.OUCH:
                    win_sound = audio.throwing_hands_1  # if winner uses fisticuffs it's assumed loser was interrupted
                    loss_sound = loser_scream
                elif winning_action.action_type == CAction.MELEE_ENGAGE:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                    loss_sound = Weapon.get_fight_sound(losing_action, False)
                else:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                    loss_sound = Weapon.get_fight_sound(losing_action, False)
            else:  # CLASHES ENDING IN TIE, no scream
                loser_scream = None
                if win_weapon:
                    win_sound = Weapon.get_fight_sound(winning_action, None)  # clash for melee, bang for guns
                else:  #elif winning_action.action_type == CAction.MELEE_ENGAGE:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                # else:
                    # win_sound = audio.brawl_struggle  # struggle sound for weaponless attacks (and default)
                if loss_weapon:
                    loss_sound = Weapon.get_fight_sound(losing_action, None)
                    if loss_weapon.item_type == Item.IT_FIREARM:
                        loss_sound = Weapon.get_fight_sound(losing_action, False)
                elif not win_sound or win_sound != audio.brawl_struggle:
                    loss_sound = audio.brawl_struggle

            if winning_action.action_type not in CAction.OUCH:
                loser_scream = None
                print("winner nonviolent, no scream")
            if not loss_sound:
                loss_sound = loser_scream
            elif loss_sound != loser_scream:
                reaction_sound = loser_scream

            print("\nCLASH SOUNDS:\nwin: {}\nextra: {}\nloss: {}\nreaction: {}\nloser_scream: {}".format(
                win_sound, extra_sound, loss_sound, reaction_sound, loser_scream
            ))
            # renpy.play(win_sound, "audio")
            utils.renpy_play(win_sound)
            if extra_sound:
                renpy.play(extra_sound, "audio")
            renpy.play(loss_sound, "audio")
            if reaction_sound:
                renpy.play(reaction_sound, "audio")  # was sound_aux

        def attack_on_pc(self, atk_action):
            return atk_action.target.is_pc and not atk_action.user.is_pc

        def damage_step(self, margin, atk_action, def_action, track=cfg.TRACK_HP, force_zero=False):
            self.combat_log.reset()
            self.combat_log.attack_record, self.combat_log.defend_record = ClashRecord(), ClashRecord()
            if margin >= 0 and atk_action.action_type in CAction.OUCH:# and attack:
                damage_val = margin if margin != 0 or force_zero else 1
                damage_val += atk_action.dmg_bonus
                print("\nATTACK DAMAGE (m={}, dv={}, action bonus={})\n".format(margin, damage_val, atk_action.dmg_bonus))
                self.combat_log.attack_record.actual_dmg_tup = state.deal_damage(
                    track, atk_action.dmg_type, damage_val, source="Combat", target=atk_action.target
                )
            if margin <= 0 and def_action.action_type in CAction.OUCH:# and defend:
                damage_val = abs(margin) if margin != 0 else 1
                damage_val += def_action.dmg_bonus
                print("\nDEFENSE DAMAGE (m={}, dv={}, action bonus={})\n".format(margin, damage_val, def_action.dmg_bonus))
                self.combat_log.defend_record.actual_dmg_tup = state.deal_damage(
                    track, def_action.dmg_type, damage_val, source="Combat", target=def_action.target
                )

        def battle_end_cleanup(self):
            self.combat_log.reset()
            self.battle_end = True
            for entity in (self.pc_team + self.enemies):
                entity.engaged = []
                entity.armor_active, entity.deathsave_active = False, False
                entity.current_pos = None
                if entity.dead:
                    print("'{}' is dead.".format(entity.name))
                    if not entity.is_pc:
                        # del entity (?)
                        entity.hp.spf_damage, entity.hp.agg_damage = 0, 0
                        entity.will.spf_damage, entity.will.agg_damage = 0, 0
                        entity.dead = False
                entity.appears_dead = False
                if entity.is_pc and cfg.DEV_MODE:
                    entity.hp.spf_damage, entity.hp.agg_damage = 0, 0
                    entity.will.spf_damage, entity.will.agg_damage = 0, 0
                # del entity (?)
                # if cfg.DEV_MODE:
                entity.purge_all_fx()
            state.in_combat = False
            state.blood_surge_active = False
            state.mended_this_turn, state.used_disc_this_turn = False, False
            state.fleet_dodge_this_turn = False
            return None, None
