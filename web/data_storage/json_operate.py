import json
import os


def add_booking(name, surname, phone, land_id):
    new_booking = {
        "name": name,
        "surname": surname,
        "phone": phone,
        "land_id": land_id
    }

    if os.path.exists('data_storage/forms.json'):
        with open('data_storage/forms.json', 'r', encoding='utf-8') as bookings_file:
            try:
                bookings = json.load(bookings_file)
            except json.JSONDecodeError:
                bookings = []
    else:
        bookings = []

    bookings.append(new_booking)

    with open('data_storage/forms.json', 'w', encoding='utf-8') as bookings_file:
        json.dump(bookings, bookings_file, indent=4)

    return 0


def add_land(land_id, cost, square, land_data_url, status):
    new_land = {
        'land_id': land_id,
        'cost': cost,
        'square': square,
        'land_data_url': land_data_url,
        'status': status,
    }
    if os.path.exists('data_storage/lands.json'):
        with open('data_storage/lands.json', 'r', encoding='utf-8') as lands_file:
            try:
                lands = json.load(lands_file)
            except json.JSONDecodeError:
                lands = []
    else:
        lands = []

    lands.append(new_land)

    with open('data_storage/lands.json', 'w', encoding='utf-8') as lands_file:
        json.dump(lands, lands_file, indent=4)

    return 0


def change_land_status(land_id, new_status):
    if os.path.exists('data_storage/lands.json'):
        with open('data_storage/lands.json', 'r', encoding='utf-8') as lands_file:
            try:
                lands = json.load(lands_file)
            except json.JSONDecodeError:
                lands = []
    else:
        lands = []

    for land in lands:
        if land['land_id'] == land_id:
            land['status'] = new_status
            break

    with open('data_storage/lands.json', 'w', encoding='utf-8') as lands_file:
        json.dump(lands, lands_file, indent=4)

    return 0


def get_lands():
    if os.path.exists('data_storage/lands.json'):
        with open('data_storage/lands.json', 'r', encoding='utf-8') as lands_file:
            try:
                lands = json.load(lands_file)
            except json.JSONDecodeError:
                lands = []
    else:
        lands = []

    return lands


# add_land('1', 1_000_000, 50, 'https://daun.com', 0)
# add_land('2', 1_500_000, 55, 'https://eblan.com', 1)
# add_land('3', 2_000_000, 100, 'https://huesos.com', 0)
# add_land('4', 500_000, 25, 'https://lox.com', 0)