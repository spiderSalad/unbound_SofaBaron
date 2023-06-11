init 1 python in flavor:
    game = renpy.store.game
    V5DiceRoll = game.V5DiceRoll

    fed_on_human_generic = {
        V5DiceRoll.RESULT_MESSY_CRIT: [
            "You find yourself standing over the dead body of {DESC_INDEF_ARTIC}. {CAP_PN_SHES_HES_THEYRE} already growing cold."
        ],
        "drained": [
            "You drink your fill of {PN_HER_HIM_THEM}, basking in warm contentment, and leave the body for your future self to worry about.",
            "That went great, except for the exsanguinated {CAP_DESC_NO_ARTIC} lying dead at your feet. That could be a problem.",
            "You find yourself standing over the dead body of {DESC_INDEF_ARTIC}. {CAP_PN_SHES_HES_THEYRE} already growing cold."
        ],
        "four_slaked": [
            "You drink your fill. Your prey will live, assuming someone notices {PN_HER_HIM_THEM} in time.",
            "You take a deep, satisfying drink. When you're finished, you look {PN_HER_HIM_THEM} over. You think there's a decent chance {PN_SHELL_HELL_THEYLL} live."
        ],
        "three_slaked": [
            "You drink your fill, and leave your prey in a daze. {CAP_PN_SHELL_HELL_THEYLL} be fine, assuming someone notices {PN_HER_HIM_THEM} in time.",
            "You lose yourself in the Kiss, drinking deep of {PN_HER_HIS_THEIR} life's blood. You've taken more than you probably should have, but not so much that {PN_SHE_HE_THEY} can't recover."
        ],
        "two_slaked_low_humanity": [
            "You drink deeply, but not so deeply that your prey won't recover."
        ],
        "two_slaked_high_humanity": [
            "You drink deeply, but not {{i}}too{{/i}} deeply. {CAP_PN_SHELL_HELL_THEYLL} be fine with some rest and a good meal."
        ],
        "one_slaked": [
            "You take a few good gulps; just enough to take the edge off before you have to split."
        ]
    }

    hunt_failed_human_generic = {
        "prey_fled_1": [
            "That could have gone better. You fail to feed, but you {{i}}think{{/i}} you managed a clean escape.",
            "At this rate you're going to be sent to bed with no dinner.",
            "Tonight just might not be your night."
        ],
        "prey_fled_2":[
            "With any luck, {PN_SHELL_HELL_THEYLL} mistake your attack for a regular mugging or assault.",
            "{CAP_PN_SHE_HE_THEY} didn't see your fangs. You're pretty sure of that. But you need to be careful.",
            "You need to be careful. You're playing Russian roulette with the Masquerade every time you let prey escape like that."
        ],
        "beastfail": []
    }

    fed_on_bagged = {
        "two_slaked": [
            "Relief, at last. But that's all. No flavor, no kick, no pathos, no {{i}}life{{/i}}. Just relief from the Hunger. For now.",
            "Your Hunger subsides as the cold, dead blood pours down your throat."
        ],
        "one_slaked": [
            "It's cold and lifeless, but it quenches the Hunger a bit. Almost like a numbing salve.",
            "Is there such a thing as \"empty calories\" for vampires? That's what drinking this stuff feels like."
        ],
        "zero_slaked": [  # You could theoretically hunt for bagged blood with a Blood Potency higher than 2.
            "Nothing... Nothing!",
            "This isn't going to do it for you. And you don't think it's just a bad batch.",
            "Burning tendrils of Hunger creep through your veins, behind your eyes, in your gut. Nothing's changed."
        ],
        "zero_slaked_beast": ["Not. Good enough.", "You seem like you could use some help. Why don't I take over?", "..."]
    }

    fed_on_animal = {  # TODO: Add separate entries for Animal Succulence?
        "two_slaked": [
            "There's flavor here. There's life. But it's {{i}}faint{{/i}}, somehow. Or maybe distorted? Incompatible, somehow. But your Hunger {{i}}does{{/i}} recede.",
            "You feel like there should be {{i}}more{{/i}} to this, somehow. They struggled. Feared. Hoped. In their own way. But there's a disconnect. Still, the Hunger fades."
        ],
        "one_slaked": [
            "It's not flavorless. Just the opposite, in fact. There's a musky taste to it. Something reminiscent of human fear, but {{i}}off{{/i}}. Faint. Unsatisfying.",
            "You taste the now-familiar animal musk of the blood, a rank, tangy, heady brew that effervesces away into nothing, satisfying just a bit of your Hunger."
        ],
        "zero_slaked": [  # Ditto animal blood.
            "Nothing... Nothing!",
            "You don't think sucking on rats is going to work. Not anymore. You need something stronger.",
            "Animal blood has lost what little flavor it had. You can't drink this shit anymore."
        ],
        "zero_slaked_beast": ["Not. Good enough.", "You seem like you could use some help. Why don't I take over?", "..."]
    }

