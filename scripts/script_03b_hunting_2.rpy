label hunting_outcome_generic_sub(*args):

    label .planning_win:
        $ state.roll_bonus, state.roll_malus = state.active_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        $ prey_ref_1C = prey_ref_1.capitalize()
        # $ what_they_were_doing = flavor.what_they_were_doing()

        "You manage to case the area and pick out a suitable target. [prey_ref_1C], [state.prey.was_doing]. Things ought to go smoothly from here."

        if time_spent < cfg.STANDARD_HUNT_TIME:
            "You're making good time, too. And the less time you have to spend getting what you need, the better."

        return time_spent

    label .planning_fail:
        $ state.roll_malus, state.roll_bonus = abs(state.active_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)

        if time_spent > cfg.STANDARD_HUNT_TIME:
            $ fail_preamble = "You're not off to the best start. It takes you a good while to find a decent mark"
        else:
            $ fail_preamble = "You're not off to the best start, and you struggle to find a decent mark"
        "[fail_preamble] - [prey_ref_1] [state.prey.was_doing]."

        if state.pc.hunger > cfg.HUNGER_MAX_CALM:
            "But you're too hungry to back off now with nothing to show for it."
        else:
            "But you're here now, so you may as well have something to show for it."

        return time_spent

    # TODO: left off here! (2023/03/15)

    # basically, I was falling into the trap of re-inventing the wheel and trying to OOP-ify flavor/writing that's better
    # expressed through what Ren'Py already does. Hence this file, which should replace the FlavorPack class and derivatives.
    # If they remain at all, they should generate and pass back their "token" parameters to a script juncture here.

    label .strike_messycrit:
        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        python:
            state.set_hunger(0, killed=True, innocent=True)
            state.feed_resonance(boost=1)

        "You find yourself standing over the dead body of [prey_ref_1]. [Shes_Hes_Theyre] already growing cold."

        "Your Hunger is sated, but now you have a different problem."

        if pc.hunger < 1:
            beast "{i}Ahh...{/i} Well done, friend. Well done. Doesn't that feel so much {i}better{/i}? We should do this more often."
        elif pc.hunger < cfg.HUNGER_MAX_CALM:
            beast "Satisfying... almost."
        else:
            "And even after taking a life some Hunger remains. That's not good."

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

        if drained:
            $ state.set_hunger(0, killed=True, innocent=True)  # TODO: add innocence check
            $ state.feed_resonance(boost=2)
            "That went great, except for the exsanguinated [prey_ref_2] lying dead at your feet. That could be a problem."
        else:
            $ state.set_hunger("-=2")
            $ state.feed_resonance(boost=1)
            "That could hardly have gone better."

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
                print("max hunger slaked for this feeding is {}".format(max_slaked))
            slaked_hunger = min(max_slaked, 1 + int(temp_margin))
            state.set_hunger("-={}".format(slaked_hunger), killed=drained, innocent=True)  # TODO: add innocence check
            her_him_them = state.prey.pronoun_set.PN_HER_HIM_THEM
            shell_hell_theyll = state.prey.pronoun_set.PN_SHELL_HELL_THEYLL
            shell_hell_theyll_C = shell_hell_theyll.capitalize()

        if drained:
            "You drink your fill of [her_him_them], basking in warm contentment, and leave the body for your future self to worry about."
            $ state.feed_resonance(boost=1)
        elif slaked_hunger > 3:
            "You drink your fill. Your prey will live, assuming someone notices [her_him_them] in time."
            $ state.feed_resonance()
        elif slaked_hunger > 2:
            "You drink your fill, and leave your prey in a daze. [shell_hell_theyll_C] be fine, assuming someone notices [her_him_them] in time."
            $ state.feed_resonance()
        elif slaked_hunger == 2 and pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX:
            "You drink deeply, but not so deeply that your prey won't recover."
        elif slaked_hunger == 2:
            "You drink deeply, but not {i}too{/i} deeply. [shell_hell_theyll_C] be fine with some rest and a good meal."
            $ state.feed_resonance()
            if utils.percent_chance(15):
                "...Assuming no one else feeds from [her_him_them] in the next few weeks."
        else:
            "You take a few good gulps; just enough to take the edge off before you have to split."
            $ state.feed_resonance(boost=-1)

        stop sound
        if drained:
            play sound audio.body_fall1

        return

    label .strike_fail:
        $ shell_hell_theyll = state.prey.pronoun_set.PN_SHELL_HELL_THEYLL

        play sound audio.fleeing_footsteps1

        "That could have gone better. You fail to feed, but manage a clean escape."

        "With any luck, [shell_hell_theyll] mistake your intentions for a regular mugging or assault."

        return

    label .strike_beastfail:
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


#
