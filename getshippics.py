from os import read


try:
    import json
    import requests
    import os
    import urllib.request
    import unidecode
    import sys
    from tqdm import tqdm
except ModuleNotFoundError as error:
    print(error)
    print("Please make sure you have the required dependencies!")
    print("Required dependencies: tqdm, unidecode, requests")
    print(
        "You can install using \033[0;32;40m pip install tqdm unidecode requests\u001b[0m")
    exit()


# wargaming_key = 'https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id=ab69ce1bc38671074dc4bdc67b3645c7&r_realm=na'
# wargaming_modules = 'https://api.worldofwarships.com/wows/encyclopedia/modules/?application_id=ab69ce1bc38671074dc4bdc67b3645c7'

ship_path = os.path.relpath('ship_pics')
ship_file_name = 'ships.json'


def remove_accents(word):
    return unidecode.unidecode(word)


def getWargaming(api_key, realm):
    wargaming_key = f"https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id={api_key}&r_realm={realm}"
    return requests.get(f'{wargaming_key}&fields={",".join(["ship_id", "name"])}').json()


def main():
    results = {
        "ship_id_list": {},
        "ships": {}
    }
    count = 0
    # get list of all ships and their ids
    api_key = input(
        "Please provide a wargaming api key!\nYou can get one by signing up at \033[1;34;40mhttps://developers.wargaming.net/applications\033[0m and creating an application\n\033[1;34;40mapi key: \033[0m")
    realm = input(
        "Which realm do you want info from?\nDefault is North America. Choose from \033[1;33;40m'na', 'ru','eu', 'asia'\033[0m\n\033[1;34;40mRealm: \033[0m")
    if realm not in ['na', 'ru', 'eu', 'asia']:
        realm = 'na'
    print(f"Using realm {realm}")
    response = getWargaming(api_key, realm)
    while response["status"] == "error":
        print(response)
        if response["error"]["message"] == "INVALID_APPLICATION_ID":
            print(
                "\033[1;31;40mInvalid api key!\033[0m\nPlease re-enter your api key or quit with '-quit'")

        else:
            print(
                f"An error \033[1;31;40m[{response['error']['message']}]\033[0m occured fetching data from wargmaing's api. Exiting now...")
            exit()
        api_key = input("\033[1;34;40mapi key: \033[0m")
        if api_key == "-quit":
            exit()
        response = getWargaming(api_key, realm)

    pages = response["meta"]["page_total"]
    # wargaming gives data back in pages (100 each I think), iterate through all of them
    for i in range(pages):
        print(f'Page {i+1} of {pages}')
        response = requests.get(
            f'https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id={api_key}&r_realm={realm}&page_no={i+1}&fields={",".join(["ship_id", "name"])}').json()
        for ship in response["data"].values():
            count += 1
            results["ship_id_list"][ship["ship_id"]] = ship["name"]

    # dump to folder ship_pics
    if not os.path.exists(ship_path):
        os.makedirs(ship_path)
    with open(os.path.join(ship_path, ship_file_name), 'w+') as f:
        json.dump(results, f)
    print("Fetched " + str(count) + " ships")

    ship_ids = list(results["ship_id_list"].keys())
    index = 0
    while(ship_ids):
        print("Length of ship list: " + str(len(ship_ids)))
        print(f'Ship {index} to {index+min(len(ship_ids), 100)}')
        fetch_ship = ship_ids[0:min(len(ship_ids), 100)]
        index += min(len(ship_ids), 100)
        ship_ids = ship_ids[min(len(ship_ids), 100):]
        response = requests.get(
            f'https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id={api_key}&r_realm={realm}&ship_id={",".join(map(str, fetch_ship))}&fields={",".join(["ship_id","name", "type", "images"])}').json()
        total_pages = response["meta"]["page_total"]
        for i in range(total_pages):
            response = requests.get(
                f'https://api.worldofwarships.com/wows/encyclopedia/ships/?application_id={api_key}&r_realm={realm}&page_no={i+1}&ship_id={",".join(map(str, fetch_ship))}&fields={",".join(["ship_id","name", "type", "images"])}').json()
            data = response["data"]
            for ship in data.values():
                results["ships"][ship["ship_id"]] = ship
    with open(os.path.join(ship_path, ship_file_name), 'w') as f:
        json.dump(results, f)
    print("Total ships fetched: ", str(len(results["ships"])))

    # download the 555 pics lolll highest quality ofc


def get_images():
    print("getting images now...")
    with open(os.path.join(ship_path, ship_file_name), 'r') as f:
        results = json.load(f)

    for ship in tqdm(results["ships"].values()):
        urllib.request.urlretrieve(ship["images"]["large"], os.path.join(
            ship_path, f"{remove_accents(ship['name'])}_large.png"))


if __name__ == "__main__":
    try:
        if sys.argv[1]:
            if sys.argv[1] in ["--images", "-i"]:
                if not os.path.isfile(os.path.join(ship_path, ship_file_name)):
                    print(f"{ship_file_name} not found, creating now...")
                    main()
                get_images()
            elif sys.argv[1] in ["-h", "--help"]:
                print("Usage: " + os.path.basename(__file__) + " <arg1>")
                print(
                    "Available arguments:\n-h => shows this message\n-i => downloads images")
            else:
                print("Invalid Arguement!")
    except IndexError:
        print("No arguments provided...running main to download ship json now\nUse argument -h to see commands")
        main()
    # except:
    #   print("some unknown error occured lol")