label hunting_outcome_generic_sub(*args):

    label .planning_win:
        $ state.roll_bonus, state.roll_malus = state.active_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        $ prey_ref_1C = state.prey.desc_indef_artic.capitalize()
        # $ what_they_were_doing = flavor.what_they_were_doing()

        "You manage to case the area and pick out a suitable target. [prey_ref_1C], [state.prey.was_doing]. Things ought to go smoothly from here."

        call hunting_tl_plan_success_post(time_spent) from human_gen_plan_phase_win

        return time_spent

    label .planning_fail:
        $ state.roll_malus, state.roll_bonus = abs(state.active_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)

        call hunting_tl_plan_failure_post(time_spent) from human_gen_plan_phase_fail

        return time_spent

    label .strike_messycrit:
        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        python:
            state.set_hunger(0, killed=True, innocent=True)
            state.feed_resonance(boost=1)
            you_feed = flavor.flav("fed_on_human_generic", "drained", subject=state.prey)

        "[you_feed]"

        "Your Hunger is sated - completely, for once. But now you have a different problem."

        call .drained_victim from strike_messycrit_drain

        stop sound
        play sound audio.body_fall1

        return

    label .strike_crit:
        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        if pc.humanity > cfg.KILLHUNT_HUMANITY_MAX:
            $ drained = False
        else:
            call hunt_kill_choice from hunt_generic_crit
            $ drained = _return

        python:
            you_feed, you_feed_ps = "", ""
            if drained:
                state.set_hunger(0, killed=True, innocent=True)  # TODO: add innocence check
                state.feed_resonance(boost=2)
                you_feed = flavor.flavor_format(flavor.fed_on_human_generic["drained"], subject=state.prey)
            # "That went great, except for the exsanguinated [prey_ref_2] lying dead at your feet. That could be a problem."
            else:
                state.set_hunger("-=2")
                state.feed_resonance(boost=1)
                hft_addendum = "_low_humanity" if pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX else "_high_humanity"
                you_feed, you_feed_ps = "That could hardly have gone better.", flavor.flavor_format(flavor.fed_on_human_generic["two_slaked" + hft_addendum], subject=state.prey)

        "[you_feed]"
        if you_feed_ps:
            "[you_feed_ps]"

        stop sound
        if drained:
            play sound audio.body_fall1

        return

    label .strike_win:
        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        if temp_margin > 2 and pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX:
            call hunt_kill_choice from hunt_generic_win
            $ drained = _return

        python:
            max_slaked = 2
            if drained:
                max_slaked = 5
            elif pc.humanity > cfg.KILLHUNT_HUMANITY_MAX:
                humanity_limit = cfg.KILLHUNT_HUMANITY_MAX + 4 - pc.humanity
                max_slaked = min(4, max(2, humanity_limit))  # Should always be 2-4 inclusive.
                utils.log("Max hunger slaked for this hooman feeding is {}.".format(max_slaked))
            slaked_hunger = min(max_slaked, 1 + int(temp_margin))
            state.set_hunger("-={}".format(slaked_hunger), killed=drained, innocent=True)  # TODO: add innocence check
            her_him_them = state.prey.pronoun_set.PN_HER_HIM_THEM
            shell_hell_theyll = state.prey.pronoun_set.PN_SHELL_HELL_THEYLL
            shell_hell_theyll_C = shell_hell_theyll.capitalize()
            you_feed, you_feed_ps = "", ""

        if drained:
            $ you_feed = flavor.flav("fed_on_human_generic", "drained", subject=state.prey)
            $ state.feed_resonance(boost=1)
        else:
            python:
                slaked_str = cfg.SCORE_WORDS[slaked_hunger]
                humanity_suffix = "_low_humanity" if pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX else "_high_humanity"
                you_feed = flavor.flav("fed_on_human_generic", "{}_slaked{}".format(slaked_str, humanity_suffix if slaked_hunger == 2 else ""), subject=state.prey)
                if slaked_hunger < 2:
                    state.feed_resonance(boost=-1)
                else:
                    state.feed_resonance()
                if slaked_hunger == 2 and utils.percent_chance(15):
                    you_feed_ps = "...Assuming no one else feeds from {} in the next few weeks.".format(state.prey.pronoun_set.PN_HER_HIM_THEM)

        "[you_feed]"
        if you_feed_ps:
            "[you_feed_ps]"

        stop sound
        if drained:
            play sound audio.body_fall1

        return

    label .strike_fail:
        $ shell_hell_theyll = state.prey.pronoun_set.PN_SHELL_HELL_THEYLL

        play sound audio.fleeing_footsteps1

        $ failure_line_1 = flavor.flav("hunt_failed_human_generic", "prey_fled_1", subject=state.prey)
        $ failure_line_2 = flavor.flav("hunt_failed_human_generic", "prey_fled_2", subject=state.prey)

        "[failure_line_1]"

        "[failure_line_2]"

        return

    label .strike_beastfail:
        call hunting_tl_strike_bestial_failure from hunting_outcome_generic_bf

        return

    label .drained_victim:

        if pc.hunger < 1:
            beast "{i}Ahh...{/i} Well done, friend. Well done. Doesn't that feel so much {i}better{/i}? We should do this more often."
        elif pc.hunger < cfg.HUNGER_MAX_CALM:
            beast "Satisfying... almost."
        else:
            "And even after taking a life some Hunger remains. That's not good."

        return


