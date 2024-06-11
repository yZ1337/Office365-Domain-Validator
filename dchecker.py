import argparse
import requests
import re
import xml.etree.ElementTree as ET
from colorama import Fore, Style, init

def check_domain_or_email(input_string):
    # Regex pattern to match a valid domain or email
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$|^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if re.match(pattern, input_string):
        return True
    else:
        return False

def parse_xml_response(response_text):
    root = ET.fromstring(response_text)
    realm_info = {}

    for child in root:
        realm_info[child.tag] = child.text

    return realm_info

def format_output(realm_info):
    output = []
    is_federated = realm_info.get('IsFederatedNS', 'false') == 'true'
    cloud_instance_name = realm_info.get('CloudInstanceName', '')

    # Adding colors
    init(autoreset=True)
    if not is_federated:
        output.append(f"[*] IsFederatedNS: {Fore.RED}false{Style.RESET_ALL}")
    else:
        output.append(f"[*] IsFederatedNS: {Fore.LIGHTGREEN_EX}true{Style.RESET_ALL}")

    if cloud_instance_name == 'microsoftonline.com':
        output.append(f"[*] Microsoft Office: {Fore.LIGHTGREEN_EX}true{Style.RESET_ALL}")
    else:
        output.append(f"[*] Microsoft Office: {Fore.RED}false{Style.RESET_ALL}")

    return "\n".join(output)

def get_realm_info(user_input):
    if not check_domain_or_email(user_input):
        raise ValueError("Invalid input. Please enter a valid domain or email address.")

    # Construct the URL
    url = f"https://login.microsoftonline.com/getuserrealm.srf?login={user_input}&xml=1"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.RequestException as e:
        raise SystemExit(f"Request failed: {e}")

def process_input(user_input):
    try:
        result = get_realm_info(user_input)
        realm_info = parse_xml_response(result)
        formatted_output = format_output(realm_info)
        print(f"{Fore.YELLOW}[{user_input}]{Style.RESET_ALL}")
        print(formatted_output)
        print("\n")
    except ValueError as e:
        print(Fore.RED + f"Error: {e}")
    except SystemExit as e:
        print(Fore.RED + str(e))

def main():
    parser = argparse.ArgumentParser(description="Retrieve Realm Info for given domains or emails.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--user', help="Single domain or email to query, e.g., example.com or user@example.com")
    group.add_argument('-f', '--file', help="Path to a text file containing domains or emails, one per line.")

    args = parser.parse_args()

    user_inputs = []

    if args.user:
        user_inputs.append(args.user)
    elif args.file:
        with open(args.file, 'r') as file:
            lines = file.readlines()
            user_inputs = [line.strip() for line in lines]

    for user_input in user_inputs:
        process_input(user_input)

if __name__ == "__main__":
    main()
