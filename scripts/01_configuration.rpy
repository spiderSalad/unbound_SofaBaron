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
    REF_SUBTYPE = "subtype"
    REF_DESC = "desc"
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

    CT_ANIMAL = "Animal"
    CT_FAMULUS = "Ghoul (Animal)"
    CT_HUMAN = "Human"
    CT_GHOUL = "Ghoul (Human)"
    CT_VAMPIRE = "Kindred"
    CT_LUPINE = "Werewolf"

    REF_MORTALS = [CT_ANIMAL, CT_FAMULUS, CT_HUMAN, CT_GHOUL, CT_LUPINE]  # TODO: revisit this for lupines
    REF_UNDEAD = [CT_VAMPIRE]

    # Pronouns
    PN_SHE_HE_THEY = "pn_subjective"
    PN_HER_HIM_THEM = "pn_objective"
    PN_STRANGER = "pn_stranger"
    PN_HER_HIS_THEIR = "pn_possessive"
    PN_SHES_HES_THEYRE = "pn_descriptive"
    PN_SHELL_HELL_THEYLL = "pn_predictive"

    PN_MAN = object()
    PN_MAN.PN_SHE_HE_THEY = "he"
    PN_MAN.PN_HER_HIM_THEM = "him"
    PN_MAN.PN_STRANGER = "man"
    PN_MAN.PN_HER_HIS_THEIR = "his"
    PN_MAN.PN_SHES_HES_THEYRE = "he's"
    PN_MAN.PN_SHELL_HELL_THEYLL = "he'll"

    PN_WOMAN = object()
    PN_WOMAN.PN_SHE_HE_THEY = "she"
    PN_WOMAN.PN_HER_HIM_THEM = "her"
    PN_WOMAN.PN_STRANGER = "woman"
    PN_WOMAN.PN_HER_HIS_THEIR = "her"
    PN_WOMAN.PN_SHES_HES_THEYRE = "she's"
    PN_WOMAN.PN_SHELL_HELL_THEYLL = "she'll"

    PN_NONBINARY_PERSON = object()
    PN_NONBINARY_PERSON.PN_SHE_HE_THEY = "they"
    PN_NONBINARY_PERSON.PN_HER_HIM_THEM = "them"
    PN_NONBINARY_PERSON.PN_STRANGER = "person"
    PN_NONBINARY_PERSON.PN_HER_HIS_THEIR = "their"
    PN_NONBINARY_PERSON.PN_SHES_HES_THEYRE = "they're"
    PN_NONBINARY_PERSON.PN_SHELL_HELL_THEYLL = "they'll"

    print("\n---\nman:{}\nwoman: {}\nenby: {}".format(PN_MAN, PN_WOMAN, PN_NONBINARY_PERSON))
    print("\n\npn man:\n{}".format(
        "\n".join(["{}:  {}".format(key, getattr(PN_MAN, key)) for key in PN_MAN.__dict__])
    ))

    HUNGER_MAX = 5
    HUNGER_MAX_CALM = 2
    HUNGER_MIN = 1
    HUNGER_MIN_KILL = 0
    MAX_HUMANITY = 8
    MIN_HUMANITY = 4
    KILLHUNT_HUMANITY_MAX = 4
    RESIST_MAX_HUNGER_HUMANITY_THRESHOLD_INC = 8
    WEAK_TO_HUNGER_HUMANITY_THRESHOLD_INC = 5

    MIN_ACTIVITY_TIME = 1
    STANDARD_HUNT_TIME = 3
    MAX_HUNT_TIME = 6

    HUNGER_BLURBS = [
        ["{i}Goddamn{/i} that feels good.", "I feel... whole.", "The emptiness is gone, just for a bit.", "Oh God, what have I done?"],
        ["Eh... I could eat.", "I'm fine...", "I'm good.", "I'm good."],
        ["Time to hunt...", "Time to hunt...", "Eh, I could eat.", "Eh, I could eat."],
        ["Ayyy where my juicebags at?", "Should feed soon...", "Getting pretty hungry...", "It can wait, if need be."],
        ["FEED. NOW.", "'Bout to grab me a fuckin' drink!", "Come on. Mind over matter.", "The Beast doesn't rule me. {i}I{/i} rule me."],
        [
            "Can't think. Blood...", "FUCKFUCKFUCKFUCKFUCK",
            "I need to feed before I lose control...", "I need to feed before I lose control..."
        ]
    ]
    HUMANITY_BLURBS = [
        "Loathsome tick",
        "Callous predator",
        "Jaded, cynical leech",
        "Concerned Kindred",
        "Doggedly principled neonate",
        "Serenely absolved undead"
    ]

    VAL_MASQUERADE_MAX = 100
    VAL_MASQUERADE_MIN = 0
    VAL_NOTORIETY_MIN = 0
    VAL_NOTORIETY_MAX = 100
    VAL_BASE_NOTORIETY_MULTIPLIER = 0.8

    CLAN_BRUJAH = "Brujah"
    CLAN_NOSFERATU = "Nosferatu"
    CLAN_RAVNOS = "Ravnos"
    CLAN_VENTRUE = "Ventrue"
    CLAN_NONE_CAITIFF = "Caitiff"

    REF_PLAYABLE_CLANS = [CLAN_BRUJAH, CLAN_NOSFERATU, CLAN_RAVNOS, CLAN_VENTRUE]

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

    # REF_VENTRUE_TARGET_COMMANDERS = "commanders"
    # REF_VENTRUE_TARGET_PAINED = "pained"
    # REF_VENTRUE_TARGET_PEACOCKS = "peacocks"

    MAX_SCORE = 5
    MIN_SCORE_ATTR = 1
    MIN_SCORE = 0
    SCORE_WORDS = ["zero", "one", "two", "three", "four", "five"]
    DEF_DOT_COLOR = "red"

    TRACK_HP = "hit_points"
    TRACK_WILL = "willpower"
    DMG_SPF = "superficial_dmg"
    DMG_FULL_SPF = "unhalved_superficial_dmg"
    DMG_AGG = "aggravated_dmg"
    DMG_NONE = "clear"

    BULLET_DODGE_PENALTY = 2
    WEAPON_DRAW_PENALTY = 2

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

    NPCAT_PHYS = "physical"
    NPCAT_SOCL = "social"
    NPCAT_MENT = "mental"

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
    # ROLL_NPC_COMBAT_ACTION = "enemy"  # Special contest in which NPC action gets run through
    REF_ROLL_BONUS_PREFIX = "bonus_"
    REF_ROLL_EVENT_BONUS = "bonus_current_event"
    # REF_ROLL_BLOOD_SURGE_BONUS
    REF_BLOOD_SURGE = "Blood Surge"
    REF_ROLL_LOOKS = "Looks"
    REF_BG_NAME = "background_name"

    REF_BG_PAST = "Past"  # Collection of stat bonuses, not a merit/flaw in the V5 parlance
    REF_BG_MERIT = "Merit"
    REF_BG_FLAW = "Flaw"
    REF_BG_LOOKS = "Looks"

    BG_BEAUTIFUL = "Beautiful"
    BG_ENEMY = "Enemy"
    BG_UGLY = "Ugly"
    BG_REPULSIVE = "Repulsive"

    REF_VENTRUE_PALATE = "ventrue_palate"
    REF_PREDATOR_TYPE = "predator_type"
    PT_ALLEYCAT = "Alley Cat"  # +1 Combat, +1 Intimidation, +1 Potence, -1 Humanity, +3 Contacts
    PT_BAGGER = "Bagger"  # +1 Clandestine, +Streetwise, +1 Obfuscate, more notoriety
    PT_FARMER = "Farmer"  # +1 Diplomacy, +1 Traversal, +1 Animalism, +1 Humanity, costs willpower to feed on humans
    PT_SIREN = "Siren"  # +1 Diplomacy, +1 Intrigue, +1 Presence, +Beautiful, more notoriety?

    CHAR_PT_STATBLOCKS = {
        PT_ALLEYCAT: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "A true predator, you stalk unwary kine and {i}take{/i} what you need.",
            SK_COMB: 1, SK_INTI: 1
        },
        PT_BAGGER: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "You prefer the bagged stuff, either negotiating or \"negotiating\" for it.",
            SK_CLAN: 1, SK_STWS: 1
        },
        PT_FARMER: {
            REF_TYPE: REF_PREDATOR_TYPE, REF_DESC: "You don't feed from human beings at all if you can help it, hunting animals instead.",
            SK_DIPL: 1, SK_TRAV: 1
        },
        PT_SIREN: {
            REF_TYPE: REF_PREDATOR_TYPE,
            REF_DESC: "Feeding via seduction is a time-honored classic, and pretty reliable if you've got charm or allure.",
            SK_DIPL: 1, SK_INTR: 1
        }
    }

    REF_RESONANCE = "Resonance"
    VAL_RESONANCE_GUI_MAX = 1000

    RESON_ANIMAL = "Animal"  # Animalism, Protean
    RESON_CHOLERIC = "Choleric"  # Celerity, Potence
    RESON_MELANCHOLIC = "Melancholic"  # Fortitude, Obfuscate
    RESON_PHLEGMATIC = "Phlegmatic"  # Auspex, Dominate
    RESON_SANGUINE = "Sanguine"  # Blood Sorcery, Presence
    RESON_EMPTY = "\"Empty\""  # Oblivion
    RESON_VARIED = "Varied"  # Thinblood Alchemy

    VAL_RESON_COLORS = {
        RESON_ANIMAL: "#da8a18",
        RESON_CHOLERIC: "#faf604",
        RESON_MELANCHOLIC: "#36347c",
        RESON_PHLEGMATIC: "#09f3a2",
        RESON_SANGUINE: "#f73939",
        RESON_EMPTY: "#101010"
    }

    RINT_BASE = 100
    RINT_BALANCED = RINT_BASE * 1
    RINT_FLEETING = RINT_BALANCED * 1.5
    RINT_INTENSE = RINT_FLEETING * 2
    RINT_ACUTE = RINT_INTENSE * 2.5

    DISC_ANIMALISM = "Animalism"
    DISC_AUSPEX = "Auspex"
    DISC_CELERITY = "Celerity"
    DISC_DOMINATE = "Dominate"
    DISC_FORTITUDE = "Fortitude"
    DISC_OBFUSCATE = "Obfuscate"
    DISC_OBLIVION = "Oblivion"
    DISC_POTENCE = "Potence"
    DISC_PRESENCE = "Presence"
    DISC_PROTEAN = "Protean"
    DISC_BLOOD_SORCERY = "Blood Sorcery"
    DISC_THINBLOOD_ALCHEMY = "Thinblood Alchemy"

    REF_BG_DISC_PRIORITY = "discipline_priority"
    REF_DISC_NOT_YET = [DISC_AUSPEX, DISC_OBLIVION, DISC_BLOOD_SORCERY, DISC_THINBLOOD_ALCHEMY]

    CHAR_BACKGROUNDS = {
        "Nursing Student": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "You could have become a nurse one day. You could have helped people.",
            REF_ATTRS_ALL: 1, AT_STA: -1, AT_MAN: 1, AT_COM: 2, AT_INT: 1, AT_RES: 1,
            REF_SKILLS_ALL: 1, SK_TECH: 2, SK_SCIE: 2, SK_LEAD: 1, SK_ACAD: 2, SK_INSP: 2,
            SK_INTI: -1, SK_ATHL: -1, SK_FIRE: -1, SK_OCCL: -1,
            REF_BG_DISC_PRIORITY: [
                DISC_DOMINATE, DISC_CELERITY, DISC_PRESENCE, DISC_FORTITUDE, DISC_POTENCE, DISC_ANIMALISM, DISC_OBFUSCATE
            ]
        },
        "Star Athlete": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "You can still remember it all. The sweat, the adrenaline, the sun on your face, the cheers...",
            REF_ATTRS_ALL: 1, AT_STR: 1, AT_DEX: 1, AT_STA: 2, AT_MAN: -1, AT_CHA: 1,
            REF_SKILLS_ALL: 1, SK_DIPL: 1, SK_LEAD: 1, SK_ACAD: 1, SK_ATHL: 3, SK_OCCL: -1,
            REF_BG_DISC_PRIORITY: [
                DISC_POTENCE, DISC_CELERITY, DISC_FORTITUDE, DISC_PRESENCE, DISC_ANIMALISM, DISC_OBFUSCATE, DISC_DOMINATE
            ]
        },
        "Bartender": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "You exist at the intersection of countless lives. One of the few things that hasn't changed.",
            REF_ATTRS_ALL: 1, AT_DEX: 1, AT_CHA: 2, AT_MAN: 1, AT_WIT: 1, AT_RES: -1,
            REF_SKILLS_ALL: 1, SK_DIPL: 2, SK_INSP: 1, SK_STWS: 2, SK_INTR: 2, SK_TRAV: 1,
            SK_ATHL: -1, SK_FIRE: -1, SK_OCCL: -1,
            REF_BG_DISC_PRIORITY: [
                DISC_PRESENCE, DISC_CELERITY, DISC_FORTITUDE, DISC_DOMINATE, DISC_ANIMALISM, DISC_POTENCE, DISC_OBFUSCATE
            ]
        },
        "Veteran": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "The more things change, the more they stay the same.",
            REF_ATTRS_ALL: 1, AT_DEX: 1, AT_STA: 1, AT_CHA: -1, AT_COM: 1, AT_WIT: 2,
            SK_ACAD: 1, SK_ATHL: 2, SK_COMB: 2, SK_TRAV: 2, SK_FIRE: 3, SK_INSP: 2,
            SK_STWS: 2, SK_INTI: 2, SK_TECH: 2, SK_CLAN: 2,
            REF_BG_DISC_PRIORITY: [
                DISC_CELERITY, DISC_ANIMALISM, DISC_OBFUSCATE, DISC_FORTITUDE, DISC_POTENCE, DISC_DOMINATE, DISC_PRESENCE
            ]
        },
        "Grad Student": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "Imagine knowing then what you know now.",
            REF_ATTRS_ALL: 1, AT_INT: 2, AT_DEX: -1, AT_WIT: 1, AT_MAN: 1, AT_RES: 1,
            SK_CLAN: 1, SK_TRAV: 1, SK_DIPL: 1, SK_INTR: 1, SK_LEAD: 1, SK_ACAD: 4,
            SK_INSP: 3, SK_OCCL: 2, SK_SCIE: 3, SK_TECH: 3,
            REF_BG_DISC_PRIORITY: [
                DISC_ANIMALISM, DISC_OBFUSCATE, DISC_FORTITUDE, DISC_PRESENCE, DISC_POTENCE, DISC_CELERITY, DISC_DOMINATE
            ]
        },
        "Influencer": {
            REF_TYPE: REF_BG_PAST, REF_SUBTYPE: REF_BG_PAST,
            REF_DESC: "Oddly enough, a lot of the bullshit you used to hawk is actually kinda useful now that you're dead.",
            REF_ATTRS_ALL: 1, AT_STR: -1, AT_CHA: 1, AT_MAN: 2, AT_COM: 1, AT_WIT: 1,
            REF_SKILLS_ALL: 1, SK_CLAN: -1, SK_COMB: -1, SK_TRAV: 2, SK_DIPL: 2, SK_INTR: 3, SK_STWS: 1,
            SK_SCIE: -1, SK_TECH: 1, SK_INTI: -1,
            REF_BG_DISC_PRIORITY: [
                DISC_PRESENCE, DISC_DOMINATE, DISC_ANIMALISM, DISC_FORTITUDE, DISC_CELERITY, DISC_POTENCE, DISC_OBFUSCATE
            ]
        },
        BG_BEAUTIFUL: {
            REF_TYPE: REF_BG_MERIT, REF_DOTS: 2, REF_SUBTYPE: REF_BG_LOOKS,
            REF_DESC: "You've got beguiling, head-turning looks."
        },
        BG_UGLY: {
            REF_TYPE: REF_BG_FLAW, REF_DOTS: 1, REF_SUBTYPE: REF_BG_LOOKS,
            REF_DESC: "Hopefully your personality makes up for it."
        },
        BG_REPULSIVE: {
            REF_TYPE: REF_BG_FLAW, REF_DOTS: 2, REF_SUBTYPE: REF_BG_LOOKS,
            REF_DESC: "People tend to react negatively to seeing you up close."
        },
        BG_ENEMY: {
            REF_TYPE: REF_BG_FLAW,
            REF_DESC: "Some mortal has it out for you. They may even know who you are, though hopefully not {i}what{/i}."
        }
    }

    REF_VENTRUE_TARGET_COMMANDERS = "Commanders"
    REF_VENTRUE_TARGET_PAINED = "Pained"
    REF_VENTRUE_TARGET_PEACOCKS = "Peacocks"
    VENTRUE_PREF_BACKGROUNDS = {
        REF_VENTRUE_TARGET_COMMANDERS: {
            REF_TYPE: REF_VENTRUE_PALATE, REF_SUBTYPE: REF_VENTRUE_PALATE, REF_BG_NAME: REF_VENTRUE_TARGET_COMMANDERS,
            REF_DESC: "You feed on people who are used to giving orders."
        },
        REF_VENTRUE_TARGET_PAINED: {
            REF_TYPE: REF_VENTRUE_PALATE, REF_SUBTYPE: REF_VENTRUE_PALATE, REF_BG_NAME: REF_VENTRUE_TARGET_PAINED,
            REF_DESC: "You feed on people in physical pain, whether acute or chronic."
        },
        REF_VENTRUE_TARGET_PEACOCKS: {
            REF_TYPE: REF_VENTRUE_PALATE, REF_SUBTYPE: REF_VENTRUE_PALATE, REF_BG_NAME: REF_VENTRUE_TARGET_PEACOCKS,
            REF_DESC: "You feed on people who spend a lot of time maintaining their appearance."
        }
    }

    VAL_DISC_LOCKED = 0  # XP multipliers, with 0 meaning locked.
    VAL_DISC_OUTCLAN = float(5) / 7
    VAL_DISC_CAITIFF = float(5) / 6
    VAL_DISC_INCLAN = 1
    VAL_DISC_XP_REQS = [500, 1000, 1500, 2000, 2500]
    REF_DISC_LOCKED = "Locked"
    REF_DISC_OUTCLAN = "Out-of-Clan"
    REF_DISC_CAITIFF = "Caitiff"
    REF_DISC_INCLAN = "In-Clan"
    REF_DISC_ACCESS = {
        REF_DISC_LOCKED: VAL_DISC_LOCKED, REF_DISC_OUTCLAN: VAL_DISC_OUTCLAN,
        REF_DISC_CAITIFF: VAL_DISC_CAITIFF, REF_DISC_INCLAN: VAL_DISC_INCLAN
    }

    REF_DISC_NICKNAME = "discipline_nickname"

    REF_DISC_BLURBS = {
        DISC_ANIMALISM: {
            REF_DISC_NICKNAME: "Doolittling", REF_RESONANCE: RESON_ANIMAL,
            REF_TOOLTIP: "Everything has a Beast. Through me, you can commune with - and command - the lesser Beasts of the world."
        },
        DISC_AUSPEX: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_PHLEGMATIC,
            REF_TOOLTIP: "We can extend our perception far beyond that of mortals and even other Kindred. Knowledge is power."
        },
        DISC_CELERITY: {
            REF_DISC_NICKNAME: "Tweaking", REF_RESONANCE: RESON_CHOLERIC,
            REF_TOOLTIP: "If they can't catch us, they can't kill us. Or stop us."
        },
        DISC_DOMINATE: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_PHLEGMATIC,
            REF_TOOLTIP: "Bend weaker minds to our will. The natural order of things, really."
        },
        DISC_FORTITUDE: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_MELANCHOLIC,
            REF_TOOLTIP: ""
        },
        DISC_OBFUSCATE: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_MELANCHOLIC,
            REF_TOOLTIP: ""
        },
        DISC_OBLIVION: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_EMPTY,
            REF_TOOLTIP: ""
        },
        DISC_POTENCE: {
            REF_DISC_NICKNAME: "Hulking", REF_RESONANCE: RESON_CHOLERIC,
            REF_TOOLTIP: ""
        },
        DISC_PRESENCE: {
            REF_DISC_NICKNAME: "Razzle Dazzle", REF_RESONANCE: RESON_SANGUINE,
            REF_TOOLTIP: ""
        },
        DISC_PROTEAN: {
            REF_DISC_NICKNAME: "Shapeshifting", REF_RESONANCE: RESON_ANIMAL,
            REF_TOOLTIP: ""
        },
        DISC_BLOOD_SORCERY: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_SANGUINE,
            REF_TOOLTIP: "The Blood is power. The Blood is alive with secrets, and a will all its own."
        },
        DISC_THINBLOOD_ALCHEMY: {
            REF_DISC_NICKNAME: "", REF_RESONANCE: RESON_VARIED,
            REF_TOOLTIP: "We have to cook!"
        }
    }

    POWER_ANIMALISM_FAMULUS = "Bond Famulus"
    POWER_ANIMALISM_SENSE = "Sense the Beast"
    POWER_ANIMALISM_SPEAK = "Feral Whispers"
    POWER_ANIMALISM_SUCCULENCE = "Animal Succulence"
    POWER_ANIMALISM_HIVE = "Unliving Hive"
    POWER_ANIMALISM_QUELL = "Quell the Beast"

    POWER_AUSPEX_DAREDEVIL = "Heightened Senses"
    POWER_AUSPEX_ESP = "Sense the Unseen"
    # Rest of Auspex here

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
    POWER_OBFUSCATE_SILENCE = "Silence of Death"
    POWER_OBFUSCATE_STEALTH = "Unseen Passage"
    POWER_OBFUSCATE_ILLUSION = "Chimerstry"
    POWER_OBFUSCATE_MASK = "Mask of a Thousand Faces"
    POWER_OBFUSCATE_LAUGHINGMAN = "Ghost in the Machine"
    POWER_OBFUSCATE_HALLUCINATION = "Fata Morgana"
    POWER_OBFUSCATE_VANISH = "Vanish"

    POWER_POTENCE_FATALITY = "Lethal Body"
    POWER_POTENCE_SUPERJUMP = "Soaring Leap"
    POWER_POTENCE_PROWESS = "Prowess"
    POWER_POTENCE_MEGASUCK = "Brutal Feed"
    POWER_POTENCE_RAGE = "Spark of Rage"

    POWER_PRESENCE_AWE = "Awe"
    POWER_PRESENCE_DAUNT = "Daunt"
    POWER_PRESENCE_ADDICTED2U = "Lingering Kiss"
    POWER_PRESENCE_ENTRANCE = "Entrancement"
    POWER_PRESENCE_SCARYFACE = "Dread Gaze"

    POWER_PROTEAN_REDEYE = "Eyes of the Beast"
    POWER_PROTEAN_FLOAT = "Weight of the Feather"
    POWER_PROTEAN_TOOTH_N_CLAW = "Feral Weapons"
    POWER_PROTEAN_MOLD_SELF = "Vicissitude"
    POWER_PROTEAN_DIRTNAP = "Earthmeld"
    POWER_PROTEAN_BOO_BLEH = "Shapechange"
    POWER_PROTEAN_MOLD_OTHERS = "Fleshcrafting"
    POWER_PROTEAN_DRUID = "Metamorphosis"
    POWER_PROTEAN_FINALFORM = "Horrid Form"

    REF_DISC_POWER_PASSIVES = [
        POWER_CELERITY_GRACE,
        POWER_DOMINATE_DEVOTION,
        POWER_FORTITUDE_HP, POWER_FORTITUDE_WILL,
        POWER_OBFUSCATE_LAUGHINGMAN,
        #POWER_POTENCE_FATALITY,
        POWER_PRESENCE_ADDICTED2U
    ]

    REF_DISC_POWER_BUFFS = [
        POWER_CELERITY_SPEED,
        POWER_FORTITUDE_TOUGH, POWER_FORTITUDE_BANE,
        POWER_OBFUSCATE_FADE, POWER_OBFUSCATE_SILENCE, POWER_OBFUSCATE_STEALTH,
        POWER_POTENCE_FATALITY, POWER_POTENCE_PROWESS,
        POWER_PROTEAN_REDEYE, POWER_PROTEAN_FLOAT, POWER_PROTEAN_TOOTH_N_CLAW, POWER_PROTEAN_MOLD_SELF
    ]

    REF_DISC_POWER_SHAPESHIFT = [POWER_PROTEAN_BOO_BLEH, POWER_PROTEAN_DRUID, POWER_PROTEAN_FINALFORM]

    REF_DISC_POWER_MENU_ONLY = [POWER_CELERITY_BLINK, POWER_POTENCE_SUPERJUMP]

    REF_DISC_POWER_TOGGLABLES = [POWER_POTENCE_FATALITY]

    REF_DISC_POWER_FREEBIES = [POWER_POTENCE_FATALITY, POWER_POTENCE_SUPERJUMP]

    REF_DISC_POWERS_SNEAKY = [POWER_OBFUSCATE_FADE, POWER_OBFUSCATE_SILENCE, POWER_OBFUSCATE_STEALTH]

    # Actual discipline power relationships
    REF_DISC_POWER_TREES = {
        DISC_ANIMALISM: [
            [POWER_ANIMALISM_FAMULUS, POWER_ANIMALISM_SENSE],
            [POWER_ANIMALISM_SPEAK],
            [POWER_ANIMALISM_HIVE, POWER_ANIMALISM_QUELL, POWER_ANIMALISM_SUCCULENCE],
            [], []
        ],
        DISC_AUSPEX: [],
        DISC_CELERITY: [
            [POWER_CELERITY_GRACE, POWER_CELERITY_TWITCH],
            [POWER_CELERITY_SPEED],
            [POWER_CELERITY_BLINK],
            [], []
        ],
        DISC_DOMINATE: [
            [POWER_DOMINATE_COMPEL, POWER_DOMINATE_FORGET],
            [POWER_DOMINATE_MESMERIZE, POWER_DOMINATE_DEVOTION],
            [POWER_DOMINATE_REWRITE],
            [], []
        ],
        DISC_FORTITUDE: [
            [POWER_FORTITUDE_HP, POWER_FORTITUDE_WILL],
            [POWER_FORTITUDE_TOUGH],
            [POWER_FORTITUDE_BANE],
            [], []
        ],
        DISC_OBFUSCATE: [
            [POWER_OBFUSCATE_FADE, POWER_OBFUSCATE_SILENCE],
            [POWER_OBFUSCATE_STEALTH, POWER_OBFUSCATE_ILLUSION],
            [POWER_OBFUSCATE_MASK, POWER_OBFUSCATE_LAUGHINGMAN, POWER_OBFUSCATE_HALLUCINATION],
            [POWER_OBFUSCATE_VANISH],
            []
        ],
        DISC_OBLIVION: [],
        DISC_POTENCE: [
            [POWER_POTENCE_FATALITY, POWER_POTENCE_SUPERJUMP],
            [POWER_POTENCE_PROWESS],
            [POWER_POTENCE_MEGASUCK, POWER_POTENCE_RAGE],
            [], []
        ],
        DISC_PRESENCE: [
            [POWER_PRESENCE_AWE, POWER_PRESENCE_DAUNT],
            [POWER_PRESENCE_ADDICTED2U],
            [POWER_PRESENCE_ENTRANCE, POWER_PRESENCE_SCARYFACE],
            [], []
        ],
        DISC_PROTEAN: [
            [POWER_PROTEAN_REDEYE, POWER_PROTEAN_FLOAT],
            [POWER_PROTEAN_TOOTH_N_CLAW, POWER_PROTEAN_MOLD_SELF],
            [POWER_PROTEAN_DIRTNAP, POWER_PROTEAN_MOLD_OTHERS, POWER_PROTEAN_BOO_BLEH],
            [POWER_PROTEAN_DRUID, POWER_PROTEAN_FINALFORM],
            []
        ],
        DISC_BLOOD_SORCERY: [],
        DISC_THINBLOOD_ALCHEMY: []
    }

    REF_DISC_AMALGAM_REQS = {
        POWER_ANIMALISM_HIVE: (DISC_OBFUSCATE, 2),
        POWER_DOMINATE_DEVOTION: (DISC_PRESENCE, 1),
        POWER_OBFUSCATE_ILLUSION: (DISC_PRESENCE, 1),
        POWER_OBFUSCATE_HALLUCINATION: (DISC_PRESENCE, 2),
        POWER_POTENCE_RAGE: (DISC_PRESENCE, 3),
        POWER_PROTEAN_MOLD_SELF: (DISC_DOMINATE, 2),
        POWER_PROTEAN_MOLD_OTHERS: (DISC_DOMINATE, 2)
    }

    REF_DISC_POWER_PREREQS = {
        POWER_OBFUSCATE_VANISH: [POWER_OBFUSCATE_FADE],
        POWER_PROTEAN_MOLD_OTHERS: [POWER_PROTEAN_MOLD_SELF],
        POWER_PROTEAN_FINALFORM: [POWER_PROTEAN_MOLD_SELF],
        POWER_PROTEAN_DRUID: [POWER_PROTEAN_BOO_BLEH]
    }



    SEM_HUB_MAIN = "haven-hub-default"

    REP_MIN = 0 # -100
    REP_MAX = 200 # 100
    REP_VALUE_ADJUST = 100

    TT_LOCKED = "tt_power_level_locked"
    TT_NEED_PREVIOUS = "tt_pick_lower_first"
    TT_POWER_AVAILABLE = "new_power_select"
    TT_AMALGAM_LOCK = "amalgam_req_not_met"
    TT_PREREQ_LOCK = "power_prereq_not_met"

    TOOLTIP_TABLE = {  # TODO finish these
        AT_STR: "Lifting, pulling, pushing, punching, kicking, etc.",
        AT_DEX: "Coordination, acuity, speed. Everything from sprinting to APM to aiming a gun.",
        AT_STA: "Bodily resilience and anatomical fortitude. How much punishment you can take.",
        AT_CHA: "Getting people to like you, fear you, want you. Making them {i}feel{/i}.",
        AT_MAN: "Getting people to do what you say, regardless of how they feel about you.",
        AT_COM: "Staying cool in the moment.",
        AT_INT: "Learning, reasoning, problem-solving, memory. The stuff they're always trying to test people for.",
        AT_WIT: "Reaction, intuition, perception, thinking on your feet.",
        AT_RES: "Focus and determination over time, the ability to ignore distractions.",

        SK_ATHL: "Experience, form, and training for coordinated physical exertion of various kinds.",
        SK_CLAN: "Sneaking around, breaking into things, etc. Doing dirt.",
        SK_COMB: "Throwing hands, or wielding the kinds of weapons that you bash, cut, or stab with.",
        SK_FIRE: "The proper handling and usage of firearms.",
        SK_TRAV: "Making your way around the city on foot or on wheels. Braving its treacherous expanses, and even adapting to them.",
        SK_INTI: "Threats, overt or implicit. Getting people to back off or fall in line without resorting to powers of the Blood.",
        SK_INTR: "Dissembling, sophistry, subtlety, and straight up lies. Concealing motives and intentions. Bullshit artistry.",
        SK_LEAD: "Effective delegation of responsibility. The ability to inspire and motivate others to act on your behalf.",
        SK_DIPL: "Persuasion, getting people to see things your way. Communicating with other beings in a way they understand.",
        SK_STWS: "What's really going on in this city? How do things work on the margins?",
        SK_ACAD: "History, philosophy, art, literature, logic. Knowledge of the humanities. Research skills.",
        SK_INSP: "Paying attention at the right time. Methodical collection and analysis of information and evidence in the field.",
        SK_OCCL: "A lot of vampires don't know shit about vampires, let alone whatever else is out there. What do {i}you{/i} know?",
        SK_SCIE: "Biology, chemistry, physics - the hard sciences, theoretical and applied.",
        SK_TECH: "Secure use of modern apps and devices, safely operating online. Banned by the Ivory Tower, at least officially.",

        TT_LOCKED: "(Locked)",
        TT_NEED_PREVIOUS: "(Locked - pick a lower level power first.)",
        TT_POWER_AVAILABLE: "The Blood responds to struggle; new powers are available.",
        TT_AMALGAM_LOCK: "Learning this power requires knowledge in another Art of the Blood.",
        TT_PREREQ_LOCK: "This power is rooted in another that we lack.",
        REF_DISC_LOCKED: "Your Blood doesn't move in the right ways. Perhaps if you had a teacher...",
        REF_DISC_OUTCLAN: "You've learned to move your Blood in new ways, with some difficulty.",
        REF_DISC_CAITIFF: "The Blood of the Clanless is unpredictable, mutable...",
        REF_DISC_INCLAN: "These powers of the Blood often come naturally to those of your Clan."
    }

    MERIT_DISPLAY_MAX = 4
    MAX_ITEM_TIER = 7

    REF_CM_ENABLED = "enabled_in_context"
    REF_CM_DISABLED = "disabled_in_context"
    REF_CM_HIDDEN = None

    COD_SUN = "Sunlight"
    COD_FIRE = "Fire"
    COD_PHYSICAL = "Physical Damage"
    COD_DECAPITATION = "Decapitation"

    DP_DISCLAIMER = "This game was created as a part of Vampire: The Masquerade game jam. "  # TODO: update this for unbound
    DP_DISCLAIMER += "Events portrayed in this game are not canon within World of Darkness."

    # renpy.music.register_channel("sound_aux", "sfx")

