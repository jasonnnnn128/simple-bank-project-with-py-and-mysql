import mysql.connector
from InquirerPy import inquirer
import random
import string

db = mysql.connector.connect(
    host="your host",
    user="your username",
    password="your password",
    database="your database"
)

cursor = db.cursor(dictionary=True)


def generate_kode():
    huruf = ''.join(random.choices(string.ascii_uppercase, k=2))
    angka = random.randint(100, 999)
    return f"{huruf}{angka}"


class BankAccount:
    def __init__(self, kode_antrian, name, balance):
        self.kode_antrian = kode_antrian
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            print("Jumlah deposit harus lebih dari 0")
            return

        self.balance += amount
        sql = "UPDATE akun SET balance=%s WHERE kode_antrian=%s"
        cursor.execute(sql, (self.balance, self.kode_antrian))
        db.commit()

        print(f"Deposit berhasil: {amount}")
        print(f"Saldo terbaru: {self.balance}")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Saldo tidak mencukupi")
            return

        self.balance -= amount
        sql = "UPDATE akun SET balance=%s WHERE kode_antrian=%s"
        cursor.execute(sql, (self.balance, self.kode_antrian))
        db.commit()

        print(f"Withdraw berhasil: {amount}")
        print(f"Saldo terbaru: {self.balance}")

    def get_balance(self):
        return self.balance


def create_account(name, pin, balance):
    cursor.execute("SELECT * FROM akun WHERE name=%s", (name,))
    if cursor.fetchone():
        print("Nama sudah terdaftar!")
        return

    kode = generate_kode()

    sql = "INSERT INTO akun (kode_antrian, name, pin, balance) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (kode, name, pin, balance))
    db.commit()

    print(f"Akun berhasil dibuat!")
    print(f"Kode Antrian Anda: {kode}")


def login_account(name, pin):
    cursor.execute("SELECT * FROM akun WHERE name=%s AND pin=%s", (name, pin))
    result = cursor.fetchone()

    if not result:
        return None

    return BankAccount(
        result["kode_antrian"],
        result["name"],
        result["balance"]
    )


print("Selamat datang")

while True:
    menu = inquirer.select(
        message="Pilih menu:",
        choices=["Login", "Daftar Akun Baru", "Keluar"]
    ).execute()

    if menu == "Daftar Akun Baru":
        name = input("Masukkan nama: ")
        pin = input("Masukkan PIN: ")
        saldo_awal = int(input("Masukkan saldo awal: "))
        create_account(name, pin, saldo_awal)

    elif menu == "Login":
        name = input("Masukkan nama: ")
        pin = input("Masukkan PIN: ")
        account = login_account(name, pin)

        if not account:
            print("Nama atau PIN salah")
            continue

        print(f"\nSelamat datang, {account.name}")
        print(f"Kode Antrian Anda: {account.kode_antrian}")

        while True:
            action = inquirer.select(
                message="Pilih transaksi:",
                choices=["Deposit", "Withdraw", "Check Balance", "Logout"]
            ).execute()

            if action == "Deposit":
                amount = int(input("Masukkan jumlah deposit: "))
                account.deposit(amount)

            elif action == "Withdraw":
                amount = int(input("Masukkan jumlah penarikan: "))
                account.withdraw(amount)

            elif action == "Check Balance":
                print(f"Saldomu: {account.get_balance()}")

            elif action == "Logout":
                print("Logout berhasil\n")
                break

    elif menu == "Keluar":
        print("Terima kasih!")
        break

cursor.close()
db.close()
