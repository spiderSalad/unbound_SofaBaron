label investigation_menu:

    beast "Knowledge is power. Wouldn't it be nice if you had some?"

    "But where to begin? Most of your old contacts are either missing or confirmed dead, including the other licks you ran with."

    # TODO: show these backgrounds once and then lower the chance drastically, e.g. 20%

    "Your coterie, in Camarilla parlance. Or what passed for one. Each of them their own unique combination of unreliable, unsavory, and unhinged."

    "But they were all you had, and now they're gone."

    beast "They were trash. Mangy ticks, the lot of them. Not that you're any better."

    # TODO: rep checks here later

    $ nossie = cfg.CLAN_BLURBS[cfg.CLAN_NOSFERATU][cfg.REF_CLAN_SLUR]
    if pc.clan == cfg.CLAN_NOSFERATU:
        $ nos_info_choice = "my clan"

        "You may not have a coterie anymore, but you've still got family, so to speak."

        "Unsurprisingly, your clan survived the purge mostly intact. Clan Nosferatu has plently of experience dealing with purges, and plenty of infrastructure and contingencies in place."

        "You're not the most well-integrated [nossie] in the city, but you're still family and you know you'll be welcome."

        "That might be your first and best option, but the more you rely on your kin the more contributions they'll expect from you in turn."

    "A lot of the Barons bit it too. The chaotic scramble for their old territory is still ongoing. The Tower's stayed out of the fray, most of the turf up for grabs being well below their standards."

    "No doubt they have their own post-apocalyptic problems to deal with as well. ...But that might be an angle you can work."

    "You'd never be welcome in Elysium, of course. But you were on speaking terms with a few members of the Tower back in the day. Maybe something could be arranged."

    "You'll {i}definitely{/i} have to put your best foot forward, and whatever you get will be costly. But the Tower has resources and contacts that no one else can match."

    "You could hit up some of the Anarch Movement's finest, of course. You don't have any particular pull, especially with your squad presumed ash."

    "But you're still in good standing, and if you've got something to offer in exchange you know you'll have takers."

    if pc.clan != cfg.CLAN_NOSFERATU:
        $ nos_info_choice = "the local Nosferatu"

        "You could always head down into the swers. Clan Nosferatu is known the world over for their trade in secrets, gossip, and intel of all kinds. The local Sewer Rats are no exception, and they'll sell to anyone."

        "Assuming you can pay whatever price they're asking."

    "Or you could just make your rounds. Take a stroll up and down a few blocks, see what catches your eye or ear. Rely on your own investigative repertoire."

    "That'd be the most dubious option by far. But whatever you came up with, you wouldn't owe anyone for it."

    if pc.hunger > cfg.HUNGER_MAX_CALM:
        $ info_search_menu_msg = "Or we could forget all that nonsense and feed. That seems like a better idea."
    else:
        $ info_search_menu_msg = "Wake me up if you need me."

    menu:
        beast "[info_search_menu_msg]"

        # Applicable disciplines: Presence, Auspex, Obfuscate

        "Let's see if I can catch the latest whispers from the Ivory Tower. ()":
            # Resolve + Streetwise + Cam Rep, THEN Charisma + Diplomacy/Manipulation + Intrigue
            ""

        "Shouldn't be too hard or expensive to parley with some of my fellow Anarchs.":
            # Charisma + Diplomacy + Anarch Rep OR Manipulation + Intimidation (former choice costs more, latter choice lowers rep)
            ""

        "I'll talk to [nos_info_choice]. Simplest way to get intel is to buy it from the professionals.":
            # No test, but costs money (favors?) depending on Nosferatu rep.
            ""

        "Before I get myself into any more debt, I want to see what I can figure out on my own.":
            # Resolve + Investigation + Contacts, THEN Wits + Technology + Contacts
            ""

        "On second thought, I have better things to do.":
            return

    return