image bg city main_menu         = "gui/main_menu.png"
image bg haven basic            = "images/bg_haven.jpg"
image bg domain basic           = "images/bg_domain.jpg"
image bg sunrise sky            = "images/bg_sunrise.jpg"

define audio.main_theme         = "audio/music/Darkstar83 - Shadow Walker.mp3"

define audio.gui_heartbeat      = "audio/sound/86886__timbre__74829-jobro-heartbeat-timbre-s-variant-1b-loop.mp3"
define audio.beastgrowl1        = "audio/sound/344903__aegersum__monster-deep-growl.mp3"
define audio.beastgag           = "audio/sound/347541__pfranzen__human-impression-of-cat-hacking-up-hairball.ogg"
define audio.feed_bite1         = "audio/sound/400174__jgriffie919__flesh-bite.mp3"
define audio.feed_heartbeat     = "audio/sound/608241__newlocknew__heart-beat-calm-rhythm-blood-flows-in-the-veins-6lrs.mp3"
define audio.body_fall1         = "audio/sound/372226__eflexmusic__bodyfall-3-mixed.mp3"
define audio.body_fall2         = "audio/sound/502553__kneeling__goblin-fall.mp3"
define audio.body_fall3_cough   = "audio/sound/222501__qubodup__person-knocked-down.mp3"

