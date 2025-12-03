from ncaa.gender_resolver import DefaultGenderResolver, GenderResolver
from ncaa.models import Gender


def test_default_gender_resolver_interface():
    resolver = DefaultGenderResolver()
    assert isinstance(resolver, GenderResolver)


def test_resolve_keeps_specified_gender():
    resolver = DefaultGenderResolver()

    assert resolver.resolve("Basketball", Gender.MEN) == Gender.MEN
    assert resolver.resolve("Basketball", Gender.WOMEN) == Gender.WOMEN
    assert resolver.resolve("Basketball", Gender.COED) == Gender.COED


def test_resolve_applies_defaults():
    resolver = DefaultGenderResolver()

    assert resolver.resolve("softball", Gender.UNSPECIFIED) == Gender.WOMEN
    assert resolver.resolve("Softball", Gender.UNSPECIFIED) == Gender.WOMEN
    assert resolver.resolve("baseball", Gender.UNSPECIFIED) == Gender.MEN
    assert resolver.resolve("Baseball", Gender.UNSPECIFIED) == Gender.MEN
    assert resolver.resolve("field hockey", Gender.UNSPECIFIED) == Gender.WOMEN
    assert resolver.resolve("football", Gender.UNSPECIFIED) == Gender.MEN


def test_resolve_unknown_sport():
    resolver = DefaultGenderResolver()

    assert resolver.resolve("Cricket", Gender.UNSPECIFIED) == Gender.UNSPECIFIED


def test_register_default():
    resolver = DefaultGenderResolver()

    resolver.register_default("Cricket", Gender.MEN)
    assert resolver.resolve("cricket", Gender.UNSPECIFIED) == Gender.MEN


def test_register_default_case_insensitive():
    resolver = DefaultGenderResolver()

    resolver.register_default("New Sport", Gender.WOMEN)
    assert resolver.resolve("new sport", Gender.UNSPECIFIED) == Gender.WOMEN
    assert resolver.resolve("NEW SPORT", Gender.UNSPECIFIED) == Gender.WOMEN
