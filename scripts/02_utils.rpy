init 1 python in utils:
    from random import randint, choices as random_choices
    import json

    def translate_dice_pool_params(pool_params):
        adjusted_params = []
        for param in pool_params:
            if param == renpy.store.cfg.REF_ROLL_FORCE_NOSBANE:
                adjusted_params.append(malus_color("Nosferatu"))
            elif param == renpy.store.cfg.BG_BEAUTIFUL:
                adjusted_params.append(bonus_color("Beautiful"))
            else:
                adjusted_params.append(str(param).capitalize())
        return " + ".join([str(p) for p in adjusted_params])

    def bonus_color(txt):
        return "{color=#23ed23}" + "{}".format(txt) + "{/color}"

    def malus_color(txt):
        return "{color=#ed2323}" + "{}".format(txt) + "{/color}"

    def nudge_int_value(current_val, delta, value_desc="this variable", floor=None, ceiling=None):
        dstr = str(delta)
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

    def get_random_list_elem(collection):
        return random_choices(collection, k=1)

    def generate_random_id_str(leng=6, label: str = None):
        return "{}_{}".format(label if label else "rid", ''.join(random_choices(string.ascii_letters, k=leng)))

    def make_dice_roll(max_val, num_dice):
        return [randint(1, max_val) for _ in range(num_dice)]

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
        credits_file = renpy.file(renpy.store.cfg.PATH_CREDITS_JSON)
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

    def log(*args):
        print(*args)
