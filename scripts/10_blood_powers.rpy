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
            if action.action_type == CAction.MELEE_ATTACK:
                return BuffPipeline.melee_attack(who, action, base_pool)
            if action.action_type == CAction.RANGED_ATTACK:
                return BuffPipeline.ranged_attack(who, action, base_pool)
            if action.action_type == CAction.DODGE:
                return BuffPipeline.attack_evasion(who, action, base_pool)
            return action, base_pool

        @staticmethod
        def noncombat_test(user, contest_params, base_pool):
            new_pool = str(base_pool)
            fx = user.status_effects

            # Prowess (feats of strength)
            if user.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE) and Entity.SE_HULKING in fx:
                if cfg.AT_STR in base_pool or (user.shapeshift_form and cfg.SK_COMB in base_pool):
                    new_pool += "+{}".format(cfg.DISC_POTENCE)

            # Fleetness (noncombat dexterity)
            if user.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY) and Entity.SE_FLEETY in fx:
                if cfg.AT_DEX in base_pool or (user.shapeshift_form and cfg.SK_ATHL in base_pool):
                    new_pool += "+{}".format(cfg.DISC_CELERITY)

            # Cat's Grace, contest_param for "balance"
            #
            return contest_params, new_pool

        @staticmethod
        def melee_attack(user, action, base_pool):
            target, weapon_used = action.target, action.weapon_used
            new_pool = str(base_pool)

            if action.alt_weapon_penalty is not None:
                new_pool += "+-{}".format(cfg.WEAPON_DRAW_PENALTY)

            # Lethal Body
            if not weapon_used and user.has_disc_power(cfg.POWER_POTENCE_FATALITY, cfg.DISC_POTENCE):
                if user.lethal_body_active and target.mortal:
                    action.dmg_type = cfg.DMG_AGG
                    action.armor_piercing = user.disciplines.levels[cfg.DISC_POTENCE]
                    action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, cfg.POWER_POTENCE_FATALITY, sep=", ")

            fx = user.status_effects
            # Prowess (combat)
            if user.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE) and Entity.SE_HULKING in fx:
                potence_rank = user.disciplines.levels[cfg.DISC_POTENCE]
                prowess_dmg = math_ceil(potence_rank / 2) if weapon_used else potence_rank
                BuffPipeline.apply_damage_bonus(action, prowess_dmg, cfg.POWER_POTENCE_PROWESS)
                action.power_used = utils.unique_append(action.power_used, cfg.POWER_POTENCE_PROWESS, sep=", ")

            # Feral Weapons and Vicissitude weapons
            feral_weapons = user.has_disc_power(cfg.POWER_PROTEAN_TOOTH_N_CLAW, cfg.DISC_PROTEAN)
            feral_weapons = feral_weapons and hasattr(user, "feral_weapons_active") and user.feral_weapons_active
            fleshcraft = user.has_disc_power(cfg.POWER_PROTEAN_MOLD_SELF, cfg.DISC_PROTEAN)
            fc_weapons = fleshcraft and Entity.SE_FLESHCRAFT_WEAPON in fx
            if not weapon_used and feral_weapons:  # NOTE: Feral and Vicissitude weapons are counted as unarmed attacks here.
                utils.log("--- Buff Pipeline --- | Feral Weapons{}".format(" (with Vicissitude-flavor)" if fc_weapons else ""))
                action.lethality = max(action.lethality, 3)
                action.attack_sound = Weapon.WEAPON_SOUNDS[Weapon.MW_KNIFE]
                BuffPipeline.apply_damage_bonus(action, 2, cfg.POWER_PROTEAN_TOOTH_N_CLAW)
                ferwep_str = "Feral Weapons{}".format(" (Vicis)" if fc_weapons else "")
                action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, ferwep_str, sep=", ")
            elif not weapon_used and fc_weapons:
                utils.log("--- Buff Pipeline --- | Vicissitude weapons")
                action.lethality = max(action.lethality, 2)
                action.attack_sound = Weapon.WEAPON_SOUNDS[Weapon.MW_SWORD]
                BuffPipeline.apply_damage_bonus(action, 2, cfg.POWER_PROTEAN_MOLD_SELF)
                action.unarmed_power_used = utils.unique_append(action.unarmed_power_used, cfg.POWER_PROTEAN_MOLD_SELF, sep=", ")

            # More?
            return action, new_pool

        @staticmethod
        def ranged_attack(user, action, base_pool):
            new_pool = str(base_pool)
            if action.alt_weapon_penalty is not None:
                new_pool += "+-{}".format(cfg.WEAPON_DRAW_PENALTY)

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

            # Fleetness (dodging)
            if user.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY) and Entity.SE_FLEETY in fx:
                if utils.caseless_in(cfg.AT_DEX, base_pool) and utils.caseless_in(cfg.SK_ATHL, base_pool):
                    new_pool += "+{}".format(cfg.DISC_CELERITY)
                elif (user.shapeshift_form and caseless_in(cfg.SK_ATHL, base_pool)):
                    new_pool += "+{}".format(cfg.DISC_CELERITY)

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
        def has_any_buff(who, buff, *buffs):
            for bf in ((buff,) + buffs):
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
        def power_is_active(who, power):  # TODO: come back to this regularly
            if power == cfg.POWER_CELERITY_SPEED:
                return StatusFX.has_buff(who, Entity.SE_FLEETY)
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
            utils.log("Power \"{}\" not accounted for in StatusFX.power_is_active().".format(power))
            return False

        @staticmethod
        def find_power_in_disc_tree(power_name):
            for dname in cfg.REF_DISC_POWER_TREES:
                disc = cfg.REF_DISC_POWER_TREES[dname]
                for level, d_tier in enumerate(disc):
                    if power_name in d_tier:
                        return dname, level
            return None, None

        @staticmethod
        def get_num_rouse_checks(power_name):
            if power_name in cfg.REF_DISC_POWER_PASSIVES + cfg.REF_DISC_POWER_TOGGLABLES:
                return 0, None
            p_disc, p_level = StatusFX.find_power_in_disc_tree(power_name)
            if p_level <= 1:  # TODO: revisit when Blood Sorcery added.
                return 0, None
            reroll_cap = utils.get_bp_disc_reroll_level(p_level)
            return 1, p_level <= reroll_cap  # TODO: implement two-check powers later

        def use_disc_power(self, power_name, who=None):
            if who is None:
                who = self.pc
            dp_name = str(power_name).lower().replace(' ', '_').replace("'", "")
            if dp_name and hasattr(self, dp_name):
                num_rouse_checks, reroll = StatusFX.get_num_rouse_checks(power_name)
                # rouse_check(num_checks=num_rouse_checks, reroll=reroll)
                if num_rouse_checks > 0 and who.can_rouse():
                    renpy.call_in_new_context("roll_control.rouse_check", num_checks=num_rouse_checks, reroll=reroll)
                elif num_rouse_checks > 0:
                    return
                getattr(self, dp_name)(who=who)
                if not (dp_name in cfg.REF_DISC_POWER_FREEBIES or dp_name in cfg.REF_DISC_POWER_PASSIVES):
                    used_disc_this_turn = True
            else:
                raise ValueError("\"{}\" is not implemented here, at least not yet.".format(dp_name))

        # Celerity

        def fleetness(self, who=None):
            if who.has_disc_power(cfg.POWER_CELERITY_SPEED, cfg.DISC_CELERITY):
                self.apply_buff(who, Entity.SE_FLEETY, 12)
                renpy.play(audio.fleeing_footsteps1, "sound")

        # Fortitude

        def toughness(self, who=None):
            if who.has_disc_power(cfg.POWER_FORTITUDE_TOUGH, cfg.DISC_FORTITUDE):
                self.apply_buff(who, Entity.SE_TOUGHNESS, 9)
                if hasattr(who, "armor_active"):
                    who.armor_active = True
                renpy.play(audio.toughness_armor, "sound")

        def defy_bane(self, who=None):
            if who.has_disc_power(cfg.POWER_FORTITUDE_BANE, cfg.DISC_FORTITUDE):
                self.apply_buff(who, Entity.SE_ANTIBANE, 9)
                renpy.play(audio.toughness_armor, "sound")

        # Potence

        def lethal_body(self, who=None):
            if hasattr(who, "lethal_body_active"):
                who.lethal_body_active = not who.lethal_body_active
                renpy.play(audio.knuckle_crack_1, "audio")

        def prowess(self, who=None):
            if who.has_disc_power(cfg.POWER_POTENCE_PROWESS, cfg.DISC_POTENCE):
                self.apply_buff(who, Entity.SE_HULKING, 9)
                renpy.play(audio.pulled_taut_1, "audio")


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
        can_use_disc = not used_disc_this_turn
        if in_combat and ability in cfg.REF_DISC_POWERS_SNEAKY:
            usable = False if pc.current_pos > -2 else can_use_disc  # Only usable in the back rank.
            return usable, StatusFX.power_is_active(pc, ability)
        if ability in cfg.REF_DISC_POWER_BUFFS:
            return can_use_disc, StatusFX.power_is_active(pc, ability)
        if in_combat and ability in game.CAction.NPC_COMBAT_DISC_POWERS:
            return can_use_disc, False
        return None, None  # TODO: come back to this regularly


#
