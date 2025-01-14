import tomli, logging, sys, requests, json, shutil, os, subprocess, argparse
from subprocess import CalledProcessError
from datetime import datetime, timedelta


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.toml")

    parser = argparse.ArgumentParser(description="Process some boolean flags.")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("--pushremote", action="store_true")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s]: %(message)s")

    logging.debug(f"Args: {args}")
    with open(config_path, mode="rb") as f:
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
    target_date = get_prev_day(today)
    logging.info("Today: %s", today)
    logging.info("Target date: %s", target_date)

    summary = {}
    new_games = []
    losses = 0
    summary["date"] = target_date
    for game in games_data:
        date = " ".join(game["date"].split()[:3])
        if date == target_date:
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
    win_perc = (
        f"{round(wins / len(new_games) * 100)}%" if len(new_games) > 0 else "No games"
    )
    winrate = f"{len(new_games) - losses}W / {losses}L ({win_perc})"
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

        # --copy
        if args.copy:
            shutil.copy(fname, dest_path)
            logging.info(f"summary copied to '{dest_path}' (format={dest_format})")
    except Exception as e:
        logging.error(f"err copying summary - {e}")

    # --pushremote
    if args.pushremote:
        logging.debug("trying to push new file to remote...")
        try:
            subprocess.run(["git", "pull"], cwd=dest_path, check=True)
            subprocess.run(["git", "add", fname], cwd=dest_path, check=True)
            commit_msg = f"[ladder] Add summary for {summary['date']}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg], cwd=dest_path, check=True
            )
            subprocess.run(["git", "push"], cwd=dest_path, check=True)
        except CalledProcessError as e:
            logging.error(f"git failed to auto commit - {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"unknown err pushing changes to remote - {e}")
            sys.exit(1)

    logging.info("done")


get_prev_day = (
    lambda date_str: (
        datetime.strptime(date_str, "%b %d %Y") - timedelta(days=1)
    ).strftime("%b %d %Y")
    if date_str
    else None
)


def find_nth(source: str, target: str, n: int) -> int:
    start = source.find(target)
    while start >= 0 and n > 1:
        start = source.find(target, start + len(target))
        n -= 1
    return start


if __name__ == "__main__":
    main()
