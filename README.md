# Clickventure Archive Project

This is a project to archive the clickhole clickventures so they are playable locally. This involved "decompiling" the adventures into a json format, and writing a player for them from scratch.

## Archiving

To archive, do:

```bash
./fetcher.py # will take a long time due to downloading all the images
./indexer.py # generates the viewer html files and main game index
```

An already archived version can be download from the internet archive (link pending)

## Playing

To play the clickventures, host the contents of the "out" folder on an http server. I recommend:

```
cd out
python3 -m http.server
```

## TODO:

 - "Your Neighbor Ate Your Bird. Time To Get Revenge." - twine based, not currently archived
 - "Mr. Circle Goes to Shape City" - mostly broken, links to other clickventures, needs more TLC than I can give right now