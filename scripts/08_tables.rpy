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

    class CAction:
        NO_ACTION = "null_action"
        FALL_BACK = "fall_back"
        MELEE_ENGAGE = "melee_engage"
        MELEE_ATTACK = "melee_attack"
        RANGED_ATTACK = "ranged_attack"
        DODGE = "dodge"
        SPECIAL_ATTACK = "special_attack"
        DISENGAGE = "back_dafuq_up"
        ESCAPE_ATTEMPT = "tryna_escape"

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

        def __init__(
            self, action_type, target:Entity, user=None, defending=False, pool=None, subtype=None, use_sidearm=False, lethality=None
        ):
            self.action_type = action_type  # Should be one of above types; subtype should be a discipline power or similar or None.
            self.pool, self.num_dice, self.using_sidearm = pool, None, None
            self.target, self.defending = target, defending
            self.user = user
            self.action_label = subtype
            self.weapon_used, self.skip_contest, self.lost_to_trump_card = None, False, False
            self.use_sidearm = use_sidearm
            if self.user and self.use_sidearm:
                self.using_sidearm = True
                utils.log("Off-hand weapon penalty imposed on {} because use_sidearm ({}) set to True.".format(
                    self.user.name, self.user.sidearm if self.user and self.user.sidearm else "None?"
                ))
            self.unarmed_power_used, self.power_used = None, None
            if self.action_type is None and self.action_label is None:
                raise ValueError("At least one of 'action_type' and 'action_label' must be defined; they can't both be empty!")
            elif self.action_type is None:
                self.action_type = self.evaluate_type()
            # ---
            self.dmg_bonus, self.lethality = 0, 1
            self.dmg_bonus_labels = {}
            weapon, weapon_alt = None, None
            if self.user:
                if hasattr(self.user, "npc_weapon"):
                    weapon = self.user.npc_weapon
                if hasattr(self.user, "npc_weapon_alt"):
                    weapon_alt = self.user.npc_weapon_alt
                if self.user.is_pc or hasattr(self.user, "inventory"):
                    weapon, weapon_alt = self.user.held, self.user.sidearm

            if CAction.attack_weapon_match(weapon, self):
                self.weapon_used = weapon
            elif CAction.attack_weapon_match(weapon_alt, self):
                self.weapon_used = weapon_alt
                self.using_sidearm = True
                utils.log("Off-hand weapon penalty applied to attack type {} by {}, who has {} at hand and {} at side".format(
                    self.action_type, self.user.name, weapon.name, weapon_alt.name
                ))
            else:
                self.weapon_used = None

            self.dmg_bonus = 0
            self.armor_piercing = 0
            if self.user:
                if hasattr(self.user, "npc_dmg_bonus") and self.user.npc_dmg_bonus:
                    self.dmg_bonus, self.lethality = self.user.npc_dmg_bonus, self.user.npc_atk_lethality
                elif self.weapon_used:
                    self.dmg_bonus, self.lethality = self.weapon_used.dmg_bonus, self.weapon_used.lethality
            if lethality is not None:  # If lethality value is passed it overrides other sources.
                self.lethality = lethality
            # ---
            if not self.target or self.action_type in CAction.NONVIOLENT:
                self.dmg_type = cfg.DMG_NONE
            else:
                self.dmg_type = Weapon.get_damage_type(self.lethality, target.creature_type)

        def __repr__(self):
            return "< {} action, label {} >".format(self.action_type, self.action_label)

        def evaluate_type(self):
            if self.defending and self.action_label in CAction.DODGE_VARIANTS:
                return CAction.DODGE
            elif self.action_label in CAction.RANGED_ACTIONS:
                return CAction.RANGED_ATTACK
            elif self.action_label in CAction.MELEE_ACTIONS:
                return CAction.MELEE_ATTACK
            elif self.action_label in CAction.ANYWHERE_ACTIONS:
                if self.target is None:
                    return CAction.ESCAPE_ATTEMPT if self.defending else CAction.SPECIAL_ATTACK
                if self.target.current_pos == self.user.current_pos:
                    return CAction.MELEE_ATTACK
                return CAction.RANGED_ATTACK
            return CAction.NO_ACTION

        @staticmethod
        def attack_weapon_match(weapon, action):
            if not weapon or not action:
                return False
            if weapon.item_type == Item.IT_FIREARM:
                return action.action_type == CAction.RANGED_ATTACK
            if weapon.item_type == Item.IT_WEAPON:
                return action.action_type == CAction.MELEE_ATTACK or weapon.throwable
            return False

        @staticmethod
        def attack_is_gunshot(attacker, atk_action):
            if atk_action.action_type != CAction.RANGED_ATTACK:
                return False
            if attacker.ranged_attacks_use_gun or utils.caseless_in(cfg.SK_FIRE, atk_action.action_label):
                return True
            return False


