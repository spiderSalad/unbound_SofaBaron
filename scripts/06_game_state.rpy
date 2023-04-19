default state.pc                    = None
default state.diceroller            = None
default state.arena                 = None
default state.clock                 = None

default state.first_hunt            = False
default state.daybreak              = False
default state.overtime              = 0

default state.outside_haven         = True
default state.indoors               = False
default state.in_combat             = False
default state.menu_label_backref    = None

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
default state.pc_laptop             = "old ASUS"

default state.prey                  = "None (a ya bidness)"
default state.innocent_killed       = False
default state.innocent_drained      = False
default state.killshelter_frenzy    = False
default state.hunger_b4_last_feeding= None
default state.current_hunt_type     = None
default state.hunt_locale          = ""
default state.baseline_hunt_diff    = cfg.VAL_BASE_HUNTING_DIFF  # + ...?

default state.opinions              = {}
default state.masquerade            = 60  # 0 - 100
default state.notoriety             = 6
default state.self_help_unlocked    = False
default state.sorties_unlocked      = False

default state.pc_cash               = 250.00
default state.roll_bonus            = 0
default state.roll_malus            = 0
default state.theoretical_sitmod    = 0
default state.current_plan          = None
default state.updated_pool          = ""
default state.last_power_used       = None
default state.blood_surge_enabled   = False
default state.blood_surge_active    = False
default state.mended_this_turn      = False
default state.used_disc_this_turn   = False
default state.fleet_dodge_this_turn = False

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
default state.cum_intensity_weights = store.utils.get_cum_weights(*state.rint_weights)
# [(rw8 + state.rint_weights[i-1] if i > 0 else rw8) for i, rw8 in enumerate(state.rint_weights)]


