init 1 python in state:

    cfg, utils = renpy.store.cfg, renpy.store.utils

    loot_tables = {}


    loot_tables["misc"] = Inventory(
        Supply(Supply.IT_MONEY, "Money", num=int(12.5 * 1000 * 1000 * 1000), desc="Local city's entire GDP"),
        Supply(
            Supply.IT_FIREARM, "Blood-spattered Colt 45", key="police_colt", dmg_bonus=2,
            desc="I'm sure I'll need this, wherever I'm going..."
        )
    )


    loot_tables[Supply.IT_MONEY] = Inventory(
        Supply(Supply.IT_MONEY, "Small bills", tier=1, num=int(20), desc="A bit of cash. You're not {i}technically{/i} broke."),
        Supply(Supply.IT_MONEY, "Billfold", tier=2, num=int(20 * 4),
            desc="Enough cash to pretend you're a normal person having a fun night on the town."
        ),
        Supply(Supply.IT_MONEY, "Fistful of dollars", tier=3, num=int(20 * 16),
            desc="Enough cash for a mugging if your local stick-up kid sees it, or \"civil asset forfeiture\" if your local cop does."
        ),
        Supply(Supply.IT_MONEY, "Rack", tier=4, num=int(20 * 64),
            desc="More money than you probably want most people to know you have. Vampires can still get robbed.")
    )

    lt_cash_weights = [1000, 200, 40, 8]

    def get_random_cash(rack_tier: int = None, boost: int = 0):
        loot_table = loot_tables[Supply.IT_MONEY]
        if rack_tier is None:
            lt_cash_cum_weights = utils.get_cum_weights(lt_cash_weights)
            i, base_rack = utils.get_wrs_adjusted(loot_table.items, boost, cum_weights=lt_cash_cum_weights)
        else:
            base_rack = loot_table.items[rack_tier]
        base_amount = base_rack.quantity
        amount = utils.random_int_range(int(base_amount * 0.6), int(base_amount * 1.1))
        return Supply(Supply.IT_MONEY, base_rack.name, tier=base_rack.tier, num=amount, desc=base_rack.desc)


    loot_tables[Supply.IT_WEAPON] = Inventory(
        Weapon(
            Supply.IT_WEAPON, "Switchblade", dmg_bonus=1, tier=1,
            desc="You know what they say about knife fights. Good thing you're already dead."
        ),
        Weapon(
            Supply.IT_WEAPON, "Claw Hammer", dmg_bonus=1, tier=1, concealable=True,
            desc="You're no Dae-Su, but you think you could make it work."
        ),
        Weapon(Supply.IT_WEAPON, "Wooden Baseball Bat", dmg_bonus=2, tier=2, desc="A true American classic."),
        Weapon(Supply.IT_WEAPON, "Black Blade of the Tal'Mahe'Ra", dmg_bonus=4, tier=7, lethality=4, desc="How did you get this?!")
    )


    loot_tables[Supply.IT_FIREARM] = Inventory(
        Supply(Supply.IT_FIREARM, "Stolen Ruger LCP", key="gun_ruger_1", dmg_bonus=2, desc="Confiscated and then re-confiscated."),
        Supply(Supply.IT_FIREARM, "S & W Model 500", dmg_bonus=3, tier=3, concealable=False, desc="Do you feel lucky?")
    )


    loot_tables["tech"] = Inventory(
        Supply(Supply.IT_EQUIPMENT, "Smartphone", desc="The latest and greatest in rooted burner phones. GPS disabled.")
    )


    loot_tables[Supply.IT_JUNK] = Inventory(
        Supply(Supply.IT_JUNK, "Bubble Gum", desc="You were hoping this would help with blood-breath. It doesn't.")
    )


    def get_random_loot(itype, min_tier=0, max_tier=cfg.MAX_ITEM_TIER, tier_weights=None, tier_cum_weights=None):
        tier_list = list(range(min_tier, max_tier + 1))
        tier = utils.get_weighted_random_sample(tier_list, weights=tier_weights, cum_weights=tier_cum_weights)
        if itype not in loot_tables:
            raise ValueError("No loot table exists for item type {}!".format(itype))
        eligible_items = [item for item in loot_tables[itype] if item.tier == tier]
        if not len(eligible_items) or len(eligible_items) < 1:
            raise ValueError("No items of type {} and tier {} found.".format(itype, tier))
        loot_item = utils.get_random_list_elem(eligible_items, num_elems=1)[0]
        return loot_item.copy()
