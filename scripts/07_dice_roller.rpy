define rollie = Character(name="Roll Results", color="#3a4a5a")

init 1 python in game:

    from math import floor as math_floor


    class RollConfig:
        OPTIONAL_STATS = [
            cfg.REF_ROLL_LOOKS
        ]

        ALT_DISPLAY_STATS = [
            cfg.REF_ROLL_LOOKS, cfg.BG_BEAUTIFUL, cfg.BG_REPULSIVE, cfg.BG_UGLY, cfg.BG_STUNNING,
            str(cfg.REF_BLOOD_SURGE).replace(" ", ""), cfg.REF_ROLL_MULTI_DEFEND_MALUS, cfg.REF_IMPAIRMENT_PARAM
        ]

        def __init__(self, pool_text, has_opp=False, action=None, sitmod=None, surge=False, rco_owner=False, **kwargs):
            utils = renpy.store.utils
            self.num_dice = 0
            self.has_opponent, self.surge, self.weaving_exemption = has_opp, surge, False
            self.action = action
            self.is_defend_act = all([self.action, self.has_opponent, self.action.defending])
            if self.action:
                self.rco_owner = self.action.user
            else:
                self.rco_owner = rco_owner if rco_owner else renpy.store.state.pc
            self.contests = utils.parse_pool_string(pool_text, situational_mod=sitmod, blood_surging=self.surge)
            utils.log(f'\n--- {"CONTESTS" if self.has_opponent else "TESTS"} ---\n{self.contests}')
            if len(self.contests) != 1:
                raise ValueError("Should be exactly one phase per RollConfig object, not {}.".format(len(self.contests)))
            self.check_optional_kwargs(**kwargs)
            self.pool_options = self.contests[0]
            self.roll_config_options = [self.evaluate(po) for po in self.pool_options]
            # Here we do a max or something
            self.chosen_rc_opt = max(self.roll_config_options, key=lambda rco: rco.num_dice)
            for key in self.chosen_rc_opt.__dict__:
                val = getattr(self.chosen_rc_opt, key)
                setattr(self, key, val)
            if self.action:
                self.action.num_dice = self.chosen_rc_opt.num_dice

        def check_optional_kwargs(self, **kwargs):
            if renpy.store.state.StatusFX.weaving_power_is_valid(self.rco_owner, self.action):
                self.weaving_exemption = True
            if "opposing_ranged_attack" in kwargs and self.action:
                self.action.vs_ranged = kwargs["opposing_ranged_attack"]

        def evaluate(self, pool_option):
            required_stats, optional_stats = [], [] # TODO: what was I doing here?
            roll_stats_main, roll_stats_alt = [], []
            buffed_pool_option = pool_option
            if self.action:
                self.action, buffed_pool_option = BuffPipeline.process_pool(
                    self.action.user, pool_option, action=self.action
                )
            if self.rco_owner.times_attacked_this_turn and self.is_defend_act and not self.weaving_exemption:
                buffed_pool_option += f' + {cfg.REF_ROLL_MULTI_DEFEND_MALUS}'
            print(f'| | | buffed_pool_option: {buffed_pool_option}')
            pool_stats = buffed_pool_option.replace(" ", "").split("+")
            pool_choice, pool_text_v2 = object(), ""
            for stat in pool_stats: # self.pool_stats:
                if stat in RollConfig.OPTIONAL_STATS:
                    optional_stats.append(stat)
                else:
                    required_stats.append(stat)
                if stat in RollConfig.ALT_DISPLAY_STATS:
                    roll_stats_alt.append(stat)
                else:
                    roll_stats_main.append(stat)
            pool_choice.num_dice = 0
            pool_choice.has_bonuses = False
            pc, bonus_key, bonus_total = renpy.store.state.pc, cfg.REF_ROLL_BONUS_PREFIX, 0
            for stat in pool_stats:  # self.pool_stats:
                stat = str(stat).capitalize()
                if utils.caseless_in("Bloodsurge", stat):
                    stat = "Blood Surge"
                utils.log(f'RollConfig parameter: {stat}')
                if str(stat).lower().startswith("pool"):
                    pool_choice.num_dice += int(str(stat)[len("pool"):])
                elif self.rco_owner.is_pc and stat in pc.attrs:
                    pool_choice.num_dice += pc.attrs[stat]
                elif self.rco_owner.is_pc and stat in pc.skills:
                    pool_choice.num_dice += pc.skills[stat]
                elif self.rco_owner.is_pc and stat in pc.disciplines.get_unlocked():
                    pool_choice.num_dice += pc.disciplines.levels[stat]
                elif self.rco_owner.is_pc and stat in (cfg.AT_CHA, cfg.SK_DIPL, cfg.REF_ROLL_LOOKS):
                    bg_names = [bg[cfg.REF_BG_NAME] for bg in pc.backgrounds]
                    looks_merits = (cfg.BG_BEAUTIFUL, cfg.BG_REPULSIVE, cfg.BG_UGLY, cfg.BG_STUNNING)
                    # A character should only ever have one Looks merit/flaw at a time.
                    look_ref = next((lk for lk in bg_names if lk in looks_merits), None)
                    if look_ref:
                        look, pool_choice.has_bonuses = cfg.CHAR_BACKGROUNDS[look_ref], True
                        bonus_malus = -1 if look[cfg.REF_TYPE] == cfg.REF_BG_FLAW else 1
                        setattr(pool_choice, f'{bonus_key}{look_ref}', bonus_malus * int(look[cfg.REF_DOTS]))
                        required_stats.append(look_ref)
                elif utils.is_number(stat) and utils.has_int(stat):
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, cfg.REF_ROLL_EVENT_BONUS, stat)
                elif utils.caseless_equal(stat, cfg.REF_BLOOD_SURGE):
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, bonus_key + cfg.REF_BLOOD_SURGE, utils.get_bp_surge_bonus(self.rco_owner.blood_potency))
                elif utils.caseless_equal(stat, cfg.REF_IMPAIRMENT_PARAM):
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, bonus_key + cfg.REF_IMPAIRMENT_PARAM, -1 * cfg.IMPAIRMENT_PENALTY)
                elif utils.caseless_equal(stat, cfg.REF_ROLL_MULTI_DEFEND_MALUS):
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, cfg.REF_ROLL_MULTI_DEFEND_MALUS, -1 * self.rco_owner.times_attacked_this_turn)
                else:
                    # TODO: backgrounds, banes
                    raise ValueError(f'Stat "{stat}" is not an attribute, skill, or discipline.')
            pp_kwargs = {cfg.REF_ROLL_MULTI_DEFEND_MALUS: self.rco_owner.times_attacked_this_turn}
            pool_choice.pool_text = utils.translate_dice_pool_params(roll_stats_main, roll_stats_alt, **pp_kwargs)
            print("\n", "\n", "\n", f'At creation, pool_text_v2: {pool_choice.pool_text}', "\n", "\n")
            for key in pool_choice.__dict__:
                if str(key).startswith(bonus_key):
                    bonus_total += int(getattr(pool_choice, key))
            pool_choice.num_dice += bonus_total
            pool_choice.bonuses_total = bonus_total
            return pool_choice

    class V5DiceRoll:
        D10_WIN_INC = 6
        D10_MAX = 10

        RESULT_BESTIAL_FAIL = "Bestial Failure"
        RESULT_FAIL = "Failure"
        RESULT_WIN = "Success"
        RESULT_CRIT = "Critical"
        RESULT_MESSY_CRIT = "Messy Critical"

        RESULT_ANY_WIN = [RESULT_WIN, RESULT_CRIT, RESULT_MESSY_CRIT]
        RESULT_ANY_FAIL = [RESULT_FAIL, RESULT_BESTIAL_FAIL]
        RESULT_ANY_VALID = RESULT_ANY_WIN + RESULT_ANY_FAIL

        def __init__(self, pool, difficulty, hunger=1, include_hunger=True, win_threshold=0, original_pool_text=None):
            self.rid = renpy.store.utils.generate_random_id_str(label="v5roll#")
            self.original_pool_text = original_pool_text
            self.hunger = int(hunger) if include_hunger else 0
            self.pool, self.difficulty = int(pool), int(difficulty)
            self.opp_ws = None
            self.win_threshold = win_threshold
            self.red_results, self.red_ones, self.red_tens = [], 0, 0
            self.black_tens, self.black_failures = 0, 0
            self.result_descriptor = V5DiceRoll.RESULT_FAIL
            self.times_rolled, self.times_outcome_checked = 0, 0
            self.crit = False
            self.can_reroll_to_improve, self.can_reroll_to_avert_mc = False, False
            self.num_successes = 0
            self.outcome, self.margin = None, 0
            self.black_pool = max(pool - self.hunger, 0) if include_hunger else pool
            self.black_results = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, self.black_pool)
            self.included_hunger = include_hunger
            if self.included_hunger:
                self.red_results = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, min(self.hunger, self.pool))
            self.calculate()

        def __repr__(self):
            return "{}: {}".format(self.rid, " ".join([str(c) for c in self.black_results + self.red_results]))

        @property
        def rerolled(self):
            return self.times_rolled > 1

        def calculate(self):
            self.times_rolled += 1
            self.crit = False
            successes = [dv for dv in self.black_results if dv >= V5DiceRoll.D10_WIN_INC]
            self.black_failures = len(self.black_results) - len(successes)
            self.black_tens = len([ten for ten in successes if ten >= V5DiceRoll.D10_MAX])
            if self.included_hunger:  # and not self.rerolled:  TODO: why did I do this?
                red_successes = [dv for dv in self.red_results if dv >= V5DiceRoll.D10_WIN_INC]
                self.red_tens = len([ten for ten in red_successes if ten >= V5DiceRoll.D10_MAX])
                self.red_ones = len([one for one in self.red_results if one < 2])
                successes += red_successes
            self.num_successes = len(successes)
            if self.red_tens + self.black_tens > 1:
                self.crit = True
                self.num_successes += (math_floor((self.red_tens + self.black_tens) / 2) * 2)
            self.margin = self.num_successes - self.difficulty
            self.set_outcome()
            # Reroll logic
            if self.rerolled:
                self.can_reroll_to_improve, self.can_reroll_to_avert_mc = False, False
            else:
                if self.black_failures > 0:
                    self.can_reroll_to_improve = True
                if self.outcome == V5DiceRoll.RESULT_MESSY_CRIT and self.red_tens < 2 and self.black_tens < 4:
                    self.can_reroll_to_avert_mc = True

        def set_outcome(self):
            self.times_outcome_checked += 1
            if self.margin >= self.win_threshold:
                if self.red_tens > 0 and self.included_hunger and self.crit:
                    self.outcome = V5DiceRoll.RESULT_MESSY_CRIT
                elif self.crit:
                    self.outcome = V5DiceRoll.RESULT_CRIT
                else:
                    self.outcome = V5DiceRoll.RESULT_WIN
            else:
                if self.red_ones > 0 and self.included_hunger:
                    self.outcome = V5DiceRoll.RESULT_BESTIAL_FAIL
                else:
                    self.outcome = V5DiceRoll.RESULT_FAIL

        def rr_fails(self):
            if not self.can_reroll_to_improve:
                utils.log("Invalid failure reroll requested.")
                return
            num_rerolls = min(3, self.black_failures)
            for i, d10result in enumerate(self.black_results):
                if num_rerolls <= 0:
                    break
                if d10result < V5DiceRoll.D10_WIN_INC:
                    tmp = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, 1)[0]
                    self.black_results[i] = tmp
                    num_rerolls -= 1
            self.calculate()

        def rr_messy_crit(self):
            if not self.can_reroll_to_avert_mc:
                utils.log("Invalid messy crit reroll requested.")
                return
            num_rerolls = min(3, self.black_tens)
            for i, d10result in enumerate(self.black_results):
                if num_rerolls <= 0:
                    break
                if d10result == V5DiceRoll.D10_MAX:
                    self.black_results[i] = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, 1)[0]
                    num_rerolls -= 1
            self.calculate()

        @staticmethod
        def zero_result():
            roll = V5DiceRoll(0, 0)
            return roll


    class DiceRoller:
        def __init__(self):
            self.current_roll = None
            self.current_opp_roll = None

        def test(self, pool, difficulty, hunger=1, include_hunger=True):
            if int(pool) < 1:
                pool = 1
            self.current_opp_roll = None
            self.current_roll = V5DiceRoll(int(pool), int(difficulty), hunger=hunger, include_hunger=include_hunger)
            return self.current_roll

        def contest(self, pool1, pool2, hunger=1, include_hunger=True, pc_defending=False):
            if pool2 is None:
                return self.test(pool1, 0, hunger=hunger, include_hunger=include_hunger), None
            if int(pool1) < 1:
                pool1 = 1
            if int(pool2) < 1:
                pool2 = 1
            self.current_opp_roll = V5DiceRoll(
                int(pool2), 0, hunger=hunger, include_hunger=(include_hunger and pc_defending), win_threshold=1
            )
            self.current_roll = V5DiceRoll(
                # int(pool1), self.current_opp_roll.num_successes, hunger=hunger, include_hunger=(include_hunger and not pc_defending)
                int(pool1), 0, hunger=hunger, include_hunger=(include_hunger and not pc_defending)
            )
            return self.calc_contest_margin(self.current_roll, self.current_opp_roll)

        def calc_contest_margin(self, active_roll=None, response_roll=None):
            if active_roll is None and response_roll is None:
                active_roll, response_roll = self.current_roll, self.current_opp_roll
            margin = active_roll.num_successes - response_roll.num_successes
            active_roll.margin = margin
            response_roll.margin = margin * -1
            active_roll.opp_ws = response_roll.num_successes
            response_roll.opp_ws = active_roll.num_successes
            active_roll.set_outcome(), response_roll.set_outcome()
            return active_roll, response_roll

        def reroll_fails(self, roll_to_reroll):
            if roll_to_reroll.rerolled:
                raise ValueError("Should not be able to reroll a single roll more than once.")
            roll_to_reroll.rr_fails()
            if roll_to_reroll.opp_ws is None:
                return roll_to_reroll
            return self.calc_contest_margin()

        def reroll_messy_crit(self, roll_to_reroll):
            if roll_to_reroll.rerolled:
                raise ValueError("Should not be able to reroll a single roll more than once.")
            if roll_to_reroll.outcome != V5DiceRoll.RESULT_MESSY_CRIT:
                raise ValueError("This option should only be available if there's a messy critical.")
            roll_to_reroll.rr_messy_crit()
            if roll_to_reroll.opp_ws is None:
                return roll_to_reroll
            return self.calc_contest_margin()


    def rollrouting_pass_fail(roll_obj, win_label, loss_label, top_label=""):
        try:
            return top_label + win_label if roll_obj.outcome in V5DiceRoll.RESULT_ANY_WIN else top_label + loss_label
        except:
            return top_label + loss_label

    def rollrouting_manual(roll_obj, win, fail, mc=None, crit=None, bfail=None, top_label=""):
        if mc is None and crit is None and bfail is None:
            return rollrouting_pass_fail(roll_obj, win, fail, top_label=top_label)
        outcome = roll_obj.outcome
        if outcome == V5DiceRoll.RESULT_MESSY_CRIT:
            if mc or crit:
                return top_label + mc if mc else top_label + crit
            return top_label + win
        elif outcome == V5DiceRoll.RESULT_CRIT:
            return top_label + crit if crit else top_label + win
        elif outcome == V5DiceRoll.RESULT_BESTIAL_FAIL:
            return top_label + bfail if bfail else top_label + fail
        elif outcome == V5DiceRoll.RESULT_WIN:
            return top_label + win
        elif outcome == V5DiceRoll.RESULT_FAIL:
            return top_label + fail
        else:
            raise ValueError("\"{}\" is not a valid roll outcome.".format(outcome))


