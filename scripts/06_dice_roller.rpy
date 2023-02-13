define rollie = Character(name="Roll Results", color="#3a4a5a")

init 1 python in game:

    from math import floor as math_floor


    class RollConfig:
        OPTIONAL_STATS = [
            cfg.REF_ROLL_LOOKS
        ]

        def __init__(self, pool_text, has_opp=False, action=None, sitmod=None, surge=False, **kwargs):
            utils = renpy.store.utils
            self.num_dice = 0
            self.has_opponent = has_opp
            self.surge = surge
            self.action = action
            self.contests = utils.parse_pool_string(pool_text, situational_mod=sitmod, blood_surging=self.surge)
            utils.log("\n--- Contests ---\n{}".format(self.contests))
            if len(self.contests) != 1:
                raise ValueError("Should be exactly one phase per RollConfig object, not {}.".format(len(self.contests)))
            self.pool_options = self.contests[0]
            self.roll_config_options = [self.evaluate(po) for po in self.pool_options]
            # Here we do a max or something
            self.chosen_rc_opt = max(self.roll_config_options, key=lambda rco: rco.num_dice)
            for key in self.chosen_rc_opt.__dict__:
                val = getattr(self.chosen_rc_opt, key)
                setattr(self, key, val)
            if self.action:
                self.action.num_dice = self.chosen_rc_opt.num_dice

        def evaluate(self, pool_option):
            required_stats, optional_stats = [], [] # TODO: what was I doing here?
            if self.action:
                self.action, buffed_pool_option = BuffPipeline.process_pool(
                    self.action.user, pool_option, action=self.action
                )
            pool_stats = buffed_pool_option.replace(" ", "").split("+")
            pool_choice = object()
            for stat in pool_stats: # self.pool_stats:
                if stat in RollConfig.OPTIONAL_STATS:
                    optional_stats.append(stat)
                else:
                    required_stats.append(stat)
            pool_choice.num_dice = 0
            pool_choice.has_bonuses = False
            bonus_key, bonus_total = cfg.REF_ROLL_BONUS_PREFIX, 0
            pc = renpy.store.state.pc
            for stat in pool_stats:  # self.pool_stats:
                stat = str(stat).capitalize()
                if "Bloodsurge" in stat:
                    stat = "Blood Surge"
                if str(stat).lower().startswith("pool"):
                    pool_choice.num_dice += int(str(stat)[len("pool"):])
                elif stat in pc.attrs:
                    pool_choice.num_dice += pc.attrs[stat]
                elif stat in pc.skills:
                    pool_choice.num_dice += pc.skills[stat]
                elif stat in pc.disciplines.get_unlocked():
                    pool_choice.num_dice += pc.disciplines.levels[stat]
                elif stat == cfg.AT_CHA or stat == cfg.SK_DIPL or stat == cfg.REF_ROLL_LOOKS:
                    bg_names = [bg[cfg.REF_BG_NAME] for bg in pc.backgrounds]
                    if cfg.BG_BEAUTIFUL in bg_names:
                        pool_choice.has_bonuses = True
                        setattr(pool_choice, bonus_key + cfg.BG_BEAUTIFUL, 1)
                        required_stats.append("Beautiful")
                    elif cfg.BG_REPULSIVE in bg_names:
                        pool_choice.has_bonuses = True
                        setattr(pool_choices, bonus_key + cfg.BG_REPULSIVE, -2)
                        required_stats.append("Repulsive")
                elif utils.is_number(stat) and utils.has_int(stat):
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, cfg.REF_ROLL_EVENT_BONUS, stat)
                elif stat == cfg.REF_BLOOD_SURGE:
                    pool_choice.has_bonuses = True
                    setattr(pool_choice, bonus_key + cfg.REF_BLOOD_SURGE, utils.get_bp_surge_bonus(pc.blood_potency))
                else:
                    # TODO: backgrounds, banes
                    raise ValueError("Stat \"{}\" is not an attribute, skill, or discipline.".format(stat))
            pool_choice.pool_text = utils.translate_dice_pool_params(required_stats)
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


    def pass_fail(roll_obj, win_label, loss_label, top_label=""):
        try:
            return top_label + win_label if roll_obj.outcome in V5DiceRoll.RESULT_ANY_WIN else top_label + loss_label
        except:
            return top_label + loss_label

    def manual_roll_route(roll_obj, win, fail, mc=None, crit=None, bfail=None, top_label=""):
        if mc is None and crit is None and bfail is None:
            return pass_fail(roll_obj, win, fail, top_label=top_label)
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

    def available_pc_will():
        return pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)

    def roll_bones(primary_rc, secondary_rc=None, difficulty=None, pc_defending=False):
        global pc_roll
        global active_roll
        global response_roll
        global active_rc

        del active_roll

        if secondary_rc:
            active_roll, response_roll = diceroller.contest(
                pool1=primary_rc.num_dice, pool2=secondary_rc.num_dice, hunger=pc.hunger, pc_defending=pc_defending
            )
        elif difficulty:
            active_roll = diceroller.test(primary_rc.num_dice, difficulty=difficulty, hunger=pc.hunger)
        else:
            raise AttributeError("Dice Roll moment must have either an opposition pool or flat difficulty!")

        if pc_defending:
            pc_rc, pc_roll = secondary_rc, response_roll
        else:
            pc_rc, pc_roll = primary_rc, active_roll

    def roll_display(rconfig=None, roll=None):
        if rconfig and roll:
            temp_rconfig, temp_roll = rconfig, roll
        else:
            temp_rconfig, temp_roll = roll_config, pc_roll
        delim = " "
        global pool_readout
        plus_min_tmp = str(temp_rconfig.pool_text).replace(" ", "").replace("+-", " - ")
        plus_min_tmp = plus_min_tmp.replace("Bloodsurge", "Blood Surge")
        pool_readout = plus_min_tmp.replace("+", " + ")
        if temp_rconfig.has_opponent:
            test_summary = "Versus {}, margin of {}".format(temp_roll.opp_ws, temp_roll.margin)
        else:
            test_summary = "Difficulty {}, margin of {}".format(temp_roll.difficulty, temp_roll.margin)
        roll_result = "{}! {} success{} from {} di{}. ({})".format(
            temp_roll.outcome, temp_roll.num_successes, "es" if temp_roll.num_successes != 1 else "",
            temp_roll.pool, "ce" if temp_roll.pool != 1 else "e", test_summary
        )
        actual_dice_repr = delim.join(["< {} >".format(dr) for dr in temp_roll.black_results])
        actual_dice_repr += delim + delim.join([
            ("{color=#ef0404}< " + "{}".format(dr) + " >{/color}")
            for dr in temp_roll.red_results
        ])
        global can_reroll_to_improve, can_reroll_to_avert_mc
        if available_pc_will() > 0 and not temp_roll.rerolled:
            can_reroll_to_improve = temp_roll.can_reroll_to_improve#temp_rconfig.can_reroll_to_improve
            can_reroll_to_avert_mc = temp_roll.can_reroll_to_avert_mc#temp_rconfig.can_reroll_to_avert_mc
        else:
            can_reroll_to_improve = False
            can_reroll_to_avert_mc = False
        return '\n\n'.join([roll_result, actual_dice_repr])  # pool_readout excluded and placed in character name

    def reroll(messy=False):
        if not messy:
            diceroller.reroll_fails(pc_roll)
        else:
            diceroller.reroll_messy_crit(pc_roll)
        deal_damage(cfg.TRACK_WILL, cfg.DMG_FULL_SPF, 1)
        roll_display()
        # self.confirm_roll()

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
            # elif q_sound is not None:
                # renpy.play(success_sound, u'sound')
            # renpy.sound.queue(q_sound, u'sound')
            renpy.play(q_sound, "audio")
        return hungrier, rc_fails

    def blood_surge(rouse_check_success_sound=None):
        if not renpy.store.state.blood_surge_enabled or not pc.can_rouse():
            return  # TODO: raise exception here?
        # rouse_check(q_sound=rouse_check_success_sound)
        renpy.call_in_new_context("roll_control.rouse_check", q_sound=rouse_check_success_sound)
        # TODO: additional sound effect here?
        renpy.store.state.blood_surge_active = True

    def can_sense_unseen(hidden, seer):
        if not seer.always_detector and not seer.get_effect_ttl(Entity.SE_AUSPEX_ESP):
            return False
        if hidden.is_pc:
            hide_pool = hidden.attrs[cfg.AT_WIT] + hidden.disciplines.levels[cfg.DISC_OBFUSCATE]
        else:
            obfu_stats = [sk for sk in hidden.special_skills if sk in CAction.SNEAK_VARIANTS]
            hide_pool = max(obfu_stats)
        if seer.is_pc:
            seek_pool = seer.attrs[cfg.AT_WIT] + seer.disciplines.levels[cfg.DISC_AUSPEX]
        else:
            ausp_stats = [sk for sk in seer.special_skills if sk in CAction.DETECTION_VARIANTS]
            seek_pool = max(ausp_stats)
        sense_roll, hide_roll = diceroller.contest(pool1=seek_pool, pool2=hide_pool, hunger=pc.hunger, include_hunger=seer.is_pc)
        return sense_roll.margin > 0# -1


