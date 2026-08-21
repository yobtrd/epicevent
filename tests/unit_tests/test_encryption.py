from epicevents.security.encryption import EncryptedString


def test_encrypt_and_decrypt():
    encrypted_string = EncryptedString()
    value = "john@example.com"

    encrypted = encrypted_string._cipher.encrypt(
        value.encode("utf-8"),
        None,
    )

    decrypted = encrypted_string._cipher.decrypt(
        encrypted,
        None,
    ).decode("utf-8")

    assert decrypted == value


def test_same_value_produces_same_ciphertext():
    encrypted_string = EncryptedString()
    value = "john@example.com"

    encrypted_1 = encrypted_string._cipher.encrypt(
        value.encode("utf-8"),
        None,
    )
    encrypted_2 = encrypted_string._cipher.encrypt(
        value.encode("utf-8"),
        None,
    )

    assert encrypted_1 == encrypted_2


def test_different_values_produce_different_ciphertext():
    encrypted_string = EncryptedString()

    encrypted_1 = encrypted_string._cipher.encrypt(
        b"john@example.com",
        None,
    )
    encrypted_2 = encrypted_string._cipher.encrypt(
        b"jane@example.com",
        None,
    )

    assert encrypted_1 != encrypted_2


def test_process_bind_param_encrypts_value():
    encrypted_string = EncryptedString()
    value = "john@example.com"

    result = encrypted_string.process_bind_param(value, None)

    assert result is not None
    assert result != value
    assert value not in result


def test_process_result_value_decrypts_value():
    encrypted_string = EncryptedString()
    value = "john@example.com"

    encrypted = encrypted_string.process_bind_param(value, None)
    result = encrypted_string.process_result_value(encrypted, None)

    assert result == value


def test_none_value_is_preserved():
    encrypted_string = EncryptedString()

    assert encrypted_string.process_bind_param(None, None) is None
    assert encrypted_string.process_result_value(None, None) is None


def test_utf8_value_is_supported():
    encrypted_string = EncryptedString()
    value = "John Doe"

    encrypted = encrypted_string.process_bind_param(value, None)
    result = encrypted_string.process_result_value(encrypted, None)

    assert result == value