init 1 python in state:
    # pc = None
    cfg, utils, devtest = renpy.store.cfg, renpy.store.utils, renpy.store.devtest

    gdict = cfg.__dict__
    attr_names = [getattr(cfg, aname) for aname in gdict if str(aname).startswith("AT_")]
    skill_names = [getattr(cfg, sname) for sname in gdict if str(sname).startswith("SK_")]
    discipline_names = [getattr(cfg, dname) for dname in gdict if str(dname).startswith("DISC_")]

    from store.game import Item, Weapon, Inventory, Entity, MortalPrey

    # pc = renpy.store.game.PlayerChar(anames=attr_names, snames=skill_names, dnames=discipline_names)

    def unspent_will(who):
        return who.will.undamaged

    def available_will(who):
        return who.will.spendable

    def unspent_pc_will():
        return unspent_will(pc)

    def available_pc_will():
        return available_will(pc)

    def pc_can_drink_swill():  # Regularly, that is.
        if pc.clan == cfg.CLAN_VENTRUE:
            return False
        has_animal_succulence = pc.has_disc_power(cfg.POWER_ANIMALISM_SUCCULENCE, cfg.DISC_ANIMALISM)
        return utils.get_feeding_penalty_swill(pc.blood_potency, has_animal_succulence) > 0

    def pc_can_drink_swill_using_willpower():  # No reason to call this for non-Ventrue.
        if not pc.clan or pc.clan != cfg.CLAN_VENTRUE:
            return pc_can_drink_swill()
        return pc_can_drink_swill() and (available_pc_will() >= utils.get_bane_severity(pc.blood_potency))

    def weapon_is_ranged(weapon):
        if not weapon:
            return False
        if weapon.item_type == Item.IT_FIREARM:
            return True
        if hasattr(weapon, "throwable") and weapon.throwable:
            return True
        return False

    def holding_ranged_weapon(who=None, check_alt=False):
        if who is None:
            who = pc
        if hasattr(who, "inventory") and who.inventory:
            held_weapon = who.inventory.equipped[Inventory.EQ_WEAPON]
            alt_weapon = who.inventory.equipped[Inventory.EQ_WEAPON_ALT]
            if held_weapon and weapon_is_ranged(held_weapon):
                return True
            if check_alt and alt_weapon and weapon_is_ranged(alt_weapon):
                return True
        if hasattr(who, "npc_weapon") and who.npc_weapon:
            if weapon_is_ranged(who.npc_weapon):
                return True
        if hasattr(who, "intrinsic_ranged_attack") and who.intrinsic_ranged_attack:
            return True
        return False

    def pc_has_ranged_attack_power():
        return False  # TODO: add this

    def pc_has_ranged_attack(check_alt=False):
        return (holding_ranged_weapon(check_alt=check_alt) or pc_has_ranged_attack_power())

    def refresh_hunger_ui():
        if pc.hunger > cfg.HUNGER_MAX_CALM:
            renpy.show_screen(_screen_name="hungerlay", _layer = "hunger_layer", _tag = "hungerlay", _transient = False)
        else:
            renpy.hide_screen("hungerlay", "master")

    def set_hunger(delta, killed=False, innocent=False, ignore_killed=False):
        previous_hunger, hunger_floor = pc.hunger, cfg.HUNGER_MIN_KILL if killed or ignore_killed else cfg.HUNGER_MIN
        new_hunger = utils.nudge_int_value(pc.hunger, delta, "Hunger", floor=hunger_floor, ceiling=7)
        pc.hunger, slaked_hunger = new_hunger, 0
        if pc.hunger > previous_hunger:
            renpy.play(renpy.store.audio.beastgrowl1, "sound")
        else:
            global hunger_b4_last_feeding
            hunger_b4_last_feeding = previous_hunger
            slaked_hunger = previous_hunger - pc.hunger
        if killed and innocent:
            set_humanity("-=1")
        refresh_hunger_ui()


    def set_humanity(delta):
        new_humanity = utils.nudge_int_value(pc.humanity, delta, "Humanity", floor=cfg.MIN_HUMANITY, ceiling=cfg.MAX_HUMANITY)
        pc.humanity = new_humanity

    def deal_damage(tracker, dtype, amount, target: Entity = None, source=None):
        dmg_target = pc if target is None else target
        print("\ndtype = {}, amount = {}, tracker = {}".format(dtype, amount, target))
        if tracker == cfg.TRACK_HP:
            return dmg_target.hp.damage(dtype, amount, source=source)
        else:
            return dmg_target.will.damage(dtype, amount, source=source)

    def mend_damage(who, tracker, dtype, amount):
        if who is None:
            who = pc
        if tracker == cfg.TRACK_HP:
            return who.hp.mend(dtype, amount)
        else:
            return who.will.mend(dtype, amount)

    def new_prey(pronoun_set=None):
        global prey
        prey = None
        # if prey:
        # del prey
        # global prey
        # prey = None
        prey = MortalPrey(pronoun_set=pronoun_set)
        print("global prey defined as: {}, renpy.store.state.prey = {}".format(prey, renpy.store.state.prey))
        # TODO: this still isn't working 4/24/23

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
            give_item(Item(Item.IT_MONEY, name="Masquerade Bucks", quantity=overfill))  # TODO: change this to rep gain later

    def nightly_event_handler():
        global masquerade, notoriety
        prev_masq, prev_notor = masquerade, notoriety
        masquerade += utils.random_int_range(-5, 5)
        masquerade = min(cfg.VAL_MASQUERADE_MAX, max(cfg.VAL_MASQUERADE_MIN, masquerade))
        if notoriety < 30:
            notoriety -= (1 if utils.percent_chance(35) else 0)
        notoriety = min(cfg.VAL_NOTORIETY_MAX, max(cfg.VAL_NOTORIETY_MIN, notoriety))
        utils.log("Nightly shift: Masquerade change from {:5.2f} to {:5.2f}. Notoriety change from {:7.4f} to {:7.4f}".format(
            prev_masq, masquerade, prev_notor, notoriety  # TODO: left off here (Apr 8)!! TODO
        ))
        if cfg.DEV_MODE and devtest.DEV_DAY_NIGHT_TEST:
            devtest.test_night_cycle()

    def feed_resonance(intensity=None, reso=None, boost: int = 0):
        if not intensity:
            i, intensity = utils.get_wrs_adjusted(reson_intensity_table, boost, cum_weights=cum_intensity_weights)
        amount = utils.random_int_range(int(intensity * 0.8), int(intensity * 1.2))
        if not reso and intensity == cfg.RINT_BALANCED:
            reso = cfg.RESON_VARIED
        elif not reso:
            reso = utils.get_random_list_elem(resonance_types) #[0]
            if reso == cfg.RESON_ANIMAL:  # Don't give animal resonance unless specified.
                reso = cfg.RESON_VARIED
        elif type(reso) in (list, tuple):
            reso = utils.get_random_list_elem(resonance_types) #[0]

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
            raise NotImplementedError("This should only apply to Thinblood Alchemy, which is not implemented.")
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

    def is_their_turn(who):
        if not in_combat or not arena:
            return False
        return arena.get_up_next() is who

    def switch_weapons(who=None, play_sound=True, reload_menu=False, as_effect=False):
        if who is None:
            who = pc
        if in_combat and not as_effect and (not arena or arena.get_up_next() is not who):
            return utils.log("Can only switch weapons in combat if it's your turn, \"{}\".".format(who.name))
        if hasattr(who, "inventory") and type(who.inventory) is Inventory:
            held_weapon, off_weapon = who.inventory.equipped[Inventory.EQ_WEAPON], who.inventory.equipped[Inventory.EQ_WEAPON_ALT]
            who.inventory.equipped[Inventory.EQ_WEAPON] = off_weapon
            who.inventory.equipped[Inventory.EQ_WEAPON_ALT] = held_weapon
        elif hasattr(who, "npc_weapon") and hasattr(who, "npc_weapon"):
            held_weapon, off_weapon = who.npc_weapon, who.npc_weapon_alt
            who.npc_weapon = off_weapon
            who.npc_weapon_alt = held_weapon
        else:
            return utils.log("An NPC can only switch weapons if they have an Inventory or the npc_weapon/alt attributes.")
        if play_sound:
            if off_weapon.item_type == Item.IT_FIREARM:
                shuffle_sound = renpy.store.audio.get_item_1_gun
            else:
                shuffle_sound = renpy.store.audio.get_item_2
            renpy.play(shuffle_sound, "sound")
        if reload_menu and who is pc and menu_label_backref:
            renpy.jump(menu_label_backref)

    def give_item(supply, *supplies, copy=True, equip_it=False, gift_sound=True):
        if pc.inventory is None:
            raise ValueError("No valid inventory to add items to.")
        gift = supply.copy() if copy else supply
        pc.inventory.add(gift)
        if supply.item_type in [Item.IT_FIREARM, Item.IT_WEAPON] and equip_it:
            pc.inventory.equip(gift, force=True)
        if gift_sound:
            if gift.item_type == Item.IT_FIREARM:
                renpy.play(renpy.store.audio.get_item_1_gun, "sound")
            else:
                renpy.play(renpy.store.audio.get_item_2, "sound")

    def take_item(ikey=None, itype=None, intended=False):
        pc.inventory.lose(ikey=ikey, itype=itype, intended=intended)

    def lose_cash(amount):
        pc.inventory.lose(cash_amount=amount, intended=False)

    def spend_cash(amount):
        pc.inventory.lose(cash_amount=amount, intended=True)

    def apply_test_build(backstory, clan, pred_type, pt_disc):
        pc.mortal_backstory = backstory
        pc.apply_background(cfg.CHAR_BACKGROUNDS[pc.mortal_backstory], bg_key=pc.mortal_backstory)
        pc.choose_clan(clan)
        clan_chosen = True
        pc.choose_predator_type(pred_type, pt_disc)


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

        call roll_control(search_pool, "diff0", situational_mod=roll_bonus) from sunburn_damage

        python:
            death_save, min_burn = _return.margin, 2 if short_notice else 0
            sunburn = utils.random_int_range(0, 10)
            sun_damage = max(min_burn, sunburn - death_save)
            state.deal_damage(cfg.TRACK_HP, cfg.DMG_AGG, sun_damage, source=cfg.COD_SUN)

        # If the sun kills the PC this shouldn't be reached.
        if sun_damage < 1:
            "Somehow you make it to shelter unscathed."
        else:
            play audio audio.sun_threat_2_burn
            play sound audio.fleeing_footsteps1
            queue sound audio.body_fall4

            beast "AAAAAAAAAAAAAAAAAAAAAAAA"

            "The sun blazes with hateful light. Blinded and burning, you flee in a Beast driven panic."

            "Thinking back later, you wonder. Were you guided by the uncanny instinct of your Beast?"

            "Or did what was left of your rational mind prevail?"

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
        state.nightly_event_handler()

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
        beast "Pull your carcass off the floor and get hunting! Chop. {i}Chop.{/i}"

    if cfg.DEV_MODE:
        call dev_tests.test_nightly_encounter_roulette from hub_dev_test_option_nightly_1

    return


