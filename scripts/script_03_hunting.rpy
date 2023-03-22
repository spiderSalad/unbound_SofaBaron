# GENERAL HUNT FORMAT:

# 1. Description of journey
# 2. Blurb reflecting current status of PC/city as it relates to hunting conditions, hinting at possible bonuses/penalties
# 3. Phase 1 - locating target; this is the first roll, modified by conditions
# 4. Phase 2 - securing and feeding on the target; this is the second roll, modified by the results of the First
# 5. Aftermath 1 - a messy critical or a failure of willpower roll (if hunger > 3) in phase 2 will result in a kill
# 6. Aftermath 2 - escape is easier if you didn't kill the target; if you did, you need to hide a body and suffer penalties
# 7. Return

# separate first hunt?

label hunt_confirm(hunt_warning, pool_desc_1, pool_desc_2, situational_mod=None):
    python:
        pool_desc_raw = "{},{}".format(pool_desc_1, pool_desc_2)
        pool_org, pool_tokens = renpy.store.utils.parse_pool_string(pool_desc_raw, situational_mod=situational_mod), []
        for phase in pool_org:
            phase_str = "/".join(phase)
            pool_tokens.append(phase_str)
        final_text = ", then ".join(pool_tokens)


    menu:
        beast "[hunt_warning]"

        "Let's do it.\n\n[final_text]":
            $ state.tried_hunt_tonight = True
            return True

        "On second thought...":
            return False


label hunt_alley_cat(status):

    $ state.current_hunt_type, planning_diff, strike_diff = cfg.PT_ALLEYCAT, "diff4", "diff4"

    label .options:

    menu:
        beast "The fear, the chase... it's best this way, isn't it? Where shall we hunt, my friend?"

        "Down by the river. Lots of drunks, homeless, and exhausted dockworkers there - easy prey.":
            $ hw = "Unless you pick the wrong target. It's a rough area; lots of people there either scrap or hold a strap."
            $ hunting_pool1, hunting_pool2 = "wits+streetwise", "strength+combat"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from alley_cat_river_confirmation
            if _return:
                jump hunt_alley_cat.river
            jump hunt_alley_cat.options

        "I'm in the mood for something... richer. I'll hunt in the parking lots at that new expensive shopping center.":
            "Hip young professionals, rich yuppies - all kinds of soft, pliant prey."

            "The kind that tend to eat at upscale restaurants and have cushy gym memberships they may or may not use."

            "But with all that juicy, upwardly mobile prey comes a lot of security."

            $ hw = "Careful not to get caught on camera. Don't let them scream or call for help."
            $ hunting_pool1, hunting_pool2 = "wits+inspection", "charisma+intimidation/manipulation+diplomacy"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from alley_cat_plaza_confirmation
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

        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from alley_cat_river_goodhunting
        $ hunt_outcome, time_spent = _return
        "river test end"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .plaza:

        "plaza test"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from alley_cat_plaza_goodhunting
        $ hunt_outcome, time_spent = _return
        "plaza test and"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .end:

        "So ends another hunt."

    return hunt_outcome, time_spent


label hunt_bagger(status):

    $ state.current_hunt_type, planning_diff, strike_diff = cfg.PT_BAGGER, "diff3", "diff3"

    label .options:

    menu:
        beast "Ugh... Your cowardice condemns us to feeding at the proverbial trough, like swine."

        "I think there are a few \"suppliers\" I can contact.":
            $ hw = "Any mortal who'd sell us blood has already betrayed their profession. You think they wouldn't betray us as well?"
            $ hunting_pool1, hunting_pool2 = "intelligence+streetwise", "composure+intrigue"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from bagger_plug_confirmation
            if _return:
                jump hunt_bagger.plug
            jump hunt_bagger.options

        "I can arrange to pick up an \"order\" at one of the local clinics.":
            "You'll need to access and sort through a lot of medical records to find some blood that can be \"misplaced\" for you."

            "And then you'll need to actually get in to retrieve the goods."

            $ hw = "It's a hunt of sorts... But one mistake and {i}we'll{/i} be the prey."
            $ hunting_pool1, hunting_pool2 = "resolve+Technology", "manipulation+academics/wits+clandestine"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from bagger_clinic_confirmation
            if _return:
                jump hunt_bagger.clinic
            jump hunt_bagger.options

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .plug:

        "bagger.plug hunt test start"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from bagger_plug_goodhunting
        $ hunt_outcome, time_spent = _return
        "bagger.plug hunt test end"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .clinic:

        "bagger.clinic hunt test start"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from bagger_clinic_goodhunting
        $ hunt_outcome, time_spent = _return
        "bagger.clinic hunt test end"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .end:

        "So ends another hunt."

    return hunt_outcome, time_spent


