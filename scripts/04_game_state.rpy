default state.pc                    = None
default state.diceroller            = None
default state.clock                 = None

default state.outside_haven         = True
default state.night                 = 0
default state.hours_left            = 12
default state.first_hunt            = False
default state.hunted_tonight        = False

default state.intro_man_drank       = False
default state.intro_man_killed      = False

default state.clan_chosen           = False
default state.clan_nickname         = None
default state.clan_slur             = None
default state.predator_type_chosen  = False
default state.siren_type_chosen     = False
default state.siren_orientation     = None
default state.starting_disc_dots    = False

default state.pc_car                = "old Toyota Camry"

default state.opinions              = {}
default state.masquerade            = 60  # 0 - 100

default state.pc_cash               = 250.00
default state.roll_bonus            = 0
default state.roll_malus            = 0

default state.resonance_types       = [getattr(cfg, rt) for rt in cfg.__dict__ if str(rt).startswith("RESON_")]
default state.resonances            = {
    cfg.RESON_ANIMAL: 50,
    cfg.RESON_CHOLERIC: 100,
    cfg.RESON_MELANCHOLIC: 60,
    cfg.RESON_PHLEGMATIC: 80,
    cfg.RESON_SANGUINE: 70,
    cfg.RESON_EMPTY: 90
}

default state.reson_intensity_table = [cfg.RINT_BALANCED, cfg.RINT_FLEETING, cfg.RINT_INTENSE, cfg.RINT_ACUTE]
default state.rint_weights          = [1000, 500, 100, 10]
default state.cum_intensity_weights = [(rw8 + state.rint_weights[i-1] if i > 0 else rw8) for i, rw8 in enumerate(state.rint_weights)]


init 1 python in state:
    # pc = None
    cfg, utils = renpy.store.cfg, renpy.store.utils

    from store.game import Supply, Inventory

    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]
    # pc = renpy.store.game.PlayerChar(anames=attr_names, snames=skill_names, dnames=discipline_names)

    def available_pc_will():
        return pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)

    def pc_can_drink_swill():
        if pc.clan == cfg.CLAN_VENTRUE:
            return False
        if pc.blood_potency > 4:
            return False
        if pc.blood_potency > 2 and cfg.POWER_ANIMALISM_SUCCULENCE not in pc.disciplines.pc_powers:
            return False
        return True

    def set_hunger(delta, killed=False, innocent=False):
        previous_hunger, hunger_floor = pc.hunger, cfg.HUNGER_MIN_KILL if killed else cfg.HUNGER_MIN
        new_hunger = utils.nudge_int_value(pc.hunger, delta, "Hunger", floor=hunger_floor, ceiling=7)
        pc.hunger = new_hunger
        if pc.hunger > previous_hunger:
            renpy.play(renpy.store.audio.beastgrowl1, "sound")
        if killed and innocent:
            set_humanity("-=1")
        if pc.hunger > cfg.HUNGER_MAX_CALM:
            renpy.show_screen(_screen_name="hungerlay", _layer = "hunger_layer", _tag = "hungerlay", _transient = False)
        else:
            renpy.hide_screen("hungerlay", "master")

    def set_humanity(delta):
        new_humanity = utils.nudge_int_value(pc.humanity, delta, "Humanity", floor=cfg.MIN_HUMANITY, ceiling=cfg.MAX_HUMANITY)
        pc.humanity = new_humanity

    def deal_damage(tracker, dtype, amount, source=None):
        if tracker == cfg.TRACK_HP:
            pc.hp.damage(dtype, amount, source=source)
        else:
            pc.will.damage(dtype, amount, source=source)

    def feed_resonance(intensity=None, reso=None, boost: int = 0):
        if not intensity:
            i, tenzity = utils.get_weighted_random_sample(list(enumerate(reson_intensity_table)), cum_weights=cum_intensity_weights)[0]
            mod_i = max(0, min(i + boost, len(reson_intensity_table) - 1))
            intensity = reson_intensity_table[mod_i]
        amount = utils.random_int_range(int(intensity * 0.8), int(intensity * 1.2))
        if not reso and intensity == cfg.RINT_BALANCED:
            reso = cfg.RESON_VARIED
        elif not reso:
            reso = utils.get_random_list_elem(resonance_types)[0]
            if reso == cfg.RESON_ANIMAL:  # Don't give animal resonance unless specified.
                reso = cfg.RESON_VARIED
        elif type(reso) in (list, tuple):
            reso = utils.get_random_list_elem(reso)[0]

        if reso == cfg.RESON_VARIED:
            for rpool in resonances:
                resonances[rpool] += int(amount / len(resonances))
        else:
            resonances[reso] += amount


    loot_table = Inventory(
        Supply(Supply.IT_MONEY, "Money", num=int(12.5 * 1000 * 1000 * 1000), desc="Local city's entire GDP"),
        Supply(Supply.IT_EQUIPMENT, "Smartphone", desc="The latest and greatest in rooted burner phones. GPS disabled."),
        Supply(Supply.IT_JUNK, "Bubble Gum", desc="You were hoping this would help with blood-breath. It doesn't."),
        Supply(
            Supply.IT_WEAPON, "Switchblade", lethality=2,
            desc="You know what they say about knife fights. Good thing you're already dead."
        ),
        Supply(Supply.IT_FIREARM, "S & W Model 500", lethality=3, concealable=False, desc="Do you feel lucky?"),
        Supply(
            Supply.IT_FIREARM, "Stolen Ruger LCP", key="gun_ruger_1", lethality=2, desc="Confiscated and then re-confiscated."
        ),
        Supply(
            Supply.IT_FIREARM, "Blood-spattered Colt 45", key="police_colt", lethality=2,
            desc="I'm sure I'll need this, wherever I'm going..."
        )
    )


    class GameClock:
        MAX_HOURS_PER_NIGHT = 12

        def __init__(self, day: int = None, hours: int = None, **kwargs):
            self._night = day or 1
            self._hours = hours or 9
            self.overtime = 0

        @property
        def night(self):
            return self._night

        @property
        def hours(self):
            return self._hours

        def advance(self, hours):
            self.overtime = 0
            self._hours -= hours
            if self.hours < 0:
                self.overtime = abs(self.hours)
                self._hours = 0
            if self.hours <= 0:
                self._night += 1
                self._hours = GameClock.MAX_HOURS_PER_NIGHT
                return self.overtime, True
            return self.overtime, False

        def spend(self, hours):
            hrs = max(hours, cfg.MIN_ACTIVITY_TIME)
            return self.advance(hrs)

        def next_night(self):
            hrs = self.hours
            return self.advance(hrs)


    def get_power_choices(disc_key):
        return pc.disciplines.power_choices[disc_key]


