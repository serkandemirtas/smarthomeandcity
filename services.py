from abc import ABC, abstractmethod
from core_patterns import Command
from controller import CityController

class BankingService(ABC):
    @abstractmethod
    def load_money(self, user_id, amount, details): pass # Bank operations template
    @abstractmethod
    def get_balance(self, user_id): pass
    @abstractmethod
    def pay_bill(self, amount, bill_type, user_id, details): pass
    @abstractmethod
    def pay_parking(self, amount, location, user_id, details): pass


class FiatPayment(BankingService):
    def get_user_record(self, user_id):
        return CityController.get_instance()._get_user_internal(user_id)

    def load_money(self, user_id, amount, details):
        """
        I do the money loading operation here.
        """
        if amount <= 0 or amount > 1000000: return False, "Invalid amount."
        user = self.get_user_record(user_id)
        if not user: return False, "User not found"

        user.balance += amount
        user.history.append(f"Deposit: +{amount} TL")
        return True, f"New Balance: {user.balance}"

    def get_balance(self, user_id):
        user = self.get_user_record(user_id)
        return user.balance if user else 0

    def pay_bill(self, amount, bill_type, user_id, details=None):
        """
        I check the bill payment here.
        """
        if amount <= 0: return False, "Invalid amount"
        user = self.get_user_record(user_id)
        if not user: return False, "No Account"

        if details and details.get("card_no"):
            user.history.append(f"Card Payment: -{amount}")
            return True, "Paid by card."

        if user.balance >= amount:
            user.balance -= amount
            user.history.append(f"Balance Payment: -{amount}")
            return True, f"Paid from balance. Remaining: {user.balance}"
        
        return False, "Insufficient Balance."

    def pay_parking(self, amount, location, user_id, details=None):
        return self.pay_bill(amount, f"Parking ({location})", user_id, details)


class OutCryptoLib:
    def send_bitcoin(self, btc_amount): return f"{btc_amount:.6f} BTC"

class CryptoAdapter(BankingService):
    def __init__(self):
        self.crypto_api = OutCryptoLib()
        self.btc_rate = 100000.0

    def get_user_record(self, user_id):
        return CityController.get_instance()._get_user_internal(user_id)

    def load_money(self, user_id, amount, details):
        """
        Doing money loading with crypto here.
        """
        if amount <= 0: return False, "Invalid."
        user = self.get_user_record(user_id)
        if not user: return False, "User not found"
        
        user.balance += amount
        user.history.append(f"Crypto Deposit: +{amount}")
        return True, "Loaded."

    def pay_bill(self, amount, bill_type, user_id, details=None):
        """
        Doing bill payment with crypto here.
        """
        if amount <= 0: return False, "Invalid."
        user = self.get_user_record(user_id)
        if not user: return False, "No Account"

        if details and details.get("wallet_id"):
            self.crypto_api.send_bitcoin(amount / self.btc_rate)
            user.history.append(f"Crypto Payment: -{amount}")
            return True, "Paid with crypto."

        if user.balance >= amount:
            user.balance -= amount
            user.history.append(f"Balance Payment: -{amount}")
            return True, "Paid from balance."
        
        return False, "Insufficient Balance"

    def pay_parking(self, amount, location, user_id, details=None):
        return self.pay_bill(amount, f"Parking ({location})", user_id, details)
    
    def get_balance(self, user_id):
        user = self.get_user_record(user_id)
        return user.balance if user else 0

class PayBillCommand(Command):
    def __init__(self, service, amount, bill_type, user_id, details=None, location=None):
        self.service = service
        self.amount = amount
        self.bill_type = bill_type
        self.user_id = user_id
        self.details = details
        self.location = location

    def execute(self):
        """
        Executing the payment command.
        """
        if self.bill_type == "Parking":
            return self.service.pay_parking(self.amount, self.location, self.user_id, self.details)
        else:
            return self.service.pay_bill(self.amount, self.bill_type, self.user_id, self.details)