init 1 python in flavor:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state
    audio, game = renpy.store.audio, renpy.store.game
    Person, CAction, Item, Weapon = game.Person, game.CAction, game.Item, game.Weapon

    STRIKE_SOUNDS = {
        Weapon.MW_KNIFE: audio.stab_1,
        Weapon.MW_SWORD: audio.multiple_cuts_2,
        Weapon.MW_BLUNT_LIGHT: audio.bashing_1_light,
        Weapon.MW_BLUNT_HEAVY: audio.bashing_2_heavy,
        Weapon.MW_AXE: audio.axe_cleave_2,
        Weapon.RW_THROWING: audio.stab_1
    }

    WHIFF_SOUNDS = {
        Weapon.MW_KNIFE: audio.melee_miss_light_1,
        Weapon.MW_SWORD: audio.melee_miss_heavy_1,
        Weapon.MW_BLUNT_LIGHT: audio.melee_miss_light_1,
        Weapon.MW_BLUNT_HEAVY: audio.melee_miss_heavy_1,
        Weapon.MW_AXE: audio.melee_miss_heavy_1
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


    def flavor_format(template_str, subject=None):
        # token_dict, tokens = {}, utils.get_all_matches_between('{', '}', template_str, lazy=True)
        token_dict, tokens = {}, utils.get_str_format_tokens(template_str)
        for token in tokens:
            token = str(token)
            if subject and token.startswith("PN_"):
                token_dict[token] = getattr(subject.pronoun_set, token)
            elif subject and token == "NPC_NAME":
                token_dict[token] = subject.name
            elif token == "FLOOR":
                token_dict[token] = "floor" if (state.indoors or not state.outside_haven) else "ground"
            elif token == "HUNGER_DESC":
                token_dict[token] = utils.get_random_list_elem(BLURBS_BLEEDING) if state.pc.hunger > cfg.HUNGER_MAX_CALM else ""
            else:
                token_val = getattr(renpy.store.flavor, token)
                if type(token_val) in (list, tuple):
                    token_val = utils.get_random_list_elem(token_val)
                token_dict[token] = token_val
        return template_str.format(**token_dict) if token_dict else template_str


    CFW_BLURBS_RC_WIN = utils.get_cum_weights(100, 30, 5, 2, 1)
    CFW_BLURBS_RC_FAIL = utils.get_cum_weights(120, 40, 10, 5, 2, 1)

    BLURBS_BLEEDING = [", {{i}}tantalizing{{/i}}", ", lovely little", ", {{i}}intoxicating{{/i}}"]

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

    VERBS_TFW = ("frowning", "chuckling", "smiling", "grimacing", "staring in horror")
    VERBS_CONVO_1 = ("talking to", "shouting at", "glaring at", "chatting with")

    PREY_ACTIVITIES = {}
    PREY_ACTIVITIES[cfg.REF_PT_AGNOSTIC] = [
        "admiring {PN_HERSELF_HIMSELF_THEMSELF} by way of a nearby window",
        "reading something on {PN_HER_HIS_THEIR} phone and {VERBS_TFW}",
        "absently humming a tune you can't place"
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

    ## -- Defense prompt blurbs for the player in response to an incoming attack --

    C_ATK_BLURBS = {}
    C_ATK_BLURBS[CAction.RANGED_ATTACK] = CAB_RNG = {
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
        Weapon.RW_AUTO: ["{NPC_NAME} points a {WEAPON_NAME} in your direction, ready to spray you (and anyone close to you)."]
    }
    C_ATK_BLURBS[CAction.MELEE_ATTACK] = CAB_MEL = {
        cfg.REF_DEFAULT: ["{NPC_WEAPON} takes a step toward you, the {WEAPON_NAME} in {PN_HER_HIS_THEIR} hand."],
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
        Weapon.MW_KNIFE: [" {PN_SHES_HES_THEYRE} trying to get inside your guard so {PN_SHE_HE_THEY} can shank you."],
        Weapon.MW_SWORD: ["{NPC_NAME} rushes you, {PN_HER_HIS_THEIR} wicked-looking blade whistling through the air toward you."],
        Weapon.MW_AXE: [
            ("{NPC_NAME} steps forward, {PN_HER_HIS_THEIR} {WEAPON_NAME} clutched in both hands."
            " A weapon like that is almost as dangerous to you as it is to mortals. You'd better do something, fast.")
        ],
        Weapon.MW_BLUNT_HEAVY: [
            "{NPC_NAME} swings a {WEAPON_NAME} wildly at you, hoping to beat you into the dirt."
        ]
    }
    CAB_MEL[Weapon.MW_BLUNT_LIGHT] = CAB_MEL[Weapon.MW_BLUNT_HEAVY]
    C_ATK_BLURBS[CAction.MELEE_ENGAGE] = {
        cfg.REF_DEFAULT: [
            "{NPC_NAME} is sprinting in your direction, closing fast. In a few seconds {PN_SHELL_HELL_THEYLL} be right on top of you."
        ]
    }
    C_ATK_BLURBS[CAction.DISENGAGE] = {
        cfg.REF_DEFAULT: [
            "{NPC_NAME} seems to be trying to slink back into the shadows, perhaps to better position {PN_HERSELF_HIMSELF_THEMSELF}."
        ]
    }

    def prompt_combat_defense(atk_action):
        attacker, action_type, weapon = atk_action.user, atk_action.action_type, atk_action.weapon_used
        weap_type = get_weapon_term(weapon)

        base_blurbs = C_ATK_BLURBS[action_type]
        if action_type == CAction.RANGED_ATTACK:
            if not weapon or weap_type in (Weapon.RW_AUTO,):
                return flavor_format(base_blurbs[weap_type], subject=attacker)
            elif weapon.item_type != Item.IT_FIREARM and weapon.throwable:
                return flavor_format(base_blurbs[Weapon.RW_THROWING][cfg.REF_DEFAULT], subject=attacker)
            elif weapon.item_type != Item.IT_FIREARM:
                return flavor_format(base_blurbs[Weapon.RW_THROWING][Weapon.NO_WEAPON], subject=attacker)
            return flavor_format(base_blurbs[cfg.REF_DEFAULT])
        elif action_type == CAction.MELEE_ATTACK:
            if not weapon and not atk_action.unarmed_power_used:
                mortality_desig = cfg.CT_HUMAN if attacker.creature_type in cfg.REF_MORTALS else cfg.CT_VAMPIRE
                return flavor_format(base_blurbs[Weapon.NO_WEAPON][mortality_desig])
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
                return flavor_format(tmpl_prefix + tmpl_body, subject=attacker)
            elif weapon:
                return flavor_format(base_blurbs[cfg.REF_DEFAULT] + base_blurbs[weap_type], subject=attacker)
            else:
                return flavor_format(
                    "You're not exactly sure what it is that {NPC_NAME} is swinging at you, but do you really want to find out?",
                    subject=attacker
                )
        elif action_type == CAction.MELEE_ENGAGE:  # TODO: later, adjust these to have unique text for blink/soaring leap
            return flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker)
        elif action_type == CAction.DISENGAGE:
            return flavor_format(base_blurbs[cfg.REF_DEFAULT], subject=attacker)
        else:
            raise NotImplementedError("Blurbs are currently only implemented for ranged/melee attacks and rush/disengage actions.")

    C_DEATH_BLURBS = {}
    C_DEATH_BLURBS[cfg.CT_HUMAN] = {
        cfg.REF_DEFAULT: ["{NPC_NAME} collapses to the {FLOOR}, bleeding out in a growing{HUNGER_DESC} crimson pool."],
    }
    C_DEATH_BLURBS[cfg.CT_VAMPIRE] = {
        cfg.REF_DEFAULT: ["{NPC_NAME} crumples to the {FLOOR} in a heap of rigor mortis."]
    }

    def prompt_combat_death(fallen, indoors=None, cause_of_death=None, pc_hunger=1):
        # TODO: expand on this
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
