define rollie = Character(name="Roll Results", color="#3a4a5a")

init 1 python in game:

    class RollConfig:
        OPTIONAL_STATS = [
            cfg.REF_ROLL_LOOKS
        ]

        def __init__(self, pool_text, has_opp=False, **kwargs):
            utils = renpy.store.utils
            self.num_dice = 0
            # self.pool_stats = str(pool_text).split('+')  # TODO: here is where I need to implement optional pools denoted by "/"
            self.has_opponent = has_opp
            self.contests = utils.parse_pool_string(pool_text)
            if len(self.contests) != 1:
                raise ValueError("There should be exactly one phase per RollConfig object, not {}.".format(len(self.contests)))
            self.pool_options = self.contests[0]
            self.roll_config_options = [self.evaluate(po) for po in self.pool_options]
            # Here we do a max or something
            self.chosen_rc_opt = max(self.roll_config_options, key=lambda rco: rco.num_dice)
            # for i, rco in enumerate(self.roll_config_options):
            #     print("OPTION #{}: {} with {} dice".format(i, rco.pool_text, rco.num_dice))
            for key in self.chosen_rc_opt.__dict__:
                val = getattr(self.chosen_rc_opt, key)
                setattr(self, key, val)

        def evaluate(self, pool_option):
            print("HEY\nHEY\npool_option = {}".format(pool_option))
            required_stats, optional_stats = [], [] # TODO: what was I doing here?
            pool_stats = pool_option.replace(" ", "").split("+")
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
                if stat in pc.attrs:
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

        def __init__(self, pool, difficulty, hunger=1, include_hunger=True):
            self.hunger = int(hunger) if include_hunger else 0
            self.pool, self.difficulty = int(pool), int(difficulty)
            self.opp_ws = None
            self.red_results, self.red_ones, self.red_tens = [], 0, 0
            self.black_tens, self.black_failures = 0, 0
            self.result_descriptor = V5DiceRoll.RESULT_FAIL
            self.rerolled = self.crit = False
            self.num_successes = 0
            self.outcome, self.margin = None, 0
            self.black_pool = max(pool - self.hunger, 0) if include_hunger else pool
            self.black_results = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, self.black_pool)
            self.included_hunger = include_hunger
            if self.included_hunger:
                self.red_results = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, min(self.hunger, self.pool))
            self.calculate()

        def calculate(self):
            self.crit = False
            successes = [dv for dv in self.black_results if dv >= V5DiceRoll.D10_WIN_INC]  # TODO: here!!
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
                self.num_successes += (self.red_tens + self.black_tens)
            self.margin = self.num_successes - self.difficulty
            if self.margin >= 0:
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


    class DiceRoller:
        def __init__(self):
            self.current_roll = None
            self.current_opp_roll = None
            self.can_reroll_to_improve = False
            self.can_reroll_to_avert_mc = False
            self.player_wins = False

        def test(self, pool, difficulty, hunger=1, include_hunger=True):
            self.current_opp_roll = None
            self.can_reroll_to_improve = self.can_reroll_to_avert_mc = False
            self.current_roll = V5DiceRoll(int(pool), int(difficulty), hunger=hunger, include_hunger=include_hunger)
            if self.current_roll.black_failures > 0:
                self.can_reroll_to_improve = True
            if self.current_roll.outcome == V5DiceRoll.RESULT_MESSY_CRIT and self.current_roll.red_tens < 2 and self.current_roll.black_tens < 4:
                self.can_reroll_to_avert_mc = True
            return self.current_roll

        def contest(self, pool1, pool2, hunger=1, include_hunger=True):
            self.can_reroll_to_improve = self.can_reroll_to_avert_mc = False
            self.current_opp_roll = V5DiceRoll(int(pool2), 0, include_hunger=False)
            self.current_roll = V5DiceRoll(int(pool1), self.current_opp_roll.num_successes, hunger=hunger, include_hunger=include_hunger)
            margin = self.current_roll.num_successes - self.current_opp_roll.num_successes
            self.current_roll.margin = margin
            self.current_roll.opp_ws = self.current_opp_roll.num_successes
            if margin >= 0:
                self.player_wins = True
            if self.current_roll.black_failures > 0:
                self.can_reroll_to_improve = True
            if self.current_roll.outcome == V5DiceRoll.RESULT_MESSY_CRIT and self.current_roll.red_tens < 2 and self.current_roll.black_tens < 4:
                self.can_reroll_to_avert_mc = True
            return self.current_roll

        def reroll_fails(self):
            if self.current_roll.rerolled:
                raise ValueError("Should not be able to reroll a single roll more than once.")
            self.current_roll.rerolled = True
            num_rerolls = min(3, self.current_roll.black_failures)
            for i, d10result in enumerate(self.current_roll.black_results):
                if num_rerolls <= 0:
                    break
                if d10result < V5DiceRoll.D10_WIN_INC:
                    tmp = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, 1)[0]
                    print("rerolling a {} at i = {}, and it's now a {}".format(self.current_roll.black_results[i], i, tmp))
                    self.current_roll.black_results[i] = tmp
                    num_rerolls -= 1
            self.current_roll.calculate()
            return self.current_roll

        def reroll_messy_crit(self):
            if self.current_roll.rerolled:
                raise ValueError("Should not be able to reroll a single roll more than once.")
            if self.current_roll.outcome != V5DiceRoll.RESULT_MESSY_CRIT:
                raise ValueError("This option should only be available if there's a messy critical.")
            self.current_roll.rerolled = True
            num_rerolls = min(3, self.current_roll.black_tens)
            for i, d10result in enumerate(self.current_roll.black_results):
                if num_rerolls <= 0:
                    break
                if d10result == V5DiceRoll.D10_MAX:
                    self.current_roll.black_results[i] = renpy.store.utils.make_dice_roll(V5DiceRoll.D10_MAX, 1)[0]
                    num_rerolls -= 1
            self.current_roll.calculate()
            return self.current_roll


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
    diceroller = None
    current_roll, roll_config, pool_readout = None, None, None
    cfg, utils = renpy.store.cfg, renpy.store.utils
    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]

    current_roll, roll_config = None, None

    def available_pc_will():
        return pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)

    def roll_bones(opp_pool=None, difficulty=None):
        # roll_config = get_roll_summary_object(player_pool, True if opp_pool else False)
        global current_roll
        global roll_config

        del current_roll

        if opp_pool:
            current_roll = diceroller.contest(pool1=roll_config.num_dice, pool2=opp_pool, hunger=pc.hunger)
        elif difficulty:
            current_roll = diceroller.test(roll_config.num_dice, difficulty=difficulty, hunger=pc.hunger)
        else:
            raise AttributeError("Dice Roll moment must have either an opposition pool or flat difficulty!")

        roll_config.can_reroll_to_improve = diceroller.can_reroll_to_improve
        roll_config.can_reroll_to_avert_mc = diceroller.can_reroll_to_avert_mc

    def roll_display(rconfig=None, roll=None):
        if rconfig and roll:
            temp_rconfig, temp_roll = rconfig, roll
        else:
            temp_rconfig, temp_roll = roll_config, current_roll
        delim = " "
        global pool_readout
        plus_min_tmp = str(temp_rconfig.pool_text).replace(" ", "").replace("+-", " - ")
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
        actual_dice_repr += delim + delim.join([("{color=#ef0404}< " + "{}".format(dr) + " >{/color}") for dr in temp_roll.red_results])
        global can_reroll_to_improve, can_reroll_to_avert_mc
        if available_pc_will() > 0 and not temp_roll.rerolled:
            can_reroll_to_improve = temp_rconfig.can_reroll_to_improve
            can_reroll_to_avert_mc = temp_rconfig.can_reroll_to_avert_mc
        else:
            can_reroll_to_improve = False
            can_reroll_to_avert_mc = False
        return '\n\n'.join([roll_result, actual_dice_repr])  # pool_readout excluded and placed in character name

    def reroll(messy=False):
        if not messy:
            diceroller.reroll_fails()
        else:
            diceroller.reroll_messy_crit()
        deal_damage(cfg.TRACK_WILL, cfg.DMG_FULL_SPF, 1)
        roll_display()
        # self.confirm_roll()

    def get_pool_readout():
        if hasattr(renpy.store.state, "pool_readout"):
            return "Roll: {}".format(renpy.store.state.pool_readout)
        return "Roll: (Empty)"

    def rouse_check(num_checks=1, reroll=False):
        num_dice, hungrier = 2 if reroll else 1, False
        for i in range(num_checks):
            rc_roll = utils.make_dice_roll(renpy.store.game.V5DiceRoll.D10_MAX, num_dice)
            rc_score = max(rc_roll)
            if rc_score < renpy.store.game.V5DiceRoll.D10_WIN_INC:
                set_hunger("+=1")
                hungrier = True
        return hungrier


label roll_control(pool_str, test_str):

    python:
        if not state.diceroller:
            state.diceroller = game.DiceRoller()
            state.diceroller_creation_count += 1
            print("\n\nCREATED NEW DICEROLLER for time #{}".format(state.diceroller_creation_count), state.diceroller)
        if not state.pc:
            state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)

    play sound dice_roll_many

    "Rolling..."

    python:
        diff, opool = None, None
        if cfg.ROLL_CONTEST in test_str:
            opool = str(test_str).split(cfg.ROLL_CONTEST)[1]
        else:
            diff = str(test_str).split(cfg.ROLL_TEST)[1]
        state.roll_config = renpy.store.game.RollConfig(pool_str, has_opp=(cfg.ROLL_CONTEST in test_str))
        state.roll_bones(opp_pool=opool, difficulty=diff)

    label .choices:

        python:
            results_readout = state.roll_display(rconfig=state.roll_config, roll=state.current_roll)
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

    label .end:

    hide roll_desc

    return state.current_roll