init python in state:
    # diceroller = None
    pc_roll, active_roll, response_roll = None, None, None
    roll_config, pool_readout = None, None

    cfg, utils = renpy.store.cfg, renpy.store.utils
    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]

    def roll_bones(primary_rc, secondary_rc=None, difficulty=None, pc_defending=False):
        global pc_roll
        global active_roll
        global response_roll
        global active_rc

        if active_roll:
            active_roll = None
        # if response_roll:
            # del response_roll

        if secondary_rc and isinstance(secondary_rc, game.RollConfig):
            active_roll, response_roll = diceroller.contest(
                pool1=primary_rc.num_dice, pool2=secondary_rc.num_dice, hunger=pc.hunger, pc_defending=pc_defending
            )
        elif secondary_rc and isinstance(secondary_rc, game.CombatAction):
            active_roll, response_roll = diceroller.contest(
                pool1=primary_rc.num_dice, pool2=None, hunger=pc.hunger, pc_defending=pc_defending
            )
            active_roll.opp_ws = 0
            response_roll = game.V5DiceRoll.zero_result()
        elif difficulty:
            active_roll = diceroller.test(primary_rc.num_dice, difficulty=difficulty, hunger=pc.hunger)
        else:
            raise AttributeError("Dice Roll moment must have either an opposition pool or flat difficulty!")

        if primary_rc and isinstance(primary_rc, game.RollConfig) and primary_rc.action:
            primary_rc.action.lifted_num_successes = active_roll.num_successes
        if secondary_rc and isinstance(secondary_rc, game.RollConfig) and secondary_rc.action:
            secondary_rc.action.lifted_num_successes = response_roll.num_successes

        if pc_defending:
            pc_rc, pc_roll = secondary_rc, response_roll
        else:
            pc_rc, pc_roll = primary_rc, active_roll

    def post_roll_routine(rconfig=None, rolled=None):
        if rconfig and rolled:
            temp_rconfig, temp_roll = rconfig, rolled
        else:
            temp_rconfig, temp_roll = roll_config, pc_roll
        readout = roll_display(rconfig=temp_rconfig, rolled=temp_roll)
        check_for_reroll(rolled=temp_roll)
        return readout

    def roll_display(rconfig, rolled):
        delim = " "
        global pool_readout
        de_pouelle_text = rconfig.pool_text
        plus_min_tmp = str(de_pouelle_text).replace(" ", "").replace("+-", " - ")
        plus_min_tmp = plus_min_tmp.replace("Bloodsurge", "Blood Surge")
        pool_readout = plus_min_tmp.replace("+", " + ").replace("_", " ")
        if rconfig.has_opponent:
            test_summary = "Versus {}, margin of {}".format(rolled.opp_ws, rolled.margin)
        else:
            test_summary = "Difficulty {}, margin of {}".format(rolled.difficulty, rolled.margin)
        roll_result = "{}! {} success{} from {} di{}. ({})".format(
            rolled.outcome, rolled.num_successes, "es" if rolled.num_successes != 1 else "",
            rolled.pool, "ce" if rolled.pool != 1 else "e", test_summary
        )
        actual_dice_repr = delim.join(["< {} >".format(dr) for dr in rolled.black_results])
        actual_dice_repr += delim + delim.join([
            ("{color=#ef0404}< " + "{}".format(dr) + " >{/color}")
            for dr in rolled.red_results
        ])
        return '\n\n'.join([roll_result, actual_dice_repr])  # pool_readout excluded and placed in character name

    def check_for_reroll(rolled):
        global can_reroll_to_improve, can_reroll_to_avert_mc
        if available_pc_will() > 0 and not rolled.rerolled:
            can_reroll_to_improve = rolled.can_reroll_to_improve  # rconfig.can_reroll_to_improve
            can_reroll_to_avert_mc = rolled.can_reroll_to_avert_mc  # rconfig.can_reroll_to_avert_mc
        else:
            can_reroll_to_improve = False
            can_reroll_to_avert_mc = False

    def reroll(messy=False):
        if not messy:
            diceroller.reroll_fails(pc_roll)
        else:
            diceroller.reroll_messy_crit(pc_roll)
        deal_damage(cfg.TRACK_WILL, cfg.DMG_FULL_SPF, 1)
        post_roll_routine()

    def get_pool_readout():
        if hasattr(renpy.store.state, "pool_readout"):
            return "Roll: {}".format(renpy.store.state.pool_readout)
        return "Roll: (Empty)"

    def rouse_check(num_checks=1, reroll=False, q_sound=None):
        num_dice_per_check = 2 if reroll else 1
        hungrier, rc_fails = False, 0
        for i in range(num_checks):
            rc_roll = utils.make_dice_roll(renpy.store.game.V5DiceRoll.D10_MAX, num_dice_per_check)
            rc_score = max(rc_roll)
            if rc_score < renpy.store.game.V5DiceRoll.D10_WIN_INC:
                set_hunger("+=1")
                rc_fails += 1
                hungrier = True
            renpy.play(q_sound, "audio")
        return hungrier, rc_fails

    def blood_surge(rouse_check_success_sound=None):
        if not renpy.store.state.blood_surge_enabled or not pc.can_rouse():
            return  # TODO: raise exception here?
        hungrier = renpy.call_in_new_context("roll_control.rouse_check", q_sound=rouse_check_success_sound)
        # TODO: additional sound effect here?
        renpy.store.state.blood_surge_active = True
        if hungrier:
            refresh_hunger_ui()

    def can_sense_unseen(hidden, seer):
        if not seer.always_detector and not seer.get_effect_ttl(Entity.SE_AUSPEX_ESP):
            return False
        if hidden.is_pc:
            hide_pool = hidden.attrs[cfg.AT_WIT] + hidden.disciplines.levels[cfg.DISC_OBFUSCATE]
        else:
            obfu_stats = [sk for sk in hidden.special_skills if sk in CombAct.SNEAK_VARIANTS]
            hide_pool = max(obfu_stats)
        if seer.is_pc:
            seek_pool = seer.attrs[cfg.AT_WIT] + seer.disciplines.levels[cfg.DISC_AUSPEX]
        else:
            ausp_stats = [sk for sk in seer.special_skills if sk in CombAct.DETECTION_VARIANTS]
            seek_pool = max(ausp_stats)
        sense_roll, hide_roll = diceroller.contest(pool1=seek_pool, pool2=hide_pool, hunger=pc.hunger, include_hunger=seer.is_pc)
        return sense_roll.margin > 0