label hunt_farmer(status):

    $ state.current_hunt_type, planning_diff, strike_diff = cfg.PT_FARMER, "diff3", "diff3"

    label .options:

    menu:
        beast "You realize that the other Kindred are all laughing at us, don't you? The {i}thinbloods{/i} are probably laughing at us."

        "I think I'll check out the dumpsters behind some of the more questionable restaurants. Spotty health standards mean lots of vermin.":
            "So long as you pick a secluded spot that will stay deserted long enough for you to drink your fill."

            "You're not sure where getting caught sucking on live rats falls on the sliding scale of Masquerade violations..."

            "...but it'd be a pretty humiliating reason to be dragged in front of a local Baron - or worse, the actual Sheriff."

            $ hw = "{b}It's pretty humiliating either way{/b}. Even if other Kindred don't witness our shame, {i}we{/i} will."
            $ hunting_pool1, hunting_pool2 = "intelligence+traversal", "composure+clandestine"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from farmer_trash_confirmation
            if _return:
                jump hunt_farmer.trash
            jump hunt_farmer.options

        # TBA: Break into a kill shelter
        "kill shelter":
            "you plan to break into a kill shelter and pick out a few of the doomed animals to drain"

            $ hw = "At least have the decency to season our food a bit. Maybe let a few loose so we can chase them?"
            $ hunting_pool1, hunting_pool2 = "dexterity+clandestine", "wits+diplomacy"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from farmer_killshelter_confirmation
            if _return:
                jump hunt_farmer.killshelter
            jump hunt_farmer.options

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .trash:

        "hunting in the trash for rats"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from farmer_trash_goodhunting
        $ hunt_outcome, time_spent = _return
        "farmer trash test end"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .killshelter:

        "hunting at shelter test (not implemented)"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from farmer_killshelter_goodhunting
        $ hunt_outcome, time_spent = _return
        "farmer kill shelter test end"
        # TODO: certain results (_return) trigger an encounter
        jump .end

    label .end:

        "So ends another hunt."

    return hunt_outcome, time_spent


label hunt_siren(status):

    $ state.current_hunt_type, planning_diff, strike_diff = cfg.PT_SIREN, "diff3", "diff3"

    label .options:

    menu:
        beast "Whatever floats your boat. So long as {i}I{/i} get what {i}I{/i} want."

        "There's this new club downtown that I've been wanting to check out. I'm sure I can find someone to spend the night with there.":
            "Clubs and other trendy entertainment venues are choice hunting grounds in almost any city. They're places where the beautiful and energetic gather."

            "Young adults in their prime, taking risks and looking for a good time."

            if pc.humanity > cfg.WEAK_TO_HUNGER_HUMANITY_THRESHOLD_INC:
                $ club_comment1 = "A metaphor whose implications you'd prefer not to think too hard about."
            else:
                $ club_comment1 = "Fitting, given all the fresh meat on display."

            "Some Kindred refer to such places as their city's \"rack\". [club_comment1]"

            $ hw = "Careful, friend. You never know which trashblood tick might have staked a claim over this or that watering hole or dance floor."
            $ hunting_pool1, hunting_pool2 = "composure+streetwise", "charisma+intrigue/charisma+diplomacy"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from siren_nightclub_confirmation
            $ retval = _return

            if not state.siren_type_chosen:
                call pc_prey_gender_dialogue from siren_first_hunt_nightclub

            if retval:
                jump hunt_siren.nightclub
            jump hunt_siren.options

        # TBA: Some other hookup spot
        "other option (party, maybe?)":
            "not implemented"

            "insert text here dsfdsf"
            $ hw = "sdfdsfds hunt warning"
            $ hunting_pool1, hunting_pool2 = "ssssss", "dddddddfdfd"
            call hunt_confirm(hw, hunting_pool1, hunting_pool2) from siren_houseparty_confirmation
            $ retval = _return

            if not state.siren_type_chosen:
                call pc_prey_gender_dialogue from siren_first_hunt_houseparty

            if retval:
                jump hunt_siren.houseparty
            jump hunt_siren.options

        "Actually, I'd rather not hunt right now.":
            $ state.outside_haven = False
            return


    label .nightclub:

        call get_prey_gender from siren_gpg_nightclub
        $ desired = _return

        "insert club siren preamble text here"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from siren_nightclub_goodhunting
        $ hunt_outcome, time_spent = _return
        "club test end here"
        jump .end

    label .houseparty:

        call get_prey_gender from siren_gpg_houseparty
        $ desired = _return

        "party (maybe?) test - not implemented"
        call default_hunt_subroutine(hunting_pool1, planning_diff, hunting_pool2, strike_diff) from siren_houseparty_goodhunting
        $ hunt_outcome, time_spent = _return
        "siren second option test end"
        jump .end

    label .end:

        "So ends another hunt."

    return hunt_outcome, time_spent


