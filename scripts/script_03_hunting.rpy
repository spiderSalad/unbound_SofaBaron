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

        call generic_hunt_results("wits+inspection", "diff3", "charisma+intimidation", "diff3") from alley_cat_temp_test_plaza
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


    label .plug:

        call generic_hunt_results("intelligence+streetwise", "diff3", "composure+intrigue", "diff3") from bagger_temp_test_plug
        "bagger.plug hunt test end"
        jump .end

    label .clinic:

        call generic_hunt_results("resolve+technology", "diff3", "manipulation+academics", "diff3") from bagger_temp_test_clinic
        "bagger.clinic hunt test end"
        jump .end

    label .end:

        "So ends another hunt."

    return


label hunt_farmer(status):

    label .options:

    menu:
        beast "You realize that the other Kindred are all laughing at us, don't you? The {i}thinbloods{/i} are probably laughing at us."

        "I think I'll check out the dumpsters behind some of the more questionable restaurants. Spotty health standards means lots of vermin.":

            "So long as you pick a secluded spot that will stay deserted long enough for you to drink your fill."

            "You're not sure where getting caught sucking on live rats falls on the sliding scale of Masquerade violations..."

            "...but what a humiliating reason to be dragged before one of the Barons - or worse, the actual Sheriff."

            $ hw = "{b}It's pretty humiliating either way{/b}. Even if other Kindred don't witness our shame, {i}we{/i} will."

            call hunt_confirm("intelligence+traversal,composure+clandestine", hw) from farmer_trash
            if _return:
                jump hunt_farmer.trash
            jump hunt_farmer.options

        # TBA: Break into a kill shelter


    label .trash:

        call generic_hunt_results("intelligence+traversal", "diff3", "composure+clandestine", "diff3") from farmer_temp_test
        jump .end

    label .shelter:

        "shelter test (not implemented)"

    label .end:

        "So ends another hunt."


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

            if not state.siren_type_chosen:
                call pc_gender_preference from siren_first_hunt

            if _return:
                jump hunt_siren.club
            jump hunt_siren.options

        # TBA: Some other hookup spot


    label .club:

        if state.siren_orientation is None:
            $ desired = utils.get_random_list_elem([cfg.PN_WOMEN, cfg.PN_MEN, cfg.PN_NONBINARY])
        else:
            $ desired = state.siren_orientation

        # TODO: specific hunting text
        call generic_hunt_results("composure+streetwise", "diff3", "charisma+intrigue", "diff3") from siren_temp_test
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


label generic_hunt_results(scoping_pool, scoping_test, feeding_pool, feeding_test):
    call roll_control(scoping_pool, scoping_test) from generic_hunt_scope_roll
    $ tll = "generic_hunt_results"
    jump expression renpy.store.game.pass_fail(_return, ".scope_win", ".scope_fail", top_label=tll)

    label .scope_win:
        "> Successfully scoped out target."
        $ state.roll_bonus = state.current_roll.margin
        jump .feed_roll

    label .scope_fail:
        "> Difficulty scoping out target. Penalty applied."
        $ state.roll_malus = abs(state.current_roll.margin)
        jump .feed_roll


    label .feed_roll:
        call roll_control(feeding_pool, feeding_test)
        $ tll = "generic_hunt_results"
        jump expression renpy.store.game.manual_roll_route(_return, ".win", ".fail", mc=".messy", crit=".crit", bfail=".beastfail", top_label=tll)


    label .messy:  # A dead body - you also get here if your hunger is high and you fail a willpower roll
        $ state.set_hunger(0, killed=True, innocent=True)
        "You find yourself standing over a dead body. The problem of your Hunger is dealt with, but now you have a different problem."
        return

    label .crit:  # You feed successfully and get a bonus
        $ state.set_hunger("-=2")
        "That could hardly have gone better."
        return

    label .win:  # successful feeding, hunger slaked depends on margin (always 1 or 2, or 3 if humanity is low)
        $ temp_margin, max_slaked = state.current_roll.margin, 2 if pc.humanity > cfg.KILL_HUNT_HUMANITY_THRESHOLD_INC else 3
        $ slaked_hunger = max(1, min(max_slaked, int(temp_margin)))
        $ state.set_hunger("-={}".format(slaked_hunger))
        if slaked_hunger > 2:
            "You drink your fill, and leave your prey in a daze. They'll be fine, assuming someone notices them in time."
        elif slaked_hunger == 2:
            "You drink deeply, but not {i}too{/i} deeply."
        else:
            "You take a few good gulps; just enough to take the edge off before you have to split."
        return

    label .fail:  # You fail to feed
        "That could have gone better. You fail to feed, but manage a clean escape."
        return

    label .beastfail:  # You fail to feed and get penalized further
        beast "YOU INCOMPETENT, MISERABLE LITTLE-"

        "Your vision goes red. There are screams, the sound of shattering glass, and what might have been a gunshot."

        "You come to your senses in an alley."
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
