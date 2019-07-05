# import the necessary packages
from PIL import Image
import pytesseract
import argparse
# import cv2
import os
import re
import phonenumbers
import csv
import logging
import time
import csv

# Use environment variable LOG_LEVEL to change
logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.INFO))
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, nargs='*',
	help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")
args = vars(ap.parse_args())

logging.debug("Args: ")
logging.debug(args)

def clean_phone(phone):
    if phone:
        cleaned = phonenumbers.parse(phone, "US")
        formatted_phone = phonenumbers.format_number(cleaned, phonenumbers.PhoneNumberFormat.E164)
        return formatted_phone
    return None

def get_phone_field(findstr, text):
    matches = re.search(r'%s\n\n?(.*)' % (findstr,), text, re.M | re.I)
    if matches:
        phone = matches.group(1).strip()
        return clean_phone(phone)
    else:
        return None

def get_field(field, text):
    matches = re.search(r'%s\n\n?(.*)' % (field,), text, re.M | re.I)
    if matches:
        return matches.group(1).strip()
    else:
        return None

def get_field_names(contacts):
    field_names = []
    for contact in contacts:
        if len(field_names) == 0:
            field_names = list(contact.keys())
        else:
            for name in contact.keys():
                if name not in field_names:
                    field_names.append(name)

    return field_names

def write_csv(contacts):
    current_time = time.strftime("%Y%m%d-%H%M%S")
    filename = f'./output/contacts.{current_time}.csv'

    f = open(filename, 'w')
    with f:
        field_names = get_field_names(contacts)
        print(field_names)
        writer = csv.DictWriter(f, fieldnames=field_names)    

        writer.writeheader()
        for contact in contacts:
            print(contact)
            writer.writerow(contact)

        logging.info(f"Wrote csv: {filename}")

def get_name_field(name):
    return {
        'Name': name,
        'Given Name': name.rsplit(' ', 1)[0],
        'Family Name': name.rsplit(' ', 1)[-1],

        # to make Google belive this is an official CSV :S
        'Yomi Name': '',
        'Given Name Yomi': '',
        'Additional Name Yomi': '',
        'Family Name Yomi': '',
        'Name Prefix': '',
        'Name Suffix': '',
        'Initials': '',
        'Nickname': '',
        'Short Name': '',
        'Maiden Name': '',
        'Birthday': '',
        'Gender': '',
        'Location': '',
        'Billing Information': '',
        'Directory Server': '',
        'Mileage': '',
        'Occupation': '',
        'Hobby': '',
        'Sensitivity': '',
        'Priority': '',
        'Subject': '',
        'Notes': '',
        'Language': '',
        'Photo': '',
        'Group Membership': '',
    }


def get_sane_phone_fields(home_phone, work_phone, mobile_phone):
    contact = {}
    if home_phone:
        contact[f'Home Phone'] = home_phone
    if work_phone:
        contact[f'Work Phone'] = work_phone
    if mobile_phone:
        contact[f'Mobile Phone'] = mobile_phone
    return contact

def get_google_contacts_phone_fields(home_phone, work_phone, mobile_phone):
    contact = {}
    counter = 1
    if home_phone:
        contact[f'Phone {counter} - Type'] = 'Home'
        contact[f'Phone {counter} - Value'] = home_phone
        counter += 1
    if work_phone:
        contact[f'Phone {counter} - Type'] = 'Work'
        contact[f'Phone {counter} - Value'] = work_phone
        counter += 1
    if mobile_phone:
        contact[f'Phone {counter} - Type'] = 'Mobile'
        contact[f'Phone {counter} - Value'] = mobile_phone
        counter += 1
    return contact

def clean_str(s):
    s = s.replace('\n', ' ').strip()
    s = re.sub(r'[0-9.\s]{2,}', '', s).strip()
    return s

def find_name(text):
    name_found = re.search(r'Edit\n\n?(.*)message', text, re.M | re.DOTALL)
    if name_found and clean_str(name_found.group(1)) != "":
        return clean_str(name_found.group(1))

    name_retry = re.search(r'Contacts\n\n?(.*)message', text, re.M | re.DOTALL)
    if name_retry and clean_str(name_retry.group(1)) != "":
        return clean_str(name_retry.group(1))
    
    name_retry = re.search(r'Edit\n\n?(.*)', text, re.M)
    if name_retry and clean_str(name_retry.group(1)) != "":
        return clean_str(name_retry.group(1))
    
    name_retry = re.search(r'Contacts\n\n?(.*)', text, re.M)
    if name_retry and clean_str(name_retry.group(1)) != "":
        return clean_str(name_retry.group(1))

    return False

def process_image(filename):

    text = pytesseract.image_to_string(Image.open(filename))
    logging.debug(f'TEXT: {text}')
    
    found_name = find_name(text)
    if not found_name:
        logging.warning(f"Can't find name in filename {filename}")
        logging.debug("Text found: " + text)
        return False

    name = found_name
    home_phone = get_phone_field(r'home', text)
    work_phone = get_phone_field(r'work', text)
    mobile_phone = get_phone_field(r'mobile', text)
    email = get_field(r'email', text)
    if not email:
        email = get_field(r'email (Siri found in Mail)', text)
    
    # print(name)
    # print(home_phone)
    # print(work_phone)
    # print(mobile_phone)
    # print(email)

    print("Found: " + str({
        "name": name,
        "home_phone": home_phone,
        "work_phone": work_phone,
        "mobile_phone": mobile_phone,
        "email": email,
    }))

    # Using google contacts field names
    contact = get_name_field(name)
    if email:
        contact['E-mail 1 - Type'] = '*'
        contact['E-mail 1 - Value'] = email
    contact.update(get_google_contacts_phone_fields(home_phone, work_phone, mobile_phone))
    print(contact)
    return contact


def run(files):

    contacts = []

    for filename in files:
        processed = process_image(filename)
        if processed:
            contacts.append(processed)
            logging.info("Contact added: " + str(processed))

    print("\nContacts:")
    print(contacts)
    write_csv(contacts)

run(args["image"])
