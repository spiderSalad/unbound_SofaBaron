# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define you = Character("You")
define beast = Character("The Beast", color="#e90505")
define james = Character("Man", color="#662222")


# The game starts here.

label start:

    if cfg.DEV_MUTE_MUSIC:
        stop music

    if cfg.DEV_MODE:
        jump intro

    stop music fadeout 1.0

    scene black with fade

    "Content warning: (Somewhat graphic descriptions of) violence, blood, alcohol, addiction, mental illness, emotional abuse."

    "Some sexual content, if you pick the option that mentions it. Lots of profanity."

    "..."

    jump intro


label intro:

    python:
        cfg, game = renpy.store.cfg, renpy.store.game
        state.pc = game.PlayerChar(anames=state.attr_names, snames=state.skill_names, dnames=state.discipline_names)
        state.pc.inventory = game.Inventory()
        state.statusfx = state.StatusFX(pc=state.pc)
        # state.give_item(game.Item(game.Item.IT_MONEY, "Cash", key="Money", tier=0, num=15, desc="Cash on hand."))
        state.give_item(state.get_random_cash())
        state.clock = state.GameClock(1, 9)
        state.diceroller_creation_count = 0

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg city main_menu

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    # show eileen happy

    if cfg.DEV_MODE:
        $ state.blood_surge_enabled = True
        show screen bl_corner_panel
        jump devtests.dt_combat_a1

    # start at hunger 3
    $ state.set_hunger(3)
    # play sound audio.beastgrowl1

    "You awaken the moment the sun goes down, and find yourself lying in a pile of garbage."

    james "Holy shit, you're alive! Thought for sure you was dead."

    "The return to consciousness is jarring, almost painful. Not at all like waking up from natural sleep, like you used to do. The man kneeling at your side reeks of cheap booze and body odor, but the concern on his face seems genuine."

    james "You alright? You wasn't movin' at all. Like a dead body or something."

    "At that, you instinctively practice your breathing. In and out. In... and out..."

    "How you ended up in this dirty back alley is a question for later. For now, there's the matter of this man who saw you - and apparently spent some time around you - while you were compromised."

    "You're not bound by the Tower or its rules, but like every other tick in this city you have a {i}visceral{/i} understanding of what happens when enough idiots violate the First of their \"Traditions\"."

    "The Masquerade."

    "The mortal masses have to be kept in the dark. The more they see, the more they learn, the more they talk, the more likely they are to draw the attention of the Inquisition's hunters."

    "And that can't happen here. Not again."

    $ state.blood_surge_enabled = True
    show screen bl_corner_panel

    menu:
        beast "He's seen too much. He has to go. Drain him."

        "He's seen too much so he has to go. Plus, I'm hungry. Let's get this over with - two birds with one stone.":
            "The man sees the look on your face and takes a step back."

            james "H-hey hold on, now-"

            call roll_control("dexterity+athletics+2", "pool3") from drain_james
            jump expression renpy.store.game.pass_fail(_return, "intro.man_drained", "intro.man_escapes_drain")

        "Let him go. He only saw me \"passed out\" on the street. And who would believe a homeless drunk anyway?":
            jump intro.man_spared

        "I'm not going to kill this man just for being here. I don't even know how {i}I{/i} got here. But I could sure use a snack.":
            "You flash him a sheepish grin."

            you "Last night was pretty crazy. You got the time?"

            "He actually does have a watch, surprisingly. When he glances down, you strike."

            james "Someone musta took your phone, huh? It's abou-"

            call roll_control("manipulation+intrigue+looks+1", "diff2") from sip_james
            jump expression renpy.store.game.pass_fail(_return, "intro.man_sipped", "intro.man_escapes_sip")

    label .man_drained:

        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        "His instincts kick in just a bit too late. He doesn't even have time to scream. Once your fangs are in he goes limp, like all the rest. A few minutes later and you've taken {i}everything{/i}."

        $ state.set_hunger(0, killed=True, innocent=True)
        $ state.feed_resonance(boost=1, reso=(cfg.RESON_MELANCHOLIC, cfg.RESON_PHLEGMATIC))
        $ state.feed_resonance(intensity=cfg.RINT_FLEETING, reso=cfg.RESON_CHOLERIC)
        $ state.intro_man_drank = state.intro_man_killed = state.innocent_killed = state.innocent_drained = True

        "Everything he is, was, and could have been pours down your throat and floods into your veins. There's a pleasant coppery tang, and an incredible rush. For once you feel... whole."

        stop sound
        play sound audio.body_fall1

        "But you know it won't last, and you have business to attend to."

        jump intro.end

    label .man_escapes_drain:

        "Maybe you're still sluggish from daysleep, or maybe the man is quicker than he looked. Either way, something in your eyes spooked him, tipped him off."

        play sound fleeing_footsteps1

        "He staggers back and spins on his heels in an impressively smooth motion, and runs away without a word. You could chase him, but that would probably just make things worse."

        $ state.masquerade_breach(base=5)

        "That could have gone better. No breakfast for you, it seems."

        jump intro.end

    label .man_spared:

        "Marshalling your will to hold the Beast in check, you force your face into what you hope looks like a sheepish grin."

        beast "Weak."

        you "Nah, I'm fine. Just... partied a bit too hard."

        james "Hah! I was young too, once 'pon a time. But it's rough out here, so you might wanna ease up a bit."

        "You raise an eyebrow at that, and make a show of looking him up and down."

        james "I ain't got nothin' left to lose, youngin'. You look like you might."

        "You smile sadly, shake his hand, and set on your way."

        jump intro.end

    label .man_sipped:

        play sound audio.feed_bite1
        queue sound audio.feed_heartbeat

        "He goes limp the moment your fangs pierce his neck, moaning softly. You take a few good mouthfuls - just enough to take the edge off. Then you gently lower him to the ground, lick the puncture wounds on his neck away, and set off into the night."

        $ state.set_hunger("-=1")
        $ state.feed_resonance(reso=(cfg.RESON_MELANCHOLIC, cfg.RESON_PHLEGMATIC))
        $ state.intro_man_drank = True

        stop sound

        jump intro.end

    label .man_escapes_sip:

        james "The fuck you doin'?"

        play sound fleeing_footsteps1

        "He doesn't wait for your response. Just turns on his heels and runs. It'd probably be a bad idea to chase him, and you don't think he saw your fangs."

        "So much for that snack."

        jump intro.end

    label .end:

        #jump haven.hub_entry
        jump backstory


