import sys

from rich.console import Console
from rich.prompt import Prompt
from telethon import TelegramClient, errors

console = Console()


async def auth(
        api_id: int,
        api_hash: str,
        session: str,
        max_attempts: int = 3
) -> TelegramClient:
    console.rule("[bold blue]Telegram Autobuyer Login[/]")

    client = TelegramClient(
        api_hash=api_hash,
        api_id=api_id,
        session=session
    )
    await client.connect()

    if await client.is_user_authorized():
        console.print("[green]✅ Session already authorized.[/]")
        return client

    attempts = 0
    two_step_detected = False

    while True:
        phone = Prompt.ask("[bold cyan]📱 Enter your Telegram phone number")
        try:
            sent_code = await client.send_code_request(phone=phone)
            console.print("[green]✔️ Code sent successfully![/]")
            break
        except errors.PhoneNumberInvalidError:
            console.print("[red]❌ Invalid phone number. Please try again.[/]")
        except errors.PhoneNumberBannedError:
            console.print("[red]❌ This number is banned by Telegram.[/]")
            sys.exit(1)
        except TypeError:
            console.print("[red]❌ Unexpected input. Please try again.[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to send code: {e}[/]")
            sys.exit(1)

    while attempts < max_attempts:
        code = Prompt.ask("[bold cyan]🔐 Enter the code you received")

        if not code:
            console.print("[yellow]⚠️ Code cannot be empty![/]")
            attempts += 1
            continue

        try:
            await client.sign_in(phone, code=code, phone_code_hash=sent_code.phone_code_hash)
            console.print("[green]✅ Successfully signed in![/]")
            break
        except errors.SessionPasswordNeededError:
            console.print("[yellow]🔒 Two-step verification is enabled.[/]")
            two_step_detected = True
            break
        except (errors.PhoneCodeEmptyError,
                errors.PhoneCodeExpiredError,
                errors.PhoneCodeHashEmptyError,
                errors.PhoneCodeInvalidError):
            console.print(f"[red]❌ Invalid or expired code. Try again ({attempts + 1}/{max_attempts})[/]")
            attempts += 1
        except Exception as e:
            console.print(f"[red]❌ Unexpected error during sign in: {e}[/]")
            attempts += 1

    else:
        raise RuntimeError(f"[red]🚫 {max_attempts} consecutive sign-in attempts failed. Aborting.[/]")

    if two_step_detected:
        for i in range(max_attempts):
            password = Prompt.ask("[bold cyan]🔑 Enter your Telegram password")
            try:
                await client.sign_in(phone=phone, password=password, phone_code_hash=sent_code.phone_code_hash)
                console.print("[green]✅ Successfully signed in with password![/]")
                break
            except errors.PasswordHashInvalidError:
                console.print(f"[red]❌ Invalid password. Attempt {i + 1}/{max_attempts}[/]")
        else:
            raise errors.PasswordHashInvalidError(request=None)

    return client
