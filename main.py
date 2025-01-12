import tomli, logging, sys, requests, json, shutil, os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]: %(message)s")


def main():
    with open("config.toml", mode="rb") as f:
        config = tomli.load(f)
        try:
            expected_keys = [
                "nonapa_user_id",
                "season",
                "region_id",
                "realm_id",
                "dest_format",
                "dest_path",
            ]
            user_id, season, region_id, realm_id, dest_format, dest_path = (
                config[key] for key in expected_keys
            )
        except KeyError:
            logging.error(
                f"Missing keys in config.toml. Expected keys: {expected_keys}"
            )
            sys.exit(1)

    logging.debug(f"Config:")
    [logging.debug(f"{key} : {config[key]}") for key in expected_keys]

    base_url = (
        f"https://nonapa.com/games/{region_id}/{realm_id}/{user_id}?season={season}"
    )
    res = requests.get(base_url)
    if res.status_code != 200:
        logging.error(f"req failed - code: {res.status_code}, content: {res.content}")
        sys.exit(1)

    # gamesData position info in the res html
    data_idx = 3
    data_comment_start = "/*<![CDATA[*/"
    data_comment_end = "/*]]>*/"

    start = find_nth(res.text, data_comment_start, data_idx)
    end = find_nth(res.text, data_comment_end, data_idx)
    if start != -1 and end != -1:
        start += len(data_comment_start)
        games_data = res.text[start:end].strip()
    else:
        logging.error("gamesData not found")
        sys.exit(1)

    js_var_str = "var gamesData  = "
    games_data = games_data.replace(js_var_str, "")
    try:
        games_data = json.loads(games_data)
        with open("games_raw.json", "w") as json_file:
            json.dump(games_data, json_file, indent=4)
    except json.JSONDecodeError as e:
        logging.error(f"err parsing json (games_data) - {e}")
        sys.exit(1)

    # get games from prev day
    today = datetime.now().strftime("%b %d %Y")
    logging.info("Today: %s", today)

    summary = {}
    new_games = []
    losses = 0
    for game in games_data:
        date = " ".join(game["date"].split()[:3])
        if is_time_diff_1d(today, date) == True:
            if not "date" in summary:
                logging.debug(f"Init summary date with {date}")
                summary["date"] = date
            logging.debug(f"Game data: {json.dumps(game, indent=4)}")
            try:
                result = "L" if game["resolution"] == "Loss" else "W"
                losses += result == "L"
                mode = f"{len(game['members'])}v{len(game['members'])}"
                game_summary = {
                    "result": result,
                    "mode": mode,
                }
                new_games.append(game_summary)
            except Exception as e:
                logging.error(f"failed to summarize game - {e}")
                sys.exit(1)

    wins = len(new_games) - losses
    win_perc = round(wins / len(new_games) * 100)
    winrate = f"{len(new_games) - losses}W / {losses}L ({win_perc}%)"
    summary["winrate"] = winrate
    summary["matches"] = new_games

    try:
        fname = f"summary {summary['date']}.json"
        with open(fname, "w") as f:
            json.dump(summary, f, indent=4)
    except json.JSONDecodeError as e:
        logging.error(f"err parsing json (summary) - {e}")
        sys.exit(1)

    logging.debug(f"dest path: {dest_path}")
    if not os.path.exists(dest_path):
        logging.error(f"destination path does not exist - {dest_path}")
        sys.exit(1)
    try:
        # copy the summary to target dest
        if dest_format == "markdown":
            fname = f"summary {summary['date']}.md"
            with open(fname, "w") as md_file:
                md_file.write(
                    f"""## Winrate {winrate}\n\n```json\n{json.dumps(summary, indent=4)}\n```"""
                )

        shutil.copy(fname, dest_path)
        logging.info(f"summary copied to '{dest_path}' (format={dest_format})")
    except Exception as e:
        logging.error(f"err copying summary - {e}")

    logging.info("done")


def is_time_diff_1d(date1, date2):
    format = "%b %d %Y"
    try:
        d1 = datetime.strptime(date1, format)
        d2 = datetime.strptime(date2, format)
    except Exception as e:
        logging.error(f"Failed to check time diff - {e}")
    return (d1 - d2).days == 1


def find_nth(source: str, target: str, n: int) -> int:
    start = source.find(target)
    while start >= 0 and n > 1:
        start = source.find(target, start + len(target))
        n -= 1
    return start


if __name__ == "__main__":
    main()