label backstory:

    $ state = renpy.store.state
    # TODO: add flavor to make this more interesting later, same with clan and predator type choices

    if state.intro_man_drank and state.intro_man_killed:
        $ blurb_having = "Having slaked your Hunger and eaten the only witness (you doubt anyone will find the body in time for it to seem unusual), "
    elif state.intro_man_drank:
        $ blurb_having = "Having temporarily brought your endless Hunger under control, "
    elif state.intro_man_killed:
        $ blurb_having = "Having dealt with that minor Masquerade breach, "
    else:
        $ blurb_having = "Doing your best to ignore the Hunger gnawing at the back of your brain, "

    "[blurb_having]you begin the long trek back to your haven."

    "It takes a few minutes for you to figure out where you actually are, but eventually you spot a familiar underpass and head north."

    if state.pc.hunger > 2:
        $ blurb_having = "Even with the throbbing ache in your head that burns its way down into your gums and behind your eyes, the "
    else:
        $ blurb_having = "The "

    "[blurb_having]walk is long enough that your mind begins to drift."

    "Back to the days when you walked in the sun, before the life was drained from you in a twitching paroxysm of pleasure and horror and shame."

    "Before the deep, black, numb {i}nothingness{/i} that felt like an eternity. (Later you learned it was less than an hour.)"

    "Before the red-hot hooks of the Hunger burrowed down to your core and dragged you from the void, kicking and screaming."

    "It wasn't {i}that{/i} long ago in the grand scheme of things. You're still a neonate, after all."

    menu:
        "But before, you were..."

        "A nursing student in residency.":
            $ state.pc.mortal_backstory = "Nursing Student"

        "A star athlete, attending college on a scholarship.":
            $ state.pc.mortal_backstory = "Star Athlete"

        "Bartender and host at a club across town.":
            $ state.pc.mortal_backstory = "Bartender"

        "A veteran between jobs and houses.":
            $ state.pc.mortal_backstory = "Veteran"

        "Pursuing your Master's in Chemical Engineering":
            $ state.pc.mortal_backstory = "Grad Student"

        "A D-list influencer.":
            $ state.pc.mortal_backstory = "Influencer"

    $ state.pc.apply_background(cfg.CHAR_BACKGROUNDS[state.pc.mortal_backstory], bg_key=state.pc.mortal_backstory)

    beast "Enough navel-gazing, \"[state.pc.mortal_backstory]\". We're almost home."

    # if cfg.DEV_MODE:
    #     $ state.pc.hp.damage(cfg.DMG_AGG, 3)

    "And you are, though you take a circuitous route that doubles back on itself a few times. Less likely you're followed that way."

    call pass_time(1) from intro_post_mortal_bg
    jump haven.hub_entry


