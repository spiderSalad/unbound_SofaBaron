# GENERAL HUNT FORMAT:

# 1. Description of journey
# 2. Blurb reflecting current status of PC/city as it relates to hunting conditions, hinting at possible bonuses/penalties
# 3. Phase 1 - locating target; this is the first roll, modified by conditions
# 4. Phase 2 - securing and feeding on the target; this is the second roll, modified by the results of the First
# 5. Aftermath 1 - a messy critical or a failure of willpower roll (if hunger > 3) in phase 2 will result in a kill
# 6. Aftermath 2 - escape is easier if you didn't kill the target; if you did, you need to hide a body and suffer penalties
# 7. Return

# separate first hunt?

label hunt_confirm(pool_desc_raw, hunt_warning):
    python:
        pool_org, pool_tokens = renpy.store.utils.parse_pool_string(pool_desc_raw), []
        for phase in pool_org:
            phase_str = "/".join(phase)
            pool_tokens.append(phase_str)
        final_text = ", then ".join(pool_tokens)


    menu:
        beast "[hunt_warning]"

        "Let's do it.\n\n[final_text]":
            return True

        "On second thought...":
            return False


label hunt_alley_cat(status):

    label .options:

    menu:
        beast "The fear, the chase... it's best this way, isn't it? Where shall we hunt, my friend?"

        "Down by the river. Lots of drunks, homeless, and exhausted dockworkers there - easy prey.":
            $ hw = "Unless you pick the wrong target. It's a rough area; lots of people there either scrap or hold a strap."
            call hunt_confirm("wits+streetwise,strength+combat", hw) from alley_cat_river
            if _return:
                jump hunt_alley_cat.river
            jump hunt_alley_cat.options

        "I'm in the mood for something... richer. I'll hunt in the parking lots at that new expensive shopping center.":
            "Hip young professionals, rich yuppies - all kinds of soft, juicy prey. But also lots of security."

            $ hw = "Careful not to get caught on camera. Don't let them scream or call for help."
            call hunt_confirm("wits+inspection,charisma+intimidation/manipulation+diplomacy", hw) from alley_cat_plaza
            if _return:
                jump hunt_alley_cat.plaza
            jump hunt_alley_cat.options

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .river:

        "You hop in your [state.pc_car] and make your way onto the Interstate. You can see the river for almost the entire trip, golden and recumbent."

        "It doesn't take long for you to arrive at the docks. You remember when this place was nicer, probably because the jobs paid better."

        "You park in a secluded spot and start looking for a good mark - someone tired, someone drunk (but not {i}too{/i} drunk), someone unwary."

        call generic_hunt_results("wits+streetwise", "diff3", "strength+combat", "diff3") from alley_cat_temp_test_river
        jump .end

        # TODO: add Blood Surge, probably a button that's always there and sometimes enabled

        # call roll_control("wits+streetwise", "diff3") from hunt_river_phase1

        label .river_drain:
            ""

        label .river_bonus_win:
            ""

        label .river_feed:
            ""

        label .river_fail:
            ""

        label .river_beastfail:
            ""


    label .plaza:

        "plaza test"

        call generic_hunt_results("wits+inspection", "diff3", "charisma+intimidation/manipulation+diplomacy", "diff3") from alley_cat_temp_test_plaza
        jump .end

    label .end:

        "So ends another hunt."

    return


label hunt_bagger(status):

    label .options:

    menu:
        beast "Ugh... Your cowardice condemns us to feeding at the proverbial trough, like swine."

        "I think there are a few \"suppliers\" I can contact.":
            $ hw = "Any mortal who'd sell us blood has already betrayed their profession. You think they wouldn't betray us as well?"
            call hunt_confirm("intelligence+streetwise,composure+intrigue", hw) from bagger_plug
            if _return:
                jump hunt_bagger.plug
            jump hunt_bagger.options

        "I can arrange to pick up an \"order\" at one of the local clinics.":
            "You'll need to access and sort through a lot of medical records to find some blood that can be \"misplaced\" for you."

            "And then you'll need to actually get in to retrieve the goods."

            $ hw = "It's a hunt of sorts... But one mistake and {i}we'll{/i} be the prey."
            call hunt_confirm("resolve+Technology,manipulation+academics/wits+clandestine", hw) from bagger_clinic
            if _return:
                jump hunt_bagger.clinic
            jump hunt_bagger.options

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .plug:

        call generic_hunt_results("intelligence+streetwise", "diff3", "composure+intrigue", "diff3") from bagger_temp_test_plug
        "bagger.plug hunt test end"
        jump .end

    label .clinic:

        call generic_hunt_results("resolve+technology", "diff3", "manipulation+academics/wits+clandestine", "diff3") from bagger_temp_test_clinic
        "bagger.clinic hunt test end"
        jump .end

    label .end:

        "So ends another hunt."

    return


