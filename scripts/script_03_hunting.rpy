# GENERAL HUNT FORMAT:

# 1. Description of journey
# 2. Blurb reflecting current status of PC/city as it relates to hunting conditions, hinting at possible bonuses/penalties
# 3. Phase 1 - locating target; this is the first roll, modified by conditions
# 4. Phase 2 - securing and feeding on the target; this is the second roll, modified by the results of the First
# 5. Aftermath 1 - a messy critical or a failure of willpower roll (if hunger > 3) in phase 2 will result in a kill
# 6. Aftermath 2 - escape is easier if you didn't kill the target; if you did, you need to hide a body and suffer penalties
# 7. Return

# separate first hunt?

label hunt_confirm(pool_desc_raw, hunt_warning, situational_mod=None):
    python:
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
            "Hip young professionals, rich yuppies - all kinds of soft, pliant prey."

            "The kind that tend to eat at upscale restaurants and have cushy gym memberships they may or may not use."

            "But with all that juicy, upwardly mobile prey comes a lot of security."

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

        # call roll_controal("wits+streetwise", "diff3") from hunt_river_phase1

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

            "...but it'd be a pretty humiliating reason to be dragged in front of a local Baron - or worse, the actual Sheriff."

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

            "Clubs and other trendy entertainment venues are choice hunting grounds in almost any city. They're places where the beautiful and energetic gather."

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
            $ desired = utils.get_random_list_elem([cfg.PN_WOMAN, cfg.PN_MAN, cfg.PN_PERSON]) #[0]
        else:
            $ desired = state.siren_orientation

        # TODO: specific hunting text
        call generic_hunt_results("composure+streetwise", "diff3", "charisma+intrigue/charisma+diplomacy", "diff3") from siren_temp_test
        jump .end

    label .party_maybe:

        if state.siren_orientation is None:
            $ desired = utils.get_random_list_elem([cfg.PN_WOMAN, cfg.PN_MAN, cfg.PN_PERSON]) #[0]
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
        $ state.roll_bonus, state.roll_malus = state.active_roll.margin, 0
        $ time_spent = max(time_spent - state.roll_bonus, cfg.MIN_ACTIVITY_TIME)
        "> Successfully scoped out target. Hunt duration reduced to [time_spent] hours, +[state.roll_bonus] to feed roll."
        jump generic_hunt_results.feed_roll

    label .scope_fail:
        $ state.roll_malus, state.roll_bonus = abs(state.active_roll.margin), 0
        $ time_spent = min(time_spent + state.roll_malus, cfg.MAX_HUNT_TIME)
        "> Difficulty scoping out target. Hunt duration increased to [time_spent], -[state.roll_malus] to feed roll."
        jump generic_hunt_results.feed_roll

    label .feed_roll:
        python:
            fp_mod = None
            if state.roll_bonus > 0:
                fp_mod = state.roll_bonus
            elif state.roll_malus > 0:
                fp_mod = -1 * state.roll_malus

            final_feeding_pool = feeding_pool
        call roll_control(final_feeding_pool, feeding_test, situational_mod=fp_mod)
        $ tll = "generic_hunt_results"
        jump expression renpy.store.game.manual_roll_route(_return, ".win", ".fail", mc=".messy", crit=".crit", bfail=".beastfail", top_label=tll)

    label .messy:  # A dead body - you also get here if your hunger is high and you fail a willpower roll
        $ state.hunted_tonight = True

        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        $ state.set_hunger(0, killed=True, innocent=True)
        $ state.feed_resonance(boost=1)
        "You find yourself standing over a dead body. The problem of your Hunger is dealt with, but now you have a different problem."

        if pc.hunger < 1:
            beast "{i}Ahh...{/i} Well done, my friend. Well done. Doesn't that feel so much {i}better{/i}? We should do this more often."
        elif pc.hunger < cfg.HUNGER_MAX_CALM:
            beast "Satisfying... almost."
        else:
            "And even after taking a life some Hunger remains. That's not good."

        stop sound
        play sound audio.body_fall1

        jump .end

    label .crit:  # You feed successfully and get a bonus
        $ state.hunted_tonight = True

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
            "That went great, except for the dead body. That could be a problem."
        else:
            $ state.set_hunger("-=2")
            $ state.feed_resonance(boost=1)
            "That could hardly have gone better."

        stop sound
        if drained:
            play sound audio.body_fall1

        jump .end

    label .win:  # successful feeding, hunger slaked depends on margin (1 or 2, 3 or 4 if humanity is low)
        $ state.hunted_tonight = True
        $ temp_margin, drained = state.active_roll.margin, False

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

        if drained:
            "You drink your fill, basking in warm contentment, and leave the body for your future self to worry about."
            $ state.feed_resonance(boost=1)
        elif slaked_hunger > 3:
            "You drink your fill. Your prey will live, assuming someone notices them in time."
            $ state.feed_resonance()
        elif slaked_hunger > 2:
            "You drink your fill, and leave your prey in a daze. They'll be fine, assuming someone notices them in time."
            $ state.feed_resonance()
        elif slaked_hunger == 2:
            "You drink deeply, but not {i}too{/i} deeply."
            $ state.feed_resonance()
        else:
            "You take a few good gulps; just enough to take the edge off before you have to split."
            $ state.feed_resonance(boost=-1)

        stop sound
        if drained:
            play sound audio.body_fall1

        jump .end

    label .fail:  # You fail to feed
        play sound audio.fleeing_footsteps1

        "That could have gone better. You fail to feed, but manage a clean escape."

        jump .end

    label .beastfail:  # You fail to feed and get penalized further
        play sound audio.fleeing_footsteps1
        queue sound audio.oncoming_frenzy_2

        beast "YOU INCOMPETENT, MISERABLE-"

        "Your vision goes red. There are screams, the sound of shattering glass, and what might have been a gunshot."

        "You come to your senses in an alley."

        $ state.masquerade_breach()
        # TODO: further consequences

        stop sound fadeout 0.5# with fadeout 0.5

        jump .end

    label .end:
        call pass_time(time_spent) from generic_hunt_results_end
        return

    $ raise ValueError("The game shouldn't ever reach here!")


label pc_gender_preference:

    menu:
        beast "So... who are we looking for?"

        "Men.":
            $ state.siren_orientation = cfg.PN_MAN

        "Women":
            $ state.siren_orientation = cfg.PN_WOMAN

        "Someone beyond those categories.":
            $ state.siren_orientation = cfg.PN_PERSON

        "Any of the above, as long as they're hot.":
            $ state.siren_orientation = None

    $ state.siren_type_chosen = True

    beast "Lovely. Let's go find someone you like so we can eat."

    return


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

        "Any Kindred-owned business they managed to learn about was seized, shut down, razed to the ground in a \"terrible act of criminal arson\", or otherwise eliminated."

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
        $ kill_yes = "I drain them dry and banish the Hunger."
        $ kill_no = "Nah. Not this time."

    menu:
        beast "[kill_choice_prompt]"

        "[kill_yes]":
            return True

        "[kill_no]":
            return False

    $ raise ValueError("Shouldn't reach here!")

# placeholder
