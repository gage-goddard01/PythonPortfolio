import random
import string

def generate_password(password_length):
    all_possible_password_characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    
    password = []
    for i in range(password_length):
        character_selected = random.choice(all_possible_password_characters)
        password.append(character_selected)
    return "".join(password)
    

