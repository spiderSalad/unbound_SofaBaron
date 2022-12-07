init 0 python in cfg:
    from string import ascii_letters, digits

    # NOTE: this persists between game load/cycles, as it's run when Ren'py starts - NOT when the game starts.
    DEV_MODE = True
    DEV_MUTE_MUSIC = False
    KEY_INPUT_ENABLED = False
    KEY_INPUT_WATCH = ascii_letters + digits
    SAVE_FILE_PREFIX = "Sofa_Baron_Save#"

    PATH_IMAGES = "images/"
    PATH_GUI_IMAGES = "gui/"
    PATH_CREDITS_JSON = "credits.json"

    DOT_NUMBERS = ("zero", "one", "two", "three", "four", "five")

    REF_TYPE = "type"
    REF_DESC = "description"
    REF_TOOLTIP = "tooltip"
    REF_DOTS = "dots"
    REF_EID = "eid"
    REF_GOTO_MOMENT = "goto"
    REF_MOMENTS = "moments"
    REF_MID = "mid"
    REF_TEXT = "text"
    REF_CHOICE_PROMPT = "text"
    REF_CHOICES = "choices"
    REF_CHOICE_LABEL = "label"
    REF_CHOICE_ENABLED = "enabled_if"
    REF_CHOICE_SHOWN = "show_if"
    REF_CHOICE_RID = "choice_id"
    REF_STATE_CHANGE_EXPR = "evex"
    REF_EVAL_TAG = "evex"

    REF_MESSYCRIT = "messycrit"
    REF_CRIT = "crit"
    REF_WIN = "win"
    REF_FAIL = "fail"
    REF_BEASTFAIL = "beastfail"
    # REF_ANY_WIN = [REF_WIN, REF_CRIT, REF_MESSYCRIT]
    # REF_ANY_FAIL = [REF_FAIL, REF_BEASTFAIL]

    PN_SHE_HE_THEY = "pn_subjective"
    PN_HER_HIM_THEM = "pn_objective"
    PN_STRANGER = "pn_stranger"

    PN_MEN = {
        PN_SHE_HE_THEY: "he",
        PN_HER_HIM_THEM: "him",
        PN_STRANGER: "man"
    }
    PN_WOMEN = {
        PN_SHE_HE_THEY: "she",
        PN_HER_HIM_THEM: "her",
        PN_STRANGER: "woman"
    }
    PN_NONBINARY = {
        PN_SHE_HE_THEY: "they",
        PN_HER_HIM_THEM: "them",
        PN_STRANGER: "person"
    }

    HUNGER_MAX = 5
    HUNGER_MAX_CALM = 2
    HUNGER_MIN = 1
    HUNGER_MIN_KILL = 0
    MAX_HUMANITY = 8
    MIN_HUMANITY = 4
    KILL_HUNT_HUMANITY_THRESHOLD_INC = 4
    RESIST_MAX_HUNGER_HUMANITY_THRESHOLD_INC = 8
    WEAK_TO_HUNGER_HUMANITY_THRESHOLD_INC = 5

    HUNGER_BLURBS = [
        ["{i}Goddamn{/i} that feels good.", "I feel... whole.", "The emptiness is gone, just for a bit.", "Oh God, what have I done?"],
        ["Eh... I could eat.", "I'm fine...", "I'm good.", "I'm good."],
        ["Time to hunt...", "Time to hunt...", "Eh, I could eat.", "Eh, I could eat."],
        ["Ayyy where my juicebags at?", "Should feed soon...", "Getting pretty hungry...", "It can wait, if need be."],
        ["FEED. NOW.", "'Bout to grab me a fuckin' drink!", "Come on. Mind over matter.", "The Beast doesn't rule me. {i}I{/i} rule me."],
        ["Can't think. Blood...", "FUCKFUCKFUCKFUCKFUCK", "I need to feed before I lose control...", "I need to feed before I lose control..."]
    ]
    HUMANITY_BLURBS = [
        "Loathsome tick",
        "Callous predator",
        "Jaded, cynical leech",
        "Concerned Kindred",
        "Doggedly principled neonate",
        "Serenely absolved undead"
    ]

    MASQUERADE_MAX = 100
    MASQUERADE_MIN = 0

    CLAN_BRUJAH = "Brujah"
    CLAN_NOSFERATU = "Nosferatu"
    CLAN_RAVNOS = "Ravnos"
    CLAN_VENTRUE = "Ventrue"
    CLAN_NONE_CAITIFF = "Caitiff"

    REF_CLAN_EPITHET = "clan_epithet"
    REF_CLAN_NICKNAME = "clan_nickname"
    REF_CLAN_SLUR = "clan_slur"
    REF_CLAN_CHOSEN = "post_choice_text"

    CLAN_BLURBS = {
        CLAN_BRUJAH: {
            REF_CLAN_EPITHET: "the Learned Clan",
            REF_CLAN_NICKNAME: "Rebel",
            REF_CLAN_SLUR: "Rabble"
        },
        CLAN_NOSFERATU: {
            REF_CLAN_EPITHET: "the Clan of the Hidden",
            REF_CLAN_NICKNAME: "Lurker",
            REF_CLAN_SLUR: "Sewer Rat"
        },
        CLAN_RAVNOS: {
            REF_CLAN_EPITHET: "the Doomed Wanderers",
            REF_CLAN_NICKNAME: "Nomad",
            REF_CLAN_SLUR: "Raven"
        },
        CLAN_VENTRUE: {
            REF_CLAN_EPITHET: "the Clan of Kings",
            REF_CLAN_NICKNAME: "Blue Blood",
            REF_CLAN_SLUR: "Tyrant"
        },
        CLAN_NONE_CAITIFF: {
            REF_CLAN_EPITHET: "the Clanless",
            REF_CLAN_NICKNAME: "Orphan",
            REF_CLAN_SLUR: "Trash"
        }
    }

    MAX_SCORE = 5
    MIN_SCORE_ATTR = 1
    MIN_SCORE = 0
    SCORE_WORDS = ["zero", "one", "two", "three", "four", "five"]
    DEFAULT_DOT_COLOR = "red"

    TRACK_HP = "hit_points"
    TRACK_WILL = "willpower"
    DMG_SPF = "superficial_dmg"
    DMG_FULL_SPF = "unhalved_superficial_dmg"
    DMG_AGG = "aggravated_dmg"
    DMG_NONE = "clear"

    REF_ATTRS_ALL = "All Attributes"
    REF_ATTRS = "attrs"
    REF_SKILLS_ALL = "All Skills"
    REF_SKILLS = "skills"

    AT_STR = "Strength"
    AT_DEX = "Dexterity"
    AT_STA = "Stamina"
    AT_CHA = "Charisma"
    AT_MAN = "Manipulation"
    AT_COM = "Composure"
    AT_INT = "Intelligence"
    AT_WIT = "Wits"
    AT_RES = "Resolve"

    REF_PHYSICAL_ATTRS = [AT_STR, AT_DEX, AT_STA]
    REF_SOCIAL_ATTRS = [AT_CHA, AT_MAN, AT_COM]
    REF_MENTAL_ATTRS = [AT_INT, AT_WIT, AT_RES]
    REF_ATTR_ORDER = REF_PHYSICAL_ATTRS + REF_SOCIAL_ATTRS + REF_MENTAL_ATTRS

    SK_ATHL = "Athletics"
    SK_CLAN = "Clandestine"  # Larceny, Stealth
    SK_COMB = "Combat"  # Brawl, Melee
    SK_FIRE = "Firearms"
    SK_TRAV = "Traversal"  # Drive, Survival
    SK_DIPL = "Diplomacy"  # Animal Ken, Etiquette, Persuasion
    SK_INTI = "Intimidation"
    SK_INTR = "Intrigue"  # Insight, Subterfuge
    SK_LEAD = "Leadership"
    SK_STWS = "Streetwise"
    SK_ACAD = "Academics"  # Academics, Politics
    SK_INSP = "Inspection"  # Awareness, Investigation
    SK_OCCL = "Occult"
    SK_SCIE = "Science"  # Science, Medicine
    SK_TECH = "Technology"

    REF_PHYSICAL_SKILLS = [SK_ATHL, SK_CLAN, SK_COMB, SK_FIRE, SK_TRAV]
    REF_SOCIAL_SKILLS = [SK_DIPL, SK_INTI, SK_INTR, SK_LEAD, SK_STWS]
    REF_MENTAL_SKILLS = [SK_ACAD, SK_INSP, SK_OCCL, SK_SCIE, SK_TECH]
    REF_SKILL_ORDER = REF_PHYSICAL_SKILLS + REF_SOCIAL_SKILLS + REF_MENTAL_SKILLS

    ROLL_TEST = "diff"
    ROLL_CONTEST = "pool"
    REF_ROLL_BONUS_PREFIX = "bonus_"
    REF_ROLL_EVENT_BONUS = "bonus_current_event"
    REF_ROLL_FORCE_NOSBANE = "nosbane"
    REF_BG_NAME = "background_name"

    REF_BG_PAST = "Past"  # Collection of stat bonuses, not a merit/flaw in the V5 parlance
    REF_BG_MERIT = "Merit"
    REF_BG_FLAW = "Flaw"

    BG_BEAUTIFUL = "Beautiful"
    BG_ENEMY = "Enemy"

    CHAR_BACKGROUNDS = {
        "Nursing Student": {
            REF_TYPE: REF_BG_PAST, REF_DESC: "You could have become a nurse one day. You could have helped people.",
            REF_ATTRS_ALL: 1, AT_MAN: 1, AT_COM: 1, AT_INT: 1, AT_RES: 1,
            REF_SKILLS_ALL: 1, SK_TECH: 1, SK_SCIE: 2, SK_LEAD: 1, SK_ACAD: 2, SK_INSP: 2, SK_INTI: -1, SK_ATHL: -1, SK_FIRE: -1
        },
        "Star Athlete": {
            REF_TYPE: REF_BG_PAST, REF_DESC: "You can still remember it all. The sweat, the adrenaline, the sun on your face, the cheers...",
            REF_ATTRS_ALL: 1, AT_STR: 1, AT_DEX: 1, AT_STA: 2, AT_CHA: 1, AT_COM: 1, AT_RES: 1,
            REF_SKILLS_ALL: 1, SK_DIPL: 1, SK_LEAD: 1, SK_ACAD: 1, SK_ATHL: 2, SK_OCCL: -1
        },
        "Bartender": {
            REF_TYPE: REF_BG_PAST, REF_DESC: "You exist at the intersection of so many lives. One of the few things that hasn't changed.",
            REF_ATTRS_ALL: 1, AT_STR: -1, AT_DEX: 1, AT_CHA: 2, AT_MAN: 1, AT_COM: 1, AT_WIT: 1,
            REF_SKILLS_ALL: 1, SK_DIPL: 2, SK_INSP: 1, SK_STWS: 2, SK_INTR: 2, SK_TRAV: 1,
            SK_ATHL: -1, SK_FIRE: -1, SK_OCCL: -1, SK_SCIE: -1
        },
        "Veteran": {
            REF_TYPE: REF_BG_PAST, REF_DESC: "The more things change, the more they stay the same.",
            REF_ATTRS_ALL: 1, AT_DEX: 1, AT_STA: 1, AT_CHA: -1, AT_COM: 1, AT_WIT: 2,
            SK_ACAD: 1, SK_ATHL: 2, SK_COMB: 3, SK_TRAV: 2, SK_FIRE: 3, SK_INSP: 2, SK_STWS: 2, SK_INTR: 1, SK_INTI: 3, SK_TECH: 2
        },
        BG_BEAUTIFUL: {REF_TYPE: REF_BG_MERIT, REF_DOTS: 2, REF_DESC: "You've got beguiling, head-turning looks."},
        BG_ENEMY: {
            REF_TYPE: REF_BG_FLAW, REF_DESC: "Some mortal has it out for you. They may even know who you are, though hopefully not {i}what{/i}."
        }
    }

    for key in CHAR_BACKGROUNDS:
        bg = CHAR_BACKGROUNDS[key]
        if REF_TYPE in bg and bg[REF_TYPE] == REF_BG_PAST:
            phys_attr_points, phys_skill_points = 0, 0
            socl_attr_points, socl_skill_points = 0, 0
            ment_attr_points, ment_skill_points = 0, 0
            for key2 in bg:
                val = bg[key2]
                if key2 == REF_ATTRS_ALL:
                    phys_attr_points += val * 3
                    socl_attr_points += val * 3
                    ment_attr_points += val * 3
                elif key2 == REF_SKILLS_ALL:
                    phys_skill_points += val * 5
                    socl_skill_points += val * 5
                    ment_skill_points += val * 5
                elif key2 in REF_PHYSICAL_ATTRS:
                    phys_attr_points += val
                elif key2 in REF_SOCIAL_ATTRS:
                    socl_attr_points += val
                elif key2 in REF_MENTAL_ATTRS:
                    ment_attr_points += val
                elif key2 in REF_PHYSICAL_SKILLS:
                    phys_skill_points += val
                elif key2 in REF_SOCIAL_SKILLS:
                    socl_skill_points += val
                elif key2 in REF_MENTAL_SKILLS:
                    ment_skill_points += val
            attr_points = phys_attr_points + socl_attr_points + ment_attr_points
            skill_points = phys_skill_points + socl_skill_points + ment_skill_points
            print("\"{}\":\nAttr points: ({} physical/{} social/{} mental) ({} total)\nSkill points: ({} physical/{} social/{} mental) ({} total)".format(
                key, phys_attr_points, socl_attr_points, ment_attr_points, attr_points,
                phys_skill_points, socl_skill_points, ment_skill_points, skill_points
            ))


    REF_PREDATOR_TYPE = "predator_type"
    PT_ALLEYCAT = "Alley Cat"  # +1 Combat, +1 Intimidation, +1 Potence, -1 Humanity, +3 Contacts
    PT_BAGGER = "Bagger"  # +1 Clandestine, +Streetwise, +1 Obfuscate, more notoriety
    PT_FARMER = "Farmer"  # +1 Diplomacy, +1 Traversal, +1 Animalism, +1 Humanity, costs willpower to feed on humans
    PT_SIREN = "Siren"  # +1 Diplomacy, +1 Intrigue, +1 Presence, +Beautiful, more notoriety?

    CHAR_PT_STATBLOCKS = {
        PT_ALLEYCAT: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "A true predator, you stalk unwary kine and {i}take{/i} what you need.",
            SK_COMB: 1, SK_INTI: 1, AT_STR: 1
        },
        PT_BAGGER: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "You prefer the bagged stuff, either negotiating or \"negotiating\" for it.",
            SK_CLAN: 1, SK_STWS: 1, AT_INT: 1
        },
        PT_FARMER: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "You don't feed from human beings at all if you can help it, hunting animals instead.",
            SK_DIPL: 1, SK_TRAV: 1, AT_RES: 1
        },
        PT_SIREN: {
            REF_TYPE: REF_PREDATOR_TYPE,
            REF_DESC: "Feeding via seduction is a time-honored classic, and pretty reliable if you're alluring enough.",
            SK_DIPL: 1, SK_INTR: 1, AT_CHA: 1
        }
    }

    # REF_PT_POOLS = {
    #     PT_ALLEYCAT: [
    #         {"Locate a vulnerable target": (AT_WIT, SK_STWS)},
    #         {
    #             "Direct assault": (cfg.AT_STR, SK_COMB),
    #             "Threaten into compliance": (cfg.AT_CHA, cfg.SK_INTI),
    #             "Sneak attack": (cfg.AT_DEX, cfg.SK_CLAN)
    #         }
    #     ],
    #     PT_BAGGER: [
    #         {
    #             "Locate and negotiate with a supplier": (cfg.AT_INT, cfg.SK_STWS),
    #             "Search medical databases": (cfg.AT_RES, cfg.SK_TECH)
    #         },
    #         {
    #             "Fabricate credentials and infiltrate": (cfg.AT_MAN, cfg.SK_ACAD),
    #             "Attempt clandestine retrieval": (cfg.AT_DEX, cfg.SK_CLAN),
    #             "Act like you belong": (cfg.AT_WIT, cfg.SK_INSP)
    #         }
    #     ],
    #     PT_FARMER: [
    #         {"Find a secluded spot for hunting rats and strays": (cfg.AT_RES, cfg.SK_TRAV), "Locate an animal shelter": (cfg.s)},
    #         {""}
    #     ],
    #     PT_SIREN: [
    #
    #     ]
    # }

    DISC_ANIMALISM = "Animalism"
    DISC_CELERITY = "Celerity"
    DISC_DOMINATE = "Dominate"
    DISC_FORTITUDE = "Fortitude"
    DISC_OBFUSCATE = "Obfuscate"
    DISC_POTENCE = "Potence"
    DISC_PRESENCE = "Presence"

    VAL_DISC_LOCKED = 0  # XP multipliers, with 0 meaning locked.
    VAL_DISC_OUTCLAN = float(5) / 7
    VAL_DISC_CAITIFF = float(5) / 6
    VAL_DISC_INCLAN = 1

    POWER_ANIMALISM_FAMULUS = "Bond Famulus"
    POWER_ANIMALISM_SPEAK = "Feral Whispers"
    POWER_ANIMALISM_SUCCULENCE = "Animal Succulence"
    POWER_ANIMALISM_HIVE = "Unliving Hive"
    POWER_ANIMALISM_QUELL = "Quell the Beast"

    POWER_CELERITY_GRACE = "Cat's Grace"
    POWER_CELERITY_TWITCH = "Rapid Reflexes"
    POWER_CELERITY_SPEED = "Fleetness"
    POWER_CELERITY_BLINK = "Blink"

    POWER_DOMINATE_FORGET = "Cloud Memory"
    POWER_DOMINATE_COMPEL = "Compel"
    POWER_DOMINATE_MESMERIZE = "Mesmerize"
    POWER_DOMINATE_DEVOTION = "Slavish Devotion"
    POWER_DOMINATE_REWRITE = "Forgetful Mind"

    POWER_FORTITUDE_HP = "Resilience"
    POWER_FORTITUDE_WILL = "Unswayable Mind"
    POWER_FORTITUDE_TOUGH = "Toughness"
    POWER_FORTITUDE_BANE = "Defy Bane"

    POWER_OBFUSCATE_FADE = "Cloak of Shadows"
    POWER_OBFUSCATE_STEALTH = "Unseen Passage"
    POWER_OBFUSCATE_ILLUSION = "Chimerstry"
    POWER_OBFUSCATE_MASK = "Mask of a Thousand Faces"
    POWER_OBFUSCATE_LAUGHINGMAN = "Ghost in the Machine"

    POWER_POTENCE_FATALITY = "Lethal Body"
    POWER_POTENCE_SUPERJUMP = "Soaring Leap"
    POWER_POTENCE_PROWESS = "Prowess"
    POWER_POTENCE_MEGASUCK = "Brutal Feed"
    POWER_POTENCE_RAGE = "Spark of Rage"

    POWER_PRESENCE_AWE = "Awe"
    POWER_PRESENCE_DAUNT = "Daunt"
    POWER_PRESENCE_ENTRANCE = "Entracement"
    POWER_PRESENCE_SCARYFACE = "Dread Gaze"

    REF_DISC_POWER_TREES = {
        DISC_ANIMALISM: [
            [POWER_ANIMALISM_FAMULUS],
            [POWER_ANIMALISM_SPEAK],
            [POWER_ANIMALISM_HIVE, POWER_ANIMALISM_QUELL, POWER_ANIMALISM_SUCCULENCE]
        ],
        DISC_CELERITY: [
            [POWER_CELERITY_GRACE, POWER_CELERITY_TWITCH],
            [POWER_CELERITY_SPEED],
            [POWER_CELERITY_BLINK]
        ],
        DISC_DOMINATE: [
            [POWER_DOMINATE_COMPEL, POWER_DOMINATE_FORGET],
            [POWER_DOMINATE_MESMERIZE, POWER_DOMINATE_DEVOTION],
            [POWER_DOMINATE_REWRITE]
        ],
        DISC_FORTITUDE: [
            [POWER_FORTITUDE_HP, POWER_FORTITUDE_WILL],
            [POWER_FORTITUDE_TOUGH],
            [POWER_FORTITUDE_BANE]
        ],
        DISC_OBFUSCATE: [
            [POWER_OBFUSCATE_FADE],
            [POWER_OBFUSCATE_STEALTH, POWER_OBFUSCATE_ILLUSION],
            [POWER_OBFUSCATE_MASK, POWER_OBFUSCATE_LAUGHINGMAN]
        ],
        DISC_POTENCE: [
            [POWER_POTENCE_FATALITY, POWER_POTENCE_SUPERJUMP],
            [POWER_POTENCE_PROWESS],
            [POWER_POTENCE_MEGASUCK, POWER_POTENCE_RAGE]
        ],
        DISC_PRESENCE: [
            [POWER_PRESENCE_AWE, POWER_PRESENCE_DAUNT],
            [],
            [POWER_PRESENCE_ENTRANCE, POWER_PRESENCE_SCARYFACE]
        ]
    }

    SEM_HUB_MAIN = "haven-hub-default"

    REP_MIN = 0 # -100
    REP_MAX = 200 # 100
    REP_VALUE_ADJUST = 100

    TOOLTIP_TABLE = {  # TODO finish these
        AT_STR: "Lifting, pulling, pushing, punching, kicking, etc.",
        AT_DEX: "Coordination, acuity, speed. Everything from sprinting to aiming a gun.",
        AT_STA: "How much punishment I can take if I have to. Or want to.",
        AT_CHA: "Getting people to like me, fear me, want me. Making them {i}feel{/i}.",
        AT_MAN: "Getting people to do what I say, however they feel about me.",
        AT_COM: "Staying cool in the moment so I don't lose my shit again.",
        AT_INT: "Learning, reasoning, problem-solving, memory. The stuff they're always trying to test people for.",
        AT_WIT: "Reaction, intuition, thinking on your feet!",
        AT_RES: "Focus and determination not to let things go like before.",

        SK_ATHL: "Experience, form, and training for various types of coordinated physical exertion.",
        SK_CLAN: "Sneaking around, breaking into things, etc. Doing dirt.",
        SK_COMB: "Throwing hands, or wielding the kinds of weapons that you bash, cut, or stab with.",
        SK_FIRE: "Handling and using guns. Blue Bloods don't get to do superhero shit like the other Clans, so coming strapped is a good idea.",
        SK_TRAV: "sdfdsfdsfdsfdsHandling a car beyond just getting from point A to point B.",
        SK_INTI: "Getting people to back off or fall in line without resorting to mind control.",
        SK_INTR: "Dissembling, sophistry, subtlety, and straight up lies. Concealing motives and intentions.",
        SK_LEAD: "DFdsfdsThe skills and wherewithal to play the necessary role, whether that's dancing well or using proper etiquette.",
        SK_DIPL: "Getting people to genuinely see things my way.",
        SK_STWS: "What's really going on in this city? How do things work on the margins?",
        SK_ACAD: "All of the assorted knowledge I've accumulated, from grade school to dropping out of college.",
        SK_INSP: "Paying attention at the right time. Methodical collection and analysis of information and evidence in the field.",
        SK_OCCL: "Supernatural stuff and how it works. I guess it makes sense that if vampires exist, so would other things.",
        SK_SCIE: "",
        SK_TECH: "In my line of work this is mostly worrying about encryption and hardware security for laptops and smartphones."
    }

    MERIT_DISPLAY_MAX = 4

    DP_DISCLAIMER = "This game was created as a part of Vampire: The Masquerade game jam. "
    DP_DISCLAIMER += "Events portrayed in this game are not canon within World of Darkness."


