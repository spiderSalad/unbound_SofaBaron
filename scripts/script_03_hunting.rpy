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
        hunt_phases = pool_desc_raw.split(",")
        phase_desc_full = []
        for hp in hunt_phases:
            hunt_options = hp.split("/")
            hopt_desc_full = []
            for hopt in hunt_options:
                hopt_params = [str(op).capitalize() for op in hopt.split("+")]
                hopt_desc_full.append("{}".format(" + ".join(hopt_params)))
            phase_desc_full.append(" or ".join(hopt_desc_full))
        final_text = ", then ".join(phase_desc_full)


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

        # TODO: add Blood Surge, probably a button that's always there and sometimes enabled

        call roll_control("wits+streetwise", "diff3") from hunt_river_phase1

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

        ""

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

        ""

    label .clinic:

        ""

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

            call hunt_confirm("intelligence+streetwise,composure+intrigue", hw) from farmer_trash
            if _return:
                jump hunt_farmer.trash
            jump hunt_farmer.options

        # TBA: Break into a kill shelter


    label .trash:

        ""

    label .shelter:

        ""

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

        ""

    label .party_maybe:

        if state.siren_orientation is None:
            $ desired = utils.get_random_list_elem([cfg.PN_WOMEN, cfg.PN_MEN, cfg.PN_NONBINARY])
        else:
            $ desired = state.siren_orientation

        ""

    label .end:

        "So ends another hunt."


label generic_hunt_results(scoping_pool, scoping_test, feeding_pool, feeding_test):

    call roll_control(scoping_pool, scoping_test) from generic_hunt_scope_roll
    jump expression renpy.store.game.pass_fail(_return, ".scope_win", ".scope_fail")

    label .scope_win:
        "> Successfully scoped out target."
        $ state.roll_bonus = roll_obj.margin
        jump .feed_roll

    label .scope_fail:
        "> Difficulty scoping out target. Penalty applied."
        $ state.roll_malus = abs(roll_obj.margin)
        jump .feed_roll


    label .feed_roll:
        call roll_control(feeding_pool, feeding_test)


    label .messy:  # A dead body - you also get here if your hunger is high and you fail a willpower roll

        ""

    label .crit:  # You feed successfully and get a bonus
        ""

    label .win:  # successful feeding, hunger slaked depends on margin (always 1 or 2, or 3 if humanity is low)
        ""

    label .fail:  # You fail to feed
        ""

    label .beastfail:  # You fail to feed and get penalized further
        ""

    return


label pc_gender_preference:

    menu:
        beast "So... what are we looking for?"

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
