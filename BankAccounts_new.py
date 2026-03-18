#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ryan
"""

from datetime import datetime, timedelta

# ==============================================================================
# Custom Exceptions for error handling
# ==============================================================================

class BalanceException(Exception):
    pass


class AccountExistsException(Exception):
    pass


class InvalidOperationException(Exception):
    pass


# ==============================================================================
# Parent class for bank accounts within a banking system
# ==============================================================================

class BankAccount:
    # Registry of all created accounts
    accounts_registry = {}

    def __init__(self, initialAmount, acctName):
        if initialAmount < 0:
            raise ValueError("Initial amount cannot be negative.")

        if acctName in BankAccount.accounts_registry:
            raise AccountExistsException(
                f"An account with name '{acctName}' already exists. Please choose a unique account name."
            )

        self.balance = float(initialAmount)
        self.name = acctName

        BankAccount.accounts_registry[self.name] = self

        print(f"\nAccount '{self.name}' created.\nBalance = ${self.balance:.2f}")

    def getBalance(self):
        print(f"\nAccount '{self.name}' balance = ${self.balance:.2f}")
        return self.balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self.balance += amount
        self.log_transaction("DEPOSIT", amount)

        print("\nDeposit complete.")
        self.getBalance()

    def viableTransaction(self, amount):
        if amount <= 0:
            raise ValueError("Transaction amount must be greater than zero.")

        if self.balance >= amount:
            return True
        else:
            raise BalanceException(
                f"Sorry, account '{self.name}' only has a balance of ${self.balance:.2f}"
            )

    def withdraw(self, amount):
        try:
            self.viableTransaction(amount)
            self.balance -= amount
            self.log_transaction("WITHDRAW", amount)

            print("\nWithdraw complete.")
            self.getBalance()

        except BalanceException as error:
            print(f"\nWithdraw interrupted: {error}")

    def transfer(self, amount, account):
        try:
            if amount <= 0:
                raise ValueError("Transfer amount must be greater than zero.")

            print("\n*****************************")
            print("Beginning transfer....... 🚀")

            self.viableTransaction(amount)

            self.balance -= amount
            account.balance += amount

            self.log_transaction("TRANSFER OUT", amount, extra=f"| to {account.name}")
            account.log_transaction("TRANSFER IN", amount, extra=f"| from {self.name}")

            print("\nTransfer complete! ✅")
            print(f"\nFrom account: '{self.name}'")
            self.getBalance()

            print(f"\nTo account: '{account.name}'")
            account.getBalance()
            print("\n*****************************")

        except (BalanceException, ValueError) as error:
            print(f"\nTransfer interrupted. ❌ {error}")

    def log_transaction(self, txn_type, amount, extra=""):
        with open("transaction_log.txt", "a") as file:
            file.write(
                f"{datetime.now()} | {self.name} | {txn_type} | "
                f"${amount:.2f} | Balance=${self.balance:.2f} {extra}\n"
            )


# ==============================================================================
# Interest bearing accounts
# ==============================================================================

class InterestRewardsAcct(BankAccount):
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        reward_amount = amount * 1.05
        self.balance += reward_amount
        self.log_transaction("DEPOSIT+REWARD", reward_amount)

        print("\nDeposit complete with reward.")
        self.getBalance()


class SavingsAcct(InterestRewardsAcct):
    def __init__(self, initialAmount, acctName):
        super().__init__(initialAmount, acctName)
        self.fee = 5.00

    def withdraw(self, amount):
        try:
            if amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")

            total_amount = amount + self.fee
            self.viableTransaction(total_amount)

            self.balance -= total_amount
            self.log_transaction("WITHDRAW+FEE", total_amount)

            print(f"\nWithdraw completed. (${amount:.2f} + ${self.fee:.2f} fee)")
            self.getBalance()

        except (BalanceException, ValueError) as error:
            print(f"\nWithdraw interrupted: {error}")


# ==============================================================================
# Certificate of Deposit class
# ==============================================================================

class CertificateDeposit(BankAccount):

    # default rate sheet used for CD placement
    RATE_SHEET = {
        15: 0.0200,
        30: 0.0225,
        45: 0.0240,
        60: 0.0260,
        90: 0.0300,
        120: 0.0330,
        150: 0.0350,
        180: 0.0380,
        210: 0.0400,
        240: 0.0420,
        270: 0.0440,
        300: 0.0460,
        330: 0.0480,
        365: 0.0500
    }

    def __init__(
        self,
        initialAmount,
        acctName,
        tenorDays,
        dateDeposited,
        linkedAccountName,
        breakRate=0.50,
        taxRate=0.25,
        minimumRemainingThreshold=500.00,
        autoRoll=True,
        useCurrentRateAtRollover=True
    ):
        if initialAmount <= 500: # Intitial amount must be greater than $500
            raise ValueError("Initial CD amount must be greater than $500.00")
            
        # This checks if tenor entered is valid and if it is not shows the client the valid dates in the rate sheet
        if tenorDays not in self.RATE_SHEET:
            raise ValueError(
                f"Invalid tenorDays '{tenorDays}'. "
                f"Valid values are: {list(self.RATE_SHEET.keys())}" 
            )
        # Ensures break rate not out of bounds
        if  not (0 <= breakRate <= 1):
            raise ValueError("Break rate cannot be negative or greater than 100%")

        if not (0 <= taxRate <= 1):
            raise ValueError("Tax rate cannot be negative or greater than 100%")
        #   All CDs must be linked to a bank account
        if linkedAccountName not in BankAccount.accounts_registry:
            raise InvalidOperationException(
                f"Linked account '{linkedAccountName}' does not exist. "
                f"A regular bank account must be created first."
            )

        self.linkedAccount = BankAccount.accounts_registry[linkedAccountName]
        self.dateDeposited = self._parse_date(dateDeposited)
        self.tenorDays = tenorDays
        self.rate = self.RATE_SHEET[tenorDays]
        self.breakRate = breakRate
        self.taxRate = taxRate
        self.minimumRemainingThreshold = minimumRemainingThreshold
        self.autoRoll = autoRoll
        self.useCurrentRateAtRollover = useCurrentRateAtRollover
        
        self.principal = float(initialAmount)
        self.lastRollDate = self.dateDeposited
        self.maturityDate = self._calculate_maturity_date(self.dateDeposited, tenorDays)

        super().__init__(initialAmount, acctName)

        self.log_transaction(
            "CD OPEN",
            initialAmount,
            extra=(
                f"| tenorDays={self.tenorDays}"
                f" | rate={self.rate:.4f}"
                f" | maturity={self.maturityDate.date()}"
                f" | linked={self.linkedAccount.name}"
            )
        )
        
        # the default rollover rate is the the 30 day rate from the rate sheet
        DEFAULT_ROLLOVER_RATE = self.RATE_SHEET[30]

    # -------------------------------------------------------------------------
    # Helper methods
    # -------------------------------------------------------------------------

    def _parse_date(self, date_value):
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            return datetime.strptime(date_value, "%Y-%m-%d")
        raise ValueError("Date must be a datetime object or a string in YYYY-MM-DD format.")

    def _calculate_maturity_date(self, start_date, tenor_days):
        return start_date + timedelta(days=tenor_days)

    def validacc(self):
        if self.linkedAccount is None:
            raise InvalidOperationException(
                "CD must be linked to an existing regular bank account."
            )
        return True

    def days_elapsed(self, asOfDate=None):
        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        return max((asOfDate - self.lastRollDate).days, 0)

    def days_to_maturity(self, asOfDate=None):
        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        return (self.maturityDate - asOfDate).days

    def has_matured(self, asOfDate=None):
        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        return asOfDate >= self.maturityDate

    # -------------------------------------------------------------------------
    # Calculation Methods
    # -------------------------------------------------------------------------

    def calculate_gross_interest(self, asOfDate=None):

        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        end_date = min(asOfDate, self.maturityDate)
        elapsed_days = max((end_date - self.lastRollDate).days, 0)

        gross_interest = self.principal * self.rate * (elapsed_days / 365)
        return gross_interest

    def calculate_break_penalty(self, asOfDate=None):
        """
        Break penalty applies only to accrued gross interest
        and is capped at accrued interest.
        """
        gross_interest = self.calculate_gross_interest(asOfDate)
        raw_penalty = gross_interest * self.breakRate
        return min(raw_penalty, gross_interest)

    def calculate_tax_on_interest(self, asOfDate=None, includePenalty=False):
        """
        If includePenalty=True, tax is applied after the penalty is taken
        from gross interest (Option B).
        """
        gross_interest = self.calculate_gross_interest(asOfDate)

        if includePenalty:
            penalty = self.calculate_break_penalty(asOfDate)
            taxable_interest = max(gross_interest - penalty, 0.0)
        else:
            taxable_interest = gross_interest

        return taxable_interest * self.taxRate

    def calculate_net_interest(self, asOfDate=None, includePenalty=False):
        """
        Net interest after tax.
        If includePenalty=True, penalty is deducted before tax.
        """
        gross_interest = self.calculate_gross_interest(asOfDate)

        if includePenalty:
            penalty = self.calculate_break_penalty(asOfDate)
            taxable_interest = max(gross_interest - penalty, 0.0)
            taxes = taxable_interest * self.taxRate
            net_interest = taxable_interest - taxes
        else:
            taxable_interest = gross_interest
            taxes = taxable_interest * self.taxRate
            net_interest = taxable_interest - taxes

        return max(net_interest, 0.0)

    # -------------------------------------------------------------------------
    # Balance methods
    # -------------------------------------------------------------------------

    def getBalance(self, asOfDate=None):
        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        gross_interest = self.calculate_gross_interest(asOfDate)
        taxes = gross_interest * self.taxRate
        net_interest = gross_interest - taxes
        total_balance = self.principal + net_interest

        print(
            f"\nCD Account '{self.name}' balance summary"
            f"\nPrincipal: ${self.principal:.2f}"
            f"\nGross Interest Accrued: ${gross_interest:.2f}"
            f"\nTax on Interest: ${taxes:.2f}"
            f"\nNet Interest: ${net_interest:.2f}"
            f"\nTotal CD Balance: ${total_balance:.2f}"
            f"\nRate: {self.rate*100:.2f}%"
            f"\nDeposit/Roll Date: {self.lastRollDate.date()}"
            f"\nMaturity Date: {self.maturityDate.date()}"
        )
        return total_balance
    
    
    # Shows the value if the CD is broken on the specified date.
    # Penalty is applied before tax and capped at accrued interest.
    def getBreakValue(self, asOfDate=None):
       
        if asOfDate is None:
            asOfDate = datetime.now()
        else:
            asOfDate = self._parse_date(asOfDate)

        gross_interest = self.calculate_gross_interest(asOfDate)

        if self.has_matured(asOfDate):
            penalty = 0.0
            taxable_interest = gross_interest
        else:
            penalty = self.calculate_break_penalty(asOfDate)
            taxable_interest = max(gross_interest - penalty, 0.0)

        taxes = taxable_interest * self.taxRate
        net_interest = max(taxable_interest - taxes, 0.0)
        break_value = self.principal + net_interest

        print(
            f"\nCD Account '{self.name}' break value summary"
            f"\nPrincipal: ${self.principal:.2f}"
            f"\nGross Interest Accrued: ${gross_interest:.2f}"
            f"\nPenalty: ${penalty:.2f}"
            f"\nTaxable Interest: ${taxable_interest:.2f}"
            f"\nTax: ${taxes:.2f}"
            f"\nNet Interest: ${net_interest:.2f}"
            f"\nBreak Value: ${break_value:.2f}"
        )
        return break_value

    # -------------------------------------------------------------------------
    # Withdrawal process
    # -------------------------------------------------------------------------

    def withdraw(self, amount, dateWithdrawn, rollRemaining=False):
        dateWithdrawn = self._parse_date(dateWithdrawn)

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        matured = self.has_matured(dateWithdrawn)
        gross_interest = self.calculate_gross_interest(dateWithdrawn)

        if matured:
            penalty = 0.0
            taxable_interest = gross_interest
        else:
            penalty = self.calculate_break_penalty(dateWithdrawn)
            taxable_interest = max(gross_interest - penalty, 0.0)

        taxes = taxable_interest * self.taxRate
        net_interest_after_charges = max(taxable_interest - taxes, 0.0)

        total_available = self.principal + net_interest_after_charges

        if amount > total_available:
            raise BalanceException(
                f"Requested withdrawal of ${amount:.2f} exceeds available CD balance "
                f"of ${total_available:.2f}"
            )

        print("\n================ CD WITHDRAWAL ================")
        print(f"Account: {self.name}")
        print(f"Withdrawal Date: {dateWithdrawn.date()}")
        print(f"Requested Withdrawal: ${amount:.2f}")
        print(f"Matured?: {'Yes' if matured else 'No'}")
        print(f"Gross Interest: ${gross_interest:.2f}")
        print(f"Break Penalty on Interest: ${penalty:.2f}")
        print(f"Taxable Interest After Penalty: ${taxable_interest:.2f}")
        print(f"Tax on Interest: ${taxes:.2f}")
        print(f"Net Interest After Tax and Penalty: ${net_interest_after_charges:.2f}")

        # Withdraw from net interest first, then principal
        if amount <= net_interest_after_charges:
            remaining_interest = net_interest_after_charges - amount
            principal_remaining = self.principal
        else:
            principal_reduction = amount - net_interest_after_charges
            principal_remaining = self.principal - principal_reduction
            remaining_interest = 0.0

        if principal_remaining < 0:
            raise BalanceException("Withdrawal calculation resulted in negative principal.")

        self.principal = principal_remaining
        self.balance = self.principal

        self.log_transaction(
            "CD WITHDRAW",
            amount,
            extra=(
                f"| gross_interest=${gross_interest:.2f}"
                f" | penalty=${penalty:.2f}"
                f" | taxable_interest=${taxable_interest:.2f}"
                f" | tax=${taxes:.2f}"
                f" | date={dateWithdrawn.date()}"
            )
        )

        remaining_total = self.principal + remaining_interest
        print(f"Remaining CD value: ${remaining_total:.2f}")

        # Threshold rule
        if self.principal > 0 and self.principal < self.minimumRemainingThreshold:
            transfer_amount = self.principal
            self.principal = 0.0
            self.balance = 0.0
            self.linkedAccount.balance += transfer_amount

            self.log_transaction(
                "CD AUTO TRANSFER REMAINDER",
                transfer_amount,
                extra=f"| transferred to linked account {self.linkedAccount.name}"
            )
            self.linkedAccount.log_transaction(
                "CD REMAINDER RECEIVED",
                transfer_amount,
                extra=f"| from {self.name}"
            )

            print(
                f"\nRemaining principal was below threshold "
                f"(${self.minimumRemainingThreshold:.2f})."
                f"\n${transfer_amount:.2f} transferred to linked account "
                f"'{self.linkedAccount.name}'."
            )

        elif self.principal >= self.minimumRemainingThreshold:
            if rollRemaining and matured:
                print("\nRemaining balance is above threshold and will be rolled over.")
                self.rollover(dateWithdrawn)
            else:
                print("\nRemaining balance stays in CD.")

        else:
            print("\nCD fully withdrawn/closed.")

        print("==============================================")

    # -------------------------------------------------------------------------
    # Rollover process
    # -------------------------------------------------------------------------

    def rollover(self, rollDate=None):
        if rollDate is None:
            rollDate = datetime.now()
        else:
            rollDate = self._parse_date(rollDate)

        gross_interest = self.calculate_gross_interest(self.maturityDate)
        taxes = gross_interest * self.taxRate
        net_interest = gross_interest - taxes

        self.principal += net_interest
        self.balance = self.principal

        if self.useCurrentRateAtRollover and self.tenorDays in self.RATE_SHEET:
            new_rate = self.RATE_SHEET[self.tenorDays]
        else:
            new_rate = self.DEFAULT_ROLLOVER_RATE

        self.rate = new_rate
        self.lastRollDate = rollDate
        self.maturityDate = self._calculate_maturity_date(rollDate, self.tenorDays)

        self.log_transaction(
            "CD ROLLOVER",
            net_interest,
            extra=(
                f"| new principal=${self.principal:.2f}"
                f" | new rate={self.rate:.4f}"
                f" | new maturity={self.maturityDate.date()}"
            )
        )

        print(
            f"\nCD '{self.name}' rolled over successfully."
            f"\nNet interest added to principal: ${net_interest:.2f}"
            f"\nNew principal: ${self.principal:.2f}"
            f"\nNew rate: {self.rate*100:.2f}%"
            f"\nNew maturity date: {self.maturityDate.date()}"
        )

    # -------------------------------------------------------------------------
    # Daily maturity check
    # -------------------------------------------------------------------------

    def dailyMaturityCheck(self, checkDate=None):
        if checkDate is None:
            checkDate = datetime.now()
        else:
            checkDate = self._parse_date(checkDate)

        if self.has_matured(checkDate):
            print(f"\nCD '{self.name}' has matured as of {checkDate.date()}.")

            if self.autoRoll and self.principal > 0:
                print("Auto-roll is enabled. Rolling over CD...")
                self.rollover(checkDate)
            else:
                print("Auto-roll is disabled. Awaiting withdrawal instructions.")
        else:
            print(
                f"\nCD '{self.name}' has not yet matured."
                f"\nDays remaining to maturity: {self.days_to_maturity(checkDate)}"
            )