image bg city main_menu         = "gui/main_menu.png"
image bg haven basic            = "images/bg_haven.jpg"
image bg domain basic           = "images/bg_domain.jpg"

define audio.main_theme         = "audio/music/Darkstar83 - Shadow Walker.mp3"

define audio.gui_heartbeat      = "audio/sound/86886__timbre__74829-jobro-heartbeat-timbre-s-variant-1b-loop.mp3"
define audio.beastgrowl1        = "audio/sound/344903__aegersum__monster-deep-growl.mp3"
define audio.beastgag           = "audio/sound/347541__pfranzen__human-impression-of-cat-hacking-up-hairball.ogg"
define audio.feed_bite1         = "audio/sound/400174__jgriffie919__flesh-bite.mp3"
define audio.feed_heartbeat     = "audio/sound/608241__newlocknew__heart-beat-calm-rhythm-blood-flows-in-the-veins-6lrs.mp3"
define audio.body_fall1         = "audio/sound/372226__eflexmusic__bodyfall-3-mixed.mp3"
define audio.body_fall2         = "audio/sound/502553__kneeling__goblin-fall.mp3"
define audio.footsteps1         = "audio/sound/318900__robinhood76__05934-heels-walking-on-pavement-looping.mp3"
define audio.dice_roll_many     = "audio/sound/220744__dermotte__dice-06.mp3"
define audio.dice_roll_few      = "audio/sound/353975__nettimato__rolling-dice-1.mp3"
define audio.fleeing_footsteps1 = "audio/sound/316924__rudmer-rotteveel__footsteps-running-away-fading.mp3"
