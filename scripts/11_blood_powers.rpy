init 1 python in game:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state


    class BuffPipeline:

        @staticmethod
        def process_pool(who, base_pool, action=None, contest_params=None):
            if action and who is not action.user:
                raise ValueError("Mismatch between \"who\" user and action.user.")
            elif contest_params and who is not contest_params.contestant:
                raise ValueError("Mismatch between \"who\" user and contest_params.contestant.")

            if action is None:
                return BuffPipeline.noncombat_test(who, contest_params, base_pool)
            who, action, base_pool = BuffPipeline.any_combat_action(who, action, base_pool)
            if action.action_type == CombAct.MELEE_ATTACK:
                return BuffPipeline.melee_attack(who, action, base_pool)
            if action.action_type == CombAct.RANGED_ATTACK:
                return BuffPipeline.ranged_attack(who, action, base_pool)
            if action.action_type == CombAct.MELEE_ENGAGE:
                return BuffPipeline.rush(who, action, base_pool)
            if action.action_type == CombAct.DODGE:
                return BuffPipeline.attack_evasion(who, action, base_pool)
            return action, base_pool

        @staticmethod
        def noncombat_test(user, contest_params, base_pool):
            new_pool = str(base_pool)
            fx = user.status_effects

            # Prowess (feats of strength)
            if user.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE) and Entity.SE_HULKING in fx:
                if cfg.AT_STR in base_pool or (user.shapeshift_form and cfg.SK_COMB in base_pool):
                    new_pool += f'+{cfg.DISC_POTENCE}'

            # Fleetness (noncombat dexterity)
            if user.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY) and Entity.SE_FLEETY in fx:
                if cfg.AT_DEX in base_pool or (user.shapeshift_form and cfg.SK_ATHL in base_pool):
                    new_pool += f'+{cfg.DISC_CELERITY}'

            # Cat's Grace, contest_param for "balance"
            #
            return contest_params, new_pool

        @staticmethod
        def any_combat_action(user, action, base_pool):
            is_physical_pool, is_mental_social_pool = False, False
            updated_pool = base_pool
            if user.crippled:
                is_physical_pool = any([
                    # Exempt: Stamina & Traversal
                    utils.caseless_in(cfg.AT_STR, base_pool), utils.caseless_in(cfg.AT_DEX, base_pool),
                    utils.caseless_in(cfg.SK_ATHL, base_pool), utils.caseless_in(cfg.SK_COMB, base_pool),
                    utils.caseless_in(cfg.SK_FIRE, base_pool), utils.caseless_in(cfg.SK_CLAN, base_pool)
                ])
            if user.shocked:
                is_mental_social_pool = any([
                    utils.caseless_in(cfg.AT_CHA, base_pool), utils.caseless_in(cfg.AT_MAN, base_pool),
                    utils.caseless_in(cfg.AT_COM, base_pool), utils.caseless_in(cfg.AT_INT, base_pool),
                    utils.caseless_in(cfg.AT_WIT, base_pool), utils.caseless_in(cfg.AT_RES, base_pool),
                    # Exempt: Streetwise, Occult
                    utils.caseless_in(cfg.SK_DIPL, base_pool), utils.caseless_in(cfg.SK_INTI, base_pool),
                    utils.caseless_in(cfg.SK_INTR, base_pool), utils.caseless_in(cfg.SK_LEAD, base_pool),
                    utils.caseless_in(cfg.SK_ACAD, base_pool), utils.caseless_in(cfg.SK_INSP, base_pool),
                    utils.caseless_in(cfg.SK_SCIE, base_pool), utils.caseless_in(cfg.SK_TECH, base_pool)
                ])

            if is_physical_pool or is_mental_social_pool:
                # updated_pool += f'+-{cfg.IMPAIRMENT_PENALTY}'
                updated_pool += f'+{cfg.REF_IMPAIRMENT_PARAM}'

            return user, action, updated_pool

        @staticmethod
        def melee_attack(user, action, base_pool):
            target, weapon_used = action.target, action.weapon_used
            new_pool = str(base_pool)

            if action.using_sidearm is not None:
                if user.has_disc_power(cfg.POWER_CELERITY_TWITCH, cfg.DISC_CELERITY):
                    utils.log(f'Quick-draw! Weapon switch penalty waived for {user.name}.')
                else:
                    new_pool += f'+-{cfg.WEAPON_DRAW_PENALTY}'

            # Lethal Body
            if not weapon_used and user.has_disc_power(cfg.POWER_POTENCE_FATALITY, cfg.DISC_POTENCE):
                if user.lethal_body_active and target.mortal and action.lethality > 0:
                    action.dmg_type = cfg.DMG_AGG
                    action.armor_piercing = user.disciplines.levels[cfg.DISC_POTENCE]
                    action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, cfg.POWER_POTENCE_FATALITY, sep=", ")

            fx = user.status_effects
            # Prowess (combat)
            if user.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE) and Entity.SE_HULKING in fx:
                # Either get Potence rank as feat-of-strength pool bonus or combat damage bonus, but not both.
                user_gat = action.grapple_action_type
                # You get feat-of-strength bonus if you're trying to escape a grapple or melee-attacking someone you've already grappled.
                if user_gat:
                    bite_actions = (CombAct.GRAPPLE_BITE, CombAct.GRAPPLE_BITE_PLUS)
                    if user_gat in (CombAct.GRAPPLE_ESCAPE,) or (user.grappling_with and target in user.grappling_with):
                        new_pool += f'+{cfg.DISC_POTENCE}'
                    elif user_gat in bite_actions and (target in user.grappling_with or target in user.grappled_by):
                        new_pool += f'+{cfg.DISC_POTENCE}'
                else:
                    potence_rank = user.disciplines.levels[cfg.DISC_POTENCE]
                    prowess_dmg = math_ceil(potence_rank / 2) if weapon_used else potence_rank
                    BuffPipeline.apply_damage_bonus(action, prowess_dmg, cfg.POWER_POTENCE_PROWESS)
                action.power_used = utils.unique_append(action.power_used, cfg.POWER_POTENCE_PROWESS, sep=", ")

            # Feral Weapons and Vicissitude weapons
            feral_weapons = user.has_disc_power(cfg.POWER_PROTEAN_TOOTH_N_CLAW, cfg.DISC_PROTEAN)
            # feral_weapons = feral_weapons and hasattr(user, "feral_weapons_active") and user.feral_weapons_active
            feral_weapons = state.StatusFX.has_buff(user, Entity.SE_FERAL_WEPS)
            fleshcraft = user.has_disc_power(cfg.POWER_PROTEAN_MOLD_SELF, cfg.DISC_PROTEAN)
            fc_weapons = fleshcraft and Entity.SE_FLESHCRAFT_WEAPON in fx
            if not weapon_used and feral_weapons:  # NOTE: Feral and Vicissitude weapons are counted as unarmed attacks here.
                utils.log("--- Buff Pipeline --- | Feral Weapons{}".format(" (with Vicissitude-flavor)" if fc_weapons else ""))
                action.lethality = max(action.lethality, 3)
                # action.attack_sound = Weapon.WEAPON_SOUNDS[Weapon.MW_KNIFE]
                BuffPipeline.apply_damage_bonus(action, 2, cfg.POWER_PROTEAN_TOOTH_N_CLAW)
                ferwep_str = "Feral Weapons{}".format(" (Vicis)" if fc_weapons else "")
                action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, ferwep_str, sep=", ")
            elif not weapon_used and fc_weapons:
                utils.log("--- Buff Pipeline --- | Vicissitude weapons")
                action.lethality = max(action.lethality, 2)
                # action.attack_sound = Weapon.WEAPON_SOUNDS[Weapon.MW_SWORD]
                BuffPipeline.apply_damage_bonus(action, 2, cfg.POWER_PROTEAN_MOLD_SELF)
                action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, cfg.POWER_PROTEAN_MOLD_SELF, sep=", ")

            # More?
            return action, new_pool

        @staticmethod
        def ranged_attack(user, action, base_pool):
            new_pool = str(base_pool)
            if action.using_sidearm is not None:
                if user.has_disc_power(cfg.POWER_CELERITY_TWITCH, cfg.DISC_CELERITY):
                    utils.log("Quick-draw! Weapon switch penalty waived for {}.".format(user.name))
                else:
                    new_pool += "+-{}".format(cfg.WEAPON_DRAW_PENALTY)

            return action, new_pool

        @staticmethod
        def rush(user, action, base_pool):
            new_pool = str(base_pool)

            # Blink (rush)
            blink = cfg.POWER_CELERITY_BLINK
            if user.has_disc_power(blink, cfg.DISC_CELERITY) and utils.caseless_in(blink, action.unarmed_power_used):
                action.autowin = True

            # Soaring Leap (rush)
            superjump = cfg.POWER_POTENCE_SUPERJUMP
            if user.has_disc_power(superjump, cfg.DISC_POTENCE) and utils.caseless_in(superjump, action.unarmed_power_used):
                new_pool += "+{}".format(cfg.DISC_POTENCE)

            return action, new_pool

        @staticmethod
        def apply_damage_bonus(action, value, db_label=None):
            if not action.dmg_bonus:
                action.dmg_bonus = value
            elif db_label and db_label in action.dmg_bonus_labels:
                action.dmg_bonus -= action.dmg_bonus_labels[db_label]
                action.dmg_bonus_labels[db_label] = max(value, action.dmg_bonus_labels[db_label])
                action.dmg_bonus += action.dmg_bonus_labels[db_label]
            else:
                action.dmg_bonus += value
            if db_label and db_label not in action.dmg_bonus_labels:
                action.dmg_bonus_labels[db_label] = value

        @staticmethod
        def attack_evasion(user, action, base_pool):
            new_pool = str(base_pool)

            fx = user.status_effects

            # Rapid Reflexes (dodging)
            # NOTE: Code implementing this is in script_05_battles.rpy for PC and 10_behavior.rpy for NPCs, considering moving it.

            # Fleetness (dodging)
            can_flit = Entity.SE_FLEETY in fx and action.defending and not state.fleet_dodge_this_turn
            flit_this_action = False
            # can_flit = user.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY)
            if can_flit and utils.caseless_in(cfg.POWER_CELERITY_SPEED, action.unarmed_power_used):
                # if utils.caseless_in(cfg.AT_DEX, base_pool) and utils.caseless_in(cfg.SK_ATHL, base_pool):
                if utils.caseless_in(cfg.SK_ATHL, base_pool):
                    new_pool += "+{}".format(cfg.DISC_CELERITY)
                    flit_this_action, state.fleet_dodge_this_turn = True, True
                # elif (user.shapeshift_form and utils.caseless_in(cfg.SK_ATHL, base_pool)):
                #     new_pool += "+{}".format(cfg.DISC_CELERITY)
                #     state.fleet_dodge_this_turn = True

            # Blink (dodge)
            blink = cfg.POWER_CELERITY_BLINK
            if user.has_disc_power(blink, cfg.DISC_CELERITY) and utils.caseless_in(blink, action.unarmed_power_used):
                action.autowin = True

            # Weaving (dodging ranged)
            can_weave = not flit_this_action and state.StatusFX.weaving_power_is_valid(user, action)  # Fleetness and Weaving don't stack.
            if can_weave and utils.caseless_in(cfg.POWER_CELERITY_MATRIX_DODGE, action.unarmed_power_used):
                if utils.caseless_in(cfg.SK_ATHL, base_pool):
                    new_pool += "+{}".format(cfg.DISC_CELERITY)

            # Soaring Leap (dodge)
            superjump = cfg.POWER_POTENCE_SUPERJUMP
            if user.has_disc_power(superjump, cfg.DISC_POTENCE) and utils.caseless_in(superjump, action.unarmed_power_used):
                new_pool += "+{}".format(cfg.DISC_POTENCE)

            # Potence power for dodging while grapples?
            if user.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE) and Entity.SE_HULKING in fx:
                user_gat = action.grapple_action_type
                # You get feat-of-strength bonus if you're trying to escape a grapple or melee-attacking someone you've already grappled.
                if (user_gat and user_gat in (CombAct.GRAPPLE_ESCAPE,)):
                    new_pool += f'+{cfg.DISC_POTENCE}'
                elif user.grappled_by or ((user.grappling_with) and action.target in user.grappling_with):
                    new_pool += f'+{cfg.DISC_POTENCE}'

            return action, new_pool


