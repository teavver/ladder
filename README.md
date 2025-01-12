# ladder
sc2 ladder progress tracking

## Cron job
1. `sudo chmod +x run.sh`
2. `0 12 * * * /<REPO_PATH>/run.sh >> /<REPO_PATH>/cron.log 2>&1`

## Configuration
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
dest_path = "/Users/teaver/Documents/Obsidian Vault/remote/SC2/stats"
```