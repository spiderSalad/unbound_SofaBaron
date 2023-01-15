default state.pc                    = None
default state.diceroller            = None
default state.clock                 = None

default state.outside_haven         = True
default state.night                 = 0
default state.hours_left            = 12
default state.first_hunt            = False
default state.daybreak              = False
default state.overtime              = 0

default state.tried_hunt_tonight    = False
default state.hunted_tonight        = False
default state.mended_agg_tonight    = False

default state.intro_man_drank       = False
default state.intro_man_killed      = False
default state.intro_pt_disc_dot     = None

default state.clan_chosen           = False
default state.clan_nickname         = None
default state.clan_slur             = None
default state.predator_type_chosen  = False
default state.siren_type_chosen     = False
default state.siren_orientation     = None
default state.starting_disc_dots    = False
default state.ventrue_palate        = None

default state.pc_car                = "old Toyota Camry"

default state.innocent_killed       = False
default state.innocent_drained      = False

default state.opinions              = {}
default state.masquerade            = 60  # 0 - 100
default state.notoriety             = 6

default state.pc_cash               = 250.00
default state.roll_bonus            = 0
default state.roll_malus            = 0
default state.blood_surge_enabled   = False
default state.blood_surge_active    = False

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
default state.cum_intensity_weights = store.utils.get_cum_weights(state.rint_weights)
# [(rw8 + state.rint_weights[i-1] if i > 0 else rw8) for i, rw8 in enumerate(state.rint_weights)]


