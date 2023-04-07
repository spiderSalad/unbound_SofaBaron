init 1 python in game:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state
    # NOTE: this persists between game load/cycles, as it's run when Ren'py starts - NOT when the game starts.


    class PC_V5Tracker(V5Tracker):
        def __init__(self, pc, boxes: int, tracker_type: str, armor: int = 0, bonus: int = 0):
            super().__init__(char=pc, boxes=boxes, tracker_type=tracker_type, armor=armor, bonus=bonus)

        @property
        def armor(self):  # Blocks superficial damage prior to halving.
            if self.tracker_type == cfg.TRACK_HP:
                return self.char.get_fort_toughness_armor()
            return self._armor

        @property
        def deathsave(self):
            if self.tracker_type == cfg.TRACK_HP:
                return self.char.get_fort_defybane_armor()
            return self._deathsave

        @property
        def bonus(self):
            if self.tracker_type == cfg.TRACK_HP:
                return self.char.get_fort_resilience_bonus()
            return self._bonus


    class SuperpowerArsenal:
        def __init__(self, dnames):
            self.dnames = dnames
            # No setters for these protected properties
            self._access = {}
            self._levels = {}
            self._pc_powers = {}
            self._chosen_powers = {}
            self._power_choices = {}
            self.reset()

        def reset(self, hard_reset=False):
            for dname in self.dnames:
                if hard_reset:
                    self._access[dname] = cfg.REF_DISC_LOCKED
                    self._levels[dname] = cfg.MIN_SCORE
                    self._chosen_powers[dname] = {}
                self._pc_powers[dname] = {}
                for i in range(1, 6):
                    score_word = cfg.SCORE_WORDS[i]
                    self._pc_powers[dname][score_word] = None
                    if dname in self.chosen_powers and self.chosen_powers[dname]:
                        if score_word in self.chosen_powers[dname]:
                            self._pc_powers[dname][score_word] = self.chosen_powers[dname][score_word]
            self.recalculate_power_choices()

        # None of these properties should have setters
        @property
        def access(self):
            return self._access

        @property
        def levels(self):
            return self._levels

        @property
        def pc_powers(self):
            return self._pc_powers

        @property
        def power_choices(self):
            return self._power_choices

        @property
        def chosen_powers(self):
            return self._chosen_powers

        def set_discipline_access(self, dname, access_token):
            self._access[dname] = access_token
            self.recalculate_power_choices()

        def unlock(self, dname, access_token):
            # Has no effect if already unlocked at an equal or "higher" level
            if cfg.REF_DISC_ACCESS[self.access[dname]] < cfg.REF_DISC_ACCESS[access_token]:
                self.set_discipline_access(dname, access_token)

        def get_unlocked(self, access_token=None):
            if access_token is None:
                locked = cfg.REF_DISC_ACCESS[cfg.REF_DISC_LOCKED]
                return [dname for dname in self.access if cfg.REF_DISC_ACCESS[self.access[dname]] > locked]
            else:
                minimum_access_level = cfg.REF_DISC_ACCESS[access_token]
                return [dname for dname in self.access if cfg.REF_DISC_ACCESS[self.access[dname]] >= minimum_access_level]

        def set_discipline_level(self, dname, dots):
            new_dot_level = utils.nudge_int_value(self.levels[dname], dots, floor=cfg.MIN_SCORE, ceiling=cfg.MAX_SCORE)
            self._levels[dname] = new_dot_level
            self.recalculate_power_choices()

        def recalculate_power_choices(self):
            for ul_disc in self.get_unlocked():
                power_tree = cfg.REF_DISC_POWER_TREES[ul_disc]
                power_options = {}
                for i in range(1, 6):
                    sw, possible_at_level = cfg.SCORE_WORDS[i], []
                    if self.pc_powers[ul_disc][sw] is not None:
                        continue
                    for j in range(i, 0, -1):
                        possible_at_level += power_tree[j-1]
                    available_at_level = [pw for pw in possible_at_level if not self.power_unlocked(pw, ul_disc)]
                    power_options[sw] = available_at_level
                self._power_choices[ul_disc] = power_options
            # print(utils.json_prettify(self.power_choices, sort_keys=False))

        def power_unlocked_known_disc(self, power, disc):
            if disc not in self.pc_powers or not self.pc_powers[disc] or not hasattr(self.pc_powers[disc], "values"):
                return False
            if power in self.pc_powers[disc].values():
                return True
            return False

        def power_unlocked(self, power, disc=None):
            if disc is not None:
                return self.power_unlocked_known_disc(power, disc)
            disciplines = [key for key in cfg.__dict__ if str(key).startswith("DISC_")]
            for dname_dict_key in disciplines:
                dname = getattr(cfg, dname_dict_key)
                if self.power_unlocked_known_disc(power, dname):
                    return True
            return False

        def power_prereqs_met(self, dname, power):
            if power in cfg.REF_DISC_POWER_PREREQS:
                prereq_power = cfg.REF_DISC_POWER_PREREQS[power]
                if not self.power_unlocked(prereq_power, dname):
                    return False, "Should not be able to choose power \"{}\" without prerequisite power \"{}\"".format(
                        power, prereq_power
                    )
            return True, None

        def amalgam_reqs_met(self, dname, power):
            if power in cfg.REF_DISC_AMALGAM_REQS:
                amalg, amalg_level = cfg.REF_DISC_AMALGAM_REQS[power]
                # We don't check to make sure all power slots of amalgam discipline are filled to required level,
                # only that the required number of dots is there.
                if self.levels[amalg] < amalg_level:
                    return False, "Cannot choose amalgam power \"{}\" with a {} level below {}.".format(
                        power, amalg, amalg_level
                    )
            return True, None

        def can_unlock_power(self, dname, power_name):
            if self.access[dname] == cfg.REF_DISC_LOCKED:
                return False, "{} is locked; can't choose powers from it.".format(dname)
            all_d_powers = []
            for i in range(0, 5):
                all_d_powers += cfg.REF_DISC_POWER_TREES[dname][i]
            if power_name not in all_d_powers:
                return False, "{} is not a power of {} discipline; something's gone wrong.".format(power_name, dname)
            del all_d_powers
            empty = [(cfg.SCORE_WORDS.index(pl), pl) for pl in self.pc_powers[dname] if self.pc_powers[dname][pl] is None]
            nxt_ava_lvl = min([pl[0] for pl in empty])
            if nxt_ava_lvl > self.levels[dname]:
                return False, "Cannot choose a level {} power; {} is at level {}.".format(
                    nxt_ava_lvl, dname, self.levels[dname]
                )
            if self.power_unlocked(power_name, dname):
                return False, "{} has already been taken.".format(power_name)
            nal_token = cfg.SCORE_WORDS[nxt_ava_lvl]
            available_powers = self.power_choices[dname][nal_token]
            if power_name not in available_powers:
                return False, "Should not be able to choose {} at {} level {}.".format(power_name, dname, nxt_ava_lvl)
            amalg, error_msg = self.amalgam_reqs_met(dname, power_name)
            if not amalg:
                return False, error_msg
            pow_prereq, error_msg = self.power_prereqs_met(dname, power_name)
            if not pow_prereq:
                return False, error_msg
            return True, nal_token

        def check_power_locks(self, dname, power_name):
            can_unlock, result_str = self.can_unlock_power(dname, power_name)
            if not can_unlock:
                raise ValueError(result_str)
            return can_unlock, result_str

        def unlock_power(self, dname, power_name, record_choice=True):
            try:
                can_unlock, nal_token = self.check_power_locks(dname, power_name)
            except ValueError as ve:
                # TODO: add something here?
                utils.log("Problem occurred while trying to unlock new power:\n{}".format(ve))
                return
            except Exception as e:
                utils.log("Unknown {} raised while trying to unlock new power:\n{}".format(e))
                return
            # Once successfully chosen:
            self._pc_powers[dname][nal_token] = power_name
            if record_choice:
                self._chosen_powers[dname][nal_token] = power_name
            self.recalculate_power_choices()
            utils.log(utils.json_prettify(self.pc_powers[dname]))


    class PlayerChar(Entity):
        def __init__(self, anames, snames, dnames, **kwargs):
            super().__init__(ctype=cfg.CT_VAMPIRE, **kwargs)
            self.is_pc, self.ftype = True, "PC"
            self.nickname = "That lick from around the way"
            self.clan = None
            self.predator_type = None
            self.blood_potency = 1
            self._hunger = 1
            self._humanity = 7
            self.hp, self.will = PC_V5Tracker(self, 3, cfg.TRACK_HP), PC_V5Tracker(self, 3, cfg.TRACK_WILL)
            # self.crippled, self.shocked = False, False
            self.frenzied_bc_hunger, self.frenzied_bc_fear = False, False
            # self.dead, self.cause_of_death = False, None
            # self._status = "(All clear)"
            self.clan_blurbs = {}
            self.anames, self.snames, self.dnames = anames, snames, dnames
            self.attrs = {}
            self.skills = {}
            self.mortal_backstory = None
            self._backgrounds = []
            self.disciplines = SuperpowerArsenal(self.dnames)
            self.disciplines.reset(hard_reset=True)
            self.inventory, self.equipped_weapon = None, None
            self.lethal_body_active = False
            self.reset_charsheet_stats()

        @property
        def name(self):
            return "You"
            # return self.nickname

        @property
        def status(self):
            status_list = []
            if self.frenzied_bc_hunger and self.hunger >= cfg.HUNGER_MAX:
                status_list.append("Hunger frenzy!")
            elif self.frenzied_bc_fear:
                status_list.append("Terror frenzy!")
            elif self.hunger >= cfg.HUNGER_MAX:
                status_list.append("Starving")
            if self.crippled:
                status_list.append("Maimed")
            if self.shocked:
                status_list.append("Shellshocked")
            if len(status_list) == 0:
                return "\"Fine\""
            else:
                return ", ".join(status_list)
            # return self._status

        @property
        def hunger(self):
            return self._hunger

        @hunger.setter
        def hunger(self, new_hunger):
            self._hunger = max(0, min(new_hunger, cfg.HUNGER_MAX + 1))
            if self.hunger > cfg.HUNGER_MAX:
                print("Hunger tested at 5; frenzy check?")  # TODO: frenzy check
                self.frenzied_bc_hunger = True
                self.hunger = cfg.HUNGER_MAX
            else:
                utils.log("Hunger now set at {}".format(self.hunger))
                if self.frenzied_bc_hunger and self.hunger < cfg.HUNGER_MAX_CALM:
                    self.frenzied_bc_hunger = False

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

        def apply_background(self, background, bg_key=None, force_add=False, force_replace=False):
            bg, key = background, bg_key
            if type(background) in (str,):
                bg = cfg.CHAR_BACKGROUNDS[background]
                key = background
            if cfg.REF_BG_NAME not in bg:
                bg[cfg.REF_BG_NAME] = key
            # Reject any background if it shares a subtype with an existing background unless force_add == True, e.g picking
            # Nosferatu and Siren should leave PC with Repulsive and not Beautiful. Setting force_replace to True removes any
            # previous backgrounds of the same type. Backgrounds with a non-exclusive subtype (or no subtype) are exempt.
            if cfg.REF_SUBTYPE not in bg or force_add:
                self._backgrounds.append(bg)
            elif force_replace:
                filtered_bgs = [_bg for _bg in self._backgrounds if _bg[cfg.REF_SUBTYPE] != bg[cfg.REF_SUBTYPE]]
                self._backgrounds = filtered_bgs
                self._backgrounds.append(bg)
            else:
                bg_subtype = bg[cfg.REF_SUBTYPE]
                existing_subtypes = [bg[cfg.REF_SUBTYPE] for bg in self.backgrounds if cfg.REF_SUBTYPE in bg]
                if bg_subtype in cfg.REF_BG_NON_EXCLUSIVE_SUBTYPES or bg_subtype not in existing_subtypes:
                    self._backgrounds.append(bg)
            if bg[cfg.REF_TYPE] == cfg.REF_BG_PAST:
                self.mortal_backstory = bg[cfg.REF_BG_NAME]
            # elif bg[cfg.REF_TYPE] == cfg.REF_VENTRUE_PALATE:
            #     self.ventrue_feeding_palate = bg[cfg.REF_BG_NAME]
            self.recalculate_stats()

        def get_matching_backgrounds(self, bg_name=None):  # TODO: update this to search for type and subtype
            matching = []
            for bg in self.backgrounds:
                if type(bg) in (str,) and bg_name == bg:
                    matching.append(bg)
                elif type(bg) in (dict,) and cfg.REF_BG_NAME in bg and bg[cfg.REF_BG_NAME] == bg_name:
                    matching.append(bg)
            return matching

        def has_background(self, bg_name=None):
            matching = self.get_matching_backgrounds(bg_name=bg_name)
            return len(matching) > 0

        def apply_xp(self):
            return self  # TODO: implement this

        def attack(self, action_order, ao_index, enemy_targets, all_targets):
            pass

        def defend(self, attacker, atk_action):
            pass

        # def impair(self, impaired, tracker_type):
        #     if tracker_type == cfg.TRACK_HP:
        #         self.crippled = impaired
        #     elif tracker_type == cfg.TRACK_WILL:
        #         self.shocked = impaired

        def get_fort_resilience_bonus(self):
            if not self.has_disc_power(cfg.POWER_FORTITUDE_HP, cfg.DISC_FORTITUDE):
                return 0
            return self.disciplines.levels[cfg.DISC_FORTITUDE]

        def get_fort_toughness_armor(self):
            if not self.has_disc_power(cfg.POWER_FORTITUDE_TOUGH, cfg.DISC_FORTITUDE):
                return 0
            return self.disciplines.levels[cfg.DISC_FORTITUDE]

        def get_fort_defybane_armor(self):
            if not self.has_disc_power(cfg.POWER_FORTITUDE_BANE, cfg.DISC_FORTITUDE):
                return 0
            return self.disciplines.levels[cfg.DISC_FORTITUDE]

        def has_disc_power(self, power, disc=None):
            return self.disciplines.power_unlocked(power, disc)

        def choose_clan(self, clan):
            self.clan = clan
            self.clan_blurbs = cfg.CLAN_BLURBS[self.clan]
            if clan == cfg.CLAN_BRUJAH:
                self.unlock_discipline(cfg.DISC_CELERITY, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.REF_DISC_INCLAN)
            elif clan == cfg.CLAN_NOSFERATU:
                self.apply_background(cfg.BG_REPULSIVE)
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_POTENCE, cfg.REF_DISC_INCLAN)
            elif clan == cfg.CLAN_RAVNOS:
                self.unlock_discipline(cfg.DISC_ANIMALISM, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_OBFUSCATE, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.REF_DISC_INCLAN)
            elif clan == cfg.CLAN_VENTRUE:
                self.unlock_discipline(cfg.DISC_DOMINATE, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_FORTITUDE, cfg.REF_DISC_INCLAN)
                self.unlock_discipline(cfg.DISC_PRESENCE, cfg.REF_DISC_INCLAN)
            elif clan == cfg.CLAN_NONE_CAITIFF:
                for dname in self.dnames:
                    if dname not in cfg.REF_DISC_NOT_YET and dname != cfg.DISC_THINBLOOD_ALCHEMY:
                        self.unlock_discipline(dname, cfg.REF_DISC_CAITIFF)
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

        def choose_predator_type(self, pt, pt_dot_disc):
            self.unlock_discipline(pt_dot_disc, cfg.REF_DISC_OUTCLAN)
            self.disciplines.set_discipline_level(pt_dot_disc, "+=1")
            if pt == cfg.PT_ALLEYCAT:
                self.humanity -= 1
                self.skills[cfg.SK_COMB] += 1
                self.skills[cfg.SK_INTI] += 1
            elif pt == cfg.PT_BAGGER:
                self.apply_background(cfg.BG_IRON_GULLET)
                self.skills[cfg.SK_CLAN] += 1
                self.skills[cfg.SK_STWS] += 1
                # TODO: Iron Gullet, Enemy (2)
            elif pt == cfg.PT_FARMER:
                self.humanity += 1
                self.skills[cfg.SK_TRAV] += 1
                self.skills[cfg.SK_DIPL] += 1
                # TODO: Vegan
            elif pt == cfg.PT_SIREN:
                self.apply_background(cfg.BG_BEAUTIFUL)
                self.skills[cfg.SK_DIPL] += 1
                self.skills[cfg.SK_INTR] += 1
                # TODO: Enemy (1)
            else:
                raise ValueError("\"{}\" is not a valid predator type.".format(pt))
            self.apply_background(cfg.CHAR_PT_STATBLOCKS[pt], bg_key=pt)
            self.predator_type = pt
            self.recalculate_stats()
            # TODO: check this
            # state.predator_type_choice_post_setup(self.predator_type)

        def unlock_discipline(self, disc, access):
            self.disciplines.unlock(disc, access)

        def handle_demise(self, tracker_type, damage_source):
            # self.dead = True
            # self.cause_of_death = damage_source
            super().handle_demise(tracker_type=tracker_type, damage_source=damage_source)
            renpy.jump("end")


#
