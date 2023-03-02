init 1 python in game:

    cfg, utils, state = renpy.store.cfg, renpy.store.utils, renpy.store.state

    import random

    class TempAgency:

        RANDOM_CTYPES_BASIC = (cfg.CT_HUMAN, cfg.CT_GHOUL, cfg.CT_VAMPIRE)
        CUM_WEIGHTS_CTYPE_BASIC = utils.get_cum_weights(100, 70, 90)
        RANDOM_FTYPES_BASIC = (NPCFighter.FT_BRAWLER, NPCFighter.FT_SHOOTER, NPCFighter.FT_WILDCARD, NPCFighter.FT_FTPC)
        CUM_WEIGHTS_FTYPE_BASIC = utils.get_cum_weights(100, 70, 50, 40)
        RANDOM_FTYPES_ALLIES = (NPCFighter.FT_BRAWLER, NPCFighter.FT_SHOOTER, NPCFighter.FT_WILDCARD)
        CUM_WEIGHTS_FTYPE_ALLIES = utils.get_cum_weights(110, 85, 65)

        CUM_WEIGHTS_DISC_PICK = utils.get_cum_weights(100, 70, 50, 50, 20)

        REF_FTYPE_DISC_SETS = {
            NPCFighter.FT_BRAWLER: [cfg.DISC_POTENCE, cfg.DISC_FORTITUDE, cfg.DISC_CELERITY, cfg.DISC_PROTEAN],
            NPCFighter.FT_SHOOTER: [cfg.DISC_CELERITY, cfg.DISC_OBFUSCATE],
            NPCFighter.FT_WILDCARD: [cfg.DISC_FORTITUDE, cfg.DISC_CELERITY, cfg.DISC_PROTEAN, cfg.DISC_POTENCE],
            NPCFighter.FT_FTPC: [cfg.DISC_CELERITY, cfg.DISC_POTENCE, cfg.DISC_PROTEAN],
            NPCFighter.FT_ESCORT: [cfg.DISC_FORTITUDE, cfg.DISC_CELERITY]
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

        def get_random_roster(self, num_fighters, cr_type=None, f_type=None, diff_adjust=0, pc_team=False):
            return [
                self.get_random_combatant(cr_type=cr_type, f_type=f_type, diff_adjust=diff_adjust, pc_team=pc_team)
                for _ in range(num_fighters)
            ]

        def get_random_combatant(self, cr_type=None, f_type=None, diff_adjust=0, pc_team=False):
            if cr_type is None:
                cr_type = utils.get_wrs(TempAgency.RANDOM_CTYPES_BASIC, cum_weights=TempAgency.CUM_WEIGHTS_CTYPE_BASIC)
            if f_type is None and pc_team:
                f_type = utils.get_wrs(TempAgency.RANDOM_FTYPES_ALLIES, cum_weights=TempAgency.CUM_WEIGHTS_FTYPE_ALLIES)
            else:
                f_type = utils.get_wrs(TempAgency.RANDOM_FTYPES_BASIC, cum_weights=TempAgency.CUM_WEIGHTS_FTYPE_BASIC)
            ent_params = {"creature_type": cr_type, "ftype": f_type}
            # Represent generic Attribute + Skill combo of that type.
            ent_params[cfg.NPCAT_PHYS] = utils.random_int_range(4, 6)
            ent_params[cfg.NPCAT_SOCL] = utils.random_int_range(4, 7)
            ent_params[cfg.NPCAT_MENT] = utils.random_int_range(3, 6)
            ent_params[cfg.SK_ATHL] = utils.random_int_range(4, 6)
            powerset = TempAgency.get_random_npc_powerset(cr_type, f_type, diff_adjust=diff_adjust)
            if f_type == NPCFighter.FT_BRAWLER:
                ent_params[cfg.SK_COMB] = max(ent_params[cfg.NPCAT_PHYS], utils.random_int_range(5, 8))
                npc_weapon, npc_weapon_alt = state.gift_weapon(key=None), None
            elif f_type == NPCFighter.FT_SHOOTER:
                ent_params[cfg.SK_FIRE] = utils.random_int_range(5, 7)
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
                utils.log("Generated creatue of type {}; no powers to speak of.".format(cr_type))
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
            cum_weight_full_set = TempAgency.CUM_WEIGHTS_DISC_PICK
            ft_disc_pack = TempAgency.REF_FTYPE_DISC_SETS[f_type]
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



#