label hunt_farmer(status):

    label .options:

    menu:
        beast "You realize that the other Kindred are all laughing at us, don't you? The {i}thinbloods{/i} are probably laughing at us."

        "I think I'll check out the dumpsters behind some of the more questionable restaurants. Spotty health standards mean lots of vermin.":

            "So long as you pick a secluded spot that will stay deserted long enough for you to drink your fill."

            "You're not sure where getting caught sucking on live rats falls on the sliding scale of Masquerade violations..."

            "...but it'd be a pretty humiliating reason to be dragged before one of the Barons - or worse, the actual Sheriff."

            $ hw = "{b}It's pretty humiliating either way{/b}. Even if other Kindred don't witness our shame, {i}we{/i} will."

            call hunt_confirm("intelligence+traversal,composure+clandestine", hw) from farmer_trash
            if _return:
                jump hunt_farmer.trash
            jump hunt_farmer.options

        # TBA: Break into a kill shelter

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .trash:

        call generic_hunt_results("intelligence+traversal", "diff3", "composure+clandestine", "diff3") from farmer_temp_test
        jump .end

    label .shelter:

        "shelter test (not implemented)"

    label .end:

        "So ends another hunt."

    return


label hunt_siren(status):

    label .options:

    menu:
        beast "Whatever floats your boat, as they say. So long as {i}I{/i} get what {i}I{/i} want."

        "There's this new club downtown that I've been wanting to check out. I'm sure I can find someone to spend the night with there.":

            #"Most of the clubs downtown are new, in part because of how many were closed down the last time the Inquisition swept through this city."

            #"Any Kindred-owned business they managed to learn about was seized, shut down, or otherwise eliminated,

            # In the aftermath, some enterprising mortal investors made a killing buying them up on the cheap."

            #"You doubt any of these mortal profiteers have any idea who or what they're poaching from, but you'll have to be careful nonetheless."

            "Clubs are choice hunting grounds in almost any city. They're places where the beautiful and energetic gather."

            "Young adults in their prime, taking risks and looking for a good time."

            if pc.humanity > cfg.WEAK_TO_HUNGER_HUMANITY_THRESHOLD_INC:
                $ club_comment1 = "A metaphor whose implications you'd prefer not to think too hard about."
            else:
                $ club_comment1 = "Fitting, given all the fresh meat on display."

            "Some Kindred refer to such places as their city's \"rack\". [club_comment1]"

            $ hw = "Careful, friend. You never know which trashblood tick might have staked a claim over this or that watering hole or dance floor."

            call hunt_confirm("composure+streetwise,charisma+intrigue/charisma+diplomacy", hw) from siren_club
            $ retval = _return

            if not state.siren_type_chosen:
                call pc_gender_preference from siren_first_hunt

            if retval:
                jump hunt_siren.club
            jump hunt_siren.options

        # TBA: Some other hookup spot

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .club:

        if state.siren_orientation is None:
            $ desired = utils.get_random_list_elem([cfg.PN_WOMEN, cfg.PN_MEN, cfg.PN_NONBINARY])
        else:
            $ desired = state.siren_orientation

        # TODO: specific hunting text
        call generic_hunt_results("composure+streetwise", "diff3", "charisma+intrigue/charisma+diplomacy", "diff3") from siren_temp_test
        jump .end

    label .party_maybe:

        if state.siren_orientation is None:
            $ desired = utils.get_random_list_elem([cfg.PN_WOMEN, cfg.PN_MEN, cfg.PN_NONBINARY])
        else:
            $ desired = state.siren_orientation

        "party (maybe?) test - not implemented"
        jump .end

    label .end:

        "So ends another hunt."

    return


