init 1 python in state:

    cfg, utils = renpy.store.cfg, renpy.store.utils

    loot_tables = {}


    def gift_weapon(itype=Item.IT_WEAPON, key=None):
        return loot_tables[itype].dupe_from(ikey=key, randomly=(key is None))

    def gift_gun(key=None):
        return gift_weapon(itype=Item.IT_FIREARM, key=key)


    loot_tables["misc"] = Inventory(
        Item(Item.IT_MONEY, "Money", num=int(12.5 * 1000 * 1000 * 1000), desc="Local city's entire GDP"),
        Item(
            Item.IT_FIREARM, "Blood-spattered Colt 45", key="police_colt", dmg_bonus=2,
            desc="I'm sure I'll need this, wherever I'm going..."
        )
    )


    loot_tables[Item.IT_MONEY] = Inventory(
        Item(Item.IT_MONEY, "Small bills", tier=1, num=int(20), desc="A bit of cash. You're not {i}technically{/i} broke."),
        Item(Item.IT_MONEY, "Billfold", tier=2, num=int(20 * 4),
            desc="Enough cash to pretend you're a normal person having a fun night on the town."
        ),
        Item(Item.IT_MONEY, "Fistful of dollars", tier=3, num=int(20 * 16),
            desc="Enough cash for a mugging if your local stick-up kid sees it, or \"civil asset forfeiture\" if your local cop does."
        ),
        Item(Item.IT_MONEY, "Rack", tier=4, num=int(20 * 64),
            desc="More money than you probably want most people to know you have. Vampires can still get robbed.")
    )

    lt_cash_weights = [1000, 200, 40, 8]

    def get_random_cash(rack_tier: int = None, boost: int = 0):
        loot_table = loot_tables[Item.IT_MONEY]
        if rack_tier is None:
            lt_cash_cum_weights = utils.get_cum_weights(*lt_cash_weights)
            i, base_rack = utils.get_wrs_adjusted(loot_table.items, boost, cum_weights=lt_cash_cum_weights)
        else:
            base_rack = loot_table.items[rack_tier]
        base_amount = base_rack.quantity
        amount = utils.random_int_range(int(base_amount * 0.6), int(base_amount * 1.1))
        return Item(Item.IT_MONEY, base_rack.name, tier=base_rack.tier, num=amount, desc=base_rack.desc)


    loot_tables[Item.IT_WEAPON] = Inventory(
        Weapon(
            Weapon.MW_KNIFE, "Switchblade", dmg_bonus=1, tier=1,
            desc="You know what they say about knife fights. Good thing you're already dead."
        ),
        Weapon(Weapon.MW_KNIFE, "Butterfly Knife", key="butterfly1", tier=1, concealable=True),
        Weapon(Weapon.MW_KNIFE, "\"Scalpel\"", key="realscalpel", tier=3, dmg_bonus=3, desc="For legitimate medical use only."),
        Weapon(Weapon.MW_SWORD, "Stained Machete", tier=2, desc="A well-seasoned weapon, good for removing limbs."),
        Weapon(
            Weapon.MW_BLUNT_LIGHT, "Claw Hammer", tier=1, concealable=True,
            desc="You're no Dae-Su, but you think you could make it work."
        ),
        Weapon(Weapon.MW_BLUNT_HEAVY, "Wooden Baseball Bat", key="woodbat", tier=2, desc="A true American classic."),
        Weapon(Weapon.MW_AXE, "Fire Axe", tier=3, desc="About as dangerous to licks as its name might imply."),
        Weapon(Weapon.MW_SWORD, "Black Blade of the Tal'Mahe'Ra", dmg_bonus=4, tier=7, lethality=4, desc="How did you get this?!")
    )


    loot_tables[Item.IT_FIREARM] = Inventory(
        Weapon(Weapon.RW_PISTOL, "Stolen Ruger LCP", key="ruger1", dmg_bonus=2, desc="Confiscated and then re-confiscated."),
        Weapon(Weapon.RW_PISTOL, "S & W Model 500", dmg_bonus=3, tier=3, concealable=False, desc="Do you feel lucky?"),
        Weapon(
            Weapon.RW_PISTOL, "Glock 19 \"Compact\" 9mm", key="glock19", tier=2, desc="The smaller version sold for concealed carry."
        ),
        Weapon(
            Weapon.RW_SHOTGUN, "Browning Double Automatic", tier=3, dmg_bonus=4, concealable=False,
            desc="Recoil-operated 12 gauge. Enough to put down any man, living or dead."
        ),
        Weapon(Weapon.RW_RIFLE, "Nosler M21", desc="A hunter's weapon.")
    )

    loot_tables["tech"] = Inventory(
        Item(Item.IT_EQUIPMENT, "Smartphone", desc="The latest and greatest in rooted burner phones. GPS disabled.")
    )


    loot_tables[Item.IT_JUNK] = Inventory(
        Item(Item.IT_JUNK, "Bubble Gum", desc="You were hoping this would help with blood-breath. It doesn't.")
    )


    def get_random_loot(itype, min_tier=0, max_tier=cfg.MAX_ITEM_TIER, tier_weights=None, tier_cum_weights=None):
        tier_list = list(range(min_tier, max_tier + 1))
        tier = utils.get_wrs(tier_list, weights=tier_weights, cum_weights=tier_cum_weights)
        if itype not in loot_tables:
            raise ValueError("No loot table exists for item type {}!".format(itype))
        eligible_items = [item for item in loot_tables[itype] if item.tier == tier]
        if not len(eligible_items) or len(eligible_items) < 1:
            raise ValueError("No items of type {} and tier {} found.".format(itype, tier))
        loot_item = utils.get_random_list_elem(eligible_items, num_elems=1) #[0]
        return loot_item.copy()