init 1 python in state:

    cfg, game, audio = renpy.store.cfg, renpy.store.game, renpy.store.audio
    Entity = game.Entity


    class StatusFX:
        def __init__(self, pc):
            self.pc = pc
            self.history = []

        def log(self, msg):
            self.history.append(msg)
            utils.log(msg)

        def apply_buff(self, who, buff, duration, force_replace=False):
            if not hasattr(who, "status_effects"):
                raise AttributeError("\"{}\" is not a valid Entity or lacks valid Entity.status_effects.".format(who))
            who.buff(buff, duration)

        def remove_buff(who, buff, purge=True, force_remove=False):
            if not hasattr(who, "status_effects"):
                raise AttributeError("Not a valid Entity or lacking valid Entity.status_effects.")
            who.purge_status(buff, purge=purge, force_remove=force_remove)

        @staticmethod
        def buff_can_be_removed(buff):  # TODO: ?
            return True

        @staticmethod
        def get_buff_ttl(who, buff):
            if not hasattr(who, "status_effects"):
                raise AttributeError("Not a valid Entity or lacking valid Entity.status_effects.")
            if buff in who.status_effects:
                return who.status_effects[buff]
            return None

        @staticmethod
        def has_buff(who, buff):
            ttl = StatusFX.get_buff_ttl(who, buff)
            if ttl is None:
                return False
            return True

        @staticmethod
        def has_any_buff(who, *buffs):
            for bf in buffs:
                if StatusFX.has_buff(who, bf):
                    return True
            return False

        @staticmethod
        def has_all_buffs(who, buff, *buffs):
            for bf in ([buff] + buffs):
                if not StatusFX.has_buff(who, bf):
                    return False
            return True

        @staticmethod
        def weaving_power_is_valid(who, def_action):
            weaving_buff = StatusFX.has_buff(who, Entity.SE_WEAVING)
            if def_action:
                return all([weaving_buff, def_action.vs_ranged, def_action.defending])
            return False

        @staticmethod
        def power_is_active(who, power):  # TODO: come back to this regularly
            if power == cfg.POWER_CELERITY_SPEED:
                return StatusFX.has_buff(who, Entity.SE_FLEETY)
            if power == cfg.POWER_CELERITY_MATRIX_DODGE:
                return StatusFX.has_buff(who, Entity.SE_WEAVING)
            if power == cfg.POWER_FORTITUDE_TOUGH:
                return StatusFX.has_buff(who, Entity.SE_TOUGHNESS)
            if power == cfg.POWER_FORTITUDE_BANE:
                return StatusFX.has_buff(who, Entity.SE_ANTIBANE)
            if power == cfg.POWER_OBFUSCATE_FADE:
                return StatusFX.has_any_buff(who, Entity.SE_OBFU_ROOTED, Entity.SE_OBFU_MOBILE)
            if power == cfg.POWER_OBFUSCATE_STEALTH:
                return StatusFX.has_buff(who, Entity.SE_OBFU_MOBILE)
            if power == cfg.POWER_POTENCE_FATALITY:
                return hasattr(who, "lethal_body_active") and who.lethal_body_active
            if power == cfg.POWER_POTENCE_PROWESS:
                return StatusFX.has_buff(who, Entity.SE_HULKING)
            if power == cfg.POWER_PROTEAN_FLOAT:
                return hasattr(who, "featherweight_active") and who.featherweight_active
            if power == cfg.POWER_PROTEAN_REDEYE:
                return hasattr(who, "beast_eyes_active") and who.beast_eyes_active
            if power == cfg.POWER_PROTEAN_TOOTH_N_CLAW:
                return StatusFX.has_buff(who, Entity.SE_FERAL_WEPS)
            utils.log("Power \"{}\" not accounted for in StatusFX.power_is_active().".format(power))
            return False

        @staticmethod
        def find_power_in_disc_tree(power_name):
            for dname in cfg.REF_DISC_POWER_TREES:
                disc = cfg.REF_DISC_POWER_TREES[dname]
                for level, d_tier in enumerate(disc):
                    if power_name in d_tier:
                        return dname, 1+level
            return None, None

        @staticmethod
        def get_num_rouse_checks(power_name, who=None, active=False):
            if who is None: who = self.pc
            if power_name in cfg.REF_DISC_POWER_PASSIVES + cfg.REF_DISC_POWER_TOGGLABLES:
                return 0, None
            if active and power_name in cfg.REF_DISC_POWER_FREE_ON_DEACTIVATE:
                return 0, None
            p_disc, p_level = StatusFX.find_power_in_disc_tree(power_name)
            if p_level <= 1:  # TODO: revisit when Blood Sorcery added.
                return 0, None
            reroll_cap = utils.get_bp_disc_reroll_level(who.blood_potency)
            gets_reroll = p_level <= reroll_cap
            if power_name in cfg.REF_DISC_TWO_ROUSE_POWERS:  # Empty list for now.
                return 2, gets_reroll
            return 1, gets_reroll

        def use_disc_power(self, power_name, who=None):
            if who is None: who = self.pc
            dp_name, power_active = str(power_name).lower().replace(' ', '_').replace("'", ""), False
            if any([
                power_name == cfg.POWER_PROTEAN_TOOTH_N_CLAW and StatusFX.has_buff(who, Entity.SE_FERAL_WEPS),
                False
            ]):
                power_active = True
            if dp_name and hasattr(self, dp_name):
                num_rouse_checks, reroll = StatusFX.get_num_rouse_checks(power_name, who, active=power_active)
                hungrier = False
                if num_rouse_checks > 0 and who.can_rouse():
                    if not cfg.DEV_MODE or not cfg.FREE_DISCIPLINES:
                        hungrier = renpy.call_in_new_context("roll_control.rouse_check", num_checks=num_rouse_checks, reroll=reroll)
                    if hungrier:
                        refresh_hunger_ui()
                elif num_rouse_checks > 0:
                    return  # TODO: check this too as per below.
                getattr(self, dp_name)(who=who)
                if power_name not in (cfg.REF_DISC_POWER_FREEBIES + cfg.REF_DISC_POWER_PASSIVES):
                    global used_disc_this_turn
                    used_disc_this_turn = True
                # return hungrier  TODO: figure out why returning values from here causes a "Nonetype not subscriptible" error
                # in the menus in script_05_battles.rpy. Something about the context?
                # It's being called from a renpy screen interaction and the error occurs when that interaction is triggered
                # while on a menu, as if that's returning None as a menu choice selection?
            else:
                raise ValueError("\"{}\" is not implemented here, at least not yet.".format(dp_name))

        # Animalism

        def sense_the_beast(self, who=None):
            if who.has_disc_power(cfg.POWER_ANIMALISM_SENSE, cfg.DISC_ANIMALISM):
                who.using_sense_the_beast = not who.using_sense_the_beast
                # renpy.play(audio.something, "audio") TODO find sound for this

        # Celerity

        def fleetness(self, who=None):
            if who.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY):
                self.apply_buff(who, Entity.SE_FLEETY, 12)
                renpy.play(audio.fleeing_footsteps1, "sound")

        def weaving(self, who=None):
            if who.has_disc_power(cfg.POWER_CELERITY_MATRIX_DODGE, cfg.DISC_CELERITY):
                self.apply_buff(who, Entity.SE_WEAVING, 12)
                renpy.play(audio.fleeing_footsteps1, "sound")

        # Fortitude

        def toughness(self, who=None):
            if who.has_disc_power(cfg.POWER_FORTITUDE_TOUGH, cfg.DISC_FORTITUDE):
                self.apply_buff(who, Entity.SE_TOUGHNESS, 9)
                # if hasattr(who, "hp"):
                #     who.hp.armor_active = True
                renpy.play(audio.toughness_frost, "sound")

        def defy_bane(self, who=None):
            if who.has_disc_power(cfg.POWER_FORTITUDE_BANE, cfg.DISC_FORTITUDE):
                self.apply_buff(who, Entity.SE_ANTIBANE, 9)
                renpy.play(audio.toughness_armor, "sound")

        # Potence

        def lethal_body(self, who=None):
            if hasattr(who, "lethal_body_active"):
                has_lb = who.has_disc_power(cfg.POWER_POTENCE_FATALITY, cfg.DISC_POTENCE)
                who.lethal_body_active = not who.lethal_body_active and has_lb
                renpy.play(audio.knuckle_crack_1, "audio")

        def prowess(self, who=None):
            if who.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE):
                self.apply_buff(who, Entity.SE_HULKING, 9)
                renpy.play(audio.pulled_taut_1, "audio")

        # Protean

        def feral_weapons(self, who=None):
            if StatusFX.has_buff(who, Entity.SE_FERAL_WEPS):
                self.remove_buff(who, Entity.SE_FERAL_WEPS)
            elif who.has_disc_power(cfg.POWER_PROTEAN_TOOTH_N_CLAW, cfg.DISC_PROTEAN):
                self.apply_buff(who, Entity.SE_FERAL_WEPS, 15)
                renpy.play(audio.beastgrowl2, "audio")


