<?xml version="1.0" encoding="UTF-8"?>
<gameSystem xmlns="http://www.battlescribe.net/schema/gameSystemSchema" id="b174-c09d-3660-f001" name="One Page Rules - Grimdark Future (Community Test)" revision="5" battleScribeVersion="2.03" authorName="Community test" >
  <costTypes><costType id="b174-c09d-3660-f002" name="pts" defaultCostLimit="-1" hidden="false"/></costTypes>
  <profileTypes>
    <profileType id="b174-c09d-3660-f010" name="Unit"><characteristicTypes>
      <characteristicType id="b174-c09d-3660-f011" name="Quality"/>
      <characteristicType id="b174-c09d-3660-f012" name="Defense"/>
      <characteristicType id="b174-c09d-3660-f013" name="Special Rules"/>
    </characteristicTypes></profileType>
    <profileType id="b174-c09d-3660-f020" name="Ranged Weapon"><characteristicTypes>
      <characteristicType id="b174-c09d-3660-f021" name="Range"/>
      <characteristicType id="b174-c09d-3660-f022" name="Attacks"/>
      <characteristicType id="b174-c09d-3660-f023" name="Special Rules"/>
    </characteristicTypes></profileType>
    <profileType id="b174-c09d-3660-f030" name="Melee Weapon"><characteristicTypes>
      <characteristicType id="b174-c09d-3660-f031" name="Attacks"/>
      <characteristicType id="b174-c09d-3660-f032" name="Special Rules"/>
    </characteristicTypes></profileType>
  </profileTypes>
  <categoryEntries>
    <categoryEntry id="opr-spell-catalogue-category" name="Spell Catalogue" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f041" name="Heroes" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f048" name="Epic Heroes" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f042" name="Core Units" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f043" name="Light Vehicles / Small Monsters" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f044" name="Vehicles / Monsters" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f045" name="Artillery" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f046" name="Titans" hidden="false"/>
    <categoryEntry id="b174-c09d-3660-f047" name="Aircraft" hidden="false"/>
  </categoryEntries>
  <forceEntries><forceEntry id="b174-c09d-3660-f050" name="Army" hidden="false">
    <categoryLinks>
        <categoryLink id="opr-spell-catalogue-force-link" name="Spell Catalogue" hidden="false" targetId="opr-spell-catalogue-category" primary="false"/>
        <categoryLink id="b174-c09d-3660-f060" name="Heroes" hidden="false" targetId="b174-c09d-3660-f041" primary="false"/>
        <categoryLink id="b174-c09d-3660-f068" name="Epic Heroes" hidden="false" targetId="b174-c09d-3660-f048" primary="false"/>
        <categoryLink id="b174-c09d-3660-f061" name="Core Units" hidden="false" targetId="b174-c09d-3660-f042" primary="false"/>
        <categoryLink id="b174-c09d-3660-f062" name="Light Vehicles / Small Monsters" hidden="false" targetId="b174-c09d-3660-f043" primary="false"/>
        <categoryLink id="b174-c09d-3660-f063" name="Vehicles / Monsters" hidden="false" targetId="b174-c09d-3660-f044" primary="false"/>
        <categoryLink id="b174-c09d-3660-f064" name="Artillery" hidden="false" targetId="b174-c09d-3660-f045" primary="false"/>
        <categoryLink id="b174-c09d-3660-f065" name="Titans" hidden="false" targetId="b174-c09d-3660-f046" primary="false"/>
        <categoryLink id="b174-c09d-3660-f066" name="Aircraft" hidden="false" targetId="b174-c09d-3660-f047" primary="false"/>
      </categoryLinks>
  </forceEntry></forceEntries>
  <sharedRules>
    <rule id="opr-core-aircraft" name="Aircraft" hidden="false"><description>May only Advance, in a straight line, adding 30 inches to movement even when Shaken. Ignores units and terrain when moving and stopping; cannot seize or contest objectives, be contacted or charged. Attacks targeting it suffer -12 inches range and -1 to hit.</description></rule>
    <rule id="opr-core-ambush" name="Ambush" hidden="false"><description>May be held off-table before deployment. At the beginning of any round after the first, deploy over 9 inches from enemies. Players alternate placing Ambush units, starting with the next player to activate. Cannot seize or contest objectives in the deployment round.</description></rule>
    <rule id="opr-core-ap" name="AP(X)" hidden="false"><description>Targets subtract X from Defense rolls against hits from this weapon.</description></rule>
    <rule id="opr-core-artillery" name="Artillery" hidden="false"><description>When holding and shooting enemies over 12 inches away, this model gets +1 to hit. If most models have this rule and have not moved this round, enemy shooting from over 12 inches suffers -1 to hit.</description></rule>
    <rule id="opr-core-assault" name="Assault" hidden="false"><description>Counts as both a ranged and a melee weapon.</description></rule>
    <rule id="opr-core-bane" name="Bane" hidden="false"><description>Ignores Regeneration; the target re-rolls unmodified Defense rolls of 6.</description></rule>
    <rule id="opr-core-blast" name="Blast(X)" hidden="false"><description>Ignores Cover. After other special rules resolve, multiply each hit by X, capped at the number of models in the target unit.</description></rule>
    <rule id="opr-core-caster" name="Caster(X)" hidden="false"><description>Gains X spell tokens at the start of each round, maximum 6. Once per activation before attacking, spend tokens equal to spell values to attempt one or more spells, once per spell. Choose a target and roll; on 4+ resolve the effect. Models within 18 inches may spend tokens before the roll for +1/-1 per token.</description></rule>
    <rule id="opr-core-counter" name="Counter" hidden="false"><description>May attack first with this weapon when charged, unless Fatigued.</description></rule>
    <rule id="opr-core-cumbersome" name="Cumbersome" hidden="false"><description>May only Hold or Advance, and cannot shoot when moving.</description></rule>
    <rule id="opr-core-deadly" name="Deadly(X)" hidden="false"><description>Assign each wound to one model and multiply by X. Resolve Deadly hits first; excess wounds do not carry over to other models.</description></rule>
    <rule id="opr-core-fast" name="Fast" hidden="false"><description>Advance +2 inches; Rush/Charge +4 inches.</description></rule>
    <rule id="opr-core-fear" name="Fear(X)" hidden="false"><description>In melee with this model, enemies count as having suffered X additional wounds when determining the winner.</description></rule>
    <rule id="opr-core-fearless" name="Fearless" hidden="false"><description>When a unit with a majority of models with this rule fails a Morale Test, roll a die; on 4+ it passes instead.</description></rule>
    <rule id="opr-core-flying" name="Flying" hidden="false"><description>May move through units and terrain, ignoring Difficult and Dangerous terrain effects.</description></rule>
    <rule id="opr-core-furious" name="Furious" hidden="false"><description>When charging, an unmodified hit roll of 6 produces one additional hit; only the original hit counts as a 6 for special rules.</description></rule>
    <rule id="opr-core-hero" name="Hero" hidden="false"><description>Heroes up to Tough(6) may deploy with a multi-model unit without another Hero, using that unit's Defense until all other models die. The Hero's unit, and units within 6 inches of friendly Heroes with Tough(9) or higher, may use the Hero's Quality for Morale Tests if the Hero is not Shaken.</description></rule>
    <rule id="opr-core-immobile" name="Immobile" hidden="false"><description>May only Hold.</description></rule>
    <rule id="opr-core-impact" name="Impact(X)" hidden="false"><description>When charging, before either side attacks, roll X dice unless Fatigued; each 2+ inflicts one hit.</description></rule>
    <rule id="opr-core-indirect" name="Indirect" hidden="false"><description>When holding and shooting, may target enemies outside line of sight as though visible and ignores Cover from Sight Blockers.</description></rule>
    <rule id="opr-core-limited" name="Limited" hidden="false"><description>May be used only once per game.</description></rule>
    <rule id="opr-core-regeneration" name="Regeneration" hidden="false"><description>When a unit with a majority of models with this rule suffers wounds, roll for each wound; on 5+ ignore it.</description></rule>
    <rule id="opr-core-relentless" name="Relentless" hidden="false"><description>When this model shoots enemies over 9 inches away, each unmodified hit roll of 6 produces one extra hit; only the original counts as a 6 for special rules.</description></rule>
    <rule id="opr-core-reliable" name="Reliable" hidden="false"><description>Attacks at Quality 2+.</description></rule>
    <rule id="opr-core-rending" name="Rending" hidden="false"><description>Ignores Regeneration; unmodified hit rolls of 6 gain AP(+4).</description></rule>
    <rule id="opr-core-scout" name="Scout" hidden="false"><description>May be held off-table before deployment. After other units deploy, deploy fully within 9 inches of own deployment zone and over 9 inches from non-Scout enemies. Players alternate placing Scouts, starting with the next player to activate.</description></rule>
    <rule id="opr-core-shred" name="Shred" hidden="false"><description>Each unmodified Defense roll of 1 against this weapon causes one additional wound.</description></rule>
    <rule id="opr-core-slow" name="Slow" hidden="false"><description>Advance -2 inches; Rush/Charge -4 inches.</description></rule>
    <rule id="opr-core-spell-amplifier" name="Spell Amplifier" hidden="false"><description>Gets +1 to casting rolls.</description></rule>
    <rule id="opr-core-stealth" name="Stealth" hidden="false"><description>When a unit with a majority of models with this rule is shot from over 9 inches, enemies suffer -1 to hit.</description></rule>
    <rule id="opr-core-strider" name="Strider" hidden="false"><description>May ignore Difficult terrain effects.</description></rule>
    <rule id="opr-core-surge" name="Surge" hidden="false"><description>Each unmodified hit roll of 6 produces one extra hit; only the original counts as a 6 for special rules.</description></rule>
    <rule id="opr-core-takedown" name="Takedown" hidden="false"><description>May choose an individual model in the target unit for this weapon's attacks, resolving it as a unit of one. Resolve Takedown attacks before other weapons.</description></rule>
    <rule id="opr-core-thrust" name="Thrust" hidden="false"><description>When charging, gains +1 to hit and AP(+1) in melee.</description></rule>
    <rule id="opr-core-tough" name="Tough(X)" hidden="false"><description>Requires X wounds to kill this model. A Tough model joining a unit without Tough is removed last. Continue assigning wounds to the most wounded Tough model until killed before moving to another; Heroes receive wounds last even if wounded.</description></rule>
    <rule id="opr-core-transport" name="Transport(X)" hidden="false"><description>Carries up to X friendly models; Heroes up to Tough(6) and non-Heroes up to Tough(3) occupy three spaces each. May deploy loaded. Units enter by contacting it using a move action and exit fully within 6 inches. Units inside and outside cannot target each other, but may target the transport. If destroyed, passengers take a Dangerous terrain test, become Shaken and are placed fully within 6 inches before removal.</description></rule>
    <rule id="opr-core-unstoppable" name="Unstoppable" hidden="false"><description>Ignores Regeneration and all negative modifiers to this weapon except those from this model's special rules.</description></rule>
  </sharedRules>
</gameSystem>