label hunting_outcome_bloodbag_sub(*args):

    label .planning_win:

        $ state.roll_bonus, state.roll_malus = state.active_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        $ planning_went_well = True

        "So far, so good."

        if state.hunt_locale == "clinic":
            jump .plan_win_clinic

        "You use a text editor app to compose a message that looks like spam while being peppered with coded language that grey and black market \"retailers\" should pick up on."

        "You send a partially randomized copy of the original message to about a dozen names on your contact list, and wait."

        $ how_many = "three" if utils.percent_chance(35) else "four"
        "You get several replies, all but [how_many] of them being \"STOP\". One seems like an obvious trap - way too forward, barely speaking in code at all."

        "You don't know if they're just an undercover cop who's bad at their job, or something much worse. But you jot the number down before blocking it."

        "Another reply seems promising, but you don't like how it feels. Something you can't put your finger on."

        "When you read the next one, you decide to risk it. It's this one or nothing. You exchange a few more texts before sending a link."

        "It looks like the world's most obvious phishing scam, but the person on the other end isn't supposed to click it. It's code, for an address five blocks down."

        "You take the battery out of the phone and drive over."

        jump .planning_end_win

        label .plan_win_clinic:

        "After a couple hours poring over spreadsheets and log files you manage to come up with a handful of good candidates - local clinics, pharmacies, schools and other facilities that have run blood drives in the past few weeks."

        "You're pretty sure that if you can get in and massage the records a bit, you'll be able to swipe a few bags without drawing the wrong kind of attention."

        "Mortals noticing something off and asking the wrong questions. Vampires angry at the increased mortal scrutiny, or just because some other lick's been rooting around in their pantry."

        # jump .planning_clinic_subchoice

        call .planning_clinic_subchoice from bagger_clinic_planning_win

        label .planning_end_win:

        call hunting_tl_plan_success_post(time_spent) from bagger_plan_phase_win

        return time_spent

    label .planning_fail:

        $ state.roll_malus, state.roll_bonus = abs(state.active_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)
        $ planning_went_well = False

        if state.hunt_locale == "clinic":
            jump .plan_fail_clinic

        $ fake_spam_type = " fundraising for one of the sleazier candidates in the upcoming mayoral election"

        "You compose a message on your burner phone designed to look like typical robotext spam[fake_spam_type]."

        "But it's laced with coded phrases that should make it clear to those in the know what you're looking for."

        "There are a lot of shady reasons why mortals would want to buy stolen blood. You send a copy of the message to several numbers from your list and wait."

        "...And wait."

        "A bit too long for your liking, in fact. But you do eventually get a reply that looks like a legitimate criminal with genuine medical supplies to fence."

        "You get back behind the wheel and drive off to the meet spot."

        jump .planning_end_fail

        label .plan_fail_clinic:


        "After wasting a couple hours poring over useless spreadsheets, indecipherable log files and obscure news blogs, you {i}think{/i} you might have found something you can use."

        python:
            place_name, place_desc = utils.get_random_list_elem(("school", "clinic", "pharmacy")), ""
            # $ blood_drive_cause = utils.get_random_list_elem(("shootings", "stabbings", ""))
            if place_name == "school":
                place_desc = " hosting some kind of after-school program."

        "A local [place_name] that held a blood drive the other week in response to a recent uptick in shootings."

        "You're not a fan of the location. It's too well lit on the outside and too busy on the inside at this time of night[place_desc]."

        call .planning_clinic_subchoice from bagger_clinic_planning_fail
        # jump .planning_clinic_subchoice

        label .planning_end_fail:

        call hunting_tl_plan_failure_post(time_spent) from bagger_plan_phase_fail

        return time_spent

    label .planning_clinic_subchoice:

        python:
            state.current_plan, state.updated_pool, state.last_power_used = "snatch", None, None
            plan_prompt = "Now" if planning_went_well else "So if you're still going to make this work,"
            sng_pool1, sng_pool2 = utils.prettify_pool("wits+clandestine"), utils.prettify_pool("wits+clandestine+obfuscate")
            tdb_pool_ugly = "manipulation+academics"
            tdb_pool1 = utils.prettify_pool(tdb_pool_ugly)
            tdb_pool2, tdb_pool3 = utils.prettify_pool(tdb_pool_ugly + "+presence"), utils.prettify_pool(tdb_pool_ugly + "+obfuscate")

        menu:
            "[plan_prompt] you have two options - social engineering or a snatch-and-grab."  # TODO TODO TODO how long does whole blood last/stay in one place?

            "I'll try and break in, grab what I need and make the kind of mess that will obscure what I came for.  ([sng_pool1])":
                $ state.current_plan, state.updated_pool = "snatch", sng_pool1
            "above, but with obfuscate" if state.pc.has_disc_power(cfg.POWER_OBFUSCATE_STEALTH, cfg.DISC_OBFUSCATE):
                $ state.current_plan, state.updated_pool = "snatch", sng_pool2
                $ state.last_power_used = cfg.POWER_OBFUSCATE_STEALTH
            "I think I can talk my way into some database credentials and see to it that what I want to take won't be missed.  ([tdb_pool1])":
                $ state.current_plan, state.updated_pool = "social_engineering", tdb_pool1
            "above, but with presence" if state.pc.has_disc_power(cfg.POWER_PRESENCE_ENTRANCE, cfg.DISC_PRESENCE):
                $ state.current_plan, state.updated_pool = "social_engineering", tdb_pool2
                $ state.last_power_used = cfg.POWER_PRESENCE_ENTRANCE
            "above, but with mask 1000 faces" if state.pc.has_disc_power(cfg.POWER_OBFUSCATE_MASK, cfg.DISC_OBFUSCATE):
                $ state.current_plan, state.updated_pool = "social_engineering", tdb_pool3
                $ state.last_power_used = cfg.POWER_OBFUSCATE_MASK

        return
        # jump expression ("hunting_outcome_bloodbag_sub.planning_end_{}".format("win" if planning_went_well else "fail"))

    label .strike_messycrit:

        "You soberly contemplate the mess you've made in your frenzied haste, and sigh."

        if pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX and state.innocent_killed:
            $ you_feed = "At least you don't have to clean up any more bodies."
        elif pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX:
            $ you_feed = "At least you don't have a body to clean up. What a headache that would be."
        else:
            $ you_feed_add = " again" if state.innocent_killed else ""
            $ you_feed = "At least this way you don't have to worry about something horrible happening{}.".format(you_feed_add)
        if pc.predator_type == cfg.PT_BAGGER:
            $ you_feed += " This is why you stick to the bagged stuff."

        # TODO: come up with consequences for a bagger messycrit

        jump .either_crit_type

    label .strike_crit:

        if pc.predator_type == cfg.PT_BAGGER:
            $ you_feed = "That could hardly have gone better. Like a quick run to the corner store to pick up a six-pack."
        else:
            $ you_feed = "That went about as well as \"hunting\" for bagged swill could have gone."

        label .either_crit_type:

        python:
            slaked_hunger = max(state.active_roll.margin, 2) * utils.get_feeding_penalty_swill(pc.blood_potency, False)
            slaked_hunger = min(cfg.VAL_SWILL_SLAKE_MAX_CRIT, slaked_hunger)
            state.set_hunger("-={}".format(slaked_hunger))
            reso = utils.get_wrs((cfg.RESON_EMPTY, cfg.RESON_MELANCHOLIC), cum_weights=(100, 120))
            state.feed_resonance(reso=reso)

        jump .any_win

    label .strike_win:

        call hunting_tl_swill_strike_success from bagger_strike_phase_win
        $ slaked_hunger = _return

        label .any_win:

        play sound audio.feed_bite1
        queue sound audio.feed_bagged_1

        # Messages for drinking bagged blood are all the same after 2.
        $ you_feed_ps = flavor.flav("fed_on_bagged", "{}_slaked".format(cfg.SCORE_WORDS[min(slaked_hunger, 2)]))

        "[you_feed]"
        if slaked_hunger < 1:
            $ beast_growl = flavor.flav("fed_on_bagged", "zero_slaked_beast")
            beast "[beast_growl]"
        elif you_feed_ps:
            "[you_feed_ps]"

        return

    label .strike_fail:

        beast "..."

        beast "{b}Seriously?!{/b}"

        "You grit your teeth and force your angry Beast back down into the recesses of your mind."

        $ beast_rant = "You can't even hunt down a fucking plastic sack of shit-blood you absolute waste of"
        $ beast_rant = utils.cascading_size_text(beast_rant, starting_sz=5, sz_delta=-5, num_words=2)
        beast "[beast_rant]"

        if state.hunt_locale == "clinic":
            "Like it or not, this one's a bust. You grab your shit and walk to the exit in a way that you hope looks normal and calm."

            "You don't know how much evidence of your activity you left, or who's going to be talking about you. You can't worry about any of that now."

            "Maybe you'll get lucky and whoever looks into it will mistake you for a more mundane sort of thief."
        else:
            "After a couple minutes of suspicious back-and-forth you can tell this deal has gone bad."

            $ pns, She_He_They = state.prey.pronoun_set, str(state.prey.pronoun_set.PN_SHE_HE_THEY).capitalize()
            "Your plug looks tense. [She_He_They] keeps glancing off to [pns.PN_HER_HIS_THEIR] right. You don't wait to find out what [pns.PN_SHES_HES_THEYRE] looking or waiting for."
            # TODO: add more response options to this, e.g. kill the dealer, threaten them, just run, etc

            "No spinning this one. You're in some shit, and you're going to have to deal with it at some point."
        "But for now, escape is all that matters."
        return

    label .strike_beastfail:

        call hunting_tl_strike_bestial_failure from hunting_outcome_bloodbag_bf

        return