label pass_time(hours_passed, in_shelter=False):

    if hours_passed is None:
        $ overtime, daybreak = store.state.clock.next_night()
    else:
        $ overtime, daybreak = store.state.clock.advance(hours_passed)

    if daybreak and in_shelter:
        call new_night from passing_time_safe
    elif daybreak:
        call sun_threat from passing_time_exposed
    else:
        return
    return


label sun_threat:

    "It's getting light out."

    "{i}Too{/i} light. What time is it?"

    beast "You idiot. You goddamned fool. YOU ABSOLUTELY WORTHLESS BRAINDEAD FUCKING-"

    beast "THE SUUUUUUUUUUUN THE SUUUUUN THE SUUUN THE SUN SUN SUN SUN SUN SUN SUN"

    # TODO: add some effects here

    call roll_control("dexterity+athletics/wits+streetwise/composure+traversal", "diff0") from sunburn_damage
    $ death_save, min_burn = _return.margin, 2
    $ sunburn = utils.random_int_range(0, 10)
    $ state.deal_damage(cfg.TRACK_HP, cfg.DMG_AGG, max(min_burn, sunburn - death_save), source=cfg.COD_SUN)

    call new_night from sun_threat_event

    return


label new_night:

    if pc.hp.agg_damage > 0:
        call mend.aggravated from new_night_standard_agg_mend

    "It's a new night. That means new opportunities and new dangers. {i}What fresh hell{/i} indeed. (Events should be processed here?)"

    $ state.hunted_tonight = False
    $ hungrier = state.rouse_check()
    $ can_hunt = (pc.hunger > cfg.HUNGER_MIN) or (pc.humanity < cfg.KILLHUNT_HUMANITY_MAX and pc.hunger > cfg.HUNGER_MIN_KILL)

    if hungrier and can_hunt:
        beast "Wake. Up. We need to feed."

    return


label mend:

    label .superficial:

        "Kindred can recover from almost anything, given enough blood and time."

        "You channel stolen life into your wounds, willing away your injuries."

        python:
            hungrier = store.state.rouse_check(1)
            store.state.pc.hp.mend(cfg.DMG_SPF, 1)

        return

    label .aggravated:

        "Kindred can recover from almost anything, given enough blood and time."

        "But the Kindred also have {i}banes{/i} - threats that cut to the core of their unnatural life, defy the vampiric power of mending..."

        "...and leave lasting physical and spiritual trauma. And yet, here you are."

        "You've experienced this kind of existential agony firsthand, and survived."

        menu:
            "\"This too shall pass.\" If you can pay the staggering cost in time and Blood."

            "I force the Blood to mend my scarred, ravaged form, even at the risk of terrible Hunger.":
                python:
                    store.state.clock.advance(1)
                    hungrier = store.state.rouse_check(num_checks=3)
                    store.state.pc.hp.mend(cfg.DMG_AGG, 1)

                "It feels like half an eternity, spent in a limbo of pain and delirium."

                "But eventually it's over, and in reality it's been about an hour."

                if hungrier:
                    "The Hunger stabs its tendrils into your brain, making your head pound and your gums throb. But you're a bit closer to being whole."

                    beast "TIME TO FEED, \"FRIEND\". Time. To. Fucking. Feed."
                else:
                    "Incredibly, you don't even feel any hungrier than before. Perhaps later you ought to ponder the meaning of such good fortune."

                    beast "Don't say I never did anything for you, dear friend."

            "I can't risk losing control now. I'll have to bear the pain for the time being.":

                beast "...Careful, now."

        return

    return
