# YellowScribe / Tabletop Simulator compatibility exports

The army catalogues remain **New Recruit-native**. Do not move optional
equipment rules permanently onto unit entries: this would display unselected
abilities. Instead convert the roster **after exporting it from New Recruit**.

```sh
python scripts/prepare_yellowscribe_rosz.py "My OPR army.rosz"
```

This creates `My OPR army-yellowscribe.rosz` for YellowScribe. You can
specify an output with `-o output.rosz`. Keep the original roster for New Recruit.

The converter works across Battle Brothers, Robot Legions and Custodian
Brothers (and other BattleScribe-compatible rosters) by reading **only
selected roster entries**, including nested model equipment. It copies
non-weapon rules from those selected entries to the containing unit's
rules and Unit-profile Special Rules. Weapon keywords, such as AP(X),
Reliable, Shatter and Rending, stay with the equipped weapon. Native
Tough(X), Quality, Defense, points and weapon profiles are untouched.
Selected rules already represented on the unit are deduplicated. The
converter is idempotent.

**Confirmed in Tabletop Simulator:** Robot Lord + Re-Animator produced
the Reanimation Aura display using the initial single-upgrade conversion.
The generalised converter was checked against an exported 1,000-point
Robot Legions roster, plus synthetic examples of all three factions.
Full YellowScribe/TTS rendering still needs a user-side check for each
distinct kind of ability (for example model-specific abilities and armour).

Run the synthetic regression suite:

```sh
python -m unittest discover -s scripts -p "test_yellowscribe_conversion.py"
```

The conversion does **not** modify the catalogues, automate New Recruit's
export UI, or automatically import the resulting roster into YellowScribe.
An equipped selection that has neither an explicit exported rule nor a
weapon profile cannot be inferred; such edge cases need source review.