# define audio.footsteps1         = "audio/sound/318900__robinhood76__05934-heels-walking-on-pavement-looping.mp3"
define audio.dice_roll_many     = "audio/sound/220744__dermotte__dice-06.mp3"
define audio.dice_roll_few      = "audio/sound/353975__nettimato__rolling-dice-1.mp3"
define audio.fleeing_footsteps1 = "audio/sound/316924__rudmer-rotteveel__footsteps-running-away-fading.mp3"
define audio.fast_footsteps_2   = "audio/sound/69296__abel_k__stairs-coming-up-ak2.mp3"
define audio.fluorescent_buzz   = "audio/sound/574540__moulaythami__buzzing-a.mp3"
define audio.heartbeat_faster   = "audio/sound/181805__klankbeeld__heart-beat-increasing-116642-excerpt02.mp3"
define audio.beastgrowl2        = "audio/sound/98337__cgeffex__roar.mp3"
define audio.samurai_blade_warp = "audio/sound/37411__funkymuskrat__chil.mp3"
define audio.mutation_jingle    = "audio/sound/342336__division4884__simple-mutate-monster.mp3"
define audio.heartbeat_faster_2 = "audio/sound/181805__klankbeeld__heart-beat-increasing-116642_EXCERPT-edit-a02.mp3"
define audio.oncoming_frenzy_2  = "audio/sound/37192__volivieri__funky-static.mp3"
define audio.flanging_clang_1   = "audio/sound/39377__shimsewn__quaver-pokes.mp3"
define audio.alien_whisper      = "audio/sound/329333__curly123456__monster-185-flange.mp3"
define audio.sun_threat_1       = "audio/sound/484461__nowism__fx-long-meepf.mp3"
define audio.get_item_1_gun     = "audio/sound/177054__woodmoose__lowerguncock.mp3"
define audio.get_item_2         = "audio/sound/630021__flem0527__shuffling-backpack.mp3"
define audio.mending_1          = "audio/sound/659959__legand569__flesh-wound-removing-bulletowi.mp3"
define audio.flesh_shifting_1   = "audio/sound/505932__pfranzen__shapeshifter-shifting-shapes.ogg"
define audio.pulled_taut_1      = "audio/sound/460382__dnaudiouk__creaky-cardboard-box.mp3"

