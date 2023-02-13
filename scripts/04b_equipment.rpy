init 1 python in game:

    cfg, utils, audio = renpy.store.cfg, renpy.store.utils, renpy.store.audio


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

        def __init__(self, type, name, key=None, num=1, desc=None, tier=1, **kwargs):
            self.item_type = type
            self.quantity = num
            self.tier = tier
            if self.item_type == Item.IT_JUNK:
                self.tier = 0
            self.color_key = Item.ITEM_COLOR_KEYS[self.item_type]
            self.key = key
            if self.key is None:
                self.key = utils.generate_random_id_str(label="supply#{}".format(self.item_type))
            self.name = name
            if desc:
                self.desc = desc
            else:
                self.desc = "({})".format(self.item_type)
            for kwarg in kwargs:
                setattr(self, kwarg, kwargs[kwarg])

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

        W_THROWING = "Throwing Weapon"

        GUN_PISTOL = "Pistol/Revolver"
        GUN_SHOTGUN = "Shotgun"
        GUN_RIFLE = "Rifle"
        GUN_AUTO = "(Semi-)Automatic"

        def __init__(self, type, name, subtype=None, key=None, num=1, desc=None, tier=1, dmg_bonus=0, lethality=None, **kwargs):
            super().__init__(type, name, key=key, num=num, desc=desc, tier=tier, **kwargs)
            self.dmg_bonus = dmg_bonus

            self.subtype = subtype
            if subtype is None:
                self.subtype = Weapon.GUN_PISTOL if self.item_type == Item.IT_FIREARM else Weapon.MW_KNIFE

            # Guns are concealable unless stated otherwise and have a default lethality of 2.
            if lethality is not None:
                self.lethality = lethality
            elif self.item_type == Item.IT_FIREARM:
                self.lethality = 2
            elif self.subtype in (Weapon.MW_KNIFE, Weapon.MW_SWORD, Weapon.MW_BLUNT_HEAVY):
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

        def copy(self):
            weapon_copy_base = Weapon(
                self.item_type, self.name, subtype=self.subtype, num=self.quantity, desc=self.desc, tier=self.tier,
                dmg_bonus=self.dmg_bonus, lethality = self.lethality
            )
            return super().copy(weapon_copy_base)

        @staticmethod
        def get_fight_sound(action, hit=False):  # True = hit/success, False = miss/failure, None = inconclusive/always
            if not action.weapon_used:
                if action.action_type in CAction.OUCH:
                    return audio.throwing_hands_1 if hit else audio.brawl_struggle
                elif action.action_type == CAction.MELEE_ENGAGE:
                    return audio.fast_footsteps_2
                return None
            wtype, subtype = action.weapon_used.item_type, action.weapon_used.subtype
            if hit:
                return cfg.IMPACT_SOUNDS[subtype] if wtype == Item.IT_FIREARM else cfg.STRIKE_SOUNDS[subtype]
            elif hit == False:
                return cfg.WHIFF_SOUNDS[subtype] if wtype == Item.IT_WEAPON else cfg.RICOCHET_SOUNDS[subtype]
            else:  # hit is None
                return cfg.FIRING_SOUNDS[subtype] if wtype == Item.IT_FIREARM else cfg.RICOCHET_SOUNDS[subtype]

        @staticmethod
        def get_damage_type(lethality, target_creature_type):
            mortal_target = target_creature_type in cfg.REF_MORTALS
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


    class Inventory:
        ITEM_TYPES = [it for it in Item.__dict__ if str(it).startswith("IT_")]
        EQ_WEAPON = "weapon"
        EQ_WEAPON_ALT = "sidearm"
        EQ_TOOL_1 = "tool_slot_1"
        EQ_TOOL_2 = "tool_slot_2"
        EQ_CONSUMABLE_1 = "consumable_slot_1"
        EQ_CONSUMABLE_2 = "consumable_slot_2"

        def __init__(self, *items: Item, auto_equip=True, **kwargs):
            self._items = []
            self._items += items
            self._equipped = {
                Inventory.EQ_WEAPON: None, Inventory.EQ_WEAPON_ALT: None, Inventory.EQ_TOOL_1: None,
                Inventory.EQ_TOOL_2: None, Inventory.EQ_CONSUMABLE_1: None, Inventory.EQ_CONSUMABLE_2: None
            }
            if auto_equip:
                if Item.IT_FIREARM in self:
                    self.equip(next(itm for itm in self.items if item.item_type == Item.IT_FIREARM))
                if Item.IT_WEAPON in self:
                    self.equip(next(itm for itm in self.items if item.item_type == Item.IT_WEAPON))

        @property
        def items(self):
            return self._items

        @property
        def equipped(self):
            return self._equipped

        def __len__(self):
            return len(self.items)

        def __contains__(self, key):
            if key in Inventory.ITEM_TYPES:
                for item in self.items:
                    if item.item_type == key:
                        return True
            else:
                for item in self.items:
                    if item.key == key:
                        return True
            return False

        @property
        def held(self):
            return self._equipped[Inventory.EQ_WEAPON]

        @property
        def sidearm(self):
            return self._equipped[Inventory.EQ_WEAPON_ALT]

        def add(self, new_item: Item):
            if new_item.item_type == Item.IT_MONEY:
                cash = next((it for it in self.items if it.item_type == Item.IT_MONEY), None)
                if cash is None:
                    self._items.append(new_item)
                else:
                    cash.quantity += new_item.quantity
                    if new_item.tier > cash.tier:
                        cash.desc, cash.tier = new_item.desc, new_item.tier
            else:
                self._items.append(new_item)

        def lose(self, ikey=None, itype=None, cash_amount=None, intended=False):
            if ikey:
                self._items = [item for item in self.items if item.key != ikey]
            elif itype:
                raise NotImplemented("Hey bub, grip these!")
            elif cash_amount:
                cash = next((it for it in self.items if it.item_type == Item.IT_MONEY), None)
                if cash:
                    cash.quantity -= cash_amount
                    if cash.quantity < 0:
                        cash.quantity = 0

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
                utils.log("Could not equip item \"{}\"; there are no free valid slots.".format(item.name))
            elif equip_slot is None:
                valid_slots = self.get_valid_equipment_slots(item.item_type)
                if valid_slots is None:
                    raise ValueError("Could not equip \"{}\"; \"{}\" is not a valid type.".format(
                        item.name, item.item_type
                    ))
                self.equipped[valid_slots[0]] = item
            else:
                self.equipped[equip_slot] = item

        def unequip(self, item, slot=None):
            if not self.is_equipped(item):
                utils.log("Attempted to unequip item \"{}\", but it's not equipped.".format(item.name))
                return
            valid_slots = self.get_valid_equipment_slots(item.item_type)
            if valid_slots is None:
                raise ValueError("Could not equip \"{}\"; \"{}\" is not a valid type.".format(item.name, item.item_type))
            for slot in valid_slots:
                if Inventory.item_match(item, self.equipped[slot]):
                    self.equipped[slot] = None
                    break