label default_hunt_subroutine(planning_pool, planning_test, feeding_pool, feeding_test):
    python:
        cfg = store.cfg
        V5DiceRoll = game.V5DiceRoll
        time_spent = cfg.STANDARD_HUNT_TIME
        tll_1, tll_2 = "default_hunt_subroutine", "hunting_outcome_generic_sub"

        # TODO: diverge here for predator types with non-human targets(?)
        # TODO: make srue prey is deleted after hunt
        if state.prey:
            del state.prey
        state.prey = game.MortalPrey()
        pns, age_desc = state.prey.pronoun_set, state.prey.apparent_age
        if age_desc.startswith(" "):
            age_desc = "a"
        prey_ref_1 = "{} {}".format(age_desc, pns.PN_STRANGER)
        prey_ref_2 = prey_ref_1.split(" ")[1]
        She_He_They, Shes_Hes_Theyre = str(pns.PN_SHE_HE_THEY).capitalize(), str(pns.PN_SHES_HES_THEYRE).capitalize()

    label .planning_roll:

        call roll_control(planning_pool, planning_test) from generic_hunt_plan_roll
        # jump expression renpy.store.game.rollrouting_pass_fail(_return, ".planning_win", ".planning_fail", top_label=tll_2)
        call expression game.rollrouting_pass_fail(_return, ".planning_win", ".planning_fail", top_label=tll_2) from dhs_planning

    label .feed_roll:
        python:
            fp_mod = None
            if state.roll_bonus > 0:
                fp_mod = state.roll_bonus
            elif state.roll_malus > 0:
                fp_mod = -1 * state.roll_malus

            final_feeding_pool = feeding_pool
        call roll_control(final_feeding_pool, feeding_test, situational_mod=fp_mod) from generic_hunt_strike_roll
        jump expression renpy.store.game.rollrouting_manual(_return, ".win", ".fail", mc=".messy", crit=".crit", bfail=".beastfail", top_label=tll_1)

    label .messy:
        # A dead body, unless you were fishing for bagged blood. You also get here if your hunger is high and you fail a willpower roll.
        $ state.hunted_tonight = True
        $ hunt_outcome = game.V5DiceRoll.RESULT_MESSY_CRIT
        call expression "{}{}".format(tll_2, ".strike_messycrit") from dhs_strike_messycrit
        jump .end

    label .crit:  # You feed successfully and get a bonus.
        $ state.hunted_tonight = True
        $ hunt_outcome = game.V5DiceRoll.RESULT_CRIT
        call expression "{}{}".format(tll_2, ".strike_crit") from dhs_strike_crit
        jump .end

    label .win:  # Successful feeding, hunger slaked depends on margin (1 or 2, up to 3 or 4 if Humanity is low).
        $ state.hunted_tonight = True
        $ hunt_outcome = game.V5DiceRoll.RESULT_WIN
        $ temp_margin, drained = state.active_roll.margin, False
        call expression "{}{}".format(tll_2, ".strike_win") from dhs_strike_win
        jump .end

    label .fail:  # You fail to feed
        $ hunt_outcome = game.V5DiceRoll.RESULT_FAIL
        call expression "{}{}".format(tll_2, ".strike_fail") from dhs_strike_fail
        jump .end

    label .beastfail:  # You fail to feed and get penalized further
        $ hunt_outcome = game.V5DiceRoll.RESULT_BESTIAL_FAIL
        call expression "{}{}".format(tll_2, ".strike_beastfail") from dhs_strike_beastfail
        jump .end

    label .say_flavor(h_phase, h_outcome):
        $ flavor_text = state.pt_flavor_pack.assemble(h_phase, h_outcome)
        call say_script(flavor_text) from hunt_2_sayscript_reroute_1
        return

    label .end:
        call pass_time(time_spent) from default_hunt_subroutine_end
        return hunt_outcome, time_spent

    $ raise ValueError("The game shouldn't ever reach here!")


