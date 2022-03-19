from API import PetFriends
from settings import valid_email, valid_password, test_email, test_password
import os

pf = PetFriends()

def test_get_api_key_for_valid_user (email = valid_email, password = valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result

def test_get_all_pets_with_valid_key(filter = ""):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result  = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet_with_valid_key(name="Vasya", animal_type="cat", age='2', pet_photo='images\pet_photo.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

def test_delete_my_pet(email = valid_email, password = valid_password):
    _, auth_key = pf.get_api_key(email, password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, name="Polkan", animal_type="dog", age='1', pet_photo='images\pet_photo.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_api_pets(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    assert status == 200
    assert pet_id not in my_pets.values()

def test_update_pet_info(email = valid_email, password = valid_password, name="Polkan", animal_type="dog", age='4'):
    _, auth_key = pf.get_api_key(email, password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

def test_create_pet_without_photo(name="Pushok", animal_type="kitty", age='2'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

def test_add_pet_photo(pet_photo='images\photo.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        pet_name = my_pets['pets'][0]['name']
        status, result = pf.set_pet_photo(auth_key, pet_id, pet_photo)
        assert status == 200
        assert pet_name == result['name']
        assert result['pet_photo'] is not None
    else:
        raise Exception("There is no pets to update photo")

def test_get_auth_key_with_wrong_password(email = valid_email):
    status, _ = pf.get_api_key(email,"0")
    assert status == 403

def test_get_my_pets_with_incorrect_key(auth_key={'key':'1111'}, filter='my_pets'):
    status, _ = pf.get_list_of_pets(auth_key, filter)
    assert status == 403

def test_create_long_pet_name(animal_type = 'dog', age = 4):
    name = '12345678asdfghjk'*20
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, _ = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 400

def test_update_pet_name(new_name = "Kitty"):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        animal_type = my_pets['pets'][0]['animal_type']
        age = my_pets['pets'][0]['age']
        status, result = pf.update_pet_info(auth_key, pet_id, new_name, "", "")
        assert status == 200
        assert result['name'] == new_name
        assert result['animal_type'] == animal_type
        assert result['age'] == age
    else:
        raise Exception('There is no pets to update')

def test_add_photo_with_incorrect_id(pet_photo='images\pet_photo.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_id = '111111111111111'
    status, result = pf.set_pet_photo(auth_key, pet_id, pet_photo)
    assert status == 400

def test_create_pet_with_wrong_file(name="Vasya", animal_type="cat", age='2', pet_photo='testdata.txt'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

def test_delete_pet_of_another_user():
    """Пытаемся удалить питомца пользователя test_email с помощью авторизационного ключа пользователя valid_email"""
    _, a_key = pf.get_api_key(test_email, test_password)
    _, my_pets = pf.get_list_of_pets(a_key, 'my_pets')
    pet_id = my_pets['pets'][0]['id']
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    __, _ = pf.delete_api_pets(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(a_key, 'my_pets')
    assert pet_id in my_pets.values()

def test_update_pet_info_of_another_user(name="Polkan", animal_type="dog", age='4'):
    """Пытаемся обновить данные питомца пользователя test_email с помощью авторизационного ключа пользователя valid_email"""
    _, a_key = pf.get_api_key(test_email, test_password)
    _, my_pets = pf.get_list_of_pets(a_key, 'my_pets')
    pet_id = my_pets['pets'][0]['id']
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, _ = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
    assert status == 403


