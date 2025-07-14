import sys

from telethon import TelegramClient, errors, utils


async def auth(
        api_id: int,
        api_hash: str,
        max_attempts: int = 3
) -> TelegramClient:
    client = TelegramClient(
        api_hash=api_hash,
        api_id=api_id,
        session='autobuyer'
    )
    await client.connect()

    if await client.is_user_authorized():
        return client

    attempts = 0
    two_step_detected = False

    while True:
        phone = input('Enter your Telegram phone number: ')

        try:
            sent_code = await client.send_code_request(phone=phone)
            break
        except (errors.PhoneNumberInvalidError, errors.PhoneNumberBannedError, TypeError):
            print('Please enter a valid phone number.')

    while attempts < max_attempts:
        try:
            code = input('Enter your received code: ')

            if not code:
                raise errors.PhoneCodeEmptyError(request=None)

            await client.sign_in(phone, code=code, phone_code_hash=sent_code.phone_code_hash)
            break
        except errors.SessionPasswordNeededError:
            two_step_detected = True
            break
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError):
            print('Invalid code. Please try again.', file=sys.stderr)

        attempts += 1
    else:
        raise RuntimeError(
            '{} consecutive sign-in attempts failed. Aborting'
            .format(max_attempts)
        )

    if two_step_detected:
        for _ in range(max_attempts):
            try:
                password = input('Enter your password: ')
                await client.sign_in(
                    phone=phone,
                    password=password,
                    phone_code_hash=sent_code.phone_code_hash
                )
                break
            except errors.PasswordHashInvalidError:
                print('Invalid password. Please try again',
                      file=sys.stderr)
        else:
            raise errors.PasswordHashInvalidError(request=None)

    return client