label pc_prey_gender_dialogue:

    menu:
        beast "So... who are we looking for?"

        "Men.":
            $ state.siren_orientation = cfg.PN_MAN

        "Women":
            $ state.siren_orientation = cfg.PN_WOMAN

        "Someone beyond those categories.":
            $ state.siren_orientation = cfg.PN_PERSON

        "Anyone, as long as they're hot.":
            $ state.siren_orientation = None

    $ state.siren_type_chosen = True

    beast "Lovely. Let's go find someone you like so we can eat."

    return


label get_prey_gender:

    if not state.siren_type_chosen:
        call pc_prey_gender_dialogue from prey_gender_check_default

    if state.siren_orientation is None:
        $ desired = utils.get_random_list_elem([cfg.PN_WOMAN, cfg.PN_MAN, cfg.PN_PERSON])
    else:
        $ desired = state.siren_orientation

    return desired


label hunger_frenzy:

    beast "Blood. BLOOD. FEED FEED FEED FEEDFEEDFEEDFEEDFEEDFEEDFEED"

    "..."
    # TODO: even more nasty consequences (esp. Masquerade), and some crazy sounds

    # masquerade penalty
    python:
        state.masquerade_breach(15)

        hf_kill = utils.percent_chance(0.4)
        hf_innocent = (hf_kill and utils.percent_chance(0.75))
        hf_hours_lost = utils.random_int_range(0, 3)  # 0 to 3 hours lost
        hf_outside_haven = utils.percent_chance(0.5)
        state.set_hunger(0, killed=hf_kill, innocent=hf_innocent)

    call pass_time(hf_hours_lost, in_shelter=not hf_outside_haven) from hunger_frenzy_blackout

    "You come to your senses some time later, your jaw and chest slick with gore. What have you done?"

    jump haven.hub_entry  # TODO: add more varied consequences/places you can end up


