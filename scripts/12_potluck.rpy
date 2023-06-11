init 1 python in game:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state

    import random
    import math


    class WeightedPulse:
        def __init__(self, name, weights=[], values=[], w8_adjust=0):
            if len(weights) != len(values):
                raise ValueError("Weights and values must have 1-to-1 relationship.")
            self.name = name
            self.orig_weights = weights
            self.orig_values = values
            self.pairs = None
            self._w8_adjust = w8_adjust
            self.reset()

        @property
        def w8_adjust(self):
            return self._w8_adjust

        @w8_adjust.setter
        def w8_adjust(self, new_adjust):
            self._w8_adjust = new_adjust

        def flatten(self, new_adjust=None, reset_first=True):
            # By default, it's assumed that we always want to flatten by w8_adjust, non-cumulatively.
            if new_adjust is not None:
                self.w8_adjust = new_adjust
            if reset_first:
                self.reset()
            mod, first_elem = self.w8_adjust / max(1, len(self.pairs) - 1), True
            for pair in self.pairs:
                pair[cfg.REF_1_WEIGHT] += (mod if not first_elem else -1 * self.w8_adjust)
                first_elem = False
            return self

        def reset(self):
            self.pairs = []
            for i in range(len(self.orig_weights)):
                self.pairs.append({cfg.REF_1_WEIGHT: self.orig_weights[i], cfg.REF_1_VALUE: self.orig_values[i]})

        def get_outcome(self):
            weights = [w[cfg.REF_1_WEIGHT] for w in self.pairs]
            result = utils.get_wrs(self.pairs, weights=weights)
            weight_sum, enc_weight_sum = sum(weights), sum(weights[1:])
            w8_str = "{} | {} | weights: ({}) ± {} | enc rate: {}%"
            print("\n\nweight adjust!   ", self.w8_adjust)
            w8_str = w8_str.format(
                self.name, result[cfg.REF_1_VALUE], ", ".join([f'{w8:.2f}' for w8 in weights]),
                f'{self.w8_adjust / (len(self.pairs) - 1):.2f}', f'{enc_weight_sum * 100 / weight_sum:.2f}'
            )
            return result, w8_str


    class TempAgency:

        NPC_CREATURE_TYPES = {
            "basic": {
                cfg.REF_VALUES: (cfg.CT_HUMAN, cfg.CT_GHOUL, cfg.CT_VAMPIRE),
                cfg.REF_CUM_WEIGHTS: utils.get_cum_weights(100, 70, 90)
            },
            "extended_weights": (150, 80, )
        }

        NPC_FIGHTER_TYPES = {
            "random_basic": {
                cfg.REF_VALUES: (NPCFighter.FT_BRAWLER, NPCFighter.FT_SHOOTER, NPCFighter.FT_WILDCARD, NPCFighter.FT_FTPC),
                cfg.REF_CUM_WEIGHTS: utils.get_cum_weights(100, 70, 50, 40)
            },
            "random_allies": {
                cfg.REF_VALUES: (NPCFighter.FT_BRAWLER, NPCFighter.FT_SHOOTER, NPCFighter.FT_WILDCARD),
                cfg.REF_CUM_WEIGHTS: utils.get_cum_weights(110, 85, 65)
            }
        }

        NPC_DISCIPLINES = {
            cfg.REF_CUM_WEIGHTS: utils.get_cum_weights(100, 70, 50, 50, 20),
            cfg.REF_VALUES: {
                NPCFighter.FT_BRAWLER: [cfg.DISC_POTENCE, cfg.DISC_FORTITUDE, cfg.DISC_CELERITY, cfg.DISC_PROTEAN],
                NPCFighter.FT_SHOOTER: [cfg.DISC_CELERITY, cfg.DISC_OBFUSCATE],
                NPCFighter.FT_WILDCARD: [cfg.DISC_FORTITUDE, cfg.DISC_CELERITY, cfg.DISC_PROTEAN, cfg.DISC_POTENCE],
                NPCFighter.FT_FTPC: [cfg.DISC_CELERITY, cfg.DISC_POTENCE, cfg.DISC_PROTEAN],
                NPCFighter.FT_ESCORT: [cfg.DISC_FORTITUDE, cfg.DISC_CELERITY]
            }
        }

        def __init__(self):
            self.creatures_generated = 0

        def roster_test_1(self, num_fighters, pc_team=False):
            roster = self.get_random_roster(num_fighters, pc_team=pc_team)
            if not pc_team:
                enemy_vampires = [ent for ent in roster if ent.creature_type == cfg.CT_VAMPIRE]
                if not enemy_vampires:
                    vf_type = roster[-1].ftype
                    del roster[-1]
                    roster.append(self.get_random_combatant(cr_type=cfg.CT_VAMPIRE, f_type=vf_type))
            return roster

        def enc_mundane(self, diff_tier=1):
            return self.get_random_roster(
                utils.random_int_range(diff_tier, math.ceil(diff_tier*2.5)),
                cr_type=cfg.CT_HUMAN,
                diff_adjust=diff_tier
            )

        def enc_hunters(self, diff_tier=1):
            return self.get_random_roster(
                utils.random_int_range(diff_tier, diff_tier*2),
                cr_type=cfg.CT_HUMAN,
                diff_adjust=diff_tier+1
            )

        def enc_vampires(self, diff_tier=1):
            goons = self.get_random_roster(
                utils.random_int_range(diff_tier, diff_tier*2),
                cr_type=utils.get_wrs((cfg.CT_HUMAN, cfg.CT_GHOUL, cfg.CT_GHOUL)),
                diff_adjust=diff_tier
            )
            vamps = []
            if diff_tier > 1:
                vamps = self.get_random_roster(
                    utils.get_wrs((1, 2), weights=(100, 25)), cr_type=cfg.CT_VAMPIRE,
                    diff_adjust=diff_tier+1
                )
            return goons + vamps

        def get_random_roster(self, num_fighters, cr_type=None, f_type=None, diff_adjust=0, pc_team=False):
            return [
                self.get_random_combatant(cr_type=cr_type, f_type=f_type, diff_adjust=diff_adjust, pc_team=pc_team)
                for _ in range(num_fighters)
            ]

        def get_random_combatant(self, cr_type=None, f_type=None, diff_adjust=0, pc_team=False):
            if cr_type is None:
                ctypes = TempAgency.NPC_CREATURE_TYPES["basic"]
                cr_type = utils.get_wrs(ctypes[cfg.REF_VALUES], cum_weights=ctypes[cfg.REF_CUM_WEIGHTS])
            elif type(cr_type) in (list, tuple):
                cr_type = utils.get_random_list_elem(cr_type)

            if f_type is None and pc_team:
                ally_ftypes = TempAgency.NPC_FIGHTER_TYPES["random_allies"]
                f_type = utils.get_wrs(ally_ftypes[cfg.REF_VALUES], cum_weights=ally_ftypes[cfg.REF_CUM_WEIGHTS])
            else:
                basic_ftypes = TempAgency.NPC_FIGHTER_TYPES["random_basic"]
                f_type = utils.get_wrs(basic_ftypes[cfg.REF_VALUES], cum_weights=basic_ftypes[cfg.REF_CUM_WEIGHTS])
            ent_params = {"creature_type": cr_type, "ftype": f_type}

            # Represents generic Attribute + Skill combo of that type.
            ent_params[cfg.NPCAT_PHYS] = utils.random_int_range(3+diff_adjust, 4+diff_adjust)
            ent_params[cfg.NPCAT_SOCL] = utils.random_int_range(3+diff_adjust, 5+diff_adjust)
            ent_params[cfg.NPCAT_MENT] = utils.random_int_range(2+diff_adjust, 4+diff_adjust)
            ent_params[cfg.SK_ATHL] = utils.random_int_range(4, 4+diff_adjust)
            powerset = TempAgency.get_random_npc_powerset(cr_type, f_type, diff_adjust=diff_adjust)
            if f_type == NPCFighter.FT_BRAWLER:
                ent_params[cfg.SK_COMB] = max(ent_params[cfg.NPCAT_PHYS], utils.random_int_range(4+diff_adjust, 6+diff_adjust))
                npc_weapon, npc_weapon_alt = state.gift_weapon(key=None), None
                # npc_weapon, npc_weapon_alt = state.gift_weapon(key="black_blade_true_hand"), None
            elif f_type == NPCFighter.FT_SHOOTER:
                ent_params[cfg.SK_FIRE] = utils.random_int_range(5+diff_adjust, 6+diff_adjust)
                # TODO: come back to this when .lose() method is less ass.
                npc_weapon, npc_weapon_alt = state.gift_gun(key=None), state.gift_weapon(key="butterfly1")
            else:
                itype = Item.IT_FIREARM if utils.percent_chance(75) else Item.IT_WEAPON
                npc_weapon, npc_weapon_alt = state.gift_weapon(itype=itype, key=None), None
            if powerset:
                for d in powerset:
                    ent_params[d] = powerset[d]["level"]
                    for p in powerset[d]:
                        if p == "level":
                            continue
                        ent_params[p] = powerset[d][p]
            else:
                utils.log("Generated creature of type {}; no powers to speak of.".format(cr_type))
            new_challenger = NPCFighter(name=utils.generate_random_id_str(label="{}#".format(f_type), leng=4), **ent_params)
            new_challenger.npc_weapon, new_challenger.npc_weapon_alt = npc_weapon, npc_weapon_alt
            self.creatures_generated += 1
            return new_challenger

        @staticmethod
        def get_random_npc_powerset(cr_type, f_type, diff_adjust=0):
            if cr_type in (cfg.CT_HUMAN, cfg.CT_ANIMAL):
                return None
            powerset = {}
            num_disciplines, power_ceil, diffa = 0, None, max(-1, diff_adjust)
            if cr_type in (cfg.CT_GHOUL, cfg.CT_FAMULUS):
                num_disciplines, power_ceil = 2, 1
            elif cr_type in (cfg.CT_VAMPIRE, cfg.CT_LUPINE):
                num_disciplines, power_ceil = utils.random_int_range(2 + diffa, 3 + diffa), 2 + diffa
            cum_weight_full_set = TempAgency.NPC_DISCIPLINES[cfg.REF_CUM_WEIGHTS]
            ft_disc_pack = TempAgency.NPC_DISCIPLINES[cfg.REF_VALUES][f_type]
            cum_weights = cum_weight_full_set[:len(ft_disc_pack)]
            powerset = {}
            # random.seed()
            chosen_disciplines = utils.get_wrs(ft_disc_pack, cum_weights=cum_weights, num_elems=num_disciplines)
            for i, disc in enumerate(chosen_disciplines):
                highest_disc_level = min(power_ceil, num_disciplines - i)
                powerset[disc] = {"level": highest_disc_level}
                for j in range(highest_disc_level):
                    # TODO: Come back to this later, for more synergistic power choices. Low priority.
                    power_level_options = cfg.REF_DISC_POWER_TREES[disc][j]
                    power = utils.get_random_list_elem(power_level_options)
                    powerset[disc][power] = highest_disc_level
            return powerset

        # @staticmethod
        # def


#
