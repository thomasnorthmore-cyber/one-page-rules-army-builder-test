<?xml version="1.0" encoding="UTF-8"?>
<gameSystem xmlns="http://www.battlescribe.net/schema/gameSystemSchema" id="b174-c09d-3660-f001" name="One Page Rules - Grimdark Future (Community Test)" revision="3" battleScribeVersion="2.03" authorName="Community test" >
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
</gameSystem>