define audio.knuckle_crack_1    = "audio/sound/475965__borq1__knuckles-cracking.mp3"
define audio.throwing_hands_1   = "audio/sound/432278__bhaveshshaha__slapping-beating-human-flesh.mp3"
define audio.single_shot_1      = "audio/sound/212607__pgi__machine-gun-002-single-shot.mp3"
define audio.shotgun_fire_1     = "audio/sound/522282__filmmakersmanual__shotgun-firing-1.mp3"
define audio.rifle_shot_1       = "audio/sound/427596__michorvath__ar15-rifle-shot.mp3"
define audio.uzi_full_auto      = "audio/sound/162436__ermfilm__uzi-serial-fire_96khz-24bit.mp3"
define audio.single_cut_1       = "audio/sound/435238__aris621__nasty-knife-stab.mp3"
define audio.stab_1             = "audio/sound/478145__aris621__nasty-knife-stab-2.mp3"
define audio.sword_clash        = "audio/sound/440069__ethanchase7744__sword-block-combo.mp3"
define audio.melee_miss_light_1 = "audio/sound/420668__sypherzent__basic-melee-swing-miss-whoosh.mp3"
define audio.melee_miss_heavy_1 = "audio/sound/420670__sypherzent__strong-melee-swing.mp3"
define audio.bullet_impacts_1   = "audio/sound/423301__u1769092__visceralbulletimpacts.mp3"
define audio.bullet_impact_2    = "audio/sound/528263__magnuswaker__pound-of-flesh-2.mp3"
define audio.striking_armor_1   = "audio/sound/420675__sypherzent__cut-through-armor-slice-clang.mp3"
define audio.bashing_1_light    = "audio/sound/319590__hybrid_v__shield-bash-impact.mp3"
define audio.bashing_2_heavy    = "audio/sound/165196__swimignorantfire__skull-crack-on-porcelain-tub.mp3"
define audio.brawl_struggle     = "audio/sound/235681__jsburgh__struggle-between-two-people.mp3"
define audio.toughness_armor    = "audio/sound/129073__harha__hardstyle-kick-01-nustyle-harha.mp3"

