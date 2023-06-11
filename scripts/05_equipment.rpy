init 1 python in game:

    cfg, utils, audio, flavor = renpy.store.cfg, renpy.store.utils, renpy.store.audio, renpy.store.flavor


    class Item:
        IT_MONEY = "Money"
        IT_WEAPON = "Weapon"
        IT_FIREARM = "Firearm"
        IT_AMMO = "Ammunition"
        IT_EQUIPMENT = "Equipment"
        IT_QUEST = "Important"
        IT_CONSUMABLE = "Consumable"
        IT_MISC = "Miscellaneous"
        IT_JUNK = "Junk"
        IT_CLUE = "Clue"

        ITEM_COLOR_KEYS = {
            IT_MONEY: "#399642", IT_JUNK: "#707070", IT_CLUE: "#ffffff", IT_WEAPON: "#8f8f8f",
            IT_EQUIPMENT: "#cbcbdc", IT_QUEST: "#763cb7", IT_MISC: "#cbcbdc", IT_FIREARM: "#71797E",
            IT_AMMO: "#60686D", IT_CONSUMABLE: "#dcdced"
        }

        def __init__(self, type, name, key=None, subtype=None, num=1, desc=None, tier=1, **kwargs):
            self.item_type = type
            self.quantity = num
            self.tier = tier
            if self.item_type == Item.IT_JUNK:
                self.tier = 0
            self.subtype = subtype
            self.color_key = Item.ITEM_COLOR_KEYS[self.item_type]
            self.key = key  # Should uniquely identify a kind of item, e.g. an iPhone 14.
            label_suffix = self.subtype if self.subtype else self.item_type
            self.item_id = utils.generate_random_id_str(label=f'supply#{label_suffix}')  # Uniquely identifies an item.
            self.name = name
            if desc:
                self.desc = desc
            else:
                self.desc = "({})".format(self.item_type)
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

        def __repr__(self):
            t_label = self.subtype if self.subtype else self.item_type
            return f'<{self.name} #{utils.truncate_string(self.item_id[7:], leng=len(t_label) + 5)}>'

        def __str__(self):
            return f'{self.name}'

        @property
        def is_melee_weapon(self):
            return False

        @property
        def is_gun(self):
            return False

        def copy(self, item_base=None):
            if item_base is None:
                item_copy = Item(self.item_type, self.name, num=self.quantity, desc=self.desc, tier=self.tier)
            else:
                item_copy = item_base
            for attr in self.__dict__:
                if not hasattr(item_copy, attr):
                    setattr(item_copy, attr, getattr(self, attr))
            return item_copy


    class Weapon(Item):

        MW_KNIFE = "Knife"
        MW_SWORD = "Sword/Blade"
        MW_AXE = "Axe"  # TODO: integrate this into other systems
        MW_BLUNT_LIGHT = "Baton/Blunt Weapon"
        MW_BLUNT_HEAVY = "Bludgeon/Heavy Blunt Weapon"

        MWEPS = (MW_KNIFE, MW_SWORD, MW_AXE, MW_BLUNT_HEAVY, MW_BLUNT_LIGHT)

        RW_THROWING = "Throwing Weapon"
        RW_PISTOL = "Pistol/Revolver"
        RW_SHOTGUN = "Shotgun"
        RW_RIFLE = "Rifle"
        RW_AUTO = "(Semi-)Automatic"

        RWEPS = (RW_PISTOL, RW_SHOTGUN, RW_RIFLE, RW_AUTO, RW_THROWING)

        NO_WEAPON = "Unarmed"
        MW_FANGS = "Fangs"
        MW_DRAIN, MW_MEGADRAIN = "feeding", "blender_feeding"

        ALT_MWEPS = (NO_WEAPON, MW_FANGS, MW_DRAIN, MW_MEGADRAIN)

        def __init__(self, type, name, subtype=None, key=None, num=1, desc=None, tier=1, dmg_bonus=None, lethality=None, **kwargs):
            t_type = type
            if type in Weapon.MWEPS or type in Weapon.ALT_MWEPS or type in (Weapon.RW_THROWING,):
                t_type, subtype = Item.IT_WEAPON, type
            elif type in Weapon.RWEPS:
                t_type, subtype = Item.IT_FIREARM, type
            super().__init__(t_type, name, key=key, subtype=subtype, num=num, desc=desc, tier=tier, **kwargs)
            if self.subtype is None:
                self.subtype = Weapon.RW_PISTOL if self.item_type == Item.IT_FIREARM else Weapon.MW_KNIFE
            self.dmg_bonus = dmg_bonus
            if dmg_bonus is None:
                self.dmg_bonus = 2 if self.item_type == Item.IT_FIREARM else 1
                if self.subtype in (Weapon.RW_RIFLE, Weapon.RW_SHOTGUN, Weapon.MW_AXE):
                    self.dmg_bonus = 3
                elif self.subtype in (Weapon.MW_SWORD, Weapon.MW_BLUNT_HEAVY):
                    self.dmg_bonus = 2

            # Guns are concealable unless stated otherwise and have a default lethality of 2.
            if lethality is not None:
                self.lethality = lethality
            elif self.item_type == Item.IT_FIREARM:
                self.lethality = 2
            elif self.subtype in (Weapon.MW_KNIFE, Weapon.MW_SWORD, Weapon.MW_BLUNT_HEAVY, Weapon.MW_AXE):
                self.lethality = 2
            else:
                self.lethality = 1

            # Melee weapons are not concealable by default and have a default lethality of 1.
            if not hasattr(self, "concealable"):
                self.concealable = (self.item_type == Item.IT_FIREARM)
            if not hasattr(self, "many"):
                self.many = False
            if not hasattr(self, "throwable"):
                self.throwable = (self.item_type == Item.IT_WEAPON and self.concealable and self.many)

            if not hasattr(self, "attack_sound"):
                if self.item_type == Item.IT_FIREARM and hasattr(self, "gun_type"):
                    self.attack_sound = Weapon.WEAPON_SOUNDS[self.gun_type]
                elif self.item_type == Item.IT_FIREARM:
                    self.attack_sound = audio.single_shot_1
                elif hasattr(self, "weapon_type"):
                    self.attack_sound = Weapon.WEAPON_SOUNDS[self.weapon_type]
                else:
                    self.attack_sound = None
        @property
        def is_melee_weapon(self):
            if self.item_type == Item.IT_WEAPON and (not hasattr(self, "throwable") or not self.throwable):
                return True
            return False

        @property
        def is_gun(self):
            return self.item_type == Item.IT_FIREARM

        def copy(self):
            weapon_copy_base = Weapon(
                self.item_type, self.name, subtype=self.subtype, num=self.quantity, desc=self.desc, tier=self.tier,
                dmg_bonus=self.dmg_bonus, lethality = self.lethality
            )
            return super().copy(weapon_copy_base)

        @staticmethod
        def get_fight_sound(action, hit=False):  # True = hit/success, False = miss/failure, None = inconclusive/always
            print(f'GET_FIGHT_SOUND | CALL | action = {action}, hit = {hit}, weapon_used = {action.weapon_used}')
            if not action:
                return None
            if action.action_type in (CombAct.MELEE_ENGAGE, CombAct.DODGE):
                if utils.caseless_in(cfg.POWER_POTENCE_SUPERJUMP, action.unarmed_power_used):
                    return audio.jump_liftoff_1, "<silence 0.5>", audio.jump_landing_1
                elif utils.caseless_in(cfg.POWER_CELERITY_BLINK, action.unarmed_power_used):
                    return audio.whoosh_1
                return audio.fast_footsteps_2 if action.action_type == CombAct.MELEE_ENGAGE else None
            if action.grapple_action_type:
                if action.grapple_action_type in (CombAct.GRAPPLE_HOLD, CombAct.GRAPPLE_MAINTAIN):
                    print(f'GRAPPLE TYPE 1 |> {action}')
                    return flavor.GRAPPLE_SOUNDS[CombAct.GRAPPLE_HOLD] if hit else audio.brawl_struggle
                elif action.grapple_action_type in (CombAct.GRAPPLE_ESCAPE,):
                    print(f'GRAPPLE TYPE 2 |> {action}')
                    return flavor.GRAPPLE_SOUNDS[CombAct.GRAPPLE_HOLD] if hit else audio.brawl_struggle
                print(f'GRAPPLE TYPE 3 |> {action}')
            if action.unarmed_power_used:
                if utils.caseless_in(cfg.POWER_PROTEAN_TOOTH_N_CLAW, action.unarmed_power_used):
                    wtype, subtype = Item.IT_WEAPON, Weapon.MW_SWORD
                else:
                    wtype, subtype = Item.IT_WEAPON, Weapon.MW_KNIFE
            elif not action.weapon_used:
                if action.action_type in CombAct.OUCH:
                    return audio.throwing_hands_1 if hit else audio.brawl_struggle
                return None
            else:
                wtype, subtype = action.weapon_used.item_type, action.weapon_used.subtype
            print(f'\nGET_FIGHT_SOUND ||| wtype = {wtype}, subtype = {subtype}, hit = {hit}')
            if hit:
                x = flavor.IMPACT_SOUNDS[subtype] if wtype == Item.IT_FIREARM else flavor.STRIKE_SOUNDS[subtype]
                print(f'option 1: returning {x}')
                print(f'IMPACT_SOUNDS[{subtype}] = {flavor.IMPACT_SOUNDS[subtype] if subtype in flavor.IMPACT_SOUNDS else None}')
                print(f'all impact sounds: {", ".join([str(isnd) for isnd in flavor.IMPACT_SOUNDS.items()])}')
                return x
            elif hit == False:
                print('option 2')
                return flavor.WHIFF_SOUNDS[subtype] if wtype == Item.IT_WEAPON else flavor.RICOCHET_SOUNDS[subtype]
            else:  # hit is None
                print('option 3')
                x = flavor.FIRING_SOUNDS[subtype] if wtype == Item.IT_FIREARM else flavor.RICOCHET_SOUNDS[subtype]
                print(f'all ricochet sounds: {", ".join([str(isnd) for isnd in flavor.RICOCHET_SOUNDS.items()])}')
                return x

        @staticmethod
        def get_damage_type(lethality, target_creature_type=None):
            # If no target is provided, we conservatively assume it's a vampire.
            mortal_target = target_creature_type in cfg.REF_MORTALS if target_creature_type else False
            if lethality >= 4:  # 4 = Always aggravated
                return cfg.DMG_AGG
            elif lethality == 3:  # 3 = Unhalved Superficial to vampires/Aggravated to mortals
                return cfg.DMG_AGG if mortal_target else cfg.DMG_FULL_SPF
            elif lethality == 2:  # 2 = Superficial to vampires/Aggravated to mortals
                return cfg.DMG_AGG if mortal_target else cfg.DMG_SPF
            elif lethality == 1:  # 1 = Always Superficial damage,
                return cfg.DMG_SPF
            else:  # 0 = Non-lethal damage? (not implemented)
                return cfg.DMG_NONE


    USING_FANGS = Weapon(Weapon.MW_FANGS, "Fangs", key="bite_attack", desc="Chomp!", tier=3, lethality=4, dmg_bonus=0, concealable=True)
    FEEDING_IN_COMBAT = Weapon(Weapon.MW_DRAIN, "feeding", key="feeding", desc="Gulp!", tier=3, lethality=0, dmg_bonus=0, concealable=True)
    # NOTE: Those lethality values for feeding need to change if feeding is changed to go through the normal damage_step.
    DEVOURING_IN_COMBAT = Weapon(
        Weapon.MW_MEGADRAIN, "brutal feeding", key="brutal_feeding", desc="holy shit",
        tier=5, lethality=0, dmg_bonus=0, concealable=True
    )


    class Inventory:
        ITEM_TYPES = [getattr(Item, it) for it in Item.__dict__ if str(it).startswith("IT_")]
        EQ_WEAPON = "weapon"
        EQ_WEAPON_ALT = "sidearm"
        EQ_TOOL_1 = "tool_slot_1"
        EQ_TOOL_2 = "tool_slot_2"
        EQ_CONSUMABLE_1 = "consumable_slot_1"
        EQ_CONSUMABLE_2 = "consumable_slot_2"

        def __init__(self, *items: Item, auto_equip=True, owner_name=None, **kwargs):
            self._items = []
            self._items += items
            self.owner_name = owner_name
            self._equipped = {
                Inventory.EQ_WEAPON: None, Inventory.EQ_WEAPON_ALT: None, Inventory.EQ_TOOL_1: None,
                Inventory.EQ_TOOL_2: None, Inventory.EQ_CONSUMABLE_1: None, Inventory.EQ_CONSUMABLE_2: None
            }
            if auto_equip:
                if Item.IT_FIREARM in self:
                    self.equip(next(itm for itm in self.items if itm.item_type == Item.IT_FIREARM))
                if Item.IT_WEAPON in self:
                    self.equip(next(itm for itm in self.items if itm.item_type == Item.IT_WEAPON))
                utils.log("Post auto-equip for {}: held weapon is {}; sidearm is {}.".format(
                    self.owner_name, self.held, self.sidearm
                ))

        def __str__(self):
            if not len(self):
                return "(Empty)"
            # print(f'LEEEEEENNNNNN for {self.owner_name} is {len(self)}')
            return '\n'.join([f'  {i+1}: {repr(itm)}' for i, itm in enumerate(self.items)])

        @property
        def items(self):
            return self._items

        @property
        def equipped(self):
            return self._equipped

        def __len__(self):
            return len(self.items)

        def __contains__(self, key):
            key_comp = None
            if key in Inventory.ITEM_TYPES:
                key_comp = "item_type"
            elif key in (Weapon.MWEPS + Weapon.RWEPS):
                key_comp = "subtype"
            elif str(key).startswith("$"):
                if not self.cash:
                    return False
                try:
                    check_amount = float(str(key)[1:])
                except Exception as e:
                    utils.log(f'Failed wallet check generated exception {e}.')
                    return False
                return self.cash.quantity >= check_amount
            else:
                key_comp = "key"
            if not key_comp:
                return False
            for item in self.items:
                if getattr(item, key_comp) == key:
                    return True
            return False

        @property
        def held(self):
            return self._equipped[Inventory.EQ_WEAPON]

        @property
        def sidearm(self):
            return self._equipped[Inventory.EQ_WEAPON_ALT]

        @property
        def cash(self):
            return next((it for it in self.items if it.item_type == Item.IT_MONEY), None)

        @property
        def wallet(self):
            if self.cash is None:
                return None
            return self.cash.quantity

        def update_wallet_params(self):
            pass

        def add_money(self, amount):
            if self.cash is None:
                self._items.append(Item(Item.IT_MONEY, "Wallet", key="wallet_default", num=amount))
            else:
                self.cash.quantity += amount
            self.update_wallet_params()

        def take_money(self, amount, remove=True):
            if not self.cash:
                return None, False
            taken_cash, took_full_amount, cash_wad = amount, True, None
            if remove:
                self.cash.quantity -= amount
                if self.cash.quantity < 0:
                    taken_cash -= abs(self.cash.quantity)
                    self.cash.quantity, took_full_amount = 0, False
                    self.update_wallet_params()
            if taken_cash > 0:
                cash_wad = Item(
                    Item.IT_MONEY, "Cash taken", key=utils.generate_random_id_str(label="cash_taken_#", leng=6),
                    num=taken_cash, desc=f'${taken_cash} lost in a transaction or theft.'
                )
            return cash_wad, took_full_amount

        def add_item(self, new_item):
            if isinstance(new_item, Item):
                if new_item.item_type == Item.IT_MONEY and self.cash:
                    self.add_money(new_item.quantity)
                else:
                    self._items.append(new_item)
            elif type(new_item) in (list, tuple):
                for nitem in new_item:
                    self.add_item(nitem)
            elif utils.is_number(new_item):
                self.add_money(new_item)
            else:
                raise TypeError("Inventory.add_item() should only be passed an Item object, a list of Items, or a number (cash).")

        def get_random_item(self, remove=True):
            item = utils.get_random_list_elem(self.items)
            if remove:
                self._items.remove(item)
            return item

        def get_items_by_func(self, grab_func, remove=True):
            taken, kept = [], []
            for item in self.items:
                added_2 = taken if grab_func(item) else kept
                added_2.append(item)
            if remove:
                self._items = kept
            return taken if len(taken) != 1 else taken[0]

        def get_item_by_id(self, item_id, remove=True):
            return self.get_items_by_func(lambda itm: itm.key == ikey, remove=remove)

        def get_items_by_key(self, ikey, remove=True):
            return self.get_items_by_func(lambda itm: itm.key == ikey, remove=remove)

        def get_items_by_subtype(self, subtype, remove=True):
            return self.get_items_by_func(lambda itm: item.subtype == subtype, remove=remove)

        def get_items_by_type(self, item_type, remove=True):
            return self.get_items_by_func(lambda itm: item.item_type == item_type, remove=remove)

        def lose(self, remove=True, item_id=None, ikey=None, itype=None, isubtype=None, cash_amount=None, intended=False, randomly=False):
            if item_id: return self.get_item_by_id(item_id, remove=remove)
            if ikey: return self.get_items_by_key(ikey, remove=remove)
            if itype: return self.get_items_by_type(itype, remove=remove)
            if isubtype: return self.get_items_by_subtype(isubtype, remove=remove)
            if cash_amount: return self.take_money(cash_amount, remove=remove)
            if randomly:
                return self.get_random_item(remove=remove)
            return None

        def dupe_from(self, item_id=None, ikey=None, itype=None, isubtype=None, cash_amount=None, randomly=False):
            x = self.lose(
                remove=False,
                item_id=item_id, ikey=ikey, itype=itype, isubtype=isubtype,
                cash_amount=cash_amount, randomly=randomly
            )
            print(f'WE GOT: {x}')
            return x

        def slot_is_free(self, slot):
            if slot not in self.equipped:
                return False
            return self.equipped[slot] is None

        def get_valid_equipment_slots(self, item_type):
            if item_type in [Item.IT_WEAPON, Item.IT_FIREARM]:
                return [Inventory.EQ_WEAPON, Inventory.EQ_WEAPON_ALT]
            elif item_type == Item.IT_EQUIPMENT:
                return [Inventory.EQ_TOOL_1, Inventory.EQ_TOOL_2]
            elif item_type == Item.IT_CONSUMABLE:
                return [Inventory.EQ_CONSUMABLE_1, Inventory.EQ_CONSUMABLE_2]
            else:
                return None

        def get_free_equipment_slot(self, item_type, preferred_slot=None):
            valid_slots = self.get_valid_equipment_slots(item_type)
            if not valid_slots:
                raise ValueError("No slots exist for item type \"{}\"; check if it's valid.".format(item_type))
            if preferred_slot is not None and preferred_slot in valid_slots and self.slot_is_free(preferred_slot):
                return preferred_slot
            for slot in valid_slots:  # If preferred slot is unavailable or invalid, returns first available.
                if self.slot_is_free(slot):
                    return slot
            return None

        @staticmethod
        def item_match(item1: Item, item2: Item, require_is_match=False):
            if item1 is item2:
                return True
            if not require_is_match and item1.name == item2.name:
                return True
            return False

        def is_equipped(self, item):
            if item.item_type in [Item.IT_WEAPON, Item.IT_FIREARM]:
                return Inventory.item_match(self.equipped[Inventory.EQ_WEAPON], self.equipped[Inventory.EQ_WEAPON_ALT])
            if item.item_type == Item.IT_EQUIPMENT:
                return Inventory.item_match(self.equipped[Inventory.EQ_TOOL_1], self.equipped[Inventory.EQ_TOOL_2])
            elif item.item_type == Item.IT_CONSUMABLE:
                return Inventory.item_match(
                    self.equipped[Inventory.EQ_CONSUMABLE_1], self.equipped[Inventory.EQ_CONSUMABLE_2]
                )
            return False

        def equip(self, item, slot=None, force=False):
            equip_slot = self.get_free_equipment_slot(item.item_type, preferred_slot=slot)
            if equip_slot is None and not force:
                utils.log("Could not equip item \"{}\"; there are no free valid slots.".format(item))
            elif equip_slot is None:
                valid_slots = self.get_valid_equipment_slots(item.item_type)
                if valid_slots is None:
                    raise ValueError("Could not equip \"{}\"; \"{}\" is not a valid type.".format(
                        item, item.item_type
                    ))
                self.equipped[valid_slots[0]] = item
            else:
                self.equipped[equip_slot] = item

        def unequip(self, item, slot=None):
            if not self.is_equipped(item):
                utils.log("Attempted to unequip item \"{}\", but it's not equipped.".format(item))
                return
            valid_slots = self.get_valid_equipment_slots(item.item_type)
            if valid_slots is None:
                raise ValueError("Could not equip \"{}\"; \"{}\" is not a valid type.".format(item, item.item_type))
            for slot in valid_slots:
                if Inventory.item_match(item, self.equipped[slot]):
                    self.equipped[slot] = None
                    break