label roll_control(active_pool, test_or_contest, situational_mod=None, active_a=True, response_a=None):
    # NOTE: active_a is True by default, so contests not involving player character should pass None.
    python:
        skip_ro = False
        if not state.diceroller:
            state.diceroller = game.DiceRoller()
            state.diceroller_creation_count += 1
        if not state.pc:
            state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)

    if response_a and response_a.no_contest:
        $ skip_ro = True
    else:
        play sound dice_roll_many

        "Rolling..."

    python:
        diffic, opp_pool, pc_defending = None, None, None

        active_user_pc = active_a is True or (hasattr(active_a, "user") and active_a.user and active_a.user.is_pc)
        if active_a is True:
            active_a = None
        response_user_pc = response_a is True or (hasattr(response_a, "user") and response_a.user and response_a.user.is_pc)
        if response_a is True:
            response_a = None

        if not active_a or active_user_pc:
            pc_defending = False
        elif response_user_pc:
            pc_defending = True
        contesting_response = hasattr(response_a, "action_type") and response_a.action_type not in game.CombAct.NO_CONTEST
        if pc_defending or contesting_response or (test_or_contest and cfg.ROLL_CONTEST in test_or_contest):
            is_contest, primary_pool, opp_pool = True, active_pool, test_or_contest
        elif test_or_contest is None or cfg.ROLL_TEST in test_or_contest:
            is_contest, primary_pool = False, active_pool
            diffic = str(test_or_contest).split(cfg.ROLL_TEST)[1] if test_or_contest else 1
        else:
            raise ValueError("All calls to roll_control should 1) have a response action, 2) be a contest, or 3) be a test.")

        if (pc_defending and (not active_a or not response_a)):
            raise ValueError("If player is defending, that implies combat which means there should be two actions passed.")
        if is_contest and not opp_pool:
            if active_a and active_a.action_type not in CombAct.NO_CONTEST:
                if response_a and response_a.action_type not in CombAct.NO_CONTEST:
                    raise ValueError(f'Contests should always have an opp pool. {opp_pool}, {active_a.action_type}')

        state.roll_config = game.RollConfig(
            primary_pool, has_opp=is_contest,
            sitmod=situational_mod if active_user_pc else None,
            surge=state.blood_surge_active if active_user_pc else False,
            action=active_a
        )
        state.test_rco = None
        if opp_pool:
            state.test_rco = game.RollConfig(
                opp_pool, has_opp=is_contest,
                sitmod=situational_mod if response_user_pc else None,
                surge=state.blood_surge_active if response_user_pc else False,
                action=response_a,
                opposing_ranged_attack=(active_a.action_type == CombAct.RANGED_ATTACK)
            )
        elif response_a:
            state.test_rco=response_a
        state.roll_bones(state.roll_config, secondary_rc=state.test_rco, difficulty=diffic, pc_defending=pc_defending)

    if pc_defending is None:  # None == NPC on NPC attack.
        $ skip_ro = True

    if (active_a and active_a.autowin) or (response_a and response_a.autowin):
        $ skip_ro = True

    if response_a and response_a.no_contest:
        $ skip_ro = True

    label .skip_roll_opts:
        if skip_ro:
            if not cfg.DEV_MODE:
                $ renpy.block_rollback()
            jump .end_npc_clash

    label .reroll_options_menu:

        python:
            if pc_defending:
                results_readout = state.post_roll_routine(rconfig=state.test_rco, rolled=state.diceroller.current_opp_roll)
            else:
                results_readout = state.post_roll_routine(rconfig=state.roll_config, rolled=state.active_roll)
            dice_pool_desc = state.get_pool_readout()
            renpy.block_rollback()

        show roll_desc "{size=+5}[dice_pool_desc]{/size}"

        menu:
            rollie "[results_readout]"

            "Confirm":
                jump roll_control.end

            "Focus your will and overcome the challenge (Re-roll)" if state.can_reroll_to_improve:
                play sound dice_roll_few
                $ state.reroll()
                jump roll_control.reroll_options_menu

            "Focus your will and try to suppress the Beast (Re-roll)" if state.can_reroll_to_avert_mc:
                play sound dice_roll_few
                $ state.reroll(messy=True)
                jump roll_control.reroll_options_menu


    label .rouse_check(num_checks=1, reroll=False, q_sound=None):
        play sound dice_roll_few

        $ hungrier, hunger_gained = state.rouse_check(num_checks=num_checks, reroll=reroll, q_sound=q_sound)
        $ hunger_roll_desc = flavor.get_rouse_check_blurb(hungrier)
        $ reroll_desc = ", with Re-roll" if reroll else ""

        show roll_desc "{size=+5}[hunger_roll_desc]{/size}"

        if num_checks == 1:
            if not hungrier:
                rollie "Passed Rouse Check[reroll_desc]."
            else:
                rollie "Failed Rouse Check[reroll_desc]."
        elif num_checks > 1:
            if not hungrier:
                rollie "Passed all [num_checks] Rouse Checks."
            elif hunger_gained >= num_checks:
                rollie "Failed all [num_checks] Rouse Checks."
            else:
                rollie "Failed [hunger_gained] out of [num_checks] Rouse Checks."
        else:
            $ raise ValueError("Number of Rouse Checks should not be less than 1!")

        jump roll_control.end_rouse_check

    label .end:

        $ state.blood_surge_active = False

        hide roll_desc

        return state.active_roll

    label .end_rouse_check:

        hide roll_desc

        return hungrier

    label .end_npc_clash:

        hide roll_desc

        return state.active_roll