define audio.grunt_pain_masc_1  = "audio/sound/497713__miksmusic__punch-grunt-1.mp3"
define audio.grunt_pain_masc_2  = "audio/sound/85553__maj061785__male-pain-grunt.mp3"
define audio.grunt_pain_masc_3  = "audio/sound/547206__mrfossy__voice_adultmale_paingrunts_06.mp3"
define audio.grunt_pain_masc_4  = "audio/sound/416838__tonsil5__grunt2-death-pain.mp3"
define audio.grunt_pain_femm_1  = "audio/sound/536750__egomassive__gruntf.mp3"
define audio.grunt_pain_femm_2  = "audio/sound/277562__coral_island_studios__woman-in-pain.mp3"
define audio.grunt_pain_femm_3  = "audio/sound/242622__reitanna__grunt2.mp3"
define audio.grunt_pain_femm_4  = "audio/sound/241545__reitanna__painful-growl.mp3"

define audio.shotgun_ricochet   = "audio/sound/423107__ogsoundfx__guns-explosions-album-bullet-impact-14.mp3"
define audio.pistol_ricochet    = "audio/sound/521370__cetsoundcrew__pistol-shot-ricochet-clean.mp3"
define audio.rifle_ricochet     = "audio/sound/523403__c-v__22-caliber-with-ricochet.mp3"
define audio.auto_ricochet      = "audio/sound/523404__c-v__22-caliber-gunfire-with-ricochet.mp3"
#