init 1 python in state:

    cfg, utils, game = renpy.store.cfg, renpy.store.utils, renpy.store.game

    # Returns (Relevant, Active).
    #  - Relevant: None = not displayed, False = inactive/unusable, True = usable
    #  - Active: Truthy/Falsy, can only activate if Falsy.
    def context_relevant(ability):  # NOTE: need to return active/inactive for buffs/toggles!
        if ability in cfg.REF_DISC_POWER_PASSIVES:  # Don't display passive powers in the context menu.
            return None, None  # This doesn't include powers that are switched on/off at will, like Lethal Body.
        if ability in cfg.REF_DISC_POWER_MENU_ONLY:
            return None, None
        can_use_disc = not used_disc_this_turn or ability in cfg.REF_DISC_POWER_FREEBIES
        if in_combat and ability in cfg.REF_DISC_POWERS_SNEAKY:
            usable = False if pc.current_pos > -2 else can_use_disc  # Only usable in the back rank.
            return usable, StatusFX.power_is_active(pc, ability)
        if ability in cfg.REF_DISC_POWER_BUFFS:
            power_active = StatusFX.power_is_active(pc, ability)
            relevance = can_use_disc or (power_active and ability in cfg.REF_DISC_POWER_FREE_ON_DEACTIVATE)
            return relevance, power_active
        if in_combat and ability in game.CombAct.NPC_COMBAT_DISC_POWERS:
            return can_use_disc, False
        return None, None  # TODO: come back to this regularly


#