init 1 python in state:
    # pc = None
    cfg, utils = renpy.store.cfg, renpy.store.utils

    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]

    from store.game import Supply, Weapon, Inventory

    # pc = renpy.store.game.PlayerChar(anames=attr_names, snames=skill_names, dnames=discipline_names)

    def available_pc_will():
        return pc.will.boxes - (pc.will.spf_damage + pc.will.agg_damage)

    def pc_can_drink_swill():
        if pc.clan == cfg.CLAN_VENTRUE:
            return False
        if pc.blood_potency > 4:
            return False
        if pc.blood_potency > 2 and cfg.POWER_ANIMALISM_SUCCULENCE not in pc.disciplines.pc_powers[cfg.DISC_ANIMALISM]:
            return False
        return True

    def pc_can_drink_swill_with_effort():
        if pc_can_drink_swill():
            return True
        elif pc.clan == cfg.CLAN_VENTRUE:
            if pc.blood_potency > 4:
                return False
            if pc.blood_potency > 2 and cfg.POWER_ANIMALISM_SUCCULENCE not in pc.disciplines.pc_powers[cfg.DISC_ANIMALISM]:
                return False
            return True
        return False

    def set_hunger(delta, killed=False, innocent=False, ignore_killed=False):
        previous_hunger, hunger_floor = pc.hunger, cfg.HUNGER_MIN_KILL if killed or ignore_killed else cfg.HUNGER_MIN
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

    def masquerade_breach(base=10):
        global masquerade
        prev_masq = masquerade
        notoriety_mult = cfg.VAL_BASE_NOTORIETY_MULTIPLIER + (float(notoriety) / 100)
        base_breach_damage = float(utils.random_int_range(base, int(base * 1.5)))
        masquerade_damage = notoriety_mult * base_breach_damage
        masquerade -= int(masquerade_damage)
        utils.log("Masquerade breach: {:5.2f} damage, sending it from {:5.2f} to {:5.2f}. Notoriety effect was {:7.4f} * {:5.2f}.".format(
            masquerade_damage, prev_masq, masquerade, notoriety_mult, base_breach_damage
        ))

    def masquerade_redemption(amount=10):
        global masquerade
        masquerade += amount
        if masquerade > cfg.VAL_MASQUERADE_MAX:
            overfill = masquerade - cfg.VAL_MASQUERADE_MAX
            give_item(Supply(Supply.IT_MONEY, name="Masquerade Bucks", quantity=overfill))  # TODO: change this to rep gain later

    def feed_resonance(intensity=None, reso=None, boost: int = 0):
        if not intensity:
            i, intensity = utils.get_wrs_adjusted(reson_intensity_table, boost, cum_weights=cum_intensity_weights)
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

    def spend_resonance(reso, amount):
        if reso == cfg.RESON_VARIED:
            amount = int(amount / 6)
            for rpool in resonances:
                if resonances[rpool] < amount:
                    raise ValueError("User shouldn't have been allowed to spend more resonance than they had.")
                resonances[rpool] -= abs(amount)
        else:
            resonances[reso] -= abs(amount)

    def buy_next_disc_level(dname, reso, amount):
        pc.disciplines.set_discipline_level(dname, "+=1")
        spend_resonance(reso, amount)

    def meet_next_level_reqs(dname, access_token):
        if intro_pt_disc_dot and dname in intro_pt_disc_dot:
            return (True, 0,
                "We could have this power {i}now{/i}, without spending resonance.",
                "Allocate free discipline dot to {}?".format(dname)
            )
        disc_resonance = cfg.REF_DISC_BLURBS[dname][cfg.REF_RESONANCE]
        access_mod = cfg.REF_DISC_ACCESS[access_token]
        next_lvl_xp = cfg.VAL_DISC_XP_REQS[min(pc.disciplines.levels[dname], cfg.MAX_SCORE - 1)]
        if disc_resonance == cfg.RESON_VARIED:
            # TODO: implement
            raise NotImplemented("This should only apply to Thinblood Alchemy, which is not implemented.")
        xp_next = next_lvl_xp * (1 / access_mod)
        if resonances[disc_resonance] >= xp_next:
            tt_addendum = "Like a mosquito ready to lay eggs, our Blood is pregnant with the resonance "
            tt_addendum += "of stolen moments, from which new powers could be born."
            return (True, xp_next, tt_addendum,"Spend {} {} resonance to gain a dot in {}?".format(xp_next, disc_resonance, dname))
        return (False, 0, "(Locked - feed on more {} resonance.)".format(disc_resonance), None)


    class GameClock:
        MAX_HOURS_PER_NIGHT = 12

        def __init__(self, day: int = None, hours: int = None, **kwargs):
            self._night = day or 1
            self._hours = hours or 9
            self.overtime = 0
            self.posted_night = None
            self.posted_hours = None
            self.update()

        @property
        def night(self):
            return self._night

        @property
        def hours(self):
            return self._hours

        def update(self):
            self.posted_night = self.night
            self.posted_hours = self.hours

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

    def get_call_stack_str():
        stack = renpy.get_return_stack()
        stack_str = "CALL STACK:\n\n"
        if len(stack) <= 0:
            return stack_str + "(empty)"
        for i, stack_layer in enumerate(stack):
            stack_str += "{}. {}\n".format(i+1, stack_layer)
        return stack_str

    def give_item(supply: Supply, copy=True, gift_sound=True):
        if pc.inventory is None:
            raise ValueError("No valid inventory to add items to.")
        gift = supply.copy() if copy else supply
        pc.inventory.add(gift)
        if gift_sound:
            if gift.item_type == Supply.IT_FIREARM:
                renpy.play(renpy.store.audio.sound.get_item_1_gun, "sound")
            else:
                renpy.play(renpy.store.audio.sound.get_item_2, "sound")

    def take_item(ikey=None, itype=None, intended=False):
        pc.inventory.lose(ikey=ikey, itype=itype, intended=intended)

    def lose_cash(amount):
        pc.inventory.lose(cash_amount=amount, intended=False)

    def spend_cash(amount):
        pc.inventory.lose(cash_amount=amount, intended=True)


label pass_time(hours_passed, in_shelter=False):

    $ state = store.state

    if hours_passed is None:
        $ state.overtime, state.daybreak = state.clock.next_night()
    else:
        $ state.overtime, state.daybreak = state.clock.advance(hours_passed)

    return