label generic_hunt_results(scoping_pool, scoping_test, feeding_pool, feeding_test):
    call roll_control(scoping_pool, scoping_test) from generic_hunt_scope_roll
    $ cfg = store.cfg
    $ tll, time_spent = "generic_hunt_results", cfg.STANDARD_HUNT_TIME
    jump expression renpy.store.game.pass_fail(_return, ".scope_win", ".scope_fail", top_label=tll)

    label .scope_win:
        $ state.roll_bonus, state.roll_malus = state.current_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        "> Successfully scoped out target. Hunt duration reduced to [time_spent] hours, +[state.roll_bonus] to feed roll."
        jump .feed_roll

    label .scope_fail:
        $ state.roll_malus, state.roll_bonus = abs(state.current_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)
        "> Difficulty scoping out target. Hunt duration increased to [time_spent], -[state.roll_malus] to feed roll."
        jump .feed_roll

    label .feed_roll:
        python:
            if state.roll_bonus > 0:
                final_feeding_pool = "{}+{}".format(feeding_pool, state.roll_bonus)
            elif state.roll_malus > 0:
                final_feeding_pool = "{}+{}".format(feeding_pool, -1 * state.roll_malus)
            else:
                final_feeding_pool = feeding_pool
        call roll_control(final_feeding_pool, feeding_test)
        $ tll = "generic_hunt_results"
        jump expression renpy.store.game.manual_roll_route(_return, ".win", ".fail", mc=".messy", crit=".crit", bfail=".beastfail", top_label=tll)

    label .messy:  # A dead body - you also get here if your hunger is high and you fail a willpower roll
        $ state.set_hunger(0, killed=True, innocent=True)
        "You find yourself standing over a dead body. The problem of your Hunger is dealt with, but now you have a different problem."
        jump .end

    label .crit:  # You feed successfully and get a bonus
        $ state.set_hunger("-=2")
        "That could hardly have gone better."
        jump .end

    label .win:  # successful feeding, hunger slaked depends on margin (1 or 2, 3 or 4 if humanity is low)
        $ temp_margin = state.current_roll.margin
        $ max_slaked = 2 if pc.humanity > cfg.KILLHUNT_HUMANITY_MAX else min(4, 3 + (cfg.KILLHUNT_HUMANITY_MAX - pc.humanity))
        $ slaked_hunger = min(max_slaked, 1 + int(temp_margin))
        $ state.set_hunger("-={}".format(slaked_hunger))
        if slaked_hunger > 3:
            "You drink your fill. Your prey will live, assuming someone notices them in time."
        elif slaked_hunger > 2:
            "You drink your fill, and leave your prey in a daze. They'll be fine, assuming someone notices them in time."
        elif slaked_hunger == 2:
            "You drink deeply, but not {i}too{/i} deeply."
        else:
            "You take a few good gulps; just enough to take the edge off before you have to split."
        jump .end

    label .fail:  # You fail to feed
        "That could have gone better. You fail to feed, but manage a clean escape."
        jump .end

    label .beastfail:  # You fail to feed and get penalized further
        beast "YOU INCOMPETENT, MISERABLE LITTLE-"

        "Your vision goes red. There are screams, the sound of shattering glass, and what might have been a gunshot."

        "You come to your senses in an alley."
        jump .end

    label .end:
        call pass_time(time_spent) from generic_hunt_results_end
        return

    $ raise ValueError("Shouldn't reach here!")


label pc_gender_preference:

    menu:
        beast "So... who are we looking for?"

        "Men.":
            $ state.siren_orientation = cfg.PN_MEN

        "Women":
            $ state.siren_orientation = cfg.PN_WOMEN

        "Someone beyond those categories.":
            $ state.siren_orientation = cfg.PN_NONBINARY

        "Any of the above, as long as they're hot.":
            $ state.siren_orientation = None

    $ state.siren_type_chosen = True

    beast "Lovely. Let's go find someone you like so we can eat."

    return


label hunger_frenzy:

    beast "Blood. BLOOD. FEED FEED FEED FEEDFEEDFEEDFEEDFEEDFEEDFEED"

    "..."
    # TODO: even more nasty consequences, and some crazy sounds

    # masquerade penalty

    python:
        hf_kill = True if utils.random_int_range(0, 4) > 3 else False
        hf_innocent = True if hf_kill and utils.random_int_range(0, 3) > 2 else False
        hf_hours_lost = utils.random_int_range(0, 3)
        hf_outside_haven = True if utils.random_int_range(0, 1) > 0 else False
        state.set_hunger(0, killed=hf_kill, innocent=hf_innocent)

    call pass_time(hf_hours_lost, in_shelter=not hf_outside_haven) from hunger_frenzy_blackout

    "You come to your senses some time later, your jaw and chest slick with gore. What have you done?"

    jump haven.main