label hunting_outcome_animal_sub(*args):

    label .trash_preamble:

        "Rats are easy to come by in most major cities. The problem is that they're about as filling as they are tasty."

        "You're going to need to eat {i}a lot{/i} of rats to slake even a little of your Hunger, and you need a place in which to do so undisturbed."

        "You probably don't need to worry too much about all the little rat corpses you'll be leaving behind - no one cares about dead rats."

        "Still, if you leave them where a lot of people will see there's a small chance that someone investigates for health code-related reasons."

        "And that could eventually become a problem, if someone gets curious about why the rats are all exsanguinated."

        return

    label .killshelter_preamble:

        $ would_eat_at_no_kill = "though you hope you'll never be that desperate" if state.pc.humanity > 6 else "just in case"
        "You already know where you're going. You keep a list of every traditional shelter in the city (and a separate list of the no-kill shelters, [would_eat_at_no_kill])."

        "Your problem is getting in and getting out."

        return

    label .planning_win:

        $ state.roll_bonus, state.roll_malus = state.active_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        $ planning_went_well = True

        beast "Yes, yes, all according to plan. Too bad the plan is to drink vermin."

        if state.hunt_locale == "killshelter":
            jump .plan_win_killshelter

        # Hehehe, ya rat sucker.
        call .trash_preamble from farmer_trash_planning_win

        $ random_food_spots = utils.get_wrs(("an eerily pristine McDonalds", "the nastiest Dairy Queen", "a smoldering ruin (was it Kindred-owned, an accident, or just mundane arson?)"), cum_weights=(100, 140, 160))

        "You drive past a few seedy-looking diners, chicken spots, dive bars with kitchens, [random_food_spots], and a handful of bodegas."

        "Most of them are no good - too crowded, too well-lit, too exposed to security cameras. But there are a couple of choice options. You pull in behind a group of reeking dumpsters."

        "The smell would be nauseating if you were still capable of nausea. But it's exactly what you're looking for. You can already see them scurrying about your peripheral vision."

        beast "{b}{i}Urgh...{/i}{/b}"

        jump .planning_end_win

        label .plan_win_killshelter:

        # You monster.
        call .killshelter_preamble from farmer_killshelter_planning_win

        "There's considerably more security than one might expect, but you know that it's for the drugs, not the animals. That means it's not evenly distributed."

        "You're able to circle the building and map out all the exterior-facing cameras. There's a clear path in over a typical chain-link fence and through an unlocked window."

        $ night_staff = game.Person.random_pronouns()
        "But you wait. For ten minutes, then twenty, for the [night_staff.PN_STRANGER] in scrubs to finish [night_staff.PN_HER_HIS_THEIR] phone call and step out."

        "You almost didn't see [night_staff.PN_HER_HIM_THEM]. But now [night_staff.PN_SHES_HES_THEYRE] on [night_staff.PN_HER_HIS_THEIR] way out, and you're in."

        label .planning_end_win:

        call hunting_tl_plan_success_post(time_spent) from farmer_plan_phase_win

        return time_spent

    label .planning_fail:

        $ state.roll_malus, state.roll_bonus = abs(state.active_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)
        $ planning_went_well = False

        if state.hunt_locale == "killshelter":
            jump .plan_fail_killshelter

        call .trash_preamble from farmer_trash_planning_fail

        "You drive past a few seedy-looking diners, chicken spots, dive bars with kitchens still open, plus a handful of bodegas."

        "Most of them are either too crowded or too well-lit. But you spot a group of trash bins at the far end of a mostly deserted parking lot, and park nearby."

        $ can_smell_rats = "(you can hear and smell them) " if sum((state.pc.attrs[cfg.AT_WIT], state.pc.skills[cfg.SK_INSP])) > 3 else ""
        "This should work. Plenty of rats around and the place seems dark and secluded enough, far from any-"

        beast "..."

        "Shit. You must have triggered a motion sensor somewhere. A few lights come on, at the far corners of a chainlink fence."

        "After a few tense moments you don't hear anything. No one's coming as far as you can tell, and most of the lot is still dark."

        jump .planning_end_fail

        label .plan_fail_killshelter:

        call .killshelter_preamble from farmer_killshelter_planning_fail

        "There's considerably more security than one might expect, but you know that it's for the drugs, not the animals."

        "If you can find an entrance away from the pharmaceuticals and toward the animals, you should be golden."

        "You're able to circle the building and map out all the exterior-facing cameras. There's a clear path in over a typical chain-link fence and through an unlocked window."

        "It's not until you make your way in that you hear someone's voice. You freeze, fearing the worst. But whoever it is, they're on the phone."

        label .planning_end_fail:

        call hunting_tl_plan_failure_post(time_spent) from farmer_plan_phase_fail

        return time_spent

    label .strike_messycrit:

        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat  # TODO: get a new sound to replace this w/ animals?

        "You soberly contemplate the mess you've made in your frenzied haste, and sigh."

        if state.hunt_locale == "killshelter":
            "Cages line the room. Most of them are still occupied, and the occupants are alive if not exactly well. Dogs and cats huddle in their cages, some hissing or barking at you with hackles raised. Others just whimper."
            # TODO: dog/cat breeds
            "A half dozen cages nearest you are torn open, upended, or just broken into pieces. Exsanguinated cats and dogs lie at your feet with ragged bite wounds."

            "That gives you an idea, and you don't have time to come up with a better one."

            "You unlock and unlatch a few cages with the most aggressive-looking dogs. Then you drag some of the corpses and toss them in or near the cages, doing your best to get blood on the dogs inside."

            if state.killshelter_frenzy and state.pc.humanity > 5:
                "If there's anything lower than framing dogs for your own frenzied killing, it's having to do so more than once. You're not even sure it'll work again."
            elif state.killshelter_frenzy:
                "You have your doubts that this trick will work again, but what choice do you have?"
            elif state.pc.humanity > 5:
                "Framing dogs for your own frenzied killing. For your own lack of control. This must be a new low."
            $ state.killshelter_frenzy = True
            $ state.masquerade_breach(base=25)  # People are much more likely to notice dead shelter animals than dead rats.

        if pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX and state.innocent_killed:
            "At least the bodies aren't human this time, because you don't have time to clean them up."
        elif pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX:
            "At least the bodies aren't human. Because you don't have time to clean them up."
        else:
            $ you_feed_add = " more" if state.innocent_killed else ""
            "At least this way you won't end up killing any[you_feed_add] human beings."
            if pc.predator_type == cfg.PT_FARMER:
                "This is why you stick to animal blood. Things would be {i}so{/i} much worse if you lost control like this among humans."

        if state.hunt_locale == "trash":
            "There's nothing to be done. You came with a roll of heavy-duty garbage bags to dispose of all the rat corpses, but there's no time for that now."

            "You hop in your [state.pc_car] and speed off. You're not {i}too{/i} worried; dead rats don't exactly demand a thorough investigation."

            "With luck, anyone finding the rats will assume they were poisoned or rabid and be more interested in disposing of them quickly than in figuring out what exactly killed them."
            $ state.masquerade_breach()
        # TODO: come up with consequences for a farmer messycrit?

        $ current_result_messycrit = True
        jump .either_crit_type

    label .strike_crit:

        $ current_result_messycrit = False
        "That went about as well as it could."

        if state.hunt_locale == "trash":
            "You drink your fill of rats, darting back and forth in the darkness amid panicked squeaks and scrabbling claws."
            # TODO: update this for animalism powers

            "They're mostly too terrified to fight back, and you easily shrug off the bites of the ones that do."

            beast "A paltry excuse for a hunt. But at least we're hunting."

        label .either_crit_type:

        python:
            slaked_hunger = max(state.active_roll.margin, 2) * utils.get_feeding_penalty_swill(pc.blood_potency, False)
            slaked_hunger = min(cfg.VAL_SWILL_SLAKE_MAX_CRIT, slaked_hunger)
            state.set_hunger("-={}".format(slaked_hunger))
            state.feed_resonance(reso=cfg.RESON_ANIMAL, boost=1)

        $ you_feed = flavor.flav("fed_on_animal", "{}_slaked".format(cfg.SCORE_WORDS[min(slaked_hunger, 2)]))

        "[you_feed]"

        if not current_result_messycrit:
            jump .any_win

        return

    label .strike_win:

        "You're able to feed uninterrupted, but you can't shake the feeling you're being watched."

        # TODO: add to this later
        call hunting_tl_swill_strike_success from farmer_strike_phase_win
        $ slaked_hunger = _return

        # Messages for drinking animal blood are all the same after 2.
        $ you_feed = flavor.flav("fed_on_animal", "{}_slaked".format(cfg.SCORE_WORDS[min(slaked_hunger, 2)]))

        $ print("you_feed :> ", you_feed)

        "[you_feed]"

        if slaked_hunger < 1:
            $ beast_growl = flavor.flav("fed_on_animal", "zero_slaked_beast")
            beast "[beast_growl]"

        label .any_win:

        if state.hunt_locale == "killshelter":
            "When you're done with each animal you lick the wounds away. You're careful to clean up any spilled blood."

            "Cats and dogs die every day, for a lot of reasons."
        else:
            "When you're done, you get a broom and some heavy-duty garbage bags from your [state.pc_car]."

            "You take a few minutes to sweep up the mess, filling a couple bags with exsanguinated rodents."

            "You'll find a furnace chute to dump them down later."

        return

    label .strike_fail:

        if state.hunt_locale == "trash":
            "..."

            "You can't shake the feeling that you're being watched. You're on your fifth rat when you hear a doorknob turning."

            security_guard "Someone out there?"

            "Shit."

            beast "..."

            # TODO add sounds here

            "There's nothing you can do but take off running. Suddenly you find yourself with a long, dark shadow stretching out in front of you."

            security_guard "What the fuck? Who's there?! Shit. Hey!"

            $ night_staff_pns = game.Person.random_pronouns()
            $ her_him_them, she_he_they = night_staff_pns.PN_HER_HIM_THEM, night_staff_pns.PN_SHE_HE_THEY
            $ kill_them = " ".join(["kill {}".format(her_him_them) for _ in range(8)])
            beast "Kill [her_him_them] [kill_them]"

            "You jump in your car and peel out with a screech. This is bad, but you're pretty sure [she_he_they] at least didn't catch your plates."

            "You were only a few rats into your meal, and a handful of dead rats shouldn't mean anything to an ordinary security guard."

            $ state.masquerade_breach(base=7)

            "...Right?"
        else:
            $ night_staff_pns = game.Person.random_pronouns()
            $ temp_char = "{} In Labcoat".format(str(night_staff_pns.PN_STRANGER).capitalize())
            "Your plan was the cow the animals. Take advantage of their instinctive fear of your kind to keep them quiet."

            "It's worked before. But not this time. Something about your movements or demeanor pushes several animals over the line between frozen terror and noisy panic."

            "Hisses, yowls, barks, whines. There's no way the labcoat in the office isn't hearing this cacophony. You get ready to vault back up to the window you came through."

            "[temp_char]" "What the...?"

            $ book_it_skill = max(state.pc.skills[cfg.SK_INSP], state.pc.skills[cfg.SK_STWS], state.pc.skills[cfg.SK_TRAV])
            $ book_it_preamble = "You don't wait for {} in the labcoat to finish. ".format(night_staff_pns.PN_STRANGER)
            $ Shes_Hes_Theyre = str(night_staff_pns.PN_SHES_HES_THEYRE).capitalize()
            if state.pc.attrs[cfg.AT_WIT] + book_it_skill > utils.random_int_range(2, 4):
                "[book_it_preamble]You start to make a beeline for your car, then immediately think better of it."

                "Instead you feint to the right, then dash left. [Shes_Hes_Theyre] not chasing you, but [night_staff_pns.PN_SHE_HE_THEY] could be watching. And you don't want to make it obvious which car you came in, if you can help it."

                "You circle part-way around the building and leap the fence, tumbling into some bushes."

                "Then you wait several minutes, watching the window you came from and the nearby exit. No one emerges from either, so you carefully make your way back to your car and speed off."
                $ state.masquerade_breach(base=6)
            else:
                "[book_it_preamble]You make a beeline for your car, sprinting as fast as your legs will carry you."

                "You jump in and drive off, hoping you weren't seen."
                $ state.masquerade_breach(base=16)

        return

    label .strike_beastfail:

        call hunting_tl_strike_bestial_failure from hunting_outcome_animal_bf

        return