init 1 python in game:

    class CombAct:
        NO_ACTION = "null_action"
        FALL_BACK = "fall_back"
        MELEE_ENGAGE = "melee_engage"
        MELEE_ATTACK = "melee_attack"
        RANGED_ATTACK = "ranged_attack"
        DODGE = "dodge"
        SPECIAL_ATTACK = "special_attack"
        DISENGAGE = "back_dafuq_up"
        ESCAPE_ATTEMPT = "tryna_escape"

        GRAPPLE_BITE = "grapple_bite"
        GRAPPLE_BITE_PLUS = "bite_instant_brutal_feed"
        GRAPPLE_HOLD = "hold_in_place"
        GRAPPLE_DMG = "damaging_grapple"
        GRAPPLE_DRINK = "combat_feeding"
        GRAPPLE_DRINK_PLUS = "brutal_combat_feeding"
        GRAPPLE_ACTIVE_ESCAPE = "get_off_me_bro"
        GRAPPLE_MAINTAIN = "maintain_grip_while"  # For non-grapple actions that shouldn't break grapple, e.g. Arms of Ahriman.

        # Not necessarily attacks, but abilities that can be actively used in combat, not including
        # passive abilities that can affect combat.
        BASIC_MELEE = [cfg.SK_COMB]
        BASIC_RANGED = [cfg.SK_FIRE]
        BASIC_SPACING = [cfg.SK_ATHL]

        RANGED_ACTIONS = [  # Ranged only, cannot use if engaged
            cfg.SK_FIRE,
            cfg.POWER_ANIMALISM_SPEAK,
            cfg.POWER_OBFUSCATE_ILLUSION, cfg.POWER_OBFUSCATE_HALLUCINATION,
            cfg.POWER_POTENCE_RAGE,
            cfg.POWER_PROTEAN_DIRTNAP, cfg.POWER_PROTEAN_BOO_BLEH, cfg.POWER_PROTEAN_DRUID, cfg.POWER_PROTEAN_FINALFORM
        ]

        MELEE_ACTIONS = [  # Melee only, must be engaged to use
            cfg.SK_COMB,
            cfg.POWER_ANIMALISM_QUELL,
            cfg.POWER_DOMINATE_MESMERIZE,
            cfg.POWER_POTENCE_PROWESS, cfg.POWER_POTENCE_MEGASUCK,
            cfg.POWER_PROTEAN_REDEYE
        ]

        ANYWHERE_ACTIONS = [  # Usable at any distance, whether engaged or not
            cfg.NPCAT_PHYS,
            cfg.POWER_CELERITY_SPEED, cfg.POWER_CELERITY_BLINK,
            cfg.POWER_DOMINATE_COMPEL,
            cfg.POWER_FORTITUDE_TOUGH, cfg.POWER_FORTITUDE_BANE,
            cfg.POWER_OBFUSCATE_VANISH,
            cfg.POWER_POTENCE_SUPERJUMP,
            cfg.POWER_PRESENCE_SCARYFACE,
            cfg.POWER_PROTEAN_TOOTH_N_CLAW, cfg.POWER_PROTEAN_MOLD_SELF
        ]

        DODGE_VARIANTS = [cfg.SK_ATHL, cfg.POWER_CELERITY_SPEED, cfg.POWER_OBFUSCATE_ILLUSION]

        RUSH_VARIANTS = [cfg.SK_ATHL, cfg.POWER_CELERITY_SPEED, cfg.POWER_CELERITY_BLINK, cfg.POWER_POTENCE_SUPERJUMP]

        SNEAK_VARIANTS = [cfg.SK_CLAN, cfg.DISC_OBFUSCATE] + cfg.REF_DISC_POWERS_SNEAKY

        DETECTION_VARIANTS = [cfg.POWER_AUSPEX_ESP]

        ESCAPE_VARIANTS = [
            cfg.SK_ATHL,
            cfg.POWER_CELERITY_SPEED, cfg.POWER_CELERITY_BLINK,
            cfg.POWER_OBFUSCATE_VANISH, cfg.POWER_OBFUSCATE_HALLUCINATION
        ]

        # For now, NPC combat discipline powers consist of all active combat discipline powers
        NPC_COMBAT_DISC_POWERS = RANGED_ACTIONS + MELEE_ACTIONS + ANYWHERE_ACTIONS + DODGE_VARIANTS + ESCAPE_VARIANTS
        NPC_COMBAT_DISC_POWERS = [p for p in NPC_COMBAT_DISC_POWERS if not str(p).startswith("SK_")]

        OUCH = (MELEE_ATTACK, RANGED_ATTACK, SPECIAL_ATTACK)
        NONVIOLENT = (DODGE, MELEE_ENGAGE, DISENGAGE, NO_ACTION, FALL_BACK)
        NO_CONTEST = (NO_ACTION, FALL_BACK)


