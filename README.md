# ladder

sc2 ladder progress tracking

<!-- 
## Cron job
* `sudo chmod +x run.sh`
* `0 12 * * * /<REPO_PATH>/run.sh >> /<REPO_PATH>/cron.log 2>&1`
 -->

<!-- 
 ## launchd
 `sudo cp ~/ladder/com.ladder.plist ~/Library/LaunchAgents/`
 `launchctl load ~/Library/LaunchAgents/com.ladder.plist`
 -->

## Configuration

| Arg              | Description                                              |
|------------------|----------------------------------------------------------|
| `--debug`        | Additional logging                                       |
| `--copy`         | Will copy summary to `dest_path`                         |
| `--pushremote`   | Will try to push copied summary to remote in `dest_path` |
| `--cleanup`      | Delete local summary files (json,md) before exiting      |

```toml

# Go to https://nonapa.com/ & search for your profile
nonapa_user_id = 6650632
season = 62

# https://develop.battle.net/documentation/guides/regionality-and-apis
region_id = 2
realm_id = 1

# json | markdown
dest_format = "markdown"

# the summary will be copied to this path
dest_path = "/Users/<USER>/Documents/Obsidian Vault/remote/SC2/stats"
```

## Example summary (JSON)

```json
{
    "date": "Jan 12 2025",
    "winrate": "1W / 1L (50%)",
    "matches": [
        {
            "result": "W",
            "mode": "1v1"
        },
        {
            "result": "L",
            "mode": "2v2"
        }
    ]
}
```