label mend:

    label .superficial:

        if utils.percent_chance(0.45):
            "Kindred can recover from almost anything, given enough blood and time."

            "You channel stolen life into your wounds, willing away your injuries."
        else:
            "There's no time to waste, but fortunately you can multitask."

            "Your flesh begins to knit itself back together, bones heave and pop back into place..."

        call roll_control.rouse_check(1) from mend_spf_rouse_check

        play sound audio.mending_1

        python:
            hungrier = _return
            spf_hp_mend = utils.get_bp_mend_value(pc.blood_potency)
            store.state.mend_damage(None, cfg.TRACK_HP, cfg.DMG_SPF, spf_hp_mend)
            # store.state.pc.hp.mend(cfg.DMG_SPF, spf_hp_mend)

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
                    store.state.mend_damage(None, cfg.TRACK_HP, cfg.DMG_AGG, 1)
                    # store.state.pc.hp.mend(cfg.DMG_AGG, 1)

                "It feels like half an eternity, spent in a limbo of pain and delirium."

                "But eventually it's over, and in reality it's been about an hour."

                if hungrier:
                    "Hunger stabs its talons into your brain, making your head pound and your gums throb."

                    "But you're a bit closer to being whole."

                    beast "TIME TO FEED, \"FRIEND\". Time. To. Fucking. Feed."
                else:
                    "Incredibly, you don't even feel any hungrier than before. Perhaps later you'll to ponder the meaning of such good fortune."

                    beast "Don't say I never did anything for you."

            "I can't risk losing control now. I'll have to bear the pain for the time being.":

                beast "...Careful, now."

        return

    return