init 1 python in flavor:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state
    audio, game = renpy.store.audio, renpy.store.game
    Person, CombAct, Item, Weapon = game.Person, game.CombAct, game.Item, game.Weapon

    STRIKE_SOUNDS = {
        Weapon.MW_KNIFE: audio.stab_1,
        Weapon.MW_SWORD: audio.sword_cut_2,  # audio.multiple_cuts_2,
        Weapon.MW_BLUNT_LIGHT: audio.bashing_1_light,
        Weapon.MW_BLUNT_HEAVY: audio.bashing_2_heavy,
        Weapon.MW_AXE: audio.axe_cleave_2,
        Weapon.MW_FANGS: audio.feed_bite1,
        Weapon.MW_DRAIN: audio.feed_heartbeat,
        Weapon.RW_THROWING: audio.stab_1
    }

    WHIFF_SOUNDS = {
        Weapon.MW_KNIFE: audio.melee_miss_light_1,
        Weapon.MW_SWORD: audio.melee_miss_heavy_1,
        Weapon.MW_BLUNT_LIGHT: audio.melee_miss_light_1,
        Weapon.MW_BLUNT_HEAVY: audio.melee_miss_heavy_1,
        Weapon.MW_AXE: audio.melee_miss_heavy_1,
        Weapon.MW_FANGS: audio.thwarted_bite_1,
        Weapon.MW_DRAIN: audio.thwarted_bite_1
    }

    FIRING_SOUNDS = {
        Weapon.RW_PISTOL: audio.single_shot_1,
        Weapon.RW_SHOTGUN: audio.shotgun_fire_1,
        Weapon.RW_RIFLE: audio.rifle_shot_1,
        Weapon.RW_AUTO: audio.uzi_full_auto
    }

    IMPACT_SOUNDS = {
        Weapon.RW_PISTOL: audio.bullet_impact_2,
        Weapon.RW_SHOTGUN: audio.bullet_impact_2,
        Weapon.RW_RIFLE: audio.bullet_impact_2,
        Weapon.RW_AUTO: audio.bullet_impacts_1
    }

    RICOCHET_SOUNDS = {
        Weapon.MW_KNIFE: audio.knife_ricochet_1,
        Weapon.MW_SWORD: audio.sword_clash,
        Weapon.MW_BLUNT_LIGHT: audio.blunt_ricochet_1,
        Weapon.MW_BLUNT_HEAVY: audio.blunt_ricochet_1,
        Weapon.MW_AXE: audio.blunt_ricochet_1,
        Weapon.MW_FANGS: audio.feed_bite1,
        Weapon.MW_DRAIN: None,
        Weapon.RW_THROWING: None,

        Weapon.RW_PISTOL: audio.pistol_ricochet,
        Weapon.RW_SHOTGUN: audio.shotgun_ricochet,
        Weapon.RW_RIFLE: audio.rifle_ricochet,
        Weapon.RW_AUTO: audio.auto_ricochet
    }

    PAIN_SOUNDS = {
        cfg.PN_MAN.PN_SHE_HE_THEY: [
            audio.grunt_pain_masc_1,
            audio.grunt_pain_masc_2,
            audio.grunt_pain_masc_3,
            audio.grunt_pain_masc_4,
            audio.grunt_pain_masc_5
        ],
        cfg.PN_WOMAN.PN_SHE_HE_THEY: [
            audio.grunt_pain_femm_1,
            audio.grunt_pain_femm_2,
            audio.grunt_pain_femm_3,
            audio.grunt_pain_femm_4,
            audio.grunt_pain_femm_5
        ],
        cfg.PN_PERSON.PN_SHE_HE_THEY: [
            audio.grunt_pain_femm_1,
            audio.grunt_pain_femm_2,
            audio.grunt_pain_masc_3,
            audio.grunt_pain_masc_4
        ]
    }

    ## NOTE: Only flavor components that get re-used in multiple contexts, e.g. how dice rolls are used in combat and open-world script,
    ## should be placed here; otherwise they should go in their relevant scripts.


    # def flavor_format(template_str, subject=None):
    def flavor_format(template_choice_ref, subject=None, action=None, indoors=False):
        if type(template_choice_ref) in (list, tuple):
            template_str = utils.get_random_list_elem(template_choice_ref)
        else:
            template_str = str(template_choice_ref)
        # token_dict, tokens = {}, utils.get_all_matches_between('{', '}', template_str, lazy=True)
        token_dict, tokens = {}, utils.get_str_format_tokens(template_str)
        for token in tokens:
            token, capitalize_it, cap_m = str(token).upper(), False, "CAP_"
            if token.startswith(cap_m):
                token, capitalize_it = token[len(cap_m):], True
            if subject and token.startswith("PN_"):
                token_dict[token] = str(getattr(subject.pronoun_set, token))
            elif subject and token.startswith("DESC_"):
                desc_property = getattr(subject, token.lower())
                token_dict[token] = str(desc_property)
            elif subject and token in ("NPC_NAME", "WEAPON_NAME"):
                if token == "NPC_NAME":
                    token_dict[token] = str(subject)
                elif token == "WEAPON_NAME":
                    weapon = None
                    if action:
                        weapon = action.weapon_used
                    elif hasattr(subject, "inventory") and isinstance(subject.inventory, game.Inventory):
                        weapon = subject.inventory.held
                    elif hasattr(subject, "npc_weapon"):
                        weapon = subject.npc_weapon
                    token_dict[token] = str(weapon) if weapon else "bare fists"#"strange, unknown weapon"
            elif token == "FLOOR":
                token_dict[token] = "floor" if (state.indoors or not state.outside_haven) else "ground"
            elif token == "HUNGER_DESC":
                token_dict[token] = utils.get_random_list_elem(BLURBS_BLEEDING) if state.pc.hunger > cfg.HUNGER_MAX_CALM else ""
                print("hunger desc  (BLEEDING) token = ", token_dict[token])
            else:
                token_val = getattr(renpy.store.flavor, token)
                if type(token_val) in (list, tuple):
                    token_val = utils.get_random_list_elem(token_val)
                token_dict[token] = token_val
            if capitalize_it:
                token_dict[cap_m + token] = str(token_dict[token]).capitalize()
        retval = template_str.format(**token_dict)# if token_dict else template_str
        print("token_dict: ", token_dict)
        print("formatted template str: {}".format(retval))
        return retval
        # NOTE: ^ ^ If template_str isn't formatted, then the renpy formatting tags with double {{}} will still have them with renpy
        # NOTE: processes them, so they show up in text. The double {{}} are meant for .format(), which will remove them.
        # NOTE: So there needs to be consistency there.
        # NOTE: ALSO, double {{}} don't belong in the token_dict consumed by .format(), only in the unformatted string.

        # TODO TODO TODO 4/14/23 VERBS_HEADPHONES gets KeyError, why?

    def flav(key1, *keys, subject=None):
        template_ref = getattr(renpy.store.flavor, key1)
        for key in keys:
            if key in template_ref:
                template_ref = template_ref[key]
            elif hasattr(template_ref, key):
                template_ref = getattr(template_ref, key)
            else:
                raise ValueError("Flavor key \"{}\" not found in \"{}\"!".format(key, template_ref))
        return flavor_format(template_ref, subject=subject)

    CFW_BLURBS_RC_WIN = utils.get_cum_weights(100, 30, 5, 2, 1)
    CFW_BLURBS_RC_FAIL = utils.get_cum_weights(120, 40, 10, 5, 2, 1)

    BLURBS_BLEEDING = [", {i}tantalizing{/i}", ", lovely little", ", {i}intoxicating{/i}"]

    BLURBS_RC_SUCCESS = ("", "...", "Lucky you.", "Feel that rush?", "Blood is power.")
    BLURBS_RC_FAILURE = (
        "Hunger. Blood.", "BLOOD",
        "...",
        "Drink them dry. You know you want to.",
        "Time to pay the piper...",
        "Them - Blood + Us (You do the math, genius)"
    )

    def get_rouse_check_blurb(hungrier):  # TODO make this more interesting, background-specific
        if hungrier:
            return utils.get_wrs(BLURBS_RC_FAILURE, cum_weights=CFW_BLURBS_RC_FAIL)
        return utils.get_wrs(BLURBS_RC_SUCCESS, cum_weights=CFW_BLURBS_RC_WIN)

    NOUNS_MUSIC = ("melody", "beat", "drop", "lyrics", "bars", "singing", "bridge", "vocals")

    VERBS_TFW = ("frowning", "chuckling", "smiling", "grimacing", "staring in horror")
    VERBS_DANCING = ("nodding", "swaying", "shaking", "gyrating")
    VERBS_HEADPHONES = ("nodding", "rocking", "aggressively banging")
    VERBS_CONVO_1 = ("talking to", "shouting at", "glaring at", "chatting with")

    PREY_ACTIVITIES = {}
    PREY_ACTIVITIES[cfg.REF_PT_AGNOSTIC] = [
        # "admiring {PN_HERSELF_HIMSELF_THEMSELF} by way of a nearby window",
        # "reading something on {PN_HER_HIS_THEIR} phone and {VERBS_TFW}",
        # "{VERBS_TFW} at something on {PN_HER_HIS_THEIR} phone",
        # "absently humming a tune you can't place",
        "{VERBS_HEADPHONES} {PN_HER_HIS_THEIR} head to the {NOUNS_MUSIC}"
    ]

    def what_they_were_doing(pred_type=None, prey=None, pronoun_set=None):
        if prey is None:
            prey = state.prey
        pt = pred_type if pred_type and pred_type in PREY_ACTIVITIES else cfg.REF_PT_AGNOSTIC
        pns = prey.pronoun_set if prey else pronoun_set
        if not pns:
            pns = Person.random_pronouns()
        prey_activity_tmpl = utils.get_random_list_elem(PREY_ACTIVITIES[pt])
        return flavor_format(prey_activity_tmpl, subject=prey)

    @property
    def whaddup_prey(self):
        return self.what_they_were_doing()


    # TODO: fix/refactor below, they're from the old Flavor class
    # update (2023/03/22): most of the combat tables/functions below should be moved to combat, and you can move CombAct back with them

    ## -- Defense prompt blurbs for the player in response to an incoming attack --

    C_ATK_BLURBS = {}
    C_ATK_BLURBS[CombAct.RANGED_ATTACK] = CAB_RNG = {
        cfg.REF_DEFAULT: ["{NPC_NAME} aims {PN_HER_HIS_THEIR} {WEAPON_NAME} squarely in your direction."],
        Weapon.NO_WEAPON: [
            "{NPC_NAME} is attacking you at range without a weapon, somehow. Maybe {PN_SHES_HES_THEYRE} psychic?"
        ],
        Weapon.RW_THROWING: {
            cfg.REF_DEFAULT: [
                ("{NPC_NAME} eyes you, and you can tell by {PN_HER_HIS_THEIR} stance {PN_SHES_HES_THEYRE}"
                " aiming to plant that {WEAPON_NAME} somewhere painful on you.")
            ],
            Weapon.NO_WEAPON: ["{NPC_NAME} is preparing to throw... something, at you."]
        },
        Weapon.RW_AUTO: ["{NPC_NAME} points a {WEAPON_NAME} in your direction, ready to spray you (and anyone close to you)."],
        CombAct.GRAPPLE_ACTIVE_ESCAPE: {
            cfg.REF_ADROIT: [
                "{NPC_NAME} wrestles against your grip, trying to point {PN_HER_HIS_THEIR} {WEAPON_NAME} at you for a point-blank shot!"
            ],
            cfg.REF_CLUMSY: [
                ("{NPC_NAME} is trying to shoot you point-blank with {PN_HER_HIS_THEIR} {WEAPON_NAME},"
                " but is clearly having trouble pointing it at you.")
            ]
        }
    }
    C_ATK_BLURBS[CombAct.MELEE_ATTACK] = CAB_MEL = {
        cfg.REF_DEFAULT: ["{NPC_NAME} takes a step toward you, the {WEAPON_NAME} in {PN_HER_HIS_THEIR} hand."],
        Weapon.NO_WEAPON: {
            cfg.CT_HUMAN: [
                ("In a flash {NPC_NAME} is on you, swinging. Apparently this mortal is either foolish "
                "or desperate enough to try beating down a Kindred with {PN_HER_HIS_THEIR} bare fists.")
            ],
            cfg.CT_VAMPIRE: [
                "In a flash {NPC_NAME} is on you, apparently intending to pummel you with {PN_HER_HIS_THEIR} bare fists."
            ]
        },
        cfg.POWER_PROTEAN_TOOTH_N_CLAW: {
            cfg.REF_DEFAULT: ["wicked black talons sprouting from {PN_HER_HIS_THEIR} fingers."],
            cfg.POWER_PROTEAN_MOLD_SELF: ["bearing a twisted, questing, barbed appendage where {PN_HER_HIS_THEIR} forearm was."],
            Weapon.NO_WEAPON: [
                "and while you don't recognize the power in {PN_HER_HIS_THEIR} raised fists, you know you don't want any part of it."
            ]
        },
        cfg.POWER_PROTEAN_MOLD_SELF: ["brandishing a grotesque appendage in the rough shape of a morning star."],
        Item.IT_FIREARM: [" Looks like you're in for a pistol-whipping if you don't move."],
        Weapon.MW_KNIFE: [" {CAP_PN_SHES_HES_THEYRE} trying to get inside your guard so {PN_SHE_HE_THEY} can shank you."],
        Weapon.MW_SWORD: ["{NPC_NAME} rushes you, {PN_HER_HIS_THEIR} wicked-looking blade whistling through the air."],
        Weapon.MW_AXE: [
            ("{NPC_NAME} steps forward, {PN_HER_HIS_THEIR} {WEAPON_NAME} clutched in both hands."
            " A weapon like that is almost as dangerous to you as it is to mortals. You'd better do something, fast.")
        ],
        Weapon.MW_BLUNT_HEAVY: [
            "{NPC_NAME} swings a {WEAPON_NAME} wildly at you, hoping to beat you into the dirt."
        ],
        CombAct.GRAPPLE_ACTIVE_ESCAPE: {
            Weapon.NO_WEAPON: [
                "{NPC_NAME} thrashes in your grip, intent on breaking free."
            ],
            Weapon.MW_FANGS: [
                "{NPC_NAME} thrashes in your grip, trying to bite you!"
            ],
            Weapon.MW_KNIFE: [
                "{NPC_NAME} wrestles against your grip, trying to stab you with {PN_HER_HIS_THEIR} {WEAPON_NAME}."
            ],
            cfg.REF_ADROIT: [
                "{NPC_NAME} wrestles against your grip, trying to get you with {PN_HER_HIS_THEIR} {WEAPON_NAME}."
            ],
            cfg.REF_CLUMSY: [
                ("{NPC_NAME} is trying to hit you with {PN_HER_HIS_THEIR} {WEAPON_NAME},"
                " but it's too big and {PN_SHES_HES_THEYRE} clearly having trouble bringing it to bear.")
            ]
        }
    }
    CAB_MEL[Weapon.MW_BLUNT_LIGHT] = CAB_MEL[Weapon.MW_BLUNT_HEAVY]
    C_ATK_BLURBS[CombAct.MELEE_ENGAGE] = {
        cfg.REF_DEFAULT: [
            "{NPC_NAME} is sprinting in your direction, closing fast. In a few seconds {PN_SHELL_HELL_THEYLL} be right on top of you."
        ]
    }
    C_ATK_BLURBS[CombAct.DISENGAGE] = {
        cfg.REF_DEFAULT: [
            "{NPC_NAME} seems to be trying to slink back into the shadows, perhaps to better position {PN_HERSELF_HIMSELF_THEMSELF}."
        ]
    }

    def prompt_combat_defense(atk_action):
        attacker, action_type, weapon = atk_action.user, atk_action.action_type, atk_action.weapon_used
        # weap_type = get_weapon_term(weapon)  # TODO: why was this here? what's that method for?
        weap_type = weapon.subtype if weapon else Weapon.NO_WEAPON

        base_blurbs = C_ATK_BLURBS[action_type]
        if action_type == CombAct.RANGED_ATTACK:
            if atk_action.grapple_action_type and atk_action.grapple_action_type == CombAct.GRAPPLE_ACTIVE_ESCAPE:
                bf_key = cfg.REF_CLUMSY
                if weap_type in (Weapon.NO_WEAPON,) or weapon.concealable:
                    bf_key = cfg.REF_ADROIT
                return flavor_format(base_blurbs[CombAct.GRAPPLE_ACTIVE_ESCAPE][bf_key], subject=attacker, action=atk_action)
            if not weapon or weap_type in (Weapon.RW_AUTO,):
                return flavor_format(base_blurbs[weap_type], subject=attacker, action=atk_action)
            elif weapon.item_type != Item.IT_FIREARM and weapon.throwable:
                return flavor_format(base_blurbs[Weapon.RW_THROWING][cfg.REF_DEFAULT], subject=attacker, action=atk_action)
            elif weapon.item_type != Item.IT_FIREARM:
                return flavor_format(base_blurbs[Weapon.RW_THROWING][Weapon.NO_WEAPON], subject=attacker, action=atk_action)
            return flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker)
        elif action_type == CombAct.MELEE_ATTACK:
            if atk_action.grapple_action_type and atk_action.grapple_action_type == CombAct.GRAPPLE_ACTIVE_ESCAPE:
                if weap_type in (Weapon.NO_WEAPON, Weapon.MW_FANGS, Weapon.MW_KNIFE):
                    bf_key = weap_type
                else:
                    bf_key = cfg.REF_ADROIT if weapon.concealable else cfg.REF_CLUMSY
                return flavor_format(base_blurbs[CombAct.GRAPPLE_ACTIVE_ESCAPE][bf_key], subject=attacker, action=atk_action)
            if not weapon and not atk_action.unarmed_power_used:
                mortality_desig = cfg.CT_HUMAN if attacker.creature_type in cfg.REF_MORTALS else cfg.CT_VAMPIRE
                return flavor_format(base_blurbs[Weapon.NO_WEAPON][mortality_desig], subject=attacker, action=atk_action)
            elif atk_action.unarmed_power_used:
                ua_power, tmpl_prefix = atk_action.unarmed_power_used, "In a flash {NPC_NAME} is on you, "
                atk_blurb_key_1, atk_blurb_key_2 = None, None
                if utils.caseless_in(cfg.POWER_PROTEAN_TOOTH_N_CLAW, ua_power):
                    atk_blurb_key_1 = cfg.POWER_PROTEAN_TOOTH_N_CLAW
                    if utils.caseless_in(cfg.POWER_PROTEAN_MOLD_SELF, ua_power):
                        atk_blurb_key_2 = cfg.POWER_PROTEAN_MOLD_SELF
                    else:
                        atk_blurb_key_2 = cfg.REF_DEFAULT
                elif vicussy:
                    atk_blurb_key_1 = cfg.POWER_PROTEAN_MOLD_SELF
                else:
                    atk_blurb_key_1 = cfg.POWER_PROTEAN_TOOTH_N_CLAW
                tmpl_body = base_blurbs[atk_blurb_key_1][atk_blurb_key_2] if atk_blurb_key_2 else base_blurbs[atk_blurb_key_1]
                return flavor_format(tmpl_prefix + tmpl_body, subject=attacker, action=atk_action)
            elif weapon:
                rep_str_2 = flavor_format(base_blurbs[weap_type], subject=attacker, action=atk_action)
                if rep_str_2.startswith(" "):  # If it starts with a space it's meant to follow an initial generic prompt.
                    rep_str_1 = flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker, action=atk_action)
                    return rep_str_1 + rep_str_2
                return rep_str_2
            else:
                return flavor_format(
                    "You're not exactly sure what it is that {NPC_NAME} is swinging at you, but do you really want to find out?",
                    subject=attacker, action=atk_action
                )
        elif action_type == CombAct.MELEE_ENGAGE:  # TODO: later, adjust these to have unique text for blink/soaring leap
            return flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker, action=atk_action)
        elif action_type == CombAct.DISENGAGE:
            return flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker, action=atk_action)
        else:
            raise NotImplementedError("Blurbs are currently only implemented for ranged/melee attacks and rush/disengage actions.")

    C_DEATH_BLURBS = {}
    C_DEATH_BLURBS[cfg.CT_HUMAN] = {
        cfg.REF_DEFAULT: ["{NPC_NAME} collapses to the {FLOOR}, bleeding out in a growing{HUNGER_DESC} crimson pool."],
    }
    C_DEATH_BLURBS[cfg.CT_VAMPIRE] = {
        cfg.REF_DEFAULT: ["{NPC_NAME} crumples to the {FLOOR} in a heap of rigor mortis."]
    }

    def prompt_combat_death(fallen, indoors=None, killer=None, cause_of_death=None, pc_hunger=1):
        # TODO: expand on this
        mortality_desig = cfg.CT_HUMAN if fallen.creature_type in cfg.REF_MORTALS else cfg.CT_VAMPIRE
        return flavor_format(C_DEATH_BLURBS[mortality_desig][cfg.REF_DEFAULT], subject=fallen, indoors=indoors)

    WEAPON_TERMS = {
        Weapon.RW_AUTO: "semiautomatic"
    }

    def get_weapon_term(weapon):
        if weapon is None:
            return Weapon.NO_WEAPON
        if hasattr(weapon, "subtype"):
            weapon_id = weapon.subtype
        elif hasattr(weapon, "item_type"):
            weapon_id = weapon.item_type
        else:
            raise ValueError("Every weapon should have an item_type or subtype, preferably both.")
        if weapon_id in WEAPON_TERMS:
            return WEAPON_TERMS[weapon_id]
        else:
            return str(weapon_id).split("/")[0].lower()


#
