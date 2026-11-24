# Tombola OPR TTS bridge (New Recruit)

This is a **standalone, original adapter** for our Grimdark Future catalogue. It converts New Recruit / BattleScribe `.rosz` lists to a response JSON shaped like Tombola's TTS Workshop importer expects. It does **not** import or copy the Tombola application source.

## Convert

Requires Python 3, no external packages.

```bash
python3 tools/opr-to-tombola/bridge.py "My list.rosz" -o list.json
```

The JSON contains `listId` and `listJson`. `listJson` contains `gameSystem: "gf"`, `rulesVersion: "3.6"`, `listName`, and `units[*].modelDefinitions[*]`, each with names, loadout summaries, TTS text and Tough values.

## Import into Tombola's existing TTS mod

TTS needs to fetch the JSON using an accessible **HTTPS URL**. This private GitHub repository cannot be used directly as an unauthenticated URL. You can upload the static JSON to a public static host, and paste the resulting HTTPS URL into [Tombola's TTS Workshop mod](https://steamcommunity.com/sharedfiles/filedetails/?id=2969610810).

A ready-to-deploy static site package, larger conversion tool, and real-roster example are available in the accompanying ChatGPT artifact.

**Status:** local conversion tested against the user's 1,300pt OPR Battle Brothers list (8 units / 26 models); TTS loading has **not** been verified. The previously exported Pathfinder Snipers contain two mutually exclusive rifles; refresh the New Recruit catalogue (revision 15 or newer) and export a clean new roster first. This compact GitHub script does not flag that conflict; the larger converter does.

## Upstream interoperability source

The expected payload fields were checked against [Tombola's public source](https://github.com/thomascgray/opr-af-to-tts), specifically `src/types.ts`, `src/utils.tsx`, and `tts_lua_code/mod.lua`. No explicit licence file was found at the root during review, so do not copy upstream code without checking permission and licensing.
