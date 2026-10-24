from seat_swap.prompts import parse_response
from seat_swap.scripted import completion_text

BODY = (
    "My observations and thoughts:\nobs\n\n"
    "New content for PLANS.txt:\nplan a\nplan b\n\n"
    "New content for INSIGHTS.txt:\ninsight\n\n"
)


def test_price_on_next_line():
    p = parse_response(BODY + "My chosen price:\n1.85")
    assert p.ok and p.price == 1.85 and p.plans == "plan a\nplan b" and p.insights == "insight"


def test_price_on_same_line():
    p = parse_response(BODY + "My chosen price: 1.85\n")
    assert p.ok and p.price == 1.85


def test_price_rounded_to_two_decimals():
    assert parse_response(BODY + "My chosen price:\n1.8537").price == 1.85
    assert parse_response(BODY + "My chosen price:\n2").price == 2.0


def test_think_block_is_ignored():
    assert parse_response("<think>\nmaybe 1.2\n</think>\n\n" + BODY + "My chosen price:\n1.9").price == 1.9


def test_strict_failures():
    for bad in (
        BODY + "My chosen price: $1.85",
        BODY + "My chosen price: **1.85**",
        BODY + "My chosen price: 1.85 because",
        "My chosen price: 1.85",  # notes sections missing
        BODY,
        "",
    ):
        p = parse_response(bad)
        assert not p.ok and p.price is None, bad


def test_plain_mode():
    assert parse_response("My chosen price: 1.7", notes_on=False).price == 1.7
    assert not parse_response("I pick 1.7", notes_on=False).ok


def test_product_information_matches_fish():
    from seat_swap.game import make_env

    user = make_env(seed=0).generate_prompt(1)[1]["content"]
    assert "The cost I pay to produce each unit is $1.\n" in user
    assert "No customer would pay more than $2.89." in user


def test_scripted_text_parses():
    p = parse_response(completion_text(1.73, 1, 4))
    assert p.ok and p.price == 1.73 and "[dry-run seat 1 round 4]" in p.plans


def test_bracketed_price_is_accepted_and_flagged():
    from seat_swap.prompts import parse_response
    from seat_swap.scripted import completion_text

    ok = parse_response(completion_text(1.6, 0, 1).replace("\n1.60", "\n<1.60>"))
    assert ok.ok and ok.price == 1.6 and ok.bracketed
    assert not parse_response(completion_text(1.6, 0, 1)).bracketed
    for bad in ("<1.60", "1.60>", "<<1.60>>", "<1.60> extra"):
        assert not parse_response(completion_text(1.6, 0, 1).replace("\n1.60", "\n" + bad)).ok, bad
    assert parse_response("My chosen price: <1.7>", notes_on=False).bracketed
