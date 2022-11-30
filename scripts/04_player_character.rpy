init 1 python in game:
    from math import ceil as math_ceil

    cfg, utils = renpy.store.cfg, renpy.store.utils

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

        def damage(self, dtype, amount):
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
                    self.playerchar.handle_demise(self.trackertype)
                    utils.log("====> damage " + str(point) + ": oh shit you dead")

                injured = True
            if dented and not injured:
                # renpy.sound.queue(audio.pc_hit_fort_melee, u'sound')  # TODO: add sounds here
                pass
            elif injured:
                # renpy.sound.queue(audio.stab2, u'sound')
                pass

        def mend(self, dtype, amount):
            if dtype == cfg.DMG_SPF or dtype == cfg.DMG_FULL_SPF:
                damage = self.spf_damage
                self.spf_damage = max(damage - amount, 0)
            else:
                damage = self.agg_damage
                self.agg_damage = max(damage - amount, 0)


    class PlayerChar:
        def __init__(self, anames, snames, dnames):
            self.nickname = "That lick from around the way"
            self.pronouns = {}  # TODO: implement this
            self.clan = None
            self.predator_type = self.predator_pools = None
            self.blood_potency = 1
            self._hunger = 1
            self._humanity = 7
            self.hp, self.will = Tracker(self, 3, cfg.TRACK_HP), Tracker(self, 3, cfg.TRACK_WILL)
            self.crippled, self.shocked = False, False
            self.clan_blurbs = {}
            self.anames, self.snames, self.dnames = anames, snames, dnames
            self.attrs = {}
            self.skills = {}
            self._backgrounds = []
            self.available_disciplines = {}
            self.discipline_levels = {}
            self.powers = []
            self.reset_charsheet_stats()

        @property
        def hunger(self):
            return self._hunger

        @hunger.setter
        def hunger(self, new_hunger):
            self._hunger = max(0, min(new_hunger, cfg.HUNGER_MAX + 1))
            if self.hunger > cfg.HUNGER_MAX:
                print("Hunger tested at 5; frenzy check?")  # TODO: frenzy check
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
            for dname in self.dnames:
                self.available_disciplines[dname] = cfg.VAL_DISC_LOCKED
                self.discipline_levels[dname] = cfg.MIN_SCORE

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

        def apply_background(self, background: (dict, str)):
            bg = background
            if isinstance(background, str):
                bg = cfg.CHAR_BACKGROUNDS[background]
            self._backgrounds.append(bg)
            self.recalculate_stats()

        def apply_xp(self):
            return self  # TODO: implement this

        def impair(self, impaired, tracker_type):
            if tracker_type == cfg.TRACK_HP:
                self.crippled = impaired
            elif tracker_type == cfg.TRACK_WILL:
                self.shocked = impaired

        def get_fort_resilience_bonus(self):
            if cfg.POWER_FORTITUDE_HP not in self.powers:
                return 0
            return self.discipline_levels[cfg.DISC_FORTITUDE]

        def get_fort_toughness_armor(self):
            if cfg.POWER_FORTITUDE_TOUGH not in self.powers:
                return 0
            return self.discipline_levels[cfg.DISC_FORTITUDE]

        def choose_clan(self, clan):
            self.clan = clan
            self.clan_blurbs = cfg.CLAN_BLURBS[self.clan]
            if clan == cfg.CLAN_BRUJAH:
                self.unlock_discipline(cfg.DISC_CELERITY, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
            elif clan == cfg.CLAN_NOSFERATU:
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.VAL_DISC_INCLAN)
                # self.clan_blurbs[cfg.REF_CLAN_CHOSEN] = "Your curse makes feeding a hassle. People don't react well to getting a good look at you."
            elif clan == cfg.CLAN_RAVNOS:
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
                # self.clan_blurbs[cfg.REF_CLAN_CHOSEN] = "Feeding isn't the problem so much as finding a place to crash afterward."
            elif clan == cfg.CLAN_VENTRUE:
                self.unlock_discipline(cfg.DISC_DOMINATE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_FORTITUDE, cfg.VAL_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.VAL_DISC_INCLAN)
                # self.clan_blurbs[cfg.REF_CLAN_CHOSEN] = "You have certain... dietary restrictions. It's not easy being a picky vampire."
            else:
                raise ValueError("Invalid clan \"{}\".".format(clan))

        def choose_predator_type(self, pt):
            if pt == cfg.PT_ALLEYCAT:
                self.humanity -= 1
                self.skills[cfg.SK_COMB] += 1
                self.skills[cfg.SK_INTI] += 1
                self.predator_pools = []
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
            self.predator_type = pt
            self.recalculate_stats()

        def unlock_discipline(self, disc, level):
            # Has no effect if already unlocked at a higher level
            if self.available_disciplines[disc] < level:
                self.available_disciplines[disc] = level

        def handle_demise(self, tracker_type):
            pass


init 1 python in state:
    pc = None
    cfg, utils = renpy.store.cfg, renpy.store.utils
    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]
    pc = renpy.store.game.PlayerChar(anames=attr_names, snames=skill_names, dnames=discipline_names)

    def available_pc_will():
        return pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)

    def pc_can_drink_swill():
        if pc.clan == cfg.CLAN_VENTRUE:
            return False
        if pc.blood_potency > 4:
            return False
        if pc.blood_potency > 2 and cfg.POWER_ANIMALISM_SUCCULENCE not in pc.powers:
            return False
        return True

    def set_hunger(delta, killed=False, innocent=False):
        new_hunger = utils.nudge_int_value(pc.hunger, delta, "Hunger", floor=cfg.HUNGER_MIN_KILL if killed else cfg.HUNGER_MIN, ceiling=7)
        pc.hunger = new_hunger
        if killed and innocent:
            pc.set_humanity("-=1")
        if pc.hunger > cfg.HUNGER_MAX_CALM:
            renpy.show_screen(_screen_name="hungerlay", _layer = "hunger_layer", _tag = "hungerlay", _transient = False)
        else:
            renpy.hide_screen("hungerlay", "master")

    def set_humanity(delta):
        new_humanity = utils.nudge_int_value(pc.humanity, delta, "Humanity", floor=cfg.MIN_HUMANITY, ceiling=cfg.MAX_HUMANITY)
        pc.humanity = new_humanity

    def deal_damage(tracker, dtype, amount):
        if tracker == cfg.TRACK_HP:
            pc.hp.damage(dtype, amount)
        else:
            pc.will.damage(dtype, amount)
