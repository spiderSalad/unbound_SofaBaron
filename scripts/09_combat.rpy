init 1 python in game:

    import math
    state, audio = renpy.store.state, renpy.store.audio

    class CombatAction(CombAct):
        def __init__(
            self, action_type, target:Entity, user=None, defending=False, pool=None, subtype=None,
            use_sidearm=False, lethality=None, grapple_type=None
        ):
            self.action_type = action_type  # Should be one of above types; subtype should be a discipline power or similar or None.
            self.pool, self.num_dice, self.using_sidearm = pool, None, None
            self.target, self.defending = target, defending
            self.user = user
            self.action_label, self.grapple_action_type = subtype, grapple_type
            self.weapon_used, self.skip_contest, self.lost_to_trump_card = None, False, False
            self.use_sidearm = use_sidearm
            if self.user and self.use_sidearm:
                self.using_sidearm = True
                utils.log("Off-hand weapon penalty imposed on {} because use_sidearm ({}) set to True.".format(
                    self.user, self.user.sidearm if self.user and self.user.sidearm else "None?"
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
            grapple_weapon_set = False
            if self.grapple_action_type:
                if self.grapple_action_type in (CombAct.GRAPPLE_BITE, CombAct.GRAPPLE_BITE_PLUS):
                    weapon, weapon_alt, grapple_weapon_set = USING_FANGS, None, True
                elif self.grapple_action_type in (CombAct.GRAPPLE_DRINK, CombAct.GRAPPLE_DRINK_PLUS):
                    weapon, weapon_alt, grapple_weapon_set = FEEDING_IN_COMBAT, None, True
            if self.user and not grapple_weapon_set:
                if hasattr(self.user, "npc_weapon"):
                    weapon = self.user.npc_weapon
                if hasattr(self.user, "npc_weapon_alt"):
                    weapon_alt = self.user.npc_weapon_alt
                if self.user.is_pc or hasattr(self.user, "inventory"):
                    weapon, weapon_alt = self.user.held, self.user.sidearm
            if CombatAction.attack_weapon_match(weapon, self):
                self.weapon_used = weapon
            elif CombatAction.attack_weapon_match(weapon_alt, self):
                self.weapon_used = weapon_alt
                self.using_sidearm = True
                utils.log("Off-hand weapon penalty applied to attack type {} by {}, who has {} at hand and {} at side".format(
                    self.action_type, self.user, weapon, weapon_alt
                ))
            else:
                self.weapon_used = None

            self.dmg_bonus = 0
            self.armor_piercing = 0
            if self.user:
                if hasattr(self.user, "npc_dmg_bonus") and self.user.npc_dmg_bonus:
                    self.dmg_bonus, self.lethality = self.user.npc_dmg_bonus, self.user.npc_atk_lethality
                elif self.weapon_used:
                    self.dmg_bonus, self.lethality = self.weapon_used.dmg_bonus, self.weapon_used.lethality
            if lethality is not None:  # If lethality value is passed it overrides other sources.
                self.lethality = lethality
            # ---
            if not self.target or self.action_type in CombAct.NONVIOLENT:
                self.dmg_type = cfg.DMG_NONE
            else:
                self.dmg_type = Weapon.get_damage_type(self.lethality, target.creature_type)
            if self.action_type in (CombAct.NO_ACTION,):
                self.grapple_action_type = CombAct.GRAPPLE_MAINTAIN
            elif self.action_type in (CombAct.DODGE,) and (self.user.grappling_with or self.user.grappled_by):
                self.grapple_action_type = None if self.user.grappled_by else CombAct.GRAPPLE_MAINTAIN
                self.pool = f'{self.pool}+-{cfg.DODGE_WHILE_GRAPPLING_PENALTY}'  # Or while grappled.

        def __repr__(self):
            return "< {} action, label {} >".format(self.action_type, self.action_label)

        def evaluate_type(self):
            if self.defending and self.action_label in CombAct.DODGE_VARIANTS:
                return CombAct.DODGE
            elif self.action_label in CombAct.RANGED_ACTIONS:
                return CombAct.RANGED_ATTACK
            elif self.action_label in CombAct.MELEE_ACTIONS:
                return CombAct.MELEE_ATTACK
            elif self.action_label in CombAct.ANYWHERE_ACTIONS:
                if self.target is None:
                    return CombAct.ESCAPE_ATTEMPT if self.defending else CombAct.SPECIAL_ATTACK
                if self.target.current_pos == self.user.current_pos:
                    return CombAct.MELEE_ATTACK
                return CombAct.RANGED_ATTACK
            return CombAct.NO_ACTION

        @staticmethod
        def attack_weapon_match(weapon, action):
            if not weapon or not action:
                print(f'AWM - 1 weapon = {weapon} and action = {action}')
                return False
            if weapon.item_type == Item.IT_FIREARM:
                print(f'AWM - 2')
                return action.action_type == CombAct.RANGED_ATTACK
            if weapon.item_type == Item.IT_WEAPON:
                print(f'AWM - 3')
                return action.action_type == CombAct.MELEE_ATTACK or weapon.throwable
            print(f'AWM - 4')
            return False

        @staticmethod
        def attack_is_gunshot(attacker, atk_action):
            if atk_action.action_type != CombAct.RANGED_ATTACK:
                return False
            if attacker.ranged_attacks_use_gun or utils.caseless_in(cfg.SK_FIRE, atk_action.action_label):
                return True
            return False


    class ClashRecord:
        DEV_LOG_FLAGS = {
            CombAct.MELEE_ENGAGE: "Rush",
            CombAct.MELEE_ATTACK: "Melee",
            CombAct.RANGED_ATTACK: "Ranged",
            CombAct.DODGE: "Dodge",
            CombAct.ESCAPE_ATTEMPT: "Flee",
            CombAct.SPECIAL_ATTACK: "Special",
            CombAct.FALL_BACK: "Slink Back",
            CombAct.DISENGAGE: "Withdraw",
            CombAct.NO_ACTION: "No Action",

            cfg.DMG_SPF: "superf dmg",
            cfg.DMG_FULL_SPF: "unhalved dmg",
            cfg.DMG_AGG: "aggrav dmg",
            cfg.DMG_NONE: "(no damage)"
        }

        def __init__(self, user, battle_id=None, record_id=None, pov_margin=None, dmg_type=None, dmg_bonus=None, target=None):
            self.user, self.battle_id = user, battle_id
            self.record_id = "{:03d}".format(int(record_id)) if record_id and utils.is_number(record_id) else "???"
            self.pov_margin, self.target = pov_margin, target
            self.dmg_type, self.dmg_bonus = dmg_type, dmg_bonus
            self.log_str = ""
            self.actual_dmg_tup = None

        def __repr__(self):
            targ = " ==> {}".format(self.target) if self.target else ""
            return "{} #{} | {}{} :: {}".format(self.battle_id, self.record_id, self.user, target, self.log_str)

        def __str__(self):
            return self.__repr__()


    class CombatLog:
        REF_HEADER = "|COMBAT|"

        def __init__(self, dfa=None, dfd=None, dbfa=None, dbfd=None, dtfa=None, dtfd=None):
            self.history = []
            self.attack_record = ClashRecord(None, pov_margin=dfa, dmg_bonus=dbfa, dmg_type=dtfa)
            self.defend_record = ClashRecord(None, pov_margin=dfd, dmg_bonus=dbfd, dmg_type=dtfd)

        def reset(self):
            del self.attack_record, self.defend_record
            self.attack_record, self.defend_record = None, None

        @staticmethod
        def set_action_params(record: ClashRecord, margin, action):
            if not action:
                return record
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
                # record.log_str = "{} (-{}) {}".format(actual_dealt_dmg, prevented_dmg, ClashRecord.DEV_LOG_FLAGS[record.dmg_type])
                record.log_str = "{} ({} blocked) => {} {}".format(
                    unhalved_dmg + prevented_dmg, prevented_dmg, unhalved_dmg, ClashRecord.DEV_LOG_FLAGS[record.dmg_type]
                )
            elif mitigated_dmg > 0:
                record.log_str = "{} {}//{} {}".format(
                    actual_dealt_dmg - mitigated_dmg, ClashRecord.DEV_LOG_FLAGS[cfg.DMG_AGG],
                    mitigated_dmg, ClashRecord.DEV_LOG_FLAGS[cfg.DMG_FULL_SPF]
                )
            else:
                record.log_str = "{} {}".format(unhalved_dmg, ClashRecord.DEV_LOG_FLAGS[record.dmg_type])

            weapon_str, power_str = "", ""
            if damaging_attack and action.weapon_used:
                weapon_str = "+{} via {}".format(record.dmg_bonus, action.weapon_used)
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

        def report(self, roll, atk_action, def_action, reset=False):
            if reset:
                self.reset()
            if roll.margin >= 0:
                if not self.attack_record:
                    self.attack_record = ClashRecord(atk_action.user)
                CombatLog.set_action_params(self.attack_record, roll.margin, atk_action)
            if roll.margin <= 0:
                if not self.defend_record:
                    self.defend_record = ClashRecord(def_action.user if def_action else None)
                CombatLog.set_action_params(self.defend_record, roll.margin, def_action)
            #
            if atk_action.action_type in CombAct.NO_CONTEST:
                rpt_template, pass_str = "{} takes no overt action, {}.", "passing the turn"
                if atk_action.action_type == CombAct.FALL_BACK:
                    pass_str = "slinking back into the shadows"
                report_str = rpt_template.format(atk_action.user, pass_str)
                return report_str
            rpt_template = "{} ({}) => {} ({})\n - Margin of {} ({}/{} vs {}/{})\n{}{}"
            pc_defending = state.arena.attack_on_pc(atk_action)
            r1, r2, r3, r4, r5 = roll.margin, roll.num_successes, roll.pool, roll.opp_ws, def_action.num_dice  # def_action.pool
            atype = ClashRecord.DEV_LOG_FLAGS[atk_action.action_type]
            dtype = ClashRecord.DEV_LOG_FLAGS[def_action.action_type]
            rep_atk_str, rep_def_str = "", ""
            if self.attack_record and self.attack_record.log_str and not atk_action.lost_to_trump_card:
                rep_atk_str = "atk: {}".format(self.attack_record.log_str)
            elif def_action.lost_to_trump_card:
                rep_atk_str = "atk: failed successfully"
            else:
                fail_weap = atk_action.weapon_used if atk_action.weapon_used else "unarmed"
                rep_atk_str = "atk: ({}) failed to connect".format(fail_weap)
            if self.defend_record and self.defend_record.log_str and not def_action.lost_to_trump_card:
                rep_def_str = "\n  /  def: {}".format(self.defend_record.log_str)
            elif atk_action.lost_to_trump_card:
                rep_def_str = "\n  /  def: failed, but got away anyway"
            else:
                fail_weap = def_action.weapon_used if def_action.weapon_used else "unarmed"
                rep_def_str = "\n  /  def: ({}) failed to defend".format(fail_weap)
            atkr_name = "{}[{}-{}]".format(
                atk_action.user, str(atk_action.user.creature_type)[:2], str(atk_action.user.ftype)[:4]
            )
            defender = atk_action.target if atk_action.target else (def_action.user if def_action.user else None)
            defr_name = "{}[{}-{}]".format(
                defender if defender else "-???-", str(defender.creature_type)[:2] if defender else "--",
                str(defender.ftype)[:4] if defender else "x"
            )
            report_str = rpt_template.format(atkr_name, atype, defr_name, dtype, r1, r2, r3, r4, r5, rep_atk_str, rep_def_str)
            history_log_str = "#{:03d} | {}".format(len(self.history) + 1, report_str)
            self.history.append(history_log_str)
            return "{}{}".format(CombatLog.REF_HEADER, report_str)


    class BattleArena:
        NUM_TURNS = 4  # originally 3, as in three and out
        PC_TEAM = "pc_team"
        ENEMY_TEAM = "enemies"
        POSITION_LIMIT = 2

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
            # for i in range(BattleArena.NUM_TURNS):
            for i in range(self.actual_num_rounds):
                self.round_order.append(lag_team if switch else self.initiative)
                switch = not switch
            utils.log("Round order: {}".format(self.round_order))
            self.player_directive = None
            self.pc_team, self.enemies = [], []
            self.action_order, self.ao_index = [], 0

        def register_combatants(self, pc_team, enemy_team):
            self.pc_team = [ent for ent in pc_team]
            self.pc_team.append(state.pc)
            self.enemies = enemy_team
            # Positions range from -2 to 2, with 0 at the center and -1/1 the usual starting positions.
            # Positions' only purpose is to determine who can hit who with what attack.
            for ent in self.pc_team:
                ent.current_pos = -1
                self.disengage(ent)
            for ent in self.enemies:
                ent.current_pos = 1
                self.disengage(ent)

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
                return self.post_battle_cleanup()
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
                    return self.post_battle_cleanup()
                if up_next.dead:
                    return None, None
                if up_next.is_pc:
                    state.mended_this_turn, state.used_disc_this_turn = False, False
                    state.fleet_dodge_this_turn = False
                    return None, None
                all_targets = self.pc_team + self.enemies
                atk_action = up_next.attack(self.action_order, self.ao_index, enemy_targets, all_targets)
            if not atk_action.target or atk_action.target.is_pc:
            # if atk_action.target and atk_action.target.is_pc:
                return atk_action, None
            def_action = atk_action.target.defend(up_next, atk_action)
            return atk_action, def_action

        def process_new_result(self, roll_result, atk_action, def_action):
            # margin_threshold = 0
            just_went = self.get_up_next()
            if roll_result is None:
                if just_went.dead:
                    self.increment()
                    return "{} is dead.".format(just_went)
                elif atk_action.action_type in CombAct.NO_CONTEST:
                    self.increment()
                    if just_went.is_pc:
                        return "..."
                    pns = just_went.pronoun_set
                    if just_went.engaged_by:
                        return "{} is unable to act while {} cornered by {} attackers.".format(
                            just_went, pns.PN_SHES_HES_THEYRE, pns.PN_HER_HIS_THEIR
                        )
                    else:
                        return "{} seems to be biding {} time...".format(just_went, pns.PN_HER_HIS_THEIR)
                raise ValueError("This should never be reached unless acting combatant is dead, and they don't seem to be.")

            follow_up = self.handle_clash(roll_result, atk_action, def_action)
            cl_report = self.combat_log.report(roll_result, atk_action, def_action)
            self.handle_post_clash(atk_action, def_action)
            if follow_up:
                return cl_report, follow_up
            self.increment()
            return cl_report, atk_action.user, (def_action.user if def_action else None)

        def increment(self):
            self.ent_turns -= 1
            up_next = self.get_up_next()
            if self.ent_turns > 0 and up_next and not up_next.dead:
                return
            self.ao_index += 1
            if self.ao_index >= len(self.action_order):
                self.ao_index = 0
                self.round += 1
                self.handle_end_of_turn()

        def handle_end_of_turn(self):
            for ent in (self.pc_team + self.enemies):
                ent.times_attacked_this_turn = 0

        def handle_clash(self, roll_result, atk_action, def_action):
            atype, dtype = atk_action.action_type, def_action.action_type if def_action else None
            self.combat_log.reset()
            # track = cfg.TRACK_HP  # TODO: add conditions for mental attacks dealing willpower damage here
            follow_up = None
            # Defender maintains their grapple (for the moment) if they're using a grapple-typed action or the attacker is.
            # NOTE: Check the above if unexpected behavior occurs.
            if not def_action.grapple_action_type and not atk_action.grapple_action_type:
                self.abandon_grapples(def_action.user)
            if atk_action.target and atk_action.action_type not in CombAct.NONVIOLENT:
                atk_action.target.times_attacked_this_turn += 1
            if atype == CombAct.MELEE_ENGAGE:  # Melee Engage always behaves the same regardless of defense action.
                follow_up = self.handle_melee_engage(roll_result, atk_action, def_action)
            elif atype == CombAct.RANGED_ATTACK:
                follow_up = self.handle_ranged_attack(roll_result, atk_action, def_action)
            elif atype == CombAct.MELEE_ATTACK:
                follow_up = self.handle_melee_attack(roll_result, atk_action, def_action)
            elif atype == CombAct.SPECIAL_ATTACK:
                follow_up = self.handle_special_attack(roll_result, atk_action, def_action)
            elif atype == CombAct.DISENGAGE:
                follow_up = self.handle_disengage_attempt(roll_result, atk_action, def_action)
            elif atype in CombAct.NO_CONTEST:
                utils.log("No action! Or at least an action that doesn't invoke a contest.")
                follow_up = self.handle_non_contest(roll_result, atk_action)
            else:
                raise ValueError("\"{}\" is not a valid action type!".format(atype))
            self.play_clash_audio(roll_result.margin, atk_action, def_action)
            return follow_up

        def handle_melee_engage(self, rolled, atk_action, def_action):
            # Move to the target's position and engage self unless it's a total failure, but only engage target on a win.
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            margin, fuiwin = rolled.margin, False
            if rolled.num_successes and rolled.outcome != V5DiceRoll.RESULT_BESTIAL_FAIL:
                atk_action.user.current_pos = atk_action.target.current_pos
                self.engage_by(atk_action.user, atk_action.target)
                fuiwin = atk_action.skip_contest
            fuiwin = fuiwin and (rolled.num_successes or atk_action.user.has_disc_power(cfg.POWER_CELERITY_GRACE, cfg.DISC_CELERITY))
            # In a blink vs blink contest, the defender wins, i.e. "fuulose" trumps "fuiwin".
            fuulose = def_action.skip_contest and rolled.outcome not in (V5DiceRoll.RESULT_CRIT, V5DiceRoll.RESULT_MESSY_CRIT)
            fuulose = fuulose and bool(def_action.lifted_num_successes)
            if def_action.action_type == CombAct.DODGE and fuulose:
                utils.log("Failed ranged attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            if margin >= 0 or fuiwin:
                self.engage_by(atk_action.target, atk_action.user, mutual=True)
                if rolled.outcome in (V5DiceRoll.RESULT_MESSY_CRIT, V5DiceRoll.RESULT_CRIT) or fuiwin:
                    # A critical win on a rush (or any successes if using Blink) allows for a free extra melee attack.
                    # Weapon used is equipped, alt, or fists - in that priority order.
                    def_action.lost_to_trump_card = True
                    rush_attack = CombatAction(CombAct.MELEE_ATTACK, atk_action.target, atk_action.user)
                    if atk_action.user.is_pc:
                        rush_attack.pool = "dexterity+combat/strength+combat"
                    else:
                        ranked_attacks = FightBrain.grucs_v2(atk_action.user, CombAct.MELEE_ATTACK)
                        rush_attack.action_label, rush_attack.pool = ranked_attacks[0]
                    return rush_attack
            elif def_action.action_type in CombAct.OUCH:
                self.damage_step(margin, atk_action, def_action)
            else:
                utils.log("Failed melee engage against non-damaging attack.")

        def handle_ranged_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            margin = rolled.margin
            # Blink dodgers can only be hit with a crit (and you still have to win), or if they totally fail.
            fuulose = def_action.skip_contest and rolled.outcome not in (V5DiceRoll.RESULT_CRIT, V5DiceRoll.RESULT_MESSY_CRIT)
            fuulose = fuulose and bool(def_action.lifted_num_successes)
            if def_action.action_type == CombAct.DODGE and fuulose:
                utils.log("Failed ranged attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            if margin > 0:  # If a ranged attack lands nothing else matters.
                self.damage_step(margin, atk_action, def_action)
            else:  # If it fails, it may matter if the response is a ranged attack.
                if def_action.action_type == CombAct.RANGED_ATTACK:
                    self.damage_step(margin, atk_action, def_action)
                elif def_action.action_type in CombAct.OUCH and atk_action.user.current_pos == atk_action.target.current_pos:
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
            if def_action.action_type == CombAct.DODGE and fuulose:
                utils.log("Failed melee attack against teleporting target.")
                atk_action.lost_to_trump_card = True
                return None
            #
            self.engage_by(atk_action.user, atk_action.target)
            grapple_results = None
            if atk_action.grapple_action_type:
                perform_damage_step = self.handle_grapple_clash(rolled, atk_action, def_action)
                if not perform_damage_step:
                    return None
            elif atk_action.user.grappling_with:  # A non-grapple action means abandoning all grapples in your favor.
                self.abandon_grapples(atk_action.user)
            if margin > 0:  # Successful melee attack engages both user and target.
                self.engage_by(atk_action.target, atk_action.user, mutual=True)
                self.damage_step(margin, atk_action, def_action)
            elif def_action.action_type in CombAct.OUCH:
                self.damage_step(margin, atk_action, def_action)
            elif margin == 0:
                self.damage_step(margin, atk_action, def_action)
            else:
                utils.log("Failed melee attack with non-damaging response.")
            return None

        def handle_grapple_clash(self, rolled, atk_action, def_action):  # TODO set ai grapple behavior, test grapple clashes
            margin, user, target = rolled.margin, atk_action.user, atk_action.target
            grapple_type = atk_action.grapple_action_type
            if margin < 0:
                self.a_escapes_b_grapple(target, user)
                return True
            self.engage_by(target, user, mutual=True)
            self.a_grapples_b(user, target)
            self.a_escapes_b_grapple(user, target)
            # self.abandon_grapples(target)
            if grapple_type in (CombAct.GRAPPLE_DMG, CombAct.GRAPPLE_MAINTAIN):
                return True
            elif grapple_type in (CombAct.GRAPPLE_HOLD, CombAct.GRAPPLE_ACTIVE_ESCAPE):  # TODO: Revisit these.
                return False
            elif grapple_type in (CombAct.GRAPPLE_BITE, CombAct.GRAPPLE_BITE_PLUS):
                # target.hp.damage(cfg.DMG_AGG, 2, source_who=user)
                if grapple_type == CombAct.GRAPPLE_BITE_PLUS:
                    self.handle_combat_feeding_turn(target, user, CombAct.GRAPPLE_DRINK_PLUS)
                return True
            elif grapple_type in (CombAct.GRAPPLE_DRINK, CombAct.GRAPPLE_DRINK_PLUS):
                self.handle_combat_feeding_turn(target, user, grapple_type)
                return False
            # TODO: still need to implement AI grappling, at least responses

        def handle_combat_feeding_turn(self, target, user, grapple_type):
            if target.mortal:
                drain_dmg, dmg_type = True, cfg.DMG_AGG
            else:
                drain_dmg = grapple_type == CombAct.GRAPPLE_DRINK_PLUS
                dmg_type = cfg.DMG_SPF
            dmg_amount = 5 if grapple_type == CombAct.GRAPPLE_DRINK_PLUS else 1
            if drain_dmg:
                target.hp.damage(dmg_type, dmg_amount, source_who=user)
            state.set_hunger(f'-={dmg_amount}', who=user, killed=target.dead)

        def handle_special_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            # margin = rolled.margin
            return None

        def handle_disengage_attempt(self, rolled, atk_action, def_action):
            user = atk_action.user
            if not def_action and rolled.num_successes:
                utils.log("{} disengages and retreats, uncontested.".format(user))
                user.current_pos += (1 if user in self.enemies else -1)
                return None
            elif not def_action:
                utils.log("{} unilaterally fails to disengage and retreat. How embarrassing for {}.".format(
                    user, user.pronoun_set.PN_HER_HIM_THEM
                ))
                return None
            fuiwin = atk_action.skip_contest
            fuiwin = fuiwin and (rolled.num_successes or user.has_disc_power(cfg.POWER_CELERITY_GRACE, cfg.DISC_CELERITY))
            if rolled.margin >= 0 or fuiwin:
                self.disengage(user)
                def_action.lost_to_trump_card = fuiwin
                user.current_pos += (1 if user in self.enemies else -1)
            elif def_action.action_type in CombAct.OUCH:
                self.damage_step(rolled.margin, atk_action, def_action)
            else:
                utils.log("Failed disengage against non-damaging attack.")
            return None

        def handle_non_contest(self, rolled, atk_action):
            user = atk_action.user
            if atk_action.action_type == CombAct.FALL_BACK:
                pos_mod = 1 if user in self.enemies else -1
                user.current_pos += pos_mod
            return None

        def handle_post_clash(self, atk_action, def_action):
            # Disengage/ungrapple check
            for ent in (self.pc_team + self.enemies):
                for i in range(len(ent.engaged_by) - 1, -1, -1):
                    opp = ent.engaged_by[i]
                    if opp.current_pos != ent.current_pos or opp.dead or opp.crippled or opp.shocked:
                        utils.log("Disengaging {} from {}.".format(ent, opp))
                        self.disengage(ent, opp, mutual=True)
                for i in range(len(ent.grappled_by) - 1, -1, -1):
                    opp, ungrapple = ent.grappled_by[i], False
                    if opp.dead or opp.crippled or opp.shocked:
                        self.abandon_grapples(opp)
                    elif ent.dead or (opp.current_pos != ent.current_pos and (not hasattr(opp, "long_grip") or not opp.long_grip)):
                        self.a_escapes_b_grapple(ent, opp)
                if ent.dead:
                    if ent.killer and isinstance(ent.killer, Entity) and ent.killer.creature_type == cfg.CT_VAMPIRE:  # Killed by a vampire!
                        if ent.cause_of_death and ent.cause_of_death in (cfg.COD_BITE, cfg.COD_DRAINED):
                            killed, slaked = bool(ent.killer.hunger < 2), 2 if ent.killer.hunger > 1 else 1
                            state.set_hunger(f'-={slaked}', who=ent.killer, killed=killed)
            # Other regular housekeeping
            for action in (atk_action, def_action):  # If an off-hand weapon was used for an attack, it's now the main held weapon.
                if action.using_sidearm:
                    state.switch_weapons(who=action.user, reload_menu=action.user.is_pc, as_effect=True)
            #

        def play_clash_audio(self, margin, atk_action, def_action):
            # There should always be an atk_action, but there isn't always a def_action.
            win_sound, loss_sound, reaction_sound, extra_sound = audio.brawl_struggle, None, None, None
            attacker, defender = atk_action.user, (def_action.user if def_action else None)
            attacker_scream, defender_scream = attacker.set_scream(), None
            if defender:
                defender_scream = defender.set_scream()

            if margin >= 0 and (not def_action or not def_action.skip_contest or atk_action.skip_contest):
                winning_action, losing_action = atk_action, def_action
                loser_scream = defender_scream
            else:
                winning_action, losing_action = def_action, atk_action
                loser_scream = attacker_scream
            if winning_action is None:
                winning_action = losing_action
                losing_action = None
            win_weapon, loss_weapon = winning_action.weapon_used, (losing_action.weapon_used if losing_action else None)

            # TODO: bite attack sound!
            if margin != 0:  # CLEAR WIN/LOSS
                win_sound = Weapon.get_fight_sound(winning_action, True)  # impact of winning weapon always plays
                if win_weapon and win_weapon.item_type == Item.IT_FIREARM:
                    extra_sound = Weapon.get_fight_sound(winning_action, None)  # gun reports always go off if winner uses gun
                    if loss_weapon and loss_weapon.item_type == Item.IT_FIREARM:
                        loss_sound = Weapon.get_fight_sound(losing_action, False)
                elif not win_weapon and winning_action and winning_action.action_type in CombAct.OUCH:
                    win_sound = audio.throwing_hands_1  # if winner uses fisticuffs it's assumed loser was interrupted
                    loss_sound = loser_scream
                elif winning_action and winning_action.action_type == CombAct.MELEE_ENGAGE:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                    loss_sound = Weapon.get_fight_sound(losing_action, False)
                else:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                    loss_sound = Weapon.get_fight_sound(losing_action, False)
            else:  # CLASHES ENDING IN TIE, no scream
                loser_scream = None
                if win_weapon:
                    win_sound = Weapon.get_fight_sound(winning_action, None)  # clash for melee, bang for guns
                else:  #elif winning_action.action_type == CombAct.MELEE_ENGAGE:
                    win_sound = Weapon.get_fight_sound(winning_action, True)
                # else:
                    # win_sound = audio.brawl_struggle  # struggle sound for weaponless attacks (and default)
                if loss_weapon:
                    loss_sound = Weapon.get_fight_sound(losing_action, None)
                    if loss_weapon.item_type == Item.IT_FIREARM:
                        loss_sound = Weapon.get_fight_sound(losing_action, False)
                elif not win_sound or win_sound != audio.brawl_struggle:
                    loss_sound = audio.brawl_struggle

            if winning_action.action_type not in CombAct.OUCH:
                loser_scream = None
            if not loss_sound:
                loss_sound = loser_scream
            elif loss_sound != loser_scream:
                reaction_sound = loser_scream

            # renpy.play(win_sound, "audio")
            utils.renpy_play(win_sound)
            if extra_sound:
                renpy.play(extra_sound, "audio")
            renpy.play(loss_sound, "audio")
            if reaction_sound:
                renpy.play(reaction_sound, "audio")  # was sound_aux

        def attack_on_pc(self, atk_action):
            if not atk_action:
                raise ValueError("Tried to determine if an attack action is targeting the PC, but action is invalid or missing.")
            if not atk_action.target:
                return False
            return atk_action.target.is_pc and (not atk_action.user or not atk_action.user.is_pc)

        def is_cornered(self, ent):
            if not ent or ent not in (self.pc_team + self.enemies):
                return False
            if ent.grappled_by and (True):  # TODO: Replace this with whatever powers/stats let you fight while cornered.
                return True
            if ent in self.pc_team and ent.current_pos <= -1 * abs(BattleArena.POSITION_LIMIT):
                return True
            if ent in self.enemies and ent.current_pos >= abs(BattleArena.POSITION_LIMIT):
                return True
            return False

        def damage_step(self, margin, atk_action, def_action, track=cfg.TRACK_HP, force_zero=False):
            self.combat_log.reset()
            self.combat_log.attack_record = ClashRecord(atk_action.user)
            self.combat_log.defend_record =  ClashRecord(def_action.user if def_action else None)
            dmg_what = "Combat"
            if margin >= 0 and atk_action.action_type in CombAct.OUCH:# and attack:
                damage_val = margin if margin != 0 or force_zero else 1
                damage_val += atk_action.dmg_bonus
                if atk_action.weapon_used and atk_action.weapon_used.key == USING_FANGS.key:
                    damage_val, atk_action.dmg_type, dmg_what = 2, cfg.DMG_AGG, cfg.COD_BITE
                self.combat_log.attack_record.actual_dmg_tup = state.deal_damage(
                    track, atk_action.dmg_type, damage_val, source_what=dmg_what, source_who=atk_action.user, target=atk_action.target
                )
            if margin <= 0 and def_action.action_type in CombAct.OUCH:# and defend:
                damage_val = abs(margin) if margin != 0 else 1
                damage_val += def_action.dmg_bonus
                if def_action.weapon_used and def_action.weapon_used.key == USING_FANGS.key:
                    damage_val, def_action.dmg_type, dmg_what = 2, cfg.DMG_AGG, cfg.COD_BITE
                self.combat_log.defend_record.actual_dmg_tup = state.deal_damage(
                    track, def_action.dmg_type, damage_val, source_what=dmg_what, source_who=def_action.user, target=def_action.target
                )

        def set_engagement_status(self, disengage, ent1, ent2=None, mutual=False):
            if disengage:
                if ent2 and mutual:
                    ent2.engaged_by = utils.list_minus(ent2.engaged_by, ent1)
                if ent2:
                    ent1.engaged_by = utils.list_minus(ent1.engaged_by, ent2)
                else:
                    ent1.engaged_by.clear()
            else:
                if not ent2:
                    raise ValueError("Creating a combat engagement requires two combatants!")
                if mutual:
                    ent2.engaged_by = utils.list_plus_nodup(ent2.engaged_by, ent1)
                ent1.engaged_by = utils.list_plus_nodup(ent1.engaged_by, ent2)

        def engage_by(self, ent1, ent2, mutual=False):
            self.set_engagement_status(False, ent1, ent2=ent2, mutual=mutual)

        def disengage(self, ent1, ent2=None, mutual=False):
            self.set_engagement_status(True, ent1, ent2=ent2, mutual=mutual)

        def set_grapple_status(self, break_free, actor, acted_upon=None, mutual=False):
            if break_free:  # Actor breaks free from Acted_upon, or from all grapples.
                if acted_upon and mutual:
                    actor.grappling_with = utils.list_minus(actor.grappling_with, acted_upon)
                    acted_upon.grappled_by = utils.list_minus(acted_upon.grappled_by, actor)
                if acted_upon:
                    acted_upon.grappling_with = utils.list_minus(acted_upon.grappling_with, actor)
                    actor.grappled_by = utils.list_minus(actor.grappled_by, acted_upon)
                else:
                    for grappler in actor.grappled_by:
                        grappler.grappling_with = utils.list_minus(grappler.grappling_with, actor)
                        if mutual:
                            grappler.grappled_by = utils.list_minus(grappler.grappled_by, actor)
                    actor.grappled_by.clear()
                    if mutual:
                        actor.grappling_with.clear()
            else:  # Actor grapples Acted_upon
                if not acted_upon:
                    raise ValueError("Creating a combat grapple requires two combatants!")
                if mutual:
                    actor.grappled_by = utils.list_plus_nodup(actor.grappled_by, acted_upon)
                    acted_upon.grappling_with = utils.list_plus_nodup(acted_upon.grappling_with, actor)
                acted_upon.grappled_by = utils.list_plus_nodup(acted_upon.grappled_by, actor)
                actor.grappling_with = utils.list_plus_nodup(actor.grappling_with, acted_upon)

        def a_grapples_b(self, actor, acted_upon, mutual=False):
            print(f'\n{actor} should soon be grappled by {acted_upon}')
            self.set_grapple_status(False, actor, acted_upon=acted_upon, mutual=mutual)
            print(f'---end of a_grapples_b---')

        def a_escapes_b_grapple(self, actor, acted_upon=None, mutual=False):
            print(f'\n{actor} should soon be free from {acted_upon}')
            self.set_grapple_status(True, actor, acted_upon=acted_upon, mutual=mutual)
            print(f'---end of a_escapes_b_grapple---')

        def abandon_grapples(self, grappler):
            if grappler and grappler.grappling_with:
                for ent in grappler.grappling_with:
                    self.a_escapes_b_grapple(ent, grappler, mutual=False)

        def post_battle_cleanup(self):
            self.combat_log.reset()
            self.battle_end = True
            for entity in (self.pc_team + self.enemies):
                self.disengage(entity)
                self.abandon_grapples(entity)
                entity.armor_active, entity.deathsave_active = False, False
                entity.current_pos = None
                if entity.dead:
                    utils.log("{} died (or \"died\") in battle.")
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


#
