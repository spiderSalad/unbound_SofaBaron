init 1 python in game:

    import math
    state, audio = renpy.store.state, renpy.store.audio

    class ClashRecord:
        DEV_LOG_FLAGS = {
            CAction.MELEE_ENGAGE: "Rush",
            CAction.MELEE_ATTACK: "Melee",
            CAction.RANGED_ATTACK: "Ranged",
            CAction.DODGE: "Dodge",
            CAction.ESCAPE_ATTEMPT: "Flee",
            CAction.SPECIAL_ATTACK: "Special",
            CAction.FALL_BACK: "Slink Back",
            CAction.DISENGAGE: "Withdraw",
            CAction.NO_ACTION: "No Action",

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
            targ = " ==> {}".format(self.target.name) if self.target else ""
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
            if atk_action.action_type in CAction.NO_CONTEST:
                rpt_template, pass_str = "{} takes no overt action, {}.", "passing the turn"
                if atk_action.action_type == CAction.FALL_BACK:
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
                fail_weap = atk_action.weapon_used.name if atk_action.weapon_used else "unarmed"
                rep_atk_str = "atk: ({}) failed to connect".format(fail_weap)
            if self.defend_record and self.defend_record.log_str and not def_action.lost_to_trump_card:
                rep_def_str = "\n  /  def: {}".format(self.defend_record.log_str)
            elif atk_action.lost_to_trump_card:
                rep_def_str = "\n  /  def: failed, but got away anyway"
            else:
                fail_weap = def_action.weapon_used.name if def_action.weapon_used else "unarmed"
                rep_def_str = "\n  /  def: ({}) failed to defend".format(fail_weap)
            atkr_name = "{}[{}-{}]".format(
                atk_action.user.name, str(atk_action.user.creature_type)[:2], str(atk_action.user.ftype)[:4]
            )
            defender = atk_action.target if atk_action.target else (def_action.user if def_action.user else None)
            defr_name = "{}[{}-{}]".format(
                defender.name if defender else "-???-", str(defender.creature_type)[:2] if defender else "--",
                str(defender.ftype)[:4] if defender else "x"
            )
            report_str = rpt_template.format(atkr_name, atype, defr_name, dtype, r1, r2, r3, r4, r5, rep_atk_str, rep_def_str)
            history_log_str = "#{:03d} | {}".format(len(self.history) + 1, report_str)
            self.history.append(history_log_str)
            return "{}{}".format(CombatLog.REF_HEADER, report_str)


    class BattleArena:
        NUM_TURNS = 3
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
                    return "{} is dead.".format(just_went.name)
                elif atk_action.action_type in CAction.NO_CONTEST:
                    self.increment()
                    if just_went.is_pc:
                        return "..."
                    pns = just_went.pronoun_set
                    if just_went.engaged:
                        return "{} is unable to act while {} cornered by {} attackers.".format(
                            just_went.name, pns.PN_SHES_HES_THEYRE, pns.PN_HER_HIS_THEIR
                        )
                    else:
                        return "{} seems to be biding {} time...".format(just_went.name, pns.PN_HER_HIS_THEIR)
                raise ValueError("This should never be reached unless acting combatant is dead, and they don't seem to be.")

            follow_up = self.handle_clash(roll_result, atk_action, def_action)
            cl_report = self.combat_log.report(roll_result, atk_action, def_action)
            self.handle_post_clash(atk_action, def_action)
            if follow_up:
                return cl_report, follow_up
            self.increment()
            return cl_report, atk_action.user, def_action.user if def_action else None

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
            follow_up = None
            if atype == CAction.MELEE_ENGAGE:  # Melee Engage always behaves the same regardless of defense action.
                follow_up = self.handle_melee_engage(roll_result, atk_action, def_action)
            elif atype == CAction.RANGED_ATTACK:
                follow_up = self.handle_ranged_attack(roll_result, atk_action, def_action)
            elif atype == CAction.MELEE_ATTACK:
                follow_up = self.handle_melee_attack(roll_result, atk_action, def_action)
            elif atype == CAction.SPECIAL_ATTACK:
                follow_up = self.handle_special_attack(roll_result, atk_action, def_action)
            elif atype == CAction.DISENGAGE:
                follow_up = self.handle_disengage_attempt(roll_result, atk_action, def_action)
            elif atype in CAction.NO_CONTEST:
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
                    if atk_action.user.is_pc:
                        rush_attack.pool = "dexterity+combat/strength+combat"
                    else:
                        ranked_attacks = FightBrain.grucs_v2(atk_action.user, CAction.MELEE_ATTACK)
                        rush_attack.action_label, rush_attack.pool = ranked_attacks[0]
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
                user.engaged = []
                def_action.lost_to_trump_card = fuiwin
                user.current_pos += (1 if user in self.enemies else -1)
            elif def_action.action_type in CAction.OUCH:
                self.damage_step(rolled.margin, atk_action, def_action)
            else:
                utils.log("Failed disengage against non-damaging attack.")
            return None

        def handle_non_contest(self, rolled, atk_action):
            user = atk_action.user
            if atk_action.action_type == CAction.FALL_BACK:
                pos_mod = 1 if user in self.enemies else -1
                user.current_pos += pos_mod
            return None

        def handle_post_clash(self, atk_action, def_action):
            # Disengage check
            for ent in (self.pc_team + self.enemies):
                for i in range(len(ent.engaged) - 1, -1, -1):
                    opp = ent.engaged[i]
                    if opp.current_pos != ent.current_pos or opp.dead or opp.crippled or opp.shocked:
                        utils.log("Disengaging {} from {}.".format(ent.name, opp.name))
                        ent.engaged.remove(opp)
            # Other regular housekeeping
            for action in (atk_action, def_action):  # If an off-hand weapon was used for an attack, it's now the main held weapon.
                if action.using_sidearm:
                    state.switch_weapons(who=action.user, reload_menu=action.user.is_pc, as_effect=True)
            #

        def play_clash_audio(self, margin, atk_action, def_action):
            # There should always be an atk_action, but there isn't always a def_action.
            win_sound, loss_sound, reaction_sound, extra_sound = audio.brawl_struggle, None, None, None
            attacker, defender = atk_action.user, (def_action.user if def_action else None)
            # TODO: standardize everywhere (def_action.user vs atk_action.target)
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

            if margin != 0:  # CLEAR WIN/LOSS
                win_sound = Weapon.get_fight_sound(winning_action, True)  # impact of winning weapon always plays
                if win_weapon and win_weapon.item_type == Item.IT_FIREARM:
                    extra_sound = Weapon.get_fight_sound(winning_action, None)  # gun reports always go off if winner uses gun
                    if loss_weapon and loss_weapon.item_type == Item.IT_FIREARM:
                        loss_sound = Weapon.get_fight_sound(losing_action, False)
                elif not win_weapon and winning_action and winning_action.action_type in CAction.OUCH:
                    win_sound = audio.throwing_hands_1  # if winner uses fisticuffs it's assumed loser was interrupted
                    loss_sound = loser_scream
                elif winning_action and winning_action.action_type == CAction.MELEE_ENGAGE:
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
            if ent in self.pc_team and ent.current_pos <= -1 * abs(BattleArena.POSITION_LIMIT):
                return True
            if ent in self.enemies and ent.current_pos >= abs(BattleArena.POSITION_LIMIT):
                return True
            return False

        def damage_step(self, margin, atk_action, def_action, track=cfg.TRACK_HP, force_zero=False):
            self.combat_log.reset()
            self.combat_log.attack_record = ClashRecord(atk_action.user)
            self.combat_log.defend_record =  ClashRecord(def_action.user if def_action else None)
            if margin >= 0 and atk_action.action_type in CAction.OUCH:# and attack:
                damage_val = margin if margin != 0 or force_zero else 1
                damage_val += atk_action.dmg_bonus
                self.combat_log.attack_record.actual_dmg_tup = state.deal_damage(
                    track, atk_action.dmg_type, damage_val, source="Combat", target=atk_action.target
                )
            if margin <= 0 and def_action.action_type in CAction.OUCH:# and defend:
                damage_val = abs(margin) if margin != 0 else 1
                damage_val += def_action.dmg_bonus
                self.combat_log.defend_record.actual_dmg_tup = state.deal_damage(
                    track, def_action.dmg_type, damage_val, source="Combat", target=def_action.target
                )

        def post_battle_cleanup(self):
            self.combat_log.reset()
            self.battle_end = True
            for entity in (self.pc_team + self.enemies):
                entity.engaged = []
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