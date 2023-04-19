init 1 python in game:

    from math import ceil as math_ceil

    cfg, utils, state, flavor = renpy.store.cfg, renpy.store.utils, renpy.store.state, renpy.store.flavor

    class V5Tracker:
        def __init__(self, char, boxes: int, tracker_type: str, armor: int = 0, bonus: int = 0):
            self.char = char
            self.tracker_type = tracker_type
            self._boxes = boxes
            self._bonus = bonus
            self._armor = armor
            self._deathsave = 0
            self._armor_active = False
            self.deathsave_active = False
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

        @property
        def unfilled(self):
            return self.total - self.agg_damage

        @property
        def spendable(self):  # 1 point "spent" == 1 point of unhalved superficial damage.
            return (self.undamaged * 2) + self.spf_damage

        @property
        def armor(self):
            return self._armor

        @armor.setter
        def armor(self, new_armor_val):
            self._armor = new_armor_val

        @property
        def armor_active(self):
            if state.StatusFX.has_any_buff(self.char, Entity.SE_TOUGHNESS):
                return True
            return self._armor_active

        @armor_active.setter
        def armor_active(self, new_aa_val):
            self._armor_active = new_aa_val

        @property
        def deathsave(self):
            return self._deathsave

        @deathsave.setter
        def deathsave(self, new_ab_val):
            self._deathsave = new_ab_val

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
                if clear_boxes > 0:  # Clear spaces get filled first.
                    self.char.impair(False, self.tracker_type)
                    if dtype in [cfg.DMG_SPF, cfg.DMG_FULL_SPF]:
                        self.spf_damage += 1
                        pt_symbol = "|/|"
                    elif temp_deathsave > 0:
                        self.spf_damage += 1
                        temp_deathsave -= 1
                        mitigated_dmg += 1
                        if temp_deathsave <= 0:
                            self.deathsave_active = False
                        pt_symbol = "|/|"
                    else:
                        self.agg_damage += 1
                        pt_symbol = "|X|"
                    utils.log("  |_| > {} :: Damage point #{}, filling a clear space.".format(pt_symbol, point+1))
                elif self.spf_damage > 0:  # If there are no clear boxes, tracker is filled with mix of damage types.
                    self.char.impair(True, self.tracker_type)
                    self.spf_damage -= 1
                    self.agg_damage += 1  # If there's any Superficial damage left, turn it into a Aggravated.
                    utils.log("  |/| > |X| :: Damage point #{}, replacing a Superficial with Aggravated.".format(point+1))
                if self.agg_damage >= total_boxes:
                    # A tracker completely filled with Aggravated damage = game over, i.e.
                    # torpor, death, or a total loss of faculties, face and status.
                    self.char.handle_demise(self.tracker_type, self.last_damage_source)
                    utils.log("  RIP :: Damage point #{}, the final point.".format(point+1))

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


    class NarrativeObject:

        def __init__(self, name="", **kwargs):
            self.name = name
            self.is_pc = False
            self.creature_type = None
            self.sapient = False
            self._pronoun_set = None
            self._hostility = None
            if isinstance(self, Person):
                self.is_animate = True
            else:
                self.is_animate = False
                self.pronoun_set = cfg.PN_INANIMATE

        @property
        def pronoun_set(self):
            return self._pronoun_set

        @pronoun_set.setter
        def pronoun_set(self, new_pn_set):
            self._pronoun_set = new_pn_set
            self.scream = self.set_scream()

        @property
        def has_Beast(self):
            return self.creature_type in cfg.REF_HAS_SUPERNATURAL_BEAST

        @property
        def hostility(self):
            if not self._hostility:
                return "calm"
            any_hostility = False
            if self._hostility is True or self._hostility > 0:
                any_hostility = True
            if hasattr(self, "in_combat") and self.in_combat:
                return "attacking" if any_hostility else "wary"
            if self._hostility > 2:
                return "intent on violence"
            return "aggressive" if self._hostility > 1 else "agitated"

        @hostility.setter
        def hostility(self, new_hostil):
            self._hostility = new_hostil

        @property
        def label(self):
            ent_label = self.name
            if state.pc and (self.is_animate or state.pc.sense_creature_types):
                beast_check = "BEAST, " if self.has_Beast else ""
                if state.pc.using_sense_the_beast and state.pc.sense_creature_types:
                    ent_label = "{} ({}{}, {})".format(ent_label, beast_check, self.creature_type, self.hostility)
                elif state.pc.using_sense_the_beast:
                    ent_label = "{} ({}{})".format(ent_label, beast_check, self.hostility)
                elif state.pc.sense_creature_types:
                    ent_label = "{} ({})".format(ent_label, self.creature_type)
            return ent_label


    class Person(NarrativeObject):

        RAND_AGES = (cfg.REF_AA_YOUNG_ADULT, cfg.REF_AA_ADULT, cfg.REF_AA_MIDDLE_AGED, cfg.REF_AA_ELDERLY)
        AGE_CUM_WEIGHTS = utils.get_cum_weights(100, 90, 80, 30)

        def __init__(self, name="", ctype=cfg.CT_HUMAN, pronoun_set=None, apparent_age=None, set_sapience=None, **kwargs):
            super().__init__(name=name, **kwargs)
            self.creature_type = ctype
            self.sapient = True
            if self.creature_type not in cfg.REF_SAPIENT_SPECIES and not sapience:
                self.sapient = False  # All persons are sentient, but not all animals are sapient
            self.scream = None  # For now.
            self.pronoun_set = pronoun_set
            if pronoun_set is None:
                self.pronoun_set = Person.random_pronouns()
            self.apparent_age = apparent_age
            if apparent_age is None:
                self.apparent_age = utils.get_wrs(Person.RAND_AGES, cum_weights=Person.AGE_CUM_WEIGHTS[:len(Person.RAND_AGES)])
            self.using_sense_the_beast = False
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

        @property
        def desc_age_adj(self):
            if ' ' in self.apparent_age:
                return self.apparent_age.split(' ')[1]
            return self.apparent_age

        @property
        def desc_indef_artic(self):
            return "{} {}".format(self.apparent_age, self.pronoun_set.PN_STRANGER)

        @property
        def desc_no_artic(self):
            return "{} {}".format(self.desc_age_adj, self.pronoun_set.PN_STRANGER)

        def set_scream(self, force_replace=False):
            if not self.pronoun_set:
                return None # TODO: add bestial screams
            if not force_replace and self.scream:
                return self.scream
            screams = flavor.PAIN_SOUNDS[self.pronoun_set.PN_SHE_HE_THEY]
            scream = utils.get_random_list_elem(screams) #[0]
            self.scream = scream
            return self.scream

        @staticmethod
        def random_pronouns():
            if utils.percent_chance(95):
                if utils.percent_chance(50):
                    return cfg.PN_WOMAN
                return cfg.PN_MAN
            return cfg.PN_PERSON


    class MortalPrey(Person):
        def __init__(self, ctype=cfg.CT_HUMAN, pronoun_set=None, apparent_age=None, **kwargs):
            super().__init__(ctype=ctype, pronoun_set=pronoun_set, apparent_age=apparent_age, **kwargs)
            self.was_doing = flavor.what_they_were_doing(prey=self)

        @property
        def resonance(self):
            return None


    class Entity(Person):
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
            super().__init__(ctype=ctype, pronoun_set=pronoun_set, **kwargs)
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
            # for kwarg in kwargs:
            #     setattr(self, kwarg, kwargs[kwarg])

        @property
        def status_effects(self):
            return self._status_effects

        @property
        def held(self):
            if hasattr(self, "inventory") and self.inventory and hasattr(self.inventory, "held"):
                return self.inventory.held
            elif hasattr(self, "npc_weapon") and self.npc_weapon:
                return self.npc_weapon
            return None

        @property
        def sidearm(self):
            if hasattr(self, "inventory") and self.inventory and hasattr(self.inventory, "sidearm"):
                return self.inventory.sidearm
            elif hasattr(self, "npc_weapon_alt") and self.npc_weapon_alt:
                return self.npc_weapon_alt
            return None

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
        FT_BRAWLER = "Brawler"  # If someone's in melee range, attacks. If not, tries to close.
        FT_SHOOTER = "Shooter"  # Shoots until someone gets close and engages, then fights in melee.
        FT_WILDCARD = "Wildcard"  # Randomly chooses target and attack type from what's available.
        FT_ESCORT = "Escort"  # Tries to avoid enemies. May use special abilities, but does not normally attack.
        FT_FTPC = "Assassin"  # Always tries to attack PC, and acts like wildcard if that's not possible.

        def __init__(self, physical=4, social=4, mental=4, name="", ftype=None, ctype=cfg.CT_HUMAN, bcs=None, **kwargs):
            super().__init__(ctype=ctype, **kwargs)
            self.ftype = NPCFighter.FT_BRAWLER if ftype is None else ftype
            self.char_id = utils.generate_random_id_str(label="npc#{}#".format(self.ftype))
            if not self.name:
                self.name = "{} {}".format(self.creature_type, self.ftype)
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
                if kwarg in cfg.REF_DISC_POWER_PASSIVES:
                    self._passive_powers.append(kwarg)
                elif kwarg in cfg.REF_SKILL_ORDER or kwarg in cfg.REF_DISC_IN_GAME or kwarg in disc_powers:
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
