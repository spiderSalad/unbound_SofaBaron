init 1 python in game:
    from math import ceil as math_ceil

    cfg, utils = renpy.store.cfg, renpy.store.utils
    # NOTE: this persists between game load/cycles, as it's run when Ren'py starts - NOT when the game starts.

    class Tracker:
        def __init__(self, pc, boxes: int, trackertype: str, armor: int = 0, bonus: int = 0):
            self.playerchar = pc
            self.trackertype = trackertype
            self._boxes = boxes
            self._armor = armor
            self.armor_active = False
            self._bonus = bonus
            self.spf_damage = 0
            self.agg_damage = 0
            self.last_damage_source = None

        @property
        def boxes(self):
            return self._boxes

        @boxes.setter
        def boxes(self, new_num_boxes: int):
            self._boxes = new_num_boxes

        @property
        def armor(self):  # Blocks superficial damage prior to halving.
            if self.trackertype == cfg.TRACK_HP:
                return self.playerchar.get_fort_toughness_armor()
            return self._armor

        @armor.setter
        def armor(self, new_armor_val):
            self._armor = new_armor_val

        @property
        def bonus(self):
            if self.trackertype == cfg.TRACK_HP:
                return self.playerchar.get_fort_resilience_bonus()
            return self._bonus

        @bonus.setter
        def bonus(self, new_bonus: int):
            self._bonus = new_bonus

        def damage(self, dtype, amount, source=None):
            total_boxes = self.boxes + self.bonus

            temp_armor = self.armor if self.armor_active else 0

            dented = False
            injured = False
            true_amount = amount
            if dtype == cfg.DMG_SPF:
                true_amount = math_ceil(float(amount) / 2)

            for point in range(int(true_amount)):
                if temp_armor > 0:
                    dented = True
                    temp_armor -= 1
                    continue

                clear_boxes = total_boxes - (self.spf_damage + self.agg_damage)
                if clear_boxes > 0:  # clear spaces get filled first
                    self.playerchar.impair(True, self.trackertype)
                    if dtype == cfg.DMG_SPF or dtype == cfg.DMG_FULL_SPF:
                        self.spf_damage += 1
                    else:
                        self.agg_damage += 1
                    utils.log("====> damage " + str(point) + ": filling a clear space")
                elif self.spf_damage > 0:  # if there are no clear boxes, tracker is filled with a mix of aggravated and superficial damage
                    self.playerchar.impair(True, self.trackertype)
                    self.spf_damage -= 1
                    self.agg_damage += 1  # if there's any superficial damage left, turn it into an aggravated
                    utils.log("====> damage " + str(point) + ": removing a superficial and replacing with aggravated")

                if self.agg_damage >= total_boxes:
                    # A tracker completely filled with aggravated damage = game over: torpor, death, or a total loss of faculties, face and status
                    self.playerchar.handle_demise(self.trackertype, self.last_damage_source)
                    utils.log("====> damage " + str(point) + ": oh shit you dead")

                injured = True
            if dented and not injured:
                # renpy.sound.queue(audio.pc_hit_fort_melee, u'sound')  # TODO: add sounds here
                pass
            elif injured:
                # renpy.sound.queue(audio.stab2, u'sound')
                self.last_damage_source = source
                if self.last_damage_source is None:
                    self.last_damage_source = cfg.COD_PHYSICAL
                pass

        def mend(self, dtype, amount):
            if dtype == cfg.DMG_SPF or dtype == cfg.DMG_FULL_SPF:
                damage = self.spf_damage
                self.spf_damage = max(damage - amount, 0)
            else:
                damage = self.agg_damage
                self.agg_damage = max(damage - amount, 0)


    class SuperpowerArsenal:
        def __init__(self, dnames):
            self.dnames = dnames
            # No setters for these protected properties
            self._access = {}
            self._levels = {}
            self._pc_powers = {}
            self.reset()

        def reset(self):
            for dname in self.dnames:
                self._access[dname] = cfg.VAL_DISC_LOCKED
                self._levels[dname] = cfg.MIN_SCORE
                self._pc_powers[dname] = {}
                for i in range(1, 6):
                    score_word = cfg.SCORE_WORDS[i]
                    self._pc_powers[dname][score_word] = None

        @property
        def access(self):
            return self._access

        @property
        def levels(self):
            return self._levels

        @property
        def pc_powers(self):
            return self._pc_powers

        def set_discipline_access(self, dname, access_level):
            self._access[dname] = access_level

        def unlock(self, dname, level):
            # Has no effect if already unlocked at a higher level
            if self.access[dname] < level:
                self.set_discipline_access(dname, level)

        def get_unlocked(self, access_level=None):
            if access_level is None:
                return [dname for dname in self.access if self.access[dname] > cfg.VAL_DISC_LOCKED]
            else:
                return [dname for dname in self.access if self.access[dname] >= access_level]

        def set_discipline_level(self, dname, dots):
            new_dot_level = utils.nudge_int_value(self.levels[dname], dots, floor=cfg.MIN_SCORE, ceiling=cfg.MAX_SCORE)
            self.levels[dname] = new_dot_level

        # def unlock_power(dname, power_name):
        #     if power_name not in


    class PlayerChar:
        def __init__(self, anames, snames, dnames):
            self.nickname = "That lick from around the way"
            self.pronouns = {}  # TODO: implement this
            self.clan = None
            self.predator_type = None
            self.blood_potency = 1
            self._hunger = 1
            self._humanity = 7
            self.hp, self.will = Tracker(self, 3, cfg.TRACK_HP), Tracker(self, 3, cfg.TRACK_WILL)
            self.crippled, self.shocked, self.frenzied = False, False, False
            self.cause_of_death = None
            self._status = "(All clear)"
            self.clan_blurbs = {}
            self.anames, self.snames, self.dnames = anames, snames, dnames
            self.attrs = {}
            self.skills = {}
            self.mortal_backstory = None
            self._backgrounds = []
            self.disciplines = SuperpowerArsenal(self.dnames)
            self.inventory = None
            self.reset_charsheet_stats()

        @property
        def status(self):
            status_list = []
            if self.frenzied and self.hunger >= cfg.HUNGER_MAX:
                status_list.append("Hunger frenzy")
            elif self.frenzied:
                status_list.append("Frenzy")
            elif self.hunger >= cfg.HUNGER_MAX:
                status_list.append("Starving")
            if self.crippled:
                status_list.append("Maimed")
            if self.shocked:
                status_list.append("Shellshocked")
            if len(status_list) == 0:
                self._status = "\"Fine\""
            else:
                self._status = ", ".join(status_list)
            return self._status

        @property
        def hunger(self):
            return self._hunger

        @hunger.setter
        def hunger(self, new_hunger):
            self._hunger = max(0, min(new_hunger, cfg.HUNGER_MAX + 1))
            if self.hunger > cfg.HUNGER_MAX:
                print("Hunger tested at 5; frenzy check?")  # TODO: frenzy check
                self.frenzied = True
                self.hunger = cfg.HUNGER_MAX
            else:
                utils.log("Hunger now set at {}".format(self.hunger))

        @property
        def humanity(self):
            return self._humanity

        @humanity.setter
        def humanity(self, new_humanity):
            self._humanity = new_humanity

        @property
        def backgrounds(self):
            return self._backgrounds

        def reset_charsheet_stats(self):
            for aname in self.anames:
                self.attrs[aname] = cfg.MIN_SCORE_ATTR
            for sname in self.snames:
                self.skills[sname] = cfg.MIN_SCORE
            self.disciplines.reset()

        def validate_charsheet_stats(self):
            for aname in self.anames:
                self.attrs[aname] = max(cfg.MIN_SCORE_ATTR, min(self.attrs[aname], cfg.MAX_SCORE))
            for sname in self.snames:
                self.skills[sname] = max(cfg.MIN_SCORE, min(self.skills[sname], cfg.MAX_SCORE))

        def recalculate_stats(self):
            self.reset_charsheet_stats()
            self.apply_xp()
            for bg in self.backgrounds:
                utils.log("Applying background: ", bg)
                for bg_stat_name in bg:
                    if bg_stat_name in self.attrs:
                        self.attrs[bg_stat_name] += bg[bg_stat_name]
                    elif bg_stat_name in self.skills:
                        self.skills[bg_stat_name] += bg[bg_stat_name]
                if cfg.REF_ATTRS_ALL in bg:
                    for attr in self.attrs:
                        self.attrs[attr] += bg[cfg.REF_ATTRS_ALL]
                if cfg.REF_SKILLS_ALL in bg:
                    for skill in self.skills:
                        self.skills[skill] += bg[cfg.REF_SKILLS_ALL]
            self.validate_charsheet_stats()
            self.recalibrate_trackers()

        def recalibrate_trackers(self):
            self.hp.boxes = int(self.attrs[cfg.AT_STA]) + 3
            self.will.boxes = int(self.attrs[cfg.AT_COM]) + int(self.attrs[cfg.AT_RES])

        def apply_background(self, background: (dict, str), bg_key=None, force_add=False):
            bg, key = background, bg_key
            if isinstance(background, str):
                bg = cfg.CHAR_BACKGROUNDS[background]
                key = background
            if cfg.REF_BG_NAME not in bg:
                bg[cfg.REF_BG_NAME] = key
            # Reject any background if it shares a subtype with an existing background unless force_add == True
            # e.g. picking Nosferatu and Siren should leave PC with Repulsive and not Beautiful
            if cfg.REF_SUBTYPE not in bg or force_add:
                self._backgrounds.append(bg)
            else:
                bg_subtype = bg[cfg.REF_SUBTYPE]
                existing_subtypes = [bg[cfg.REF_SUBTYPE] for bg in self.backgrounds if cfg.REF_SUBTYPE in bg]
                if bg_subtype not in existing_subtypes:
                    self._backgrounds.append(bg)
            if bg[cfg.REF_TYPE] == cfg.REF_BG_PAST:
                self.mortal_backstory = bg[cfg.REF_BG_NAME]
            self.recalculate_stats()

        def apply_xp(self):
            return self  # TODO: implement this

        def impair(self, impaired, tracker_type):
            if tracker_type == cfg.TRACK_HP:
                self.crippled = impaired
            elif tracker_type == cfg.TRACK_WILL:
                self.shocked = impaired

        def get_fort_resilience_bonus(self):
            if cfg.POWER_FORTITUDE_HP not in self.disciplines.pc_powers:
                return 0
            return self.disciplines.levels[cfg.DISC_FORTITUDE]

        def get_fort_toughness_armor(self):
            if cfg.POWER_FORTITUDE_TOUGH not in self.disciplines.pc_powers:
                return 0
            return self.disciplines.levels[cfg.DISC_FORTITUDE]

        def choose_clan(self, clan):
            self.clan = clan
            self.clan_blurbs = cfg.CLAN_BLURBS[self.clan]
            if clan == cfg.CLAN_BRUJAH:
                self.unlock_discipline(cfg.DISC_CELERITY, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
            elif clan == cfg.CLAN_NOSFERATU:
                self.apply_background(cfg.BG_REPULSIVE)
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.VAL_DISC_INCLAN)
            elif clan == cfg.CLAN_RAVNOS:
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
            elif clan == cfg.CLAN_VENTRUE:
                self.unlock_discipline(cfg.DISC_DOMINATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_FORTITUDE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
            elif clan == cfg.CLAN_NONE_CAITIFF:
                for dname in self.dnames:
                    self.unlock_discipline(dname, cfg.VAL_DISC_CAITIFF)
            else:
                raise ValueError("Invalid clan \"{}\".".format(clan))
            self.apply_background_discipline_priority()

        def apply_background_discipline_priority(self):
            if not self.mortal_backstory:
                raise ValueError("Missing blurb of character's mortal past.")
            priority = cfg.CHAR_BACKGROUNDS[self.mortal_backstory][cfg.REF_BG_DISC_PRIORITY]
            short_list = [disc for disc in priority if disc in self.disciplines.get_unlocked()]
            disc1, disc2 = short_list[0], short_list[1]
            self.disciplines.set_discipline_level(disc1, "+=2")
            self.disciplines.set_discipline_level(disc2, "+=1")

        def choose_predator_type(self, pt):
            if pt == cfg.PT_ALLEYCAT:
                self.humanity -= 1
                self.skills[cfg.SK_COMB] += 1
                self.skills[cfg.SK_INTI] += 1
                self.unlock_discipline(cfg.DISC_CELERITY, cfg.VAL_DISC_OUTCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.VAL_DISC_OUTCLAN)
            elif pt == cfg.PT_BAGGER:
                self.skills[cfg.SK_CLAN] += 1
                self.skills[cfg.SK_STWS] += 1
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.VAL_DISC_OUTCLAN)
                # TODO: Iron Gullet, Enemy (2)
            elif pt == cfg.PT_FARMER:
                self.humanity += 1
                self.skills[cfg.SK_TRAV] += 1
                self.skills[cfg.SK_DIPL] += 1
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.VAL_DISC_OUTCLAN)
                # TODO: Vegan
            elif pt == cfg.PT_SIREN:
                self.apply_background(cfg.BG_BEAUTIFUL)
                self.skills[cfg.SK_DIPL] += 1
                self.skills[cfg.SK_INTR] += 1
                self.unlock_discipline(cfg.DISC_FORTITUDE, cfg.VAL_DISC_OUTCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_OUTCLAN)
                # TODO: Enemy (1)
            else:
                raise ValueError("\"{}\" is not a valid predator type.".format(pt))
            self.apply_background(cfg.CHAR_PT_STATBLOCKS[pt], bg_key=pt)
            self.predator_type = pt
            self.recalculate_stats()

        def unlock_discipline(self, disc, level):
            self.disciplines.unlock(disc, level)

        def handle_demise(self, tracker_type, damage_source):
            self.cause_of_death = damage_source
            renpy.jump("end")


    class Supply:
        IT_MONEY = "Money"
        IT_WEAPON = "Weapon"
        IT_FIREARM = "Firearm"
        IT_EQUIPMENT = "Equipment"
        IT_QUEST = "Important"
        IT_MISC = "Miscellaneous"
        IT_JUNK = "Junk"
        IT_CLUE = "Clue"

        ITEM_COLOR_KEYS = {
            IT_MONEY: "#399642", IT_JUNK: "#707070", IT_CLUE: "#ffffff", IT_WEAPON: "#8f8f8f",
            IT_EQUIPMENT: "#cbcbdc", IT_QUEST: "#763cb7", IT_MISC: "#cbcbdc", IT_FIREARM: "#71797E"
        }

        def __init__(self, type, name, key=None, num=1, desc=None, **kwargs):
            self.item_type = type
            self.quantity = num
            self.color_key = Supply.ITEM_COLOR_KEYS[self.item_type]
            self.key = key
            if self.key is None:
                self.key = utils.generate_random_id_str(label="supply#{}".format(self.item_type))
            self.name = name
            if desc:
                self.description = desc
            else:
                self.description = "({})".format(self.item_type)
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])
            if self.item_type == Supply.IT_FIREARM:
                if not hasattr(self, "concealable"):
                    self.concealable = True


    class Inventory:
        ITEM_TYPES = [it for it in Supply.__dict__ if str(it).startswith("IT_")]

        def __init__(self, *items: Supply, **kwargs):
            self.items = []
            self.items += items

        def __len__(self):
            return len(self.items)

        def __contains__(self, key):
            if key in Inventory.ITEM_TYPES:
                for item in self.items:
                    if item.item_type == key:
                        return True
            else:
                for item in self.items:
                    if item.key == key:
                        return True
            return False

        def add(self, new_item: Supply):
            if new_item.item_type == Supply.IT_MONEY:
                cash = next((it for it in self.items if it.item_type == Supply.IT_MONEY), None)
                if cash is None:
                    self.items.append(new_item)
                else:
                    cash.quantity += new_item.quantity
            else:
                self.items.append(new_item)
