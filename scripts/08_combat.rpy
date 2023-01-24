init 1 python in game:

    import math
    state = renpy.store.state

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

        def __init__(self, action_type, target:Entity, user=None, defending=False, pool=None, lethality=None, subtype=None):
            self.action_type = action_type  # Should be one of above types; subtype should be a discipline power or similar or None.
            self.pool = pool
            self.target, self.defending = target, defending
            self.user = user
            self.action_label = subtype
            if self.action_type is None and self.action_label is None:
                raise ValueError("At least one of 'action_type' and 'action_label' must be defined; they can't both be empty!")
            elif self.action_type is None:
                self.action_type = self.evaluate_type()
            # ---
            self.dmg_bonus, self.lethality = 0, 1
            if hasattr(self.user, "npc_dmg_bonus"):
                self.dmg_bonus, self.lethality = self.user.npc_dmg_bonus, self.user.npc_atk_lethality
            elif self.user.inventory and hasattr(self.user.inventory, "equipped"):
                equipment, self.dmg_bonus = self.user.inventory.equipped, 0
                if Inventory.EQ_WEAPON in equipment and equipment[Inventory.EQ_WEAPON]:
                    hwep, atype = equipment[Inventory.EQ_WEAPON], self.action_type
                    if atype == CAction.MELEE_ATTACK or hwep.item_type == Supply.IT_FIREARM or hwep.throwable:
                        self.dmg_bonus, self.lethality = hwep.dmg_bonus, hwep.lethality
            # TODO: add checks for active buffs e.g. Fist of Caine.
            if lethality is not None:  # If lethality value is passed it overrides other sources.
                self.lethality = lethality
            # ---
            if self.action_type in [CAction.DODGE, CAction.NO_ACTION, CAction.FALL_BACK] or not self.target:
                self.dmg_type = cfg.DMG_NONE
            else:
                self.dmg_type = Weapon.get_damage_type(self.lethality, target.creature_type)

        def evaluate_type(self):
            if self.defending and self.action_label in CAction.DODGE_VARIANTS:
                print("this action evaluates to {}".format(CAction.DODGE))
                return CAction.DODGE
            elif self.action_label in CAction.RANGED_ACTIONS:
                print("this action evaluates to {}".format(CAction.RANGED_ATTACK))
                return CAction.RANGED_ATTACK
            elif self.action_label in CAction.MELEE_ACTIONS:
                print("this action evaluates to {}".format(CAction.MELEE_ATTACK))
                return CAction.MELEE_ATTACK
            elif self.action_label in CAction.ANYWHERE_ACTIONS:
                if self.target is None:
                    print("escape or special")
                    return CAction.ESCAPE_ATTEMPT if self.defending else CAction.SPECIAL_ATTACK
                if self.target.current_pos == self.user.current_pos:
                    print("this action evaluates to {} (anywhere)".format(CAction.MELEE_ATTACK))
                    return CAction.MELEE_ATTACK
                print("this action evaluates to {} (anywhere)".format(CAction.RANGED_ATTACK))
                return CAction.RANGED_ATTACK
            print("this action evaluates to {} (wtf)".format(CAction.NO_ACTION))
            print(
                "\n-- self.user = {}, self.user.current_pos = {}, self.defending = {},\n".format(
                    self.user.name, self.user.current_pos, self.defending
                ) + "-- self.action_label = {}, self.target = {}, self.target.current_pos = {}".format(
                    self.action_label, self.target.name, self.target.current_pos
                )
            )
            return CAction.NO_ACTION

        @staticmethod
        def attack_is_gunshot(attacker, atk_action):
            if atk_action.action_type != CAction.RANGED_ATTACK:
                return False
            if str(cfg.SK_FIRE).lower() in str(atk_action.action_label).lower() or attacker.ranged_attacks_use_gun:
                return True
            return False


    # TODO: delete this nephew
    at_trl = {
        CAction.MELEE_ENGAGE: "Rush",
        CAction.MELEE_ATTACK: "Melee",
        CAction.RANGED_ATTACK: "Ranged",
        CAction.DODGE: "Dodge",
        CAction.ESCAPE_ATTEMPT: "Flee",
        CAction.SPECIAL_ATTACK: "Special",
        CAction.FALL_BACK: "Slink Back",
        CAction.NO_ACTION: "No Action",

        cfg.DMG_SPF: "spf dmg",
        cfg.DMG_FULL_SPF: "full spf dmg",
        cfg.DMG_AGG: "agg dmg"
    }


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
            self.action_order, self.ao_index = [], 0
            self.dmg_flag, self.dmg_bonus_flag = None, None
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
            print("Round order: {}".format(self.round_order))
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

        def get_next_contest(self):
            if self.round >= self.actual_num_rounds:
                self.battle_end = True
                self.battle_end_cleanup()
                return None, None
            up_next = self.get_up_next()
            if not up_next:
                return None, None
            if up_next.is_pc:
                return None, None
            enemy_targets = self.pc_team if up_next in self.enemies else self.enemies
            all_targets = self.pc_team + self.enemies
            atk_action = up_next.attack(self.action_order, self.ao_index, enemy_targets, all_targets)
            t_arget = atk_action.target  # t_arget, not to be confused with target  TODO: clean this up
            if t_arget.is_pc:
                return atk_action, None
            def_action = t_arget.defend(up_next, atk_action)
            return atk_action, def_action

        def process_new_result(self, roll_result, atk_action, def_action):
            margin_threshold = 0
            if atk_action.action_type not in CAction.NO_CONTEST:
                if def_action.user.is_pc or (atk_action.target.is_pc and not atk_action.user.is_pc):
                    margin_threshold = 1
            self.handle_clash(roll_result, atk_action, def_action, mt=margin_threshold)
            self.ao_index += 1
            return self.report(roll_result, atk_action, def_action)

        def handle_clash(self, roll_result, atk_action, def_action, mt=0):
            atype, dtype = atk_action.action_type, def_action.action_type if def_action else None
            self.dmg_flag = 0
            # track = cfg.TRACK_HP  # TODO: add conditions for mental attacks dealing willpower damage here

            if atype == CAction.MELEE_ENGAGE:  # Melee Engage always behaves the same regardless of defense action.
                self.handle_melee_engage(roll_result, atk_action, def_action)
            elif atype == CAction.RANGED_ATTACK:
                self.handle_ranged_attack(roll_result, atk_action, def_action)
            elif atype == CAction.MELEE_ATTACK:
                self.handle_melee_attack(roll_result, atk_action, def_action)
            elif atype == CAction.SPECIAL_ATTACK:
                self.handle_special_attack(roll_result, atk_action, def_action)
            elif atype in CAction.NO_CONTEST:
                utils.log("No action! Or at least an action that doesn't invoke a contest.")
                self.handle_non_contest(roll_result, atk_action)
            else:
                raise ValueError("\"{}\" is not a valid action type!".format(atype))

        def handle_melee_engage(self, rolled, atk_action, def_action, mt=0):
            # Always move to the target's position and engage self, but only engage them if successful.
            margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            self.dmg_flag = None
            atk_action.user.current_pos = atk_action.target.current_pos
            atk_action.user.engaged.append(atk_action.target)
            if margin >= mt:
                atk_action.target.engaged.append(atk_action.user)
            elif def_action.action_type in CAction.OUCH:
                self.deal_damage(margin, atk_action, def_action)
            else:
                print("Failed melee engage against non-damaging attack.")

        def handle_ranged_attack(self, rolled, atk_action, def_action, mt=0):
            margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            if margin >= mt:  # If a ranged attack lands nothing else matters.
                self.deal_damage(margin, atk_action, def_action)
            else:  # If it fails, it may matter if the response is a ranged attack.
                if def_action.action_type == CAction.RANGED_ATTACK:
                    self.deal_damage(margin, atk_action, def_action)
                elif def_action.action_type in CAction.OUCH and atk_action.user.current_pos == atk_action.target.current_pos:
                    self.deal_damage(margin, atk_action, def_action)
                else:
                    self.dmg_flag = None
                    print("Failed ranged attack with non-damaging response.")

        def handle_melee_attack(self, rolled, atk_action, def_action, mt=0):
            margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            if atk_action.user.current_pos != atk_action.target.current_pos:
                print("Melee attack launched against out-of-position target. This shouldn't ever be reached.")
                return
            atk_action.user.engaged.append(atk_action.target)
            if margin >= mt:  # Successful melee attack engages both user and target.
                atk_action.target.engaged.append(atk_action.user)
                self.deal_damage(margin, atk_action, def_action)
            elif def_action.action_type in CAction.OUCH:
                self.deal_damage(margin, atk_action, def_action)
            else:
                self.dmg_flag = None
                print("Failed melee attack with non-damaging response.")

        def handle_special_attack(self, rolled, atk_action, def_action):
            # margin = rolled.margin * (-1 if self.attack_on_pc(atk_action) else 1)
            pass

        def handle_non_contest(self, rolled, atk_action):
            user = atk_action.user
            if atk_action.action_type == CAction.FALL_BACK:
                pos_mod = 1 if user in self.enemies else -1
                user.current_pos += pos_mod

        def attack_on_pc(self, atk_action):
            return atk_action.target.is_pc and not atk_action.user.is_pc

        def deal_damage(self, margin, atk_action, def_action, track=cfg.TRACK_HP, mt=0):
            if margin >= mt:
                target, dmg_type, dmg_bonus = atk_action.target, atk_action.dmg_type, atk_action.dmg_bonus
            else:
                target, dmg_type, dmg_bonus = atk_action.user, def_action.dmg_type, def_action.dmg_bonus
            self.dmg_bonus_flag = "+{} dmg".format(dmg_bonus)
            self.dmg_flag, df_append = max(1, abs(margin)) + dmg_bonus, "{}".format(at_trl[dmg_type])
            if dmg_type == cfg.DMG_SPF:
                df_append += " =/=> {}".format(math.ceil(float(self.dmg_flag) / 2))
            state.deal_damage(track, dmg_type, self.dmg_flag, source="Combat", target=target)
            self.dmg_flag = str(self.dmg_flag) + df_append

        def report(self, roll, atk_action, def_action):
            rep_round, rep_ao_index = self.round + 1, self.ao_index
            if self.ao_index >= len(self.action_order):
                self.ao_index = 0
                self.round += 1
            if atk_action.action_type in CAction.NO_CONTEST:
                rpt_template, pass_str = "{} takes no overt action, {}.", "passing the turn"
                if atk_action.action_type == CAction.FALL_BACK:
                    pass_str = "slinking back into the shadows"
                rpt_str = rpt_template.format(atk_action.user, pass_str)
                return rpt_str
            # rpt_template = "R{}, T{}/{} | {} ({}) => {} ({}). | margin of {} ({}/{} vs {}/{}) (dmg: {})"
            rpt_template = "{} ({}) => {} ({}). | margin of {} ({}/{} vs {}/{}) ({}) => {}"
            if self.attack_on_pc(atk_action):
                r1, r2, r3, r4, r5 = roll.margin * -1, roll.opp_ws, atk_action.pool, roll.num_successes, roll.pool
            else:
                r1, r2, r3, r4, r5 = roll.margin, roll.num_successes, roll.pool, roll.opp_ws, def_action.pool,
            rpt_str = rpt_template.format(
                # rep_round, rep_ao_index, len(self.action_order),
                atk_action.user.name, at_trl[atk_action.action_type],
                atk_action.target.name, at_trl[def_action.action_type], r1, r2, r3, r4, r5,
                self.dmg_bonus_flag, self.dmg_flag
            )
            return rpt_str

        def battle_end_cleanup(self):
            self.dmg_flag, self.dmg_bonus_flag = None, None
            for entity in (self.pc_team + self.enemies):
                entity.engaged = []
                entity.current_pos = None
                if entity.dead:
                    print("'{}' is dead.".format(entity.name))
                    if not entity.is_pc:
                        # del entity (?)
                        entity.hp.spf_damage, entity.hp.agg_damage = 0, 0
                        entity.will.spf_damage, entity.will.agg_damage = 0, 0
                        entity.dead = False
                if entity.is_pc:
                    entity.hp.spf_damage, entity.hp.agg_damage = 0, 0
                    entity.will.spf_damage, entity.will.agg_damage = 0, 0
                else:
                    # del entity (?)
                    print("")
            state.in_combat = False


init 1 python in state:

    cfg, utils, game = renpy.store.cfg, renpy.store.utils, renpy.store.game

    def context_relevant(ability):
        if ability in cfg.REF_DISC_POWER_PASSIVES:  # Don't display passive powers in the context menu.
            return False  # This doesn't include powers that are switched on/off at will, like Lethal Body.
        if in_combat and ability in cfg.REF_DISC_POWERS_SNEAKY:
            return False if pc.current_pos > -2 else True  # Only usable in the back rank.
        if in_combat and ability in game.CAction.NPC_COMBAT_DISC_POWERS:
            return True
        if ability in cfg.REF_DISC_POWER_BUFFS:
            return True
        return False  # TODO: come back to this regularly

#
