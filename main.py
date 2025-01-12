import tomli, logging, sys, requests, re, json

logging.basicConfig(format="[%(levelname)s]: %(message)s")


def main():
    with open("config.toml", mode="rb") as f:
        config = tomli.load(f)
        try:
            expected_keys = ["nonapa_user_id", "season", "region_id", "realm_id"]
            user_id, season, region_id, realm_id = (
                config[key] for key in expected_keys
            )
        except KeyError:
            logging.error(
                f"Missing keys in config.toml. Expected keys: {expected_keys}"
            )
            sys.exit(1)

    print(f"Config:")
    [print(f"{key} : {config[key]}") for key in expected_keys]

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
        print("gamesData not found")
        
    js_var_str = "var gamesData  = "
    games_data = games_data.replace(js_var_str, "")
    try:
        games_data = json.loads(games_data)
        # print(games_data)
        with open('games.json', 'w') as json_file:
            json.dump(games_data, json_file, indent=4)
    except json.JSONDecodeError as e:
        print(f'err parsing json - {e}')
    
    print("done")


def find_nth(source: str, target: str, n: int) -> int:
    start = source.find(target)
    while start >= 0 and n > 1:
        start = source.find(target, start + len(target))
        n -= 1
    return start


if __name__ == "__main__":
    main()
