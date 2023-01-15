init 1 python in utils:
    import random
    import json

    from math import ceil
    from string import ascii_letters

    cfg = renpy.store.cfg

    def parse_pool_string(pool_str, pool_mod=None, surge=False):
        raw_pool_str = str(pool_str)
        phases, contests = raw_pool_str.split(","), []
        for phase in phases:
            pools, phase_options = phase.split("/"), []
            for pool in pools:
                 pool_params = [str(prm).capitalize() for prm in pool.split("+")]
                 if pool_mod:  # Should skip if we have an empty string (""), None, or 0
                     pool_params.append(str(pool_mod))
                 if surge:
                     pool_params.append(cfg.REF_BLOOD_SURGE)
                 pretty_pool_str = " + ".join(pool_params)
                 phase_options.append(pretty_pool_str)
            contests.append(phase_options)
        return contests

    def translate_dice_pool_params(pool_params):
        adjusted_params = []
        for param in pool_params:
            if param == cfg.REF_ROLL_LOOKS:
                adjusted_params.append(malus_color("Nosferatu"))
            elif param == cfg.BG_BEAUTIFUL:
                adjusted_params.append(bonus_color("Beautiful"))
            elif param == cfg.BG_REPULSIVE:
                adjusted_params.append(malus_color("Repulsive"))
            else:
                adjusted_params.append(str(param).capitalize())
        return " + ".join([str(p) for p in adjusted_params])

    def get_bp_surge_bonus(potency):
        return 1 + ceil(potency / 2)

    def bonus_color(txt):
        return "{color=#23ed23}" + "{}".format(txt) + "{/color}"

    def malus_color(txt):
        return "{color=#ed2323}" + "{}".format(txt) + "{/color}"

    def get_cum_weights(weights):
        enum_weights = enumerate(weights)
        return [(w8 + weights[i-1] if i > 0 else w8) for i, w8 in enum_weights]

    def percent_chance(chance_out_of_100):
        threshold = chance_out_of_100 / 100
        return (random.random() < threshold)

    def nudge_int_value(current_val, delta, value_desc="this variable", floor=None, ceiling=None):
        dstr = str(delta)
        print("dstr = {}".format(dstr))
        dint = int(dstr.replace('=', ''))
        if "+" in dstr and "-" in dstr:
            raise ValueError("Attempting to add and substract at the same time?")
        elif "+" in dstr:
            new_val = current_val + dint
        elif "-" in dstr:
            new_val = current_val - abs(dint)
        elif not has_int(dstr):
            raise ValueError("Can't set {} to a non-integer value.".format(value_desc))
        else:
            new_val = dint
        if floor is not None:
            new_val = max(floor, new_val)
        if ceiling is not None:
            new_val = min(ceiling, new_val)
        return new_val

    def has_int(val):
        try:
            int(val)
            return True
        except ValueError:
            return False

    def is_number(val):
        try:
            float(val)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def is_iterable(obj):
        try:
            iter(obj)
            return True
        except Exception as e:
            e.__repr__()
            return False

    def get_random_list_elem(collection, num_elems=1):
        return random.choices(collection, k=num_elems)

    def get_weighted_random_sample(collection, weights=None, cum_weights=None, num_elems=1):
        return random.choices(collection, weights=weights, cum_weights=cum_weights, k=num_elems)

    def get_wrs_adjusted(collection, i_delta, weights=None, cum_weights=None):
        i1, item = get_weighted_random_sample(list(enumerate(collection)), weights=weights, cum_weights=cum_weights)[0]
        i2 = max(0, min(i1 + i_delta, len(collection) - 1))
        return i2, collection[i2]

    def generate_random_id_str(leng=6, label: str = None):
        return "{}_{}".format(label if label else "rid", ''.join(random.choices(ascii_letters, k=leng)))

    def make_dice_roll(max_val, num_dice):
        return [random.randint(1, max_val) for _ in range(num_dice)]

    def random_int_range(min_val, max_val):
        return random.randint(min_val, max_val)

    def get_excerpt(exstr: str, start_token, end_token):
        tokens = exstr.split(start_token, maxsplit=1)
        if len(tokens) < 2:
            return exstr
        return tokens[1].split(end_token)[0]

    def truncate_string(tstring, leng=20):
        leng = 5 if leng < 5 else leng
        return tstring[:leng-3] + "..." if len(tstring) > leng else tstring

    def open_url(url):  # TODO: implement this
        print("opening url: {}".format(url))

    def PREDICTS_HERE ():
        pass

    def get_credits_json():
        # global creditsFile
        # global creditsJSON
        credits_file = renpy.file(cfg.PATH_CREDITS_JSON)
        credits_json = json.load(credits_file)
        return credits_json

    def sort_credits(credits_json):
        sorted_credits = {}

        for credit in credits_json:
            ctype = credit["type"]
            if ctype and ctype not in sorted_credits:
                sorted_credits[ctype] = []
            elif ctype:
                sorted_credits[ctype].append(credit)

        return sorted_credits

    def json_prettify(prim_data, sort_keys=True):
        return json.dumps(prim_data, sort_keys=sort_keys, indent=4)

    def log(*args):
        print(*args)

    for key in cfg.CHAR_BACKGROUNDS:
        bg = cfg.CHAR_BACKGROUNDS[key]
        if cfg.REF_TYPE in bg and bg[cfg.REF_TYPE] == cfg.REF_BG_PAST:
            phys_attr_points, phys_skill_points = 3, 0
            socl_attr_points, socl_skill_points = 3, 0
            ment_attr_points, ment_skill_points = 3, 0
            for key2 in bg:
                val = bg[key2]
                if key2 == cfg.REF_ATTRS_ALL:
                    phys_attr_points += val * 3
                    socl_attr_points += val * 3
                    ment_attr_points += val * 3
                elif key2 == cfg.REF_SKILLS_ALL:
                    phys_skill_points += val * 5
                    socl_skill_points += val * 5
                    ment_skill_points += val * 5
                elif key2 in cfg.REF_PHYSICAL_ATTRS:
                    phys_attr_points += val
                elif key2 in cfg.REF_SOCIAL_ATTRS:
                    socl_attr_points += val
                elif key2 in cfg.REF_MENTAL_ATTRS:
                    ment_attr_points += val
                elif key2 in cfg.REF_PHYSICAL_SKILLS:
                    phys_skill_points += val
                elif key2 in cfg.REF_SOCIAL_SKILLS:
                    socl_skill_points += val
                elif key2 in cfg.REF_MENTAL_SKILLS:
                    ment_skill_points += val
            attr_points = phys_attr_points + socl_attr_points + ment_attr_points
            skill_points = phys_skill_points + socl_skill_points + ment_skill_points
            print("\n\"{}\":\nAttr points: ({} physical/{} social/{} mental) ({} total)".format(
                key, phys_attr_points, socl_attr_points, ment_attr_points, attr_points
            ))
            print("Skill points: ({} physical/{} social/{} mental) ({} total)".format(
                phys_skill_points, socl_skill_points, ment_skill_points, skill_points
            ))