label predator_type_subsets:

    label .alley_cat:
        beast "So many pulse-pounding hunts. So many exquisitely exhilarating memories to choose from."

        menu:
            beast "What's your {i}favorite{/i}? Don't be coy; I know you have one..."

            "Once, I hit this drunk guy with a flying tackle and had him limp in my arms before we stopped rolling.  (+Celerity)":
                # +1 Combat, +1 Intimidation, +1 Celerity
                $ state.pc.choose_predator_type(cfg.PT_ALLEYCAT, cfg.DISC_CELERITY)
                beast "And the sound of his head cracking on the pavement! Classic!"

                beast "...I mean, such a {i}shame{/i} about the accident that befell the poor man. We wish him a speedy recovery."

            # "That time I had that muscly, tatted-up gym rat quaking in his sweatsuit.  (+1 Intimidate, +1 Potence)":
            #     # +1 Intimidate, +1 Potence
            #     $ state.pc.choose_predator_type(cfg.PT_ALLEYCAT, cfg.SK_INTI, cfg.DISC_POTENCE)
            #     beast "Isn't it wonderful when the kine, even the \"strong\" ones, instinctively recognize a predator higher than them on the food chain?"

            "Where's the fun if they don't fight back? That one dockworker must have been taking Muay Thai lessons or something, but her blood was a rush of power like I haven't had in a while.  (+Potence) ":
                # +1 Combat, +1 Intimidation, +1 Potence
                $ state.pc.choose_predator_type(cfg.PT_ALLEYCAT, cfg.DISC_POTENCE)
                beast "That one fought like a trapped wolf. She would have mopped the floor with you without my help, hehehe..."

            # "My favorite hunts are the ones where I get what I need as quickly as possible, with as little fuss as possible. (+1 Intimidate, +1 Celerity)":
            #     # +1 Intimidate, +1 Celerity
            #     $ state.pc.choose_predator_type(cfg.PT_ALLEYCAT, cfg.SK_INTI, cfg.DISC_CELERITY)
            #     beast "Fine, be that way."
        return

    label .bagger:
        # +1 Clandestine, +1 Streetwise, +1 Obfuscate
        $ state.pc.choose_predator_type(cfg.PT_BAGGER, cfg.DISC_OBFUSCATE)
        return
        # TODO: implement Blood Sorcery option if Banu Haqim or Tremere are added.

    label .farmer:
        "The blood of animals is never as flavorful or nourishing as human blood, no matter what animal you feed on or how much you drink."

        "But when hunting animals you can sometimes act the predator in ways that wouldn't fly when moving among the kine."

        "There's a certain spiritual satisfaction in the act, which can appease your Beast. ...Somewhat. Sometimes."

        python:
            state.feed_resonance(reso=cfg.RESON_ANIMAL, boost=1)
            is_nerd = False
            if state.pc.mortal_backstory == "Nursing Student" or state.pc.mortal_backstory == "Grad Student":
                is_nerd = True
            if state.pc.disciplines.levels[cfg.DISC_ANIMALISM] > 1:
                anim_token = "but I honed my ability to commune with animals even futher than before."
            else:
                anim_token = "but I learned to... {i}commune{/i} with the animals around me, on some level."
            if state.pc.disciplines.levels[cfg.DISC_PROTEAN] > 1 and is_nerd:
                prot_token = "my ability to change my shape grew more advanced. Like I was adding their genomes to my arsenal or something."
            elif state.pc.disciplines.levels[cfg.DISC_PROTEAN] > 1:
                prot_token = "my ability to change my shape grew even more. Like their blood was teaching me about all the different forms the body can take."
            else:
                prot_token = "I found myself... {i}changing{/i}. Like I was learning to emulate them through their blood, somehow."

        menu:
            beast "A paltry pantomime. I suppose I should be grateful you're not buying pig blood under the table like some thinblooded dreg."

            "I can't tell if it was a result of feeding on so many animals, or if my Blood adapted in order to hunt them better, [anim_token]  (+Animalism)":
                # +1 Traversal, +1 Diplomacy, +1 Animalism
                $ state.pc.choose_predator_type(cfg.PT_FARMER, cfg.DISC_ANIMALISM)

            "As I fed on more and more animals of different kinds, [prot_token]  (+Protean)":
                # +1 Traversal, +1 Diplomacy, +1 Protean
                $ state.pc.choose_predator_type(cfg.PT_FARMER, cfg.DISC_PROTEAN)

        return

    label .siren:
        "Most of the clubs downtown are new, in part because of how many closed down the last time the Inquisition swept through this city."

        "Any Kindred-owned business they managed to learn about was seized, shut down, razed to the ground in an act of \"criminal arson\", or otherwise eliminated."

        "In the aftermath, some enterprising mortal investors made a killing buying up what was left on the cheap."

        "You doubt the profiteering kine have any idea who or what they've been poaching from, but you'll have to be careful nonetheless."

        "You're probably lucky that your antics didn't get you fried along with some of those other licks."

        menu:
            "You think of yourself as a smooth operator, but you won't be able to \"operate\" the way you used to, back when you..."

            "I spent some time making friends (and \"friends\") in a few local kink communities. Great way to feed, or at least it used to be. The experiences also taught me some... {i}interesting{/i} things about myself and my body.  (+Fortitude)":
                # +1 Diplomacy, +1 Intrigue, +1 Fortitude
                $ state.pc.choose_predator_type(cfg.PT_SIREN, cfg.DISC_FORTITUDE)

            "It's all about making the right first impression, and with my aura I {i}always{/i} make the impression I want.  (+Presence)":
                # +1 Diplomacy, +1 Intrigue, +1 Presence
                $ state.pc.choose_predator_type(cfg.PT_SIREN, cfg.DISC_PRESENCE)

        return


label hunt_kill_choice:

    beast "This kine is helpless. Let's drain it. We have to eat well to keep up our strength, don't we?"

    python:
        kill_choice_prompt = "Just let it happen. They were going to die soon anyway. Relatively speaking."
        kill_yes = "I take everything they have to give."
        if state.innocent_drained:
            kill_no = "No, I can't do this again."
        else:
            kill_no = "No, it's not worth it."

    if pc.humanity <= cfg.KILLHUNT_HUMANITY_MAX and pc.hunger > cfg.HUNGER_MAX_CALM:
        $ kill_choice_prompt = "Yes... You know what to do."
        $ kill_yes, kill_no = "I drain them dry and banish the Hunger.", "Nah. Not this time."

    menu:
        beast "[kill_choice_prompt]"

        "[kill_yes]":
            return True

        "[kill_no]":
            return False

    $ raise ValueError("Shouldn't reach here!")

# placeholder