label roll_control(active_pool, test_or_contest, situational_mod=None, active_a=None, response_a=None, pc_defending=False):

    python:
        if not state.diceroller:
            state.diceroller = game.DiceRoller()
            state.diceroller_creation_count += 1
        if not state.pc:
            state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)

    play sound dice_roll_many

    "Rolling..."

    python:
        diffic, opp_pool = None, None
        if pc_defending or response_a or cfg.ROLL_CONTEST in test_or_contest:
            is_contest, primary_pool, opp_pool = True, active_pool, test_or_contest
        elif cfg.ROLL_TEST in test_or_contest:
            is_contest, primary_pool, diff = False, active_pool, str(test_or_contest).split(cfg.ROLL_TEST)[1]
        else:
            raise ValueError("All calls to roll_control should 1) have a response action, 2) be a contest, or 3) be a test.")

        if (active_a or response_a) and not is_contest:
            raise ValueError("Action arguments passed to roll control implies combat, which implies a contest.")
        if (pc_defending and (not active_a or not response_a)):
            raise ValueError("If player is defending, that implies combat which means there should be two actions passed.")
        if is_contest and not opp_pool:
            raise ValueError("Contests should always have an opp pool.")

        # if active_a:
        #     active_a, primary_pool = game.BuffPipeline.process_pool(active_a.user, primary_pool, action=active_a)
        # if response_a:
        #     response_a, opp_pool = game.BuffPipeline.process_pool(response_a.user, opp_pool, action=response_a)
            # TODO: left off HERE (feb 9 23), move BuffPipeline processing to rollconfig so bonuses are applied to all pool options
        state.roll_config = game.RollConfig(
            primary_pool, has_opp=is_contest, sitmod=situational_mod if active_a.user.is_pc else None,
            surge=state.blood_surge_active if active_a.user.is_pc else False, action=active_a
        )
        if opp_pool:
            state.test_rco = game.RollConfig(
                opp_pool, has_opp=is_contest, sitmod=situational_mod if active_a.user.is_pc else None,
                surge=state.blood_surge_active if response_a.user.is_pc else False, action=response_a
            )
        # if active_a:
        #     active_a.num_dice = state.roll_config.num_dice
        # if response_a:
        #     response_a.num_dice = state.test_rco.num_dice
        state.roll_bones(state.roll_config, secondary_rc=state.test_rco, difficulty=diffic, pc_defending=pc_defending)
        # TODO: left off here, but have not tested. Also, consider making a roll_config object for both attack and response every time,
        # not just for PC actions. But we still want to the ability to do expedient number-only opposition rolls.

    if pc_defending is None:  # None == NPC on NPC attack.
        if not cfg.DEV_MODE:
            $ renpy.block_rollback()
        jump .end_npc_clash

    label .choices:

        python:
            if pc_defending:
                results_readout = state.roll_display(rconfig=state.test_rco, roll=state.diceroller.current_opp_roll)
            else:
                results_readout = state.roll_display(rconfig=state.roll_config, roll=state.active_roll)
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
                jump roll_control.choices

            "Focus your will and try to suppress the Beast (Re-roll)" if state.can_reroll_to_avert_mc:
                play sound dice_roll_few
                $ state.reroll(messy=True)
                jump roll_control.choices


    label .rouse_check(num_checks=1, reroll=False, q_sound=None):
        play sound dice_roll_few

        $ hungrier, hunger_gained = state.rouse_check(num_checks=num_checks, reroll=reroll, q_sound=q_sound)

        show roll_desc "{size=+5}Hunger. Blood.{/size}"

        if num_checks == 1:
            if not hungrier:
                rollie "Passed Rouse Check."
            else:
                rollie "Failed Rouse Check."
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
