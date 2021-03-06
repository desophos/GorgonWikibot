import sys

import pywikibot
from gorgonwikibot.content import Ability, get_content_by_iname
from gorgonwikibot.entrypoint import entrypoint
from scripts.create_ai_profiles import get_abilities, get_ais


def basic_ability(a):
    return "{{Combat Ability|%s}}(%i damage)" % (
        a.iname,
        a.data["PvE"].get("Damage", 0),
    )


def split_ability(a):
    dmg = a.data["PvE"].get("Damage")
    return "".join(
        [
            "{{Combat Ability icon|%s}}" % a.iname,
            " || ",
            "{{Combat Ability name|%s}}" % a.iname,
            f" || ({dmg} damage)" if dmg else "",
        ]
    )


def level_table(ai, abilities):
    rows = []

    for a in abilities:
        ability_data = ai.data["Abilities"][a.iname]
        min = ability_data.get("minLevel", 1)
        max = ability_data.get("maxLevel")

        rows.append(
            "".join(
                [
                    f"| Level {min}",
                    f"-{max}" if max else "+",
                    f": || {split_ability(a)}",
                ]
            )
        )

    # css for toggle link
    rows[0] += ' || style="width:100%; text-align:right;" |'

    return "\n".join(
        [
            '{| class="mw-collapsible mw-collapsed"',
            "\n|-\n".join(rows),
            "|}",
        ]
    )


def generate_pet_profiles():
    abilities = get_abilities(lambda a: a.is_pet, ["GrimalkinBite", "GrimalkinClaw"])
    ais = get_ais(lambda ai: ai.is_pet)
    profiles = {}

    # Grimalkin_Pet and Grimalkin_PetHissy use these for their basic attack.
    # they are the only pets that use non-pet abilities.
    # just monkey-patch these because they're a special case.
    for name in ["GrimalkinBite", "GrimalkinClaw"]:
        abilities[name]["Keywords"].append("PetBasicAttack")

    for ai in ais:
        # ignore abilities that have already been filtered out
        # and get Ability instances from the ai ability list
        alist = [
            get_content_by_iname(Ability, a)
            for a in ai.abilities(include_scaled=True)
            if a in abilities
        ]
        if alist:  # ai has at least one valid ability
            cmds = {cmd: [] for cmd in Ability.PetCommands}
            for a in alist:
                try:
                    cmds[a.which_pet_command].append(a)
                except ValueError:
                    pywikibot.output(
                        f"WARNING: Skipped ability {a.name} for AI {ai.name} because it is not a pet command\n"
                    )

            basic_text = ", ".join(
                [basic_ability(a) for a in cmds[Ability.PetCommands.BASIC]]
            )

            profiles[ai.name] = "\n".join(
                [
                    '{| class="wikitable extimage32px" style="white-space:nowrap;"',
                    f"| Basic Attack: || {basic_text}",
                    "|-",
                    "| Sic 'Em Attack: || ",
                    level_table(ai, cmds[Ability.PetCommands.SIC]),
                    "|-",
                    "| Special Trick: || ",
                    level_table(ai, cmds[Ability.PetCommands.TRICK]),
                    "|}",
                    "<noinclude>[[Category:Pet Profile]]</noinclude>",
                ]
            )

    return profiles


@entrypoint
def main(site, options):
    for name, profile in generate_pet_profiles().items():
        title = f"AIP:{name}"
        page = pywikibot.Page(site, title)
        if page.text == profile:
            pywikibot.output(f"No changes to {title}\n")
            continue
        page.text = profile
        if options.dry:
            pywikibot.output(f"{title}\n{page.text}\n")
        else:
            page.save(summary=options.msg or "Create Pet Profile page")


if __name__ == "__main__":
    main(sys.argv)
