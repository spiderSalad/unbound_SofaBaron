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


init 1 python in cfg:

    audio = renpy.store.audio
    Weapon = renpy.store.game.Weapon

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
        PN_MAN.PN_SHE_HE_THEY: [
            audio.grunt_pain_masc_1,
            audio.grunt_pain_masc_2,
            audio.grunt_pain_masc_3,
            audio.grunt_pain_masc_4,
            audio.grunt_pain_masc_5
        ],
        PN_WOMAN.PN_SHE_HE_THEY: [
            audio.grunt_pain_femm_1,
            audio.grunt_pain_femm_2,
            audio.grunt_pain_femm_3,
            audio.grunt_pain_femm_4,
            audio.grunt_pain_femm_5
        ],
        PN_PERSON.PN_SHE_HE_THEY: [
            audio.grunt_pain_femm_1,
            audio.grunt_pain_femm_2,
            audio.grunt_pain_masc_3,
            audio.grunt_pain_masc_4
        ]
    }


init 1 python in game:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state

    class Flavorizer:
        WEAPON_TERMS = {
            Weapon.RW_AUTO: "semiautomatic"
        }

        CUM_FLAVOR_WEIGHTS = {
            "rc_success": utils.get_cum_weights(100, 30, 5, 2, 1),
            "rc_fail": utils.get_cum_weights(120, 40, 10, 5, 2, 1)
        }

        @staticmethod
        def get_rouse_check_blurb(hungrier):  # TODO make this more interesting, background-specific
            rc_success_blurbs = ("", "...", "Lucky you.", "Feel that rush?", "Blood is power.")
            rc_fail_blurbs = (
                "Hunger. Blood.", "BLOOD",
                "...",
                "Drink them dry. You know you want to.",
                "Time to pay the piper...",
                "Them - Blood + Us (You do the math, genius)"
            )
            if hungrier:
                return utils.get_wrs(rc_fail_blurbs, cum_weights=Flavorizer.CUM_FLAVOR_WEIGHTS["rc_fail"])
            return utils.get_wrs(rc_success_blurbs, cum_weights=Flavorizer.CUM_FLAVOR_WEIGHTS["rc_success"])


        @staticmethod
        def prompt_combat_defense(atk_action):
            attacker, action_type, weapon = atk_action.user, atk_action.action_type, atk_action.weapon_used
            template, wep_term, pns = "", Flavorizer.get_weapon_term(weapon), Flavorizer.get_pronouns(attacker)

            if action_type == CAction.RANGED_ATTACK:
                template = "{} aims {} {} squarely in your direction."
                if not weapon:
                    template = "{} is attacking you at range without a weapon, somehow. Maybe {} psychic?"
                    return template.format(attacker.name, pns.PN_SHES_HES_THEYRE)
                elif weapon.item_type != Item.IT_FIREARM and weapon.throwable:
                    template = "{} eyes you, and you can tell by {} stance {} aiming to plant a {} somewhere painful on you."
                    return template.format(attacker.name, pns.PN_HER_HIS_THEIR, pns.PN_SHES_HES_THEYRE, weapon.name)
                elif weapon.item_type != Item.IT_FIREARM:
                    return "{} is preparing to throw... something, at you.".format(attacker.name)
                elif wep_term == Weapon.RW_AUTO:
                    template = "{} points a {} in your direction, ready to spray you (and anyone close to you)."
                    return template.format(attacker.name, wep_term)
                return template.format(attacker.name, pns.PN_HER_HIS_THEIR, weapon.name)
            elif action_type == CAction.MELEE_ATTACK:
                template = "{} takes a step toward you, the {} in {} hand."
                if not weapon and attacker.creature_type in cfg.REF_MORTALS:
                    template = "In a flash {} is on you, swinging. Apparently this mortal is either foolish "
                    template += "or desperate enough to try beating down a Kindred with {} bare fists."
                    return template.format(attacker.name, pns.PN_HER_HIS_THEIR)
                elif not weapon and atk_action.unarmed_power_used:
                    template = "In a flash {} is on you, "
                    if utils.caseless_in(cfg.POWER_PROTEAN_TOOTH_N_CLAW, atk_action.unarmed_power_used):
                        if utils.caseless_in(cfg.POWER_PROTEAN_MOLD_SELF, atk_action.unarmed_power_used):
                            template += "bearing a twisted, questing, barbed appendage where {} forearm was."
                        else:
                            template += "wicked black talons sprouting from {} fingers."
                        return template.format(attacker.name, pns.PN_HER_HIS_THEIR)
                    elif utils.caseless_in(cfg.POWER_PROTEAN_MOLD_SELF, atk_action.unarmed_power_used):
                        template += "brandishing a grotesque appendage in the rough shape of a morning star."
                        return template.format(attacker.name)
                    else:
                        template += "and while you don't recognize the power in {} raised fists, "
                        template += "you know you don't want any part of it."
                        return template.format(attacker.name, pns.PN_HER_HIS_THEIR)
                elif not weapon:
                    template = "In a flash {} is on you, apparently intending to pummel you with {} bare fists."
                    return template.format(attacker.name, pns.PN_HER_HIS_THEIR)
                elif weapon.item_type == Item.IT_FIREARM:
                    template += " Looks like you're in for a pistol-whipping if you don't move."
                    return template.format(attacker.name, weapon.name, pns.PN_HER_HIS_THEIR)
                elif weapon.subtype:
                    if weapon.subtype == Weapon.MW_KNIFE:
                        template += " {} trying to get inside your guard so {} can shank you."
                        return template.format(
                            attacker.name, weapon.name, pns.PN_HER_HIS_THEIR, str(pns.PN_SHES_HES_THEYRE).capitalize(),
                            pns.PN_SHE_HE_THEY
                        )
                    elif weapon.subtype == Weapon.MW_SWORD:
                        template = "{} rushes you, {} wicked-looking blade whistling through the air toward you."
                        return template.format(attacker.name, pns.PN_HER_HIS_THEIR)
                    elif weapon.subtype == Weapon.MW_AXE:
                        template = "{} steps forward, the {} clutched in both hands. A weapon like that is almost as dangerous to you "
                        template += "as it is to mortals. You'd better do something, fast."
                        return template.format(attacker.name, weapon.name)
                    else:
                        return "{} swings a {} wildly at you, hoping to beat you into the dirt.".format(attacker.name, weapon.name)
                else:
                    template = "You're not exactly sure what is is that {} is swinging at you, but do you really want to find out?"
                    return template.format(attacker.name)
            elif action_type == CAction.MELEE_ENGAGE:
                template = "{} is sprinting in your direction, closing fast. In a few seconds {} be right on you."
                return template.format(attacker.name, pns.PN_SHELL_HELL_THEYLL)
            elif action_type == CAction.DISENGAGE:
                template = "{} seems to be trying to slink back into the shadows, perhaps to better position {}."
                return template.format(attacker.name, pns.PN_HERSELF_HIMSELF_THEMSELF)
            else:
                raise NotImplementedError("Flavor is currently only implemented for ranged, melee, and rush actions.")
            # blurb = template.format(attacker.name)

        @staticmethod
        def get_pronouns(ent):
            if not hasattr(ent, "pronoun_set") or not ent.pronoun_set:
                return cfg.PN_PERSON
            else:
                return ent.pronoun_set

        @staticmethod
        def get_weapon_term(weapon):
            if weapon is None:
                return ""
            if hasattr(weapon, "subtype"):
                weapon_id = weapon.subtype
            elif hasattr(weapon, "item_type"):
                weapon_id = weapon.item_type
            else:
                raise ValueError("Every weapon should have an item_type or subtype, preferably both.")
            if weapon_id in Flavorizer.WEAPON_TERMS:
                return Flavorizer.WEAPON_TERMS[weapon_id]
            else:
                return str(weapon_id).split("/")[0].lower()
#
