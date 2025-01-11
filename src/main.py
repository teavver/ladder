import os, tomli, logging, sys, requests
from dotenv import load_dotenv

logging.basicConfig(format="[%(levelname)s]: %(message)s")


def main():
    load_dotenv()

    client_id, client_secret = os.environ["client_id"], os.environ["client_secret"]
    if not client_id or not client_secret:
        logging.error("Missing 'client_id' or 'client_secret' env variables")
        sys.exit(1)

    with open("config.toml", mode="rb") as f:
        config = tomli.load(f)
        try:
            profile_id = config["profile_id"]
        except KeyError:
            logging.error("Missing 'profile_id' in config.toml")
            sys.exit(1)

    print(client_id)
    print(client_secret)
    print(profile_id)

    oauth_url = "https://oauth.battle.net/token"
    payload = {"grant_type": "client_credentials"}

    res = requests.post(oauth_url, auth=(client_id, client_secret), data=payload)
    if res.status_code == 200:
        print("res ", res.json())
        token_data = res.json()
        access_token = token_data.get("access_token")
        print(f"Access Token: {access_token}")
    else:
        logging.error(f"Failed to retrieve token: {res.status_code} - {res.text}")
        sys.exit(1)
        
    


if __name__ == "__main__":
    main()
