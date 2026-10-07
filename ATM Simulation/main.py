from datetime import datetime

ACCOUNTS = {
    "1001": {"name": "Aarav Mehta", "pin": "1234", "balance": 25000},
    "1002": {"name": "Diya Kapoor", "pin": "4321", "balance": 48500},
    "1003": {"name": "Rohan Verma", "pin": "1111", "balance": 1200},
}

MAX_PIN_ATTEMPTS = 3
WITHDRAW_LIMIT = 10000
DAILY_LIMIT = 20000
DEPOSIT_LIMIT = 50000
NOTES = (2000, 500, 200, 100)
WIDTH = 44

for account in ACCOUNTS.values():
    account["blocked"] = False
    account["withdrawn_today"] = 0
    account["history"] = []


def money(amount):
    return f"Rs. {amount:,}"


def banner(title):
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def log(account, kind, amount):
    stamp = datetime.now().strftime("%d-%m-%Y %H:%M")
    account["history"].append((stamp, kind, amount, account["balance"]))


def read_amount(prompt):
    text = input(prompt).strip()
    if text.isascii() and text.isdigit() and int(text) > 0:
        return int(text)
    print("Please enter a valid whole-number amount.")
    return None


def authenticate(account):
    for attempt in range(1, MAX_PIN_ATTEMPTS + 1):
        pin = input("Enter your 4-digit PIN: ").strip()
        if pin == account["pin"]:
            return True
        left = MAX_PIN_ATTEMPTS - attempt
        if left:
            print(f"Incorrect PIN. {left} attempt(s) remaining.")
    account["blocked"] = True
    print("Too many wrong attempts. This card has been blocked.")
    return False


def show_balance(account):
    print(f"\nAvailable balance: {money(account['balance'])}")


def deposit(account):
    amount = read_amount("Enter amount to deposit: ")
    if amount is None:
        return
    if amount > DEPOSIT_LIMIT:
        print(f"Maximum deposit per transaction is {money(DEPOSIT_LIMIT)}.")
        return
    account["balance"] += amount
    log(account, "Deposit", amount)
    print(f"\n{money(amount)} deposited successfully.")
    print(f"Available balance: {money(account['balance'])}")


def withdraw(account):
    amount = read_amount("Enter amount to withdraw: ")
    if amount is None:
        return
    if amount % 100 != 0:
        print("Amount must be a multiple of Rs. 100.")
        return
    if amount > WITHDRAW_LIMIT:
        print(f"Maximum withdrawal per transaction is {money(WITHDRAW_LIMIT)}.")
        return
    remaining_limit = DAILY_LIMIT - account["withdrawn_today"]
    if amount > remaining_limit:
        print(f"Daily limit exceeded. You can still withdraw {money(remaining_limit)} today.")
        return
    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    account["balance"] -= amount
    account["withdrawn_today"] += amount
    log(account, "Withdrawal", amount)

    print("\nPlease collect your cash:")
    left = amount
    for note in NOTES:
        count, left = divmod(left, note)
        if count:
            print(f"  {count} x Rs. {note}")
    print(f"Available balance: {money(account['balance'])}")


def mini_statement(account):
    print("\n" + "-" * WIDTH)
    print("MINI STATEMENT".center(WIDTH))
    print("-" * WIDTH)
    if not account["history"]:
        print("No transactions yet.".center(WIDTH))
    for stamp, kind, amount, balance in account["history"][-5:]:
        sign = "+" if kind == "Deposit" else "-"
        print(f"{stamp}  {kind:<11} {sign}{amount:>7,}  Bal {balance:>8,}")
    print("-" * WIDTH)
    print(f"Available balance: {money(account['balance'])}")


def change_pin(account):
    if input("Enter current PIN: ").strip() != account["pin"]:
        print("Incorrect PIN.")
        return
    new_pin = input("Enter new 4-digit PIN: ").strip()
    if not (new_pin.isascii() and new_pin.isdigit() and len(new_pin) == 4):
        print("PIN must be exactly 4 digits.")
        return
    if new_pin == account["pin"]:
        print("New PIN must be different from the current PIN.")
        return
    if input("Confirm new PIN: ").strip() != new_pin:
        print("PINs do not match. PIN not changed.")
        return
    account["pin"] = new_pin
    print("PIN changed successfully.")


def session(account):
    print(f"\nWelcome, {account['name']}!")
    actions = {
        "1": show_balance,
        "2": deposit,
        "3": withdraw,
        "4": mini_statement,
        "5": change_pin,
    }
    while True:
        print("\n1. Check balance")
        print("2. Deposit cash")
        print("3. Withdraw cash")
        print("4. Mini statement")
        print("5. Change PIN")
        print("6. Exit")
        choice = input("Select an option (1-6): ").strip()
        if choice == "6":
            break
        action = actions.get(choice)
        if action:
            action(account)
        else:
            print("Invalid option. Please choose 1-6.")


def main():
    banner("WELCOME TO INDIAN BANK ATM")
    print("Demo cards: 1001 (PIN 1234), 1002 (PIN 4321), 1003 (PIN 1111)")
    try:
        while True:
            number = input("\nInsert card (enter card number, or Q to quit): ").strip()
            if number.lower() == "q":
                break
            account = ACCOUNTS.get(number)
            if account is None:
                print("Card not recognised.")
                continue
            if account["blocked"]:
                print("This card is blocked. Please contact your bank.")
                continue
            if authenticate(account):
                session(account)
            print("\nCard ejected. Thank you for banking with us.")
    except (KeyboardInterrupt, EOFError):
        print()
    print("ATM shutting down. Goodbye!")


if __name__ == "__main__":
    main()