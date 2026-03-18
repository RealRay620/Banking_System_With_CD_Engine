# Banking System & Certificate of Deposit (CD) Cash Flow Engine

## Project Overview

This project implements a structured Certificate of Deposit (CD) engine within a Python-based banking system.

The focus is on modeling the **internal mechanics of a deposit product**, including:
- time-based interest accrual  
- early withdrawal behavior  
- penalty and tax ordering  
- maturity and rollover dynamics  

The implementation emphasizes both **financial correctness** and **clean system design**, aligning real-world product rules with object-oriented programming principles.

---

## CD Product Mechanics

### Interest Accrual
- Accrues using **Actual/365 convention**
- Based on:
  - principal  
  - annual rate  
  - elapsed time in days  
- Accrual is **time-dependent and capped at maturity**

---

### Early Withdrawal Structure

The CD incorporates a structured early-exit payoff:

- Penalty applies **only to accrued interest**
- Penalty is **capped at total accrued interest**
- Penalty is applied **before taxation**
- Tax is applied only to the **remaining interest**

This ensures:
- principal is preserved unless withdrawn  
- penalties do not exceed earned value  
- payout reflects realistic banking rules  

---

### Cash Flow Hierarchy

Withdrawals are processed in the following order:

1. Accrued net interest  
2. Principal  

This enforces a clear separation between:
- earned returns  
- invested capital  

---

### Maturity and Rollover

- CD automatically detects maturity based on tenor  
- At maturity:
  - accrued net interest is added to principal  
  - a new term is initiated  
- Rollover behavior:
  - resets time horizon  
  - updates applicable rate  
  - maintains continuity of investment  

---

### Residual Balance Handling

- Partial withdrawals are supported  
- If remaining principal falls below a threshold:
  - funds are transferred to a linked account  
- Otherwise:
  - CD remains active or rolls forward  

---

## Financial Formulation

### Interest Accrual

\[
I_g = P \cdot r \cdot \frac{t}{365}
\]

---

### Early Withdrawal Payoff

\[
\text{Penalty} = \min(I_g \cdot b,\; I_g)
\]

\[
\text{Taxable Interest} = I_g - \text{Penalty}
\]

\[
T = \text{Taxable Interest} \cdot \tau
\]

\[
I_n = \text{Taxable Interest} - T
\]

\[
\text{Break Value} = P + I_n
\]

---

## System Implementation

### Class Design


---

### Key Design Decisions

#### Object-Oriented Structure
- Base class (`BankAccount`) handles shared functionality  
- Derived classes specialize behavior  
- CD logic is encapsulated within its own class  

#### Inheritance
- Enables reuse of core banking functionality  
- Supports extension into new account types  

#### Polymorphism
- Method overriding for:
  - deposit behavior  
  - withdrawal logic  
- Allows product-specific behavior while maintaining a unified interface  

#### Encapsulation
- Financial calculations contained within class methods  
- Internal state (principal, interest) managed consistently  

#### Constraint Enforcement
- Balance validation before transactions  
- Unique account registry  
- Controlled interaction between accounts  

---

## Data Handling

### Transaction Logging
- All transactions are recorded to file  
- Includes:
  - timestamps  
  - account names  
  - transaction type  
  - balances  

This provides a basic audit trail and supports future extension into reporting systems.

---

## Design Considerations

- Separation of:
  - financial logic  
  - system operations  
- Avoidance of hard-coded flows  
- Extensible structure for additional products  
- Clear mapping between financial rules and implementation  

---

## Future Enhancements

- Integration with **CSV / Excel** for:
  - input data ingestion  
  - persistent record keeping  
- Migration to `Decimal` for financial precision  
- Support for **compounding interest structures**  
- Dynamic rate modeling using yield curves  
- Portfolio-level extensions:
  - duration  
  - sensitivity analysis  
- Event-driven simulation of time progression  

---

## Author

Ryan Landey  
Master of Financial Mathematics  
North Carolina State University
