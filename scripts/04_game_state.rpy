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

default state.resonances            = {
    cfg.RESON_ANIMAL: 50,
    cfg.RESON_CHOLERIC: 100,
    cfg.RESON_MELANCHOLIC: 60,
    cfg.RESON_PHLEGMATIC: 80,
    cfg.RESON_SANGUINE: 70,
    cfg.RESON_EMPTY: 90
}

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
        new_hunger = utils.nudge_int_value(pc.hunger, delta, "Hunger", floor=cfg.HUNGER_MIN_KILL if killed else cfg.HUNGER_MIN, ceiling=7)
        pc.hunger = new_hunger
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
    $ death_save = _return.margin
    $ sunburn = utils.random_int_range(0, 10)
    $ state.deal_damage(cfg.TRACK_HP, cfg.DMG_AGG, max(2, sunburn - death_save), source=cfg.COD_SUN)

    call new_night from sun_threat_event

    return


label new_night:

    "New night, new opportunities (Events should be processed here?)"

    $ state.hunted_tonight = False
    $ hungrier = state.rouse_check()

    if hungrier:
        beast "Wake. Up. We need to feed."

    return
