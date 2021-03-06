from functools import reduce
from operator import not_, truth

import pytest
from scripts.create_ability_pages import (ability_chains, disambiguate,
                                          is_learnable)
from gorgonwikibot.content import separate_words


@pytest.mark.parametrize(
    "btest,data",
    [
        (not_, {"Keywords": ["Lint_NotLearnable"]}),
        (not_, {"Keywords": ["_", "Lint_NotLearnable", "test"]}),
        (truth, {"Keywords": ["_", "test"]}),
        (truth, {}),
    ],
)
def test_is_learnable(dummy_ability, btest, data):
    assert btest(is_learnable(dummy_ability(custom=data)))


def test_ability_chains():
    chains = ability_chains()
    # check sorting
    for basename, chain in chains.items():
        assert reduce(lambda a, b: a.name <= b.name and b, chain), basename
    # special cases
    for name in ["(Self Bomb)", "Self Bomb", "Charm Rat"]:
        assert name not in chains
    for name in ["Punch", "Sword Slash"]:
        assert name in chains
    for k, v in disambiguate.items():
        assert v in chains and k not in chains
    # duplicates
    dupe_skills = {
        "Front Kick": ["Unarmed", "Cow"],
        "Cold Protection": ["Fire Magic", "Ice Magic"],
    }
    dupe_names = []
    for name, skills in dupe_skills.items():
        assert name not in chains
        for skill in skills:
            fullname = f"{name} ({skill})"
            assert fullname in chains
            for a in chains[fullname]:
                assert separate_words(a.data["Skill"]) == skill
            dupe_names.append(fullname)
    # make sure keys match values
    for basename, chain in chains.items():
        # exclude special cases
        assert basename in dupe_names + list(disambiguate.values()) or all(
            basename in a.name for a in chain
        )


@pytest.mark.xfail
def test_generate_infobox():
    raise NotImplementedError


@pytest.mark.xfail
def test_generate_infoboxes():
    raise NotImplementedError


@pytest.mark.xfail
def test_generate_page():
    raise NotImplementedError
