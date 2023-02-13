init 1 python in game:

    from math import ceil as math_ceil

    cfg, utils = renpy.store.cfg, renpy.store.utils

    class V5Tracker:
        def __init__(self, char, boxes: int, tracker_type: str, armor: int = 0, bonus: int = 0):
            self.char = char
            self.tracker_type = tracker_type
            self._boxes = boxes
            self._armor = armor
            self._deathsave = 0
            self.armor_active = False
            self.deathsave_active = False
            self._bonus = bonus
            self.spf_damage = 0
            self.agg_damage = 0
            self.last_damage_source = None

        def __repr__(self):
            repr_str = ''.join(["|x" for _ in range(self.agg_damage)])
            repr_str += ''.join(["|/" for _ in range(self.spf_damage)])
            repr_str += ''.join(["|_" for _ in range(self.undamaged)])
            return repr_str + "|"

        @property
        def boxes(self):
            return self._boxes

        @boxes.setter
        def boxes(self, new_num_boxes: int):
            self._boxes = new_num_boxes

        @property
        def armor(self):
            return self._armor

        @armor.setter
        def armor(self, new_armor_val):
            self._armor = new_armor_val

        @property
        def deathsave(self):
            return self._deathsave

        @deathsave.setter
        def deathsave(self, new_ab_val):
            self._deathsave = new_ab_val

        @property
        def bonus(self):
            return self._bonus

        @bonus.setter
        def bonus(self, new_bonus: int):
            self._bonus = new_bonus

        @property
        def total(self):
            return self.boxes + self.bonus

        @property
        def undamaged(self):
            return self.total - (self.spf_damage + self.agg_damage)

        def damage(self, dtype, amount, source=None):
            if not utils.is_number(amount) or amount < 0:
                raise ValueError("Damage should always be an integer of zero or more.")

            total_boxes = self.boxes + self.bonus

            temp_armor = self.armor if self.armor_active else 0
            temp_deathsave = self.deathsave if self.deathsave_active else 0

            dented, injured, true_amount = False, False, amount
            actual_dmg, unhalved_dmg, prevented_dmg, mitigated_dmg = 0, 0, 0, 0

            # Superficial damage is mitigated before halving.
            if temp_armor > 0 and dtype in [cfg.DMG_SPF, cfg.DMG_FULL_SPF]:
                dented = True
                chip_damage = max(true_amount - temp_armor, 1)  # Chip damage
                prevented_dmg = true_amount - chip_damage
                true_amount = chip_damage #max(true_amount - temp_armor, 1)
                temp_armor = 0

            unhalved_dmg = true_amount
            if dtype == cfg.DMG_SPF:
                true_amount = math_ceil(float(unhalved_dmg) / 2)

            for point in range(int(true_amount)):
                clear_boxes = total_boxes - (self.spf_damage + self.agg_damage)
                if clear_boxes > 0:  # clear spaces get filled first
                    self.char.impair(False, self.tracker_type)
                    if dtype in [cfg.DMG_SPF, cfg.DMG_FULL_SPF]:
                        self.spf_damage += 1
                    elif temp_deathsave > 0:
                        self.spf_damage += 1
                        temp_deathsave -= 1
                        mitigated_dmg += 1
                        if temp_deathsave <= 0:
                            self.deathsave_active = False
                    else:
                        self.agg_damage += 1
                    utils.log("====> damage " + str(point) + ": filling a clear space")
                elif self.spf_damage > 0:  # if there are no clear boxes, tracker is filled with mix of damage types
                    self.char.impair(True, self.tracker_type)
                    self.spf_damage -= 1
                    self.agg_damage += 1  # if there's any superficial damage left, turn it into an aggravated
                    utils.log("====> damage " + str(point) + ": removing a superficial and replacing with aggravated")
                if self.agg_damage >= total_boxes:
                    # A tracker completely filled with aggravated damage = game over:
                    # torpor, death, or a total loss of faculties, face and status
                    self.char.handle_demise(self.tracker_type, self.last_damage_source)
                    utils.log("====> damage " + str(point) + ": oh shit you dead")

                actual_dmg += 1
                injured = True
            if dented and not injured:
                # renpy.sound.queue(audio.pc_hit_fort_melee, u'sound')  # TODO: add sounds here
                pass
            elif injured:
                # renpy.sound.queue(audio.stab2, u'sound')
                self.last_damage_source = source
                if self.last_damage_source is None:
                    self.last_damage_source = cfg.COD_PHYSICAL
            return (actual_dmg, unhalved_dmg, prevented_dmg, mitigated_dmg,)

        def mend(self, dtype, amount):
            if dtype == cfg.DMG_SPF or dtype == cfg.DMG_FULL_SPF:
                damage = self.spf_damage
                self.spf_damage = max(damage - amount, 0)
            else:
                damage = self.agg_damage
                self.agg_damage = max(damage - amount, 0)


    class Entity:

        STATUS_LASTING = -1

        SE_BERSERK = "rage_frenzy"
        SE_SHOCKED = "will_impaired"
        SE_CRIPPLED = "hp_impaired"
        SE_AUSPEX_ESP = "auspex_detector"
        SE_FLEETY = "fleetness_boost"
        SE_TOUGHNESS = "toughness_armor"
        SE_ANTIBANE = "bane_armor"
        SE_OBFU_ROOTED = "stealth_mode"
        SE_OBFU_MOBILE = "stealth_mobile"
        SE_HULKING = "prowess_strength"
        SE_FLESHCRAFT_WEAPON = "vicissitude_weapons"
        SE_FLESHCRAFTED_STACK = "vicissitude_effects"

        LASTING_STATUS_FX = [SE_SHOCKED, SE_CRIPPLED, SE_FLESHCRAFT_WEAPON, SE_FLESHCRAFTED_STACK]

        def __init__(self, ctype=cfg.CT_HUMAN, pronoun_set=None, **kwargs):
            self.is_pc = False
            self.creature_type = ctype
            self._pronoun_set = None
            self.pronoun_set = pronoun_set
            if pronoun_set is None:
                self.pronoun_set = self.random_pronouns()
            self.hp = self.will = None
            self.dead, self.cause_of_death = False, None
            self.appears_dead = self.dead
            self.shocked = self.crippled = False
            self.last_rolled_init = None
            self.engaged = []  # Melee engagement is mutual. If they're in your list you should be in theirs.
            self.current_pos = None  # Actually that contradicts code I wrote elsewhere; fuck
            self.ranged_attacks_use_gun = False
            self.inventory, self.equipped = [], []
            self.mortal = False
            self._status_effects = {}
            self.always_detector, self.detector_tech = False, False
            self.stealth_ignore_tech = False
            self.shapeshift_form = None
            if self.creature_type in cfg.REF_MORTALS:
                self.mortal = True
            self._hunger = 1 if self.creature_type == cfg.CT_VAMPIRE else None
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

        @property
        def pronoun_set(self):
            return self._pronoun_set

        @pronoun_set.setter
        def pronoun_set(self, new_pn_set):
            self._pronoun_set = new_pn_set
            self.scream = self.set_scream()

        @property
        def status_effects(self):
            return self._status_effects

        def set_scream(self, force_replace=False):
            if not self.pronoun_set:
                print("no pronouns!")
                return None # TODO: add bestial screams
            if not force_replace and self.scream:
                return self.scream
            screams = cfg.PAIN_SOUNDS[self.pronoun_set.PN_SHE_HE_THEY]
            scream = utils.get_random_list_elem(screams)[0]
            self.scream = scream
            return self.scream

        def afflict(self, effect, turns=1):
            if effect not in self.status_effects:
                self._status_effects[effect] = turns
            else:
                self._status_effects[effect] += turns

        def buff(self, effect, turns=1):  # Alias, maybe for different logging/effects?
            self.afflict(effect, turns)

        def purge_status(self, effect, purge=True, force_remove=False):
            if effect not in self.status_effects:
                utils.log("Could not purge effect \"{}\" from \"{}\" because it wasn't found.".format(effect, self.name))
                return
            if not force_remove and effect in Entity.LASTING_STATUS_FX:
                utils.log("\"{}\" is a persistent effect; set force_remove to True to remove.".format(effect))
                return
            self._status_effects[effect] = None
            if purge:
                del self._status_effects[effect]

        def purge_all_fx(self, purge=True, force_remove=False):
            if force_remove:
                self._status_effects = {}
                return
            fx_keys = list(self.status_effects.keys())
            for fx in fx_keys:
                self.purge_status(fx, purge=purge)

        def get_effect_ttl(self, effect):
            if effect in self.status_effects:
                return self.status_effects[effect]
            return None

        def random_pronouns(self):
            if utils.percent_chance(95):
                if utils.percent_chance(50):
                    return cfg.PN_WOMAN
                return cfg.PN_MAN
            return cfg.PN_NONBINARY_PERSON

        def can_rouse(self):
            if self.creature_type != cfg.CT_VAMPIRE:
                return True  # TODO: revisit
            return self.hunger < cfg.HUNGER_MAX

        def attack(self, action_order, ao_index, enemy_targets, all_targets):
            pass

        def defend(self, attacker, atk_action):
            pass

        def impair(self, impaired, tracker_type):
            if tracker_type == cfg.TRACK_HP:
                self.crippled = impaired
            elif tracker_type == cfg.TRACK_WILL:
                self.shocked = impaired

        def handle_demise(self, tracker_type, damage_source):
            self.dead = True
            self.cause_of_death = damage_source


    class NPCFighter(Entity):
        FT_BRAWLER = "brawler"  # If someone's in melee range, attacks. If not, tries to close.
        FT_SHOOTER = "shooter"  # Shoots until someone gets close and engages, then fights in melee.
        FT_WILDCARD = "wildcard"  # Randomly chooses target and attack type from what's available.
        FT_ESCORT = "escort"  # Tries to avoid enemies. May use special abilities, but does not normally attack.
        FT_FTPC = "pc_hunter"  # Always tries to attack PC, and acts like wildcard if that's not possible.

        def __init__(self, physical=4, social=4, mental=4, name="", ftype=None, ctype=cfg.CT_HUMAN, bcs=None, **kwargs):
            super().__init__(ctype=ctype, **kwargs)
            self.ftype = NPCFighter.FT_BRAWLER if ftype is None else ftype
            self.name = name
            if not self.name:
                self.name = utils.generate_random_id_str(label="npc#{}#".format(self.ftype))
            self.physical, self.social, self.mental = physical, social, mental
            self.hp = V5Tracker(self, self.physical + 3, cfg.TRACK_HP)
            self.will = V5Tracker(self, self.mental + self.social, cfg.TRACK_WILL)
            self._special_skills = {}  # Skills or discipline ratings
            self.base_combat_stat = bcs
            if bcs is None:
                self.base_combat_stat = cfg.NPCAT_PHYS  # TODO: change this if new ftypes are added
            self._passive_powers = []
            self.brain = FightBrain  # Should reference a static class
            disc_powers = [dp for dp in cfg.__dict__ if str(dp).startswith("POWER_")]
            self.npc_weapon = None
            self.ranged_attacks_use_gun = True  # Always true unless specifically turned off.
            for kwarg in kwargs:
                if kwarg in cfg.REF_SKILL_ORDER or kwarg in disc_powers:
                    self._special_skills[kwarg] = kwargs[kwarg]
                elif not hasattr(self, kwarg):
                    setattr(self, kwarg, kwargs[kwarg])

        @property
        def special_skills(self):
            return self._special_skills

        @property
        def passive_powers(self):
            return self._passive_powers

        def add_special_skill(self, skill, value):
            if skill not in cfg.REF_SKILL_ORDER:
                raise ValueError("\"{}\" is not a valid NPC skill.".format(skill))
            self._special_skills[skill] = value

        def skill(self, skill):
            if skill in self.special_skills:
                return self.special_skills[skill]
            if skill not in cfg.REF_SKILL_ORDER:
                raise ValueError("NPC \"{}\" does not have the \"{}\" skill; check if it's valid.".format(self.name, skill))
            if skill in cfg.REF_PHYSICAL_SKILLS:
                return self.physical
            if skill in cfg.REF_SOCIAL_SKILLS:
                return self.social
            if skill in cfg.REF_MENTAL_SKILLS:
                return self.mental
            raise ValueError("Should never reach here! (Tried to check \"{}\" for skill \"{}\")".format(self.name, skill))

        def has_disc_power(self, power, disc=None):
            return power in self.special_skills or power in self.passive_powers

        def attack(self, action_order, ao_index, enemy_targets, all_targets):
            return self.brain.npc_attack(self, action_order, ao_index, enemy_targets, all_targets)

        def defend(self, attacker, atk_action):
            return self.brain.npc_defend(self, attacker, atk_action)

        def handle_demise(self, tracker_type, damage_source):
            super().handle_demise(tracker_type=tracker_type, damage_source=damage_source)
            print("NPC \"{}\" has died.".format(self.name))


#