label sun_threat:

    # TODO: add bg for this

    "It's getting light out."

    "{i}Too{/i} light. What time is it?"

    play sound audio.sun_threat_1

    beast "You idiot. You goddamned fool. YOU ABSOLUTELY WORTHLESS BRAINDEAD FUCKING-"

    scene bg sunrise sky with dissolve

    beast "THE SUUUUUUUUUUUN THE SUUUUUN THE SUUUN THE SUN SUN SUN SUN SUN SUN SUN"

    # TODO: add some effects here

    label .shelter_search(short_notice=True, roll_bonus=0):
        python:
            search_pool = "dexterity+athletics/wits+streetwise/composure+traversal"
            if roll_bonus and roll_bonus > 0:
                search_pool += "+{}".format(int(roll_bonus))

        call roll_control(search_pool, "diff0", pool_mod=roll_bonus) from sunburn_damage

        python:
            death_save, min_burn = _return.margin, 2 if short_notice else 0
            sunburn = utils.random_int_range(0, 10)
            sun_damage = max(min_burn, sunburn - death_save)
            state.deal_damage(cfg.TRACK_HP, cfg.DMG_AGG, sun_damage, source=cfg.COD_SUN)

        # If the sun kills the PC this shouldn't be reached.
        if sun_damage < 1:
            "Somehow you make it to shelter unscathed."
        else:
            # TODO: add sound effect here

            beast "AAAAAAAAAAAAAAAAAAAAAAAA"

            "The sun blazes with hateful light. Blinded and burning, you flee in a Beast driven panic."

            "Thinking back later, you wonder. Were you guided by the uncanny instinct of your Beast? Or did what was left of your rational mind prevail?"

            "And where the hell are you, anyway?"

            "The answers to those questions might matter later, but they don't matter now."

            "The only thing that matters now is that you made it to shelter. You collapse in a charred heap as the daysleep takes you."

            $ state.masquerade_breach(base=utils.random_int_range(1, 20))

    # call new_night from sun_threat_event

    return sun_damage


label new_night:

    python:
        state.daybreak = False
        state.hunted_tonight = False
        state.tried_hunt_tonight = False
        state.mended_agg_tonight = False

    if pc.hp.agg_damage > 0:
        call mend.aggravated from new_night_standard_agg_mend

    if state.outside_haven:
        "When you awaken, it takes you a moment to remember where you are."

    "It's a new night. New opportunities, new dangers. {i}What fresh hell{/i} indeed."

    # TODO: process events?

    call roll_control.rouse_check() from new_night_rouse_check

    $ hungrier = _return
    $ can_hunt = (pc.hunger > cfg.HUNGER_MIN) or (pc.humanity < cfg.KILLHUNT_HUMANITY_MAX and pc.hunger > cfg.HUNGER_MIN_KILL)

    if hungrier and can_hunt and not state.mended_agg_tonight:
        beast "Wake. Up. We need to feed."
    elif hungrier and can_hunt:
        beast "Pull your carcass off the floor and get hunting! Chop. Chop."

    return


label mend:

    label .superficial:

        "Kindred can recover from almost anything, given enough blood and time."

        "You channel stolen life into your wounds, willing away your injuries."

        call roll_control.rouse_check(1) from mend_spf_rouse_check

        python:
            hungrier = _return
            spf_hp_mend = 1 # TODO: adjust for Blood Potency
            store.state.pc.hp.mend(cfg.DMG_SPF, spf_hp_mend)

        return

    label .aggravated:

        "Kindred can recover from almost anything, given enough blood and time."

        "But the Kindred also have {i}banes{/i} - threats that cut to the core of their unnatural life, defy the vampiric power of mending..."

        "...and leave lasting physical and spiritual trauma. And yet, here you are."

        "You've experienced this kind of existential agony firsthand, and survived."

        menu:
            "\"This too shall pass.\" If you can pay the staggering cost in time and Blood."

            "I force the Blood to mend my scarred, ravaged form, even at the risk of terrible Hunger.":
                call roll_control.rouse_check(num_checks=3) from mend_agg_rouse_check

                python:
                    hungrier = _return
                    state.mended_agg_tonight = True
                    store.state.clock.advance(1)
                    store.state.pc.hp.mend(cfg.DMG_AGG, 1)

                "It feels like half an eternity, spent in a limbo of pain and delirium."

                "But eventually it's over, and in reality it's been about an hour."

                if hungrier:
                    "The Hunger stabs its talons into your brain, making your head pound and your gums throb. But you're a bit closer to being whole."

                    beast "TIME TO FEED, \"FRIEND\". Time. To. Fucking. Feed."
                else:
                    "Incredibly, you don't even feel any hungrier than before. Perhaps later you ought to ponder the meaning of such good fortune."

                    beast "Don't say I never did anything for you."

            "I can't risk losing control now. I'll have to bear the pain for the time being.":

                beast "...Careful, now."

        return

    return
