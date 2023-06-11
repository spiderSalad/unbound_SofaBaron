init 1 python in utils:
    import random
    import json
    import unicodedata
    import re

    from math import ceil as math_ceil, floor as math_floor
    from string import ascii_letters, Formatter

    cfg = renpy.store.cfg

    def wrap_dict_in_obj(**kwargs):
        dict_obj = object()
        for kwarg in kwargs:
            if not hasattr(dict_obj, kwarg):
                setattr(dict_obj, kwarg, kwargs[kwarg])
        return dict_obj

    def parse_pool_string(pool_str, situational_mod=None, blood_surging=False):
        if pool_str is None:
            return [[]]
        log("Parsing pool string \"{}\". {}, {}".format(
            pool_str,
            "Situational mod = {}".format(situational_mod) if situational_mod else "No situational modifier",
            "Blood Surge ACTIVE." if blood_surging else "no Blood Surge."
        ))
        raw_pool_str = str(pool_str)
        phases, contests = raw_pool_str.split(","), []
        for phase in phases:
            pools, phase_options = phase.split("/"), []
            for pool in pools:
                 pool_params = [str(prm).capitalize() for prm in pool.split("+")]
                 if situational_mod:  # Should skip if we have an empty string (""), None, or 0
                     pool_params.append(str(situational_mod))
                 if blood_surging:
                     pool_params.append(cfg.REF_BLOOD_SURGE)
                 pretty_pool_str = " + ".join(pool_params)
                 phase_options.append(pretty_pool_str)
            contests.append(phase_options)
        return contests

    def unparse_pool_object(contests_obj, situational_mod=None, remove_blood_surge=False):
        if len(contests_obj) != 1:
            raise ValueError("Should be exactly one phase per RollConfig object, not {}.".format(len(contests_obj)))
        phase, new_pool_str = contests_obj[0], ""
        for pool_option in phase:
            po_string, po_set = "", []
            if type(pool_option) in (list, tuple):
                po_operand = pool_option
            else:
                # po_operand = pool_option.split("+").replace(" ", "") NOTE shouldn't those functions be called in opposite order?
                po_operand = pool_option.replace(" ", "").split("+")  # <-- like this?
            for pool_param in po_operand:
                include = True
                if remove_blood_surge:
                    if caseless_in("blood surge", pool_param) or caseless_in("bloodsurge", pool_param):
                        include = False
                if include:
                    po_set.append(str(pool_param).capitalize())
            po_string = " + ".join(po_set)
            if situational_mod:
                po_string += " + {}".format(str(situational_mod).capitalize())
            new_pool_str += po_string
        return new_pool_str

    def prettify_pool(pool_str, sitmod=None, add_blood_surge=False):
        pool_obj = parse_pool_string(pool_str, situational_mod=sitmod, blood_surging=add_blood_surge)
        return unparse_pool_object(pool_obj, situational_mod=sitmod, remove_blood_surge=not add_blood_surge)

    def translate_dice_pool_params(main_params, alt_params, **kwargs):
        adjusted_mains, adjusted_alts, bs_alt = [], [], cfg.REF_BLOOD_SURGE.replace(" ", "")
        for param in main_params:
            adjusted_mains.append(str(param).capitalize())
        for param in alt_params:
            if param in (cfg.BG_BEAUTIFUL, cfg.BG_STUNNING):
                adjusted_alts.append(bonus_color(param))
            elif param in (cfg.BG_REPULSIVE, cfg.BG_UGLY, cfg.REF_IMPAIRMENT_PARAM):
                adjusted_alts.append(malus_color(param))
            elif param == cfg.REF_ROLL_LOOKS:
                adjusted_alts.append(malus_color("Nosferatu"))
            elif param == cfg.REF_BLOOD_SURGE:
                adjusted_alts.append(blood_surge_color(cfg.REF_BLOOD_SURGE))
            elif caseless_equal(param, cfg.REF_ROLL_MULTI_DEFEND_MALUS):
                times_atkd = "multiple"
                if cfg.REF_ROLL_MULTI_DEFEND_MALUS in kwargs:
                    times_atkd = kwargs[cfg.REF_ROLL_MULTI_DEFEND_MALUS]
                # adjusted_alts.append(malus_color(f'vs_{times_atkd}_attack{"s" if times_atkd != 1 else ""}'))
                ordinal, plural = get_short_ordinal(times_atkd+1), "" if has_int(times_atkd) else "s"
                adjusted_alts.append(malus_color(f'{ordinal}_defense{plural}'))
            else:
                adjusted_alts.append(str(param).capitalize())
        main_str = " + ".join([str(p) for p in adjusted_mains])
        if adjusted_alts:
            alt_str = ",_".join([str(p) for p in adjusted_alts])
            return f'_[{alt_str}]__{main_str}'
        return f'_{main_str}'

    def get_bp_surge_bonus(potency):
        return 1 + math_ceil(potency / 2)

    def get_bp_mend_value(potency):
        if potency < 6:
            return 1 + math_floor(potency / 2)
        return math_floor(potency / 2)

    def get_bp_disc_bonus(potency):
        return math_floor(potency / 2)

    def get_bp_disc_reroll_level(potency):
        return math_ceil(potency / 2)

    def get_bane_severity(potency, tb_clan_curse=False):
        if potency < 1:
            return 1 if tb_clan_curse else 0
        return 1 + math_ceil(potency / 2)

    def get_feeding_modifier(potency, creature_type):
        pass

    def get_feeding_penalty_human(potency):
        pass

    def get_feeding_penalty_swill(potency, has_animal_succulence=False):
        adj_potency = potency - 2 if has_animal_succulence else potency
        if adj_potency >= 3:
            return 0
        if adj_potency >= 2:
            return 0.5
        return 1

    def bonus_color(txt):
        # return "{color=}" + "{}".format(txt) + "{/color}"
        return f'{{color={cfg.COLOR_BONUS_MAIN}}}{txt}{{/color}}'

    def malus_color(txt):
        # return "{color=#ed2323}" + "{}".format(txt) + "{/color}"
        return f'{{color={cfg.COLOR_MALUS_MAIN}}}{txt}{{/color}}'
        cbb67a

    def blood_surge_color(txt):
        return f'{{color={cfg.COLOR_BLOOD_SURGE}}}{txt}{{/color}}'

    def renpy_tag_wrap(txt, *tags):
        altered_txt = txt
        for tag in tags:
            t = str(tag)
            opening, closing = "{" + t + "}", "{/" + t + "}"
            altered_txt = opening + altered_txt + closing
        return altered_txt

    def cascading_size_text(str_2b_sized, starting_sz=0, sz_delta=5, num_words=1, separator=' ', size_tup=None):
        tokens, sized_tokens = str_2b_sized.split(separator), []
        prev_i, cur_size, count = 0, starting_sz, 0
        for i in range(num_words, len(tokens), num_words):
            token = separator.join(tokens[prev_i:i])
            if size_tup and type(size_tup) in (list, tuple):
                print(" count = {}, len(size_tup) = {}, size_tup = {}".format(count, len(size_tup), size_tup))
                cur_size = size_tup[count] if count < len(size_tup) else size_tup[-1]
            else:
                cur_size += sz_delta
            str_cur_size = "+{}".format(cur_size) if int(cur_size) >= 0 else str(cur_size)
            prev_i, count = i, count + 1
            sized_token = "{{size={sz}}}{tk}{{/size}}".format(sz=str_cur_size, tk=token)
            print("token #{} (index={}, size={}, num_words={})  ::  \"{}\"  |>  \"{}\"".format(count, i, cur_size, num_words, token, sized_token))
            sized_tokens.append(sized_token)
        return separator.join(sized_tokens)

    def get_all_matches_between(start, end, operand_str, lazy=True, inclusive=True):
        # TODO implement inclusive
        regexpr = "\\{s}([^{e}]*{lz})\\{e}".format(s=start, e=end, lz='?' if lazy else '')
        return re.findall(regexpr, operand_str)

    def get_str_format_tokens(template_str, include_unused=False):
        return [seg[1] for seg in Formatter().parse(template_str) if include_unused or seg[1] is not None]
        # TODO: look up why Formatter had to be instantiated for parse to work.

    def str_append(txt, append, separator=""):
        if not txt:
            return append
        return "{}{}{}".format(txt, separator, append)

    def unique_append(txt, append, sep=""):
        if not txt:
            txt = ""
        if not caseless_in(append, txt):
            return str_append(txt, append, separator=sep)
        return txt

    def caseless_replace(str, caseless_search_term, replacement):
        caseless_pattern = re.compile(caseless_search_term, re.IGNORECASE)
        return caseless_pattern.sub(replacement, str)

    def caseless_normalize(str):
        return unicodedata.normalize("NFKD", str.casefold())

    def caseless_equal(str1, str2):
        if not str1 or not str2:
            return False
        return caseless_normalize(str1) == caseless_normalize(str2)

    def caseless_in(excerpt, str):
        if not excerpt or not str:
            return False
        return caseless_normalize(excerpt) in caseless_normalize(str)

    def get_short_ordinal(num):
        if not has_int(num):
            raise TypeError(f'Can only return ordinals for integer values, not "{num}"!')
        intval = int(num)
        last_digit, all_else = str(intval)[-1], str(intval)[:-1]
        print(f'|>| ----- intval = {intval}, all_else = {all_else}, last_digit = {last_digit}')
        return f'{all_else}{cfg.REF_BASIC_ORDINALS[int(last_digit)][1]}'

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

    def oneify_list(collection):
        if not collection:
            return []
        if len(collection) == 1:
            return collection[0]
        return collection

    def list_minus(collec, item):
        collec_copy = collec[:]
        try:
            collec.remove(item)
            return collec
        except ValueError:
            log("[utils.remove_from]: {} was not found in collection:\n{}".format(item, collec))
            return collec_copy
        except Exception as e:
            log("[utils.remove_from]: Unexplained exception: {}".format(e))
            return collec_copy

    def list_plus_nodup(collec, item):
        if item not in collec:
            collec.append(item)
        return collec

    def get_random_list_elem(collection, num_elems=1):
        elem_set = random.choices(collection, k=num_elems)
        return oneify_list(elem_set)

    def get_weighted_random_sample(collection, weights=None, cum_weights=None, num_elems=1):
        wr_sample = random.choices(collection, weights=weights, cum_weights=cum_weights, k=num_elems)
        return oneify_list(wr_sample)

    def get_wrs(collection, weights=None, cum_weights=None, num_elems=1):
        return get_weighted_random_sample(collection, weights=weights, cum_weights=cum_weights, num_elems=num_elems)

    def get_wrs_adjusted(collection, i_delta, weights=None, cum_weights=None):
        i1, item = get_wrs(list(enumerate(collection)), weights=weights, cum_weights=cum_weights)
        i2 = max(0, min(i1 + i_delta, len(collection) - 1))
        return i2, collection[i2]

    def get_cum_weights(*weights):
        cum_weights = []
        for i, w8 in enumerate(weights):
            if i != 0:
                cum_weights.append(cum_weights[i-1] + w8)
            else:
                cum_weights.append(w8)
        return cum_weights

    def generate_random_id_str(leng=4, label: str = None):
        return "{}_{}".format(label if label else "rid", ''.join(random.choices(ascii_letters, k=leng)))

    def make_dice_roll(max_val, num_dice):
        return [random.randint(1, max_val) for _ in range(num_dice)]

    def random_int_range(min_val, max_val):
        if min_val > max_val:
            temp, min_val = min_val, max_val
            max_val = temp
        return random.randint(min_val, max_val)

    def get_excerpt(exstr: str, start_token, end_token):
        tokens = exstr.split(start_token, maxsplit=1)
        if len(tokens) < 2:
            return exstr
        return tokens[1].split(end_token)[0]

    def truncate_string(tstring, leng=20, reverse=False):
        leng, len_t = 5 if leng < 5 else leng, len(tstring)
        if reverse:
            return "..." + tstring[len_t - (leng-3):] if len_t > leng else tstring
        return tstring[:leng-3] + "..." if len_t > leng else tstring

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

    def renpy_say(who, what, **kwargs):
        who(what, **kwargs)

    def renpy_play(*tracks, at_once=False):
        print(f'received tracks: {", ".join([str(trk) for trk in tracks])}')
        for i, track in enumerate(tracks):
            if at_once:
                print(f'{i}: at_once audio play: {track}')
                renpy.play(track, channel="audio")
            elif i == 0:
                print(f'{i}: init sound play: {track}')
                renpy.play(track, channel="sound")
            else:
                print(f'{i}: in-order sound queue: {track}')
                renpy.music.queue(track, channel="sound")

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
