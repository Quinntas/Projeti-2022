import requests


def get_ip_info(ip: str, api_key: str) -> dict:
    """
    To get info from ip
    """
    url = f"https://ipinfo.io/{ip}?token={api_key}"
    data = requests.get(url).json()
    ip = data['ip']
    org = data['org']
    city = data['city']
    country = data['country']
    region = data['region']

    return {
        "ip": ip,
        "org": org,
        "city": city,
        "country": country,
        "region": region
    }