label hunting_tl_plan_success_post(time_spent, *args):
    if time_spent < cfg.STANDARD_HUNT_TIME:
        python:
            post_script = utils.get_random_list_elem((
                "You're making good time, too. And the less time you have to spend getting what you need, the better.",
                "Fortunately, you're making good time. And the less time you have to spend getting what you need, the better.",
                "And on top of everything, you're making good time. The less time you have to spend getting what you need, the better."
            ))
        "[post_script]"
    $ state.outside_haven = True
    return


label hunting_tl_plan_failure_post(time_spent, *args):
    if state.current_hunt_type in (cfg.PT_BAGGER, cfg.PT_FARMER):
        "You're not off to the best start, but you think you can still make this work."

        if time_spent > cfg.STANDARD_HUNT_TIME:
            "And now you're pressed for time."
    else:
        if time_spent > cfg.STANDARD_HUNT_TIME:
            $ fail_preamble = "You're not off to the best start. It takes you a good while to find a decent mark"
        else:
            $ fail_preamble = "You're not off to the best start, and you struggle to find a decent mark"
        "[fail_preamble] - [prey_ref_1] [state.prey.was_doing]."

    if state.pc.hunger > cfg.HUNGER_MAX_CALM:
        "But you're too hungry to back off now with nothing to show for it."
    else:
        "But you're here now, so you may as well have something to show for it."

    $ state.outside_haven = True
    return