label clan_choice:

    "Here you're as safe and secure as you'll ever be, unless you somehow manage to improve your rather dismal situation."

    python:
        clan_choice_brujah = "{}, Clan {}".format(cfg.CLAN_BLURBS[cfg.CLAN_BRUJAH][cfg.REF_CLAN_EPITHET], cfg.CLAN_BRUJAH)
        # clan_choice_brujah = str(clan_choice_brujah).capitalize()
        clan_choice_nosferatu = "{}, Clan {}".format(cfg.CLAN_BLURBS[cfg.CLAN_NOSFERATU][cfg.REF_CLAN_EPITHET], cfg.CLAN_NOSFERATU)
        # clan_choice_nosferatu = str(clan_choice_nosferatu).capitalize()
        clan_choice_ravnos = "{}, Clan {}".format(cfg.CLAN_BLURBS[cfg.CLAN_RAVNOS][cfg.REF_CLAN_EPITHET], cfg.CLAN_RAVNOS)
        # clan_choice_ravnos = str(clan_choice_ravnos).capitalize()
        clan_choice_ventrue = "{}, Clan {}".format(cfg.CLAN_BLURBS[cfg.CLAN_VENTRUE][cfg.REF_CLAN_EPITHET], cfg.CLAN_VENTRUE)
        # clan_choice_ventrue = str(clan_choice_ventrue).capitalize()
        clan_choice_caitiff = "I am Clanless - one of the so-called Caitiff"

    menu:
        "As a member of-"

        "[clan_choice_brujah]":
            $ state.pc.choose_clan(cfg.CLAN_BRUJAH)
            $ state.clan_slur = pc.clan_blurbs[cfg.REF_CLAN_SLUR]
            "\"The Learned Clan\". Someone's idea of a joke, you guess."

            "Or maybe not. Apparently your Clan used to be something more than ornery ticks scrabbling in the dirt."

            "At least the other breeds of tick understand that your Clan bites hardest. Smart Kindred think twice before pissing off even the lowliest [state.clan_slur]. In person, anyway."

            "You often struggle to control your temper. Even more so than what's normal for vampires, or so you've been told."

        "[clan_choice_nosferatu]":
            $ state.pc.choose_clan(cfg.CLAN_NOSFERATU)
            "You were twisted and disfigured by your Embrace. You don't have it as bad as some of your cousins who have to stay down in the communal warrens - you can at least pass as human. Mostly. From a respectable distance."

            "And in these modern nights there are plenty of ways to conceal or explain away the rest. But no matter what you do mortals still seem to get uneasy when you get close. Even Kindred of other clans tend not to appreciate your presence."

            $ state.masquerade_redemption(10)

        "[clan_choice_ravnos]":
            $ state.pc.choose_clan(cfg.CLAN_RAVNOS)
            "You feel it in your daysleep sometimes - a scream in a language you don't know. Loud like a roaring furnace, quiet like the hum of an incandescent bulb. Hotter than you could ever describe."

            "You instinctively understood what would happen if you let it catch you. If you didn't {i}move{/i}. Every night, before dawn. Like a shark - if you stop moving for long enough, you die."

        "[clan_choice_ventrue]":
            $ state.pc.choose_clan(cfg.CLAN_VENTRUE)
            "You sometimes envy other vampires who are just out there drinking anybody. Members of your clan usually have specific dietary requirements, though it's different for every Blue Blood. Not just any mortal will do."

            $ state.give_item(state.get_random_cash(boost=1))

            call ventrue_feeding_choice from clan_choice_ventrue_1

        "[clan_choice_caitiff]":
            $ state.pc.choose_clan(cfg.CLAN_NONE_CAITIFF)
            "Out here, in the places the Camarilla has deemed beneath them, there's less need to hide it. Though you certainly don't advertise."

            "You claim no Blood, and no Blood claims you. You don't remember your Embrace and God knows who your sire might be. {i}Proper{/i} Kindred tend to look down on your kind."

            "If you're lucky, that is - in some domains you're treated no better than the thin-bloods, who aren't even real vampires!"

            "There are upsides, of course. Other Kindred argue in hushed whispers about the nature of the Clans and their Banes. None of that shit is your problem."

            "But you're adrift and unmoored in Kindred society, even by Anarch standards."

    python:
        state.clan_chosen = True
        if not state.clan_slur:
            state.clan_slur = pc.clan_blurbs[cfg.REF_CLAN_SLUR]
        if not state.clan_nickname:
            state.clan_nickname = pc.clan_blurbs[cfg.REF_CLAN_NICKNAME]

    "That can make things difficult, but over those first few horrifying months you learned to adapt, drawing on skills and experiences from your mortal life."

    beast "We are all inexorably shaped by our pasts. Even the Blood resonates with it."

    # call pick_first_powers from intro_discipline_choice_v1
    "(You can choose from available discipline powers by clicking on a discipline's name on the Powers panel.)"

    "You've also learned to adapt where it most counts. The hunt."

    menu:
        beast "We'll do it your way. For now."

        "I skip all the pretense and bullshit and just {i}take{/i} what I need. It ain't pretty, but it's usually quick and simple.":
            "Your hunting blends in nicely with the city's mundane mortal crime. As long as you're careful and don't leave any obviously exsanguinated corpses lying around, things tend to work out okay."
            call predator_type_subsets.alley_cat from intro_pt_choice_alley_cat

        "I didn't hunt my own food when I was alive. Why start now? I just drink the bagged stuff. Less dangerous." if state.pc_can_drink_swill():
            "Realistically it's just a different kind of danger. Blood is a commodity even among mortals, and it tends to be closely watched."

            "Statistical abnormalities or a careless lick caught on the wrong camera feed can draw the attention of law enforcement and hunters alike. But that's a less direct kind of danger, the kind you're much better at managing."
            call predator_type_subsets.bagger from intro_pt_choice_bagger

        "I feed on animals, usually. City's chock full of animals if you know where to look." if state.pc_can_drink_swill():
            if state.intro_man_killed:
                "Hunting animals is easier and safer than hunting people. Nobody notices or cares if vermin or strays go missing."
            else:
                "Hunting animals is a bit easier on the conscience, and a lot safer. Nobody notices or cares if vermin or strays go missing."

            "Other licks can say what they like. Just means more rat for you."
            call predator_type_subsets.farmer from intro_pt_choice_farmer

        "My favorite way to feed is during sex. One pleasure heightens the other, for everyone involved.":
            "Fucking your food is.... a choice. A choice you'd make {i}every{/i} time, if you could."
            call predator_type_subsets.siren from intro_pt_choice_siren

    # No time passes here
    jump haven.hub_main


