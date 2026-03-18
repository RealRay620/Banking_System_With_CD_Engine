#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: ryan
"""

from BankAccounts_new import *

Dave = BankAccount(1000, "Dave")  #creates and instance of a bank account
Sara = BankAccount(1000, "Sara")

Dave.getBalance()
Sara.getBalance()

Sara.deposit(200)

Sara.withdraw(200)
Sara.withdraw(2000)

Dave.transfer(200, Sara)
Dave.transfer(10_000, Sara)

Jim = InterestRewardsAcct(1000, "Jim")
Jim.getBalance()
Jim.deposit(200)
Jim.getBalance()

Jim.transfer(250, Dave)

Blaze = SavingsAcct(1000, 'Blaze')

Blaze.getBalance()
Blaze.deposit(100)
Blaze.transfer(10000, Sara)

# ==============================================================================
# Example Testing
# ==============================================================================


# Create linked regular account first
Ryan = BankAccount(3000, "Ryan")

# Create CD record
Ryan_CD = CertificateDeposit(
    initialAmount=200,
    acctName="Ryan_CD_1",
    tenorDays=180,
    dateDeposited="2026-01-01",
    linkedAccountName="Ryan",
    breakRate=0.50,   # 50% of accrued interest forfeited if broken early
    taxRate=0.25,
    minimumRemainingThreshold=500,
    autoRoll=True,
    useCurrentRateAtRollover=True
)

# Standard balance inquiry
cd1.getBalance("2026-03-15")

# Break-value inquiry
cd1.getBreakValue("2026-03-15")

# Early withdrawal
cd1.withdraw(amount=4000, dateWithdrawn="2026-03-15")

# Maturity check
cd1.dailyMaturityCheck("2026-07-10")

# Final balances
cd1.getBalance("2026-07-10")
checking.getBalance()


# =============================================================================
# Clearingg the registry
# =============================================================================
    
print(BankAccount.accounts_registry)
