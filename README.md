# Jellyfin Episode Grouper

Since Jellyfin doesn't automatically group episodes with multiple versions I
created a small script using the HTTP API to do this for me. You may use the
script however you like on your own risk, I offer no guarranties or support and
provide the script as is.

To run it use python (I use 3.10.5 but I'm pretty sure it would work for most
python 3 versions) and run:

```sh
./jellyfin-episode-grouper.py <JELLYFIN_URL> <API_KEY> <USERNAME>
```

- `<JELLYFIN_URL>` would be the url where you normally access your Jellyfin
  instance, e.g. `https://media.example.com`.
- `<API_KEY>` is generated under `Dashboard -> API Keys`, click the `+` button to
  generate your key.
- `<USERNAME>` you seem to be able to use any username that exists on your server

The script will collect all items on the server that are marked as a series and
loop through each series season looking for episodes that has one or more
duplicates on `imdbId`, `tvdbId` or `name` (without the "version flag" in the
name). The "version flag" in the name is removed using this regex: `r" - [\w]+$"`

Vote for the [feature request in their tracker](https://features.jellyfin.org/posts/251/multiple-versions-drop-down-on-tv-series).