label ventrue_feeding_choice:

    "Your \"palate\" manifested itself over time. At first you could feed at will, but as the nights went by you found it harder and harder to drink from most people."

    menu:
        "With one increasingly clear exception."

        "People who are used to giving orders.":  # +2 to Dominate
            $ chosen_palate = cfg.REF_VENTRUE_TARGET_COMMANDERS
            "(ventrue type is commanders)"

        "People in physical pain.":  # +2 to Fortitude
            $ chosen_palate = cfg.REF_VENTRUE_TARGET_PAINED
            "(ventrue type is pained)"

        "People who spend a lot of time or money maintaining their appearance.":  # +2 to Presence
            $ chosen_palate = cfg.REF_VENTRUE_TARGET_PEACOCKS
            "(ventrue type is peacocks)"

    python:
        pc.apply_background(cfg.VENTRUE_PREF_BACKGROUNDS[chosen_palate])
        if not state.ventrue_palate:
            state.ventrue_palate = chosen_palate
            if state.ventrue_palate != cfg.REF_VENTRUE_TARGET_PAINED and state.intro_man_drank:
                state.deal_damage(cfg.TRACK_WILL, cfg.DMG_FULL_SPF, 2, source="Fed on James when he's not your Ventrue type")

    return


label end:

    # This ends the game.
    if state.pc.cause_of_death == cfg.COD_SUN:
        "Unable to escape the merciless wrath of the sun, you crumple to the ground in a smoldering heap."

        "By that time, of course, your mind is long gone."
    else:
        "The ability of the vampiric to absorb punishment that would kill a mortal several times over is nothing short of extraordinary."

        "But it has its limits, and in your case they've been reached. Your unnatural body begins to behave like the corpse it is."

        "For a moment it seems as if you can feel yourself being lowered back into that pit of absolute emptiness."

        "The one you were dragged out of so many years ago. The Hunger is gone. The need is gone."

        "There's just nothing."

    "And so ends your unlife. Thanks for playing."

    $ MainMenu(confirm=False)()

    # return