label hunting_tl_strike_bestial_failure(*args):
    play sound audio.fleeing_footsteps1
    queue sound audio.oncoming_frenzy_2

    beast "YOU INCOMPETENT, MISERABLE-"

    "Your vision goes red."

    beast "{b}You had your chance. I'm taking over.{/b}"

    "There are screams, the sound of shattering glass, and what might have been a gunshot."

    "..."

    "You come to your senses in an alley."

    $ state.masquerade_breach()
    # TODO TODO: further consequences, also consider changing beast dynamic

    stop sound fadeout 0.5# with fadeout 0.5

    return


label hunting_tl_swill_strike_success(*args):
    python:
        feeding_penalty = utils.get_feeding_penalty_swill(pc.blood_potency, False)
        slaked_hunger_initial = min(cfg.VAL_SWILL_SLAKE_MAX, max(1, state.active_roll.margin))
        slaked_hunger = utils.math_floor(slaked_hunger_initial * feeding_penalty)
        state.set_hunger("-={}".format(slaked_hunger))  # Can bagged blood be innocent or guilty? We may never know.
        if state.current_hunt_type == cfg.PT_FARMER:
            state.feed_resonance(boost=-1, reso=cfg.RESON_EMPTY)
        else:
            state.feed_resonance(reso=cfg.RESON_ANIMAL)
        you_feed = "Mission accomplished."

    return slaked_hunger


#
