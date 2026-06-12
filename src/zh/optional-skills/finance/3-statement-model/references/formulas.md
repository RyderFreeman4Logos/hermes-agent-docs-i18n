# 公式参考手册

**重要提示：** 除非用户另有指定，否则请始终使用本参考手册中列出的公式。

---

## 核心关联关系

```
Balance Sheet:        Assets = Liabilities + Equity
Net Income:           IS Net Income → CF Operations (starting point)
Cash Flow:            ΔCash = CFO + CFI + CFF
Cash Tie-Out:         Ending Cash (CF) = Cash (BS Asset)
Cash Monthly/Annual:  Closing Cash (Monthly) = Closing Cash (Annual)
Retained Earnings:    Prior RE + Net Income - Dividends = Ending RE
Equity Raise:         ΔCommon Stock/APIC (BS) = Equity Issuance (CFF)
Year 0 Equity:        Equity Raised (Year 0) = Beginning Equity (Year 1)
```

## 毛利润计算方式

**重要提示：** 毛利润必须基于净收入来计算，而非总收入。

```
Net Revenue - Cost of Revenue = Gross Profit
```

| 术语 | 定义 |
|------|------|
| 总收入 | 扣除任何费用之前的总收入 |
| 净收入 | 总收入 - 退货额 - 折让额 - 折扣额 |
| 营业成本 | 与所销售商品或服务的生产直接相关的成本 |
| 毛利润 | 净收入 - 营业成本 |

**注意：** 在计算盈利能力时，应始终以净收入（在大多数财务报表中也称为“净销售额”或简称“收入”）作为起点。总收入会高估真实的营收表现。

## 利润率计算公式

```
Gross Margin %      = Gross Profit / Net Revenue
EBITDA              = EBIT + D&A  (or = Gross Profit - OpEx)
EBITDA Margin %     = EBITDA / Net Revenue
EBIT Margin %       = EBIT / Net Revenue
Net Income Margin % = Net Income / Net Revenue
```

## 信用度量公式

```
Total Debt            = Current Portion of Debt + Long-Term Debt
Net Debt              = Total Debt - Cash
Total Debt / EBITDA   = Total Debt / EBITDA (from IS)
Net Debt / EBITDA     = Net Debt / EBITDA (from IS)
Interest Coverage     = EBITDA / Interest Expense (from IS)
Net Int Exp % Debt    = Net Interest Expense / Long-Term Debt
Debt / Total Cap      = Total Debt / (Total Debt + Total Equity)
Debt / Equity         = Total Debt / Total Equity
Current Ratio         = Total Current Assets / Total Current Liabilities
Quick Ratio           = (Total Current Assets - Inventory) / Total Current Liabilities
```

## 预测公式（净收入百分比法）

```
Cost of Revenue (Forecast) = Net Revenue × Cost of Revenue % Assumption
S&M (Forecast)             = Net Revenue × S&M % Assumption
G&A (Forecast)             = Net Revenue × G&A % Assumption
R&D (Forecast)             = Net Revenue × R&D % Assumption
SBC (Forecast)             = Net Revenue × SBC % Assumption
```

## 流动资金计算公式

```
Accounts Receivable
  Prior AR
  + Revenue (from IS)
  - Cash Collections (plug)
  = Ending AR
  DSO = (AR / Revenue) × 365

Inventory
  Prior Inventory
  + Purchases (plug)
  - COGS (from IS)
  = Ending Inventory
  DIO = (Inventory / COGS) × 365

Accounts Payable
  Prior AP
  + Purchases (from Inventory calc)
  - Cash Payments (plug)
  = Ending AP
  DPO = (AP / COGS) × 365

Net Working Capital = AR + Inventory - AP
ΔWC = Current NWC - Prior NWC
```

## 数据与分析调度公式

```
Beginning PP&E (Gross)
+ CapEx
= Ending PP&E (Gross)

Beginning Accumulated Depreciation
+ Depreciation Expense
= Ending Accumulated Depreciation

PP&E (Net) = Gross PP&E - Accumulated Depreciation
```

## 债务分期计算公式

```
Beginning Debt Balance
+ New Borrowings
- Repayments
= Ending Debt Balance

Interest Expense = Avg Debt Balance × Interest Rate
  (Use beginning balance to avoid circularity, or iterate if circular refs enabled)
```

## 留存收益计算公式

```
Beginning Retained Earnings
+ Net Income (from IS)
+ Stock-Based Compensation (SBC) (from IS)
- Dividends
= Ending Retained Earnings
```

## 净经营亏损申报表公式

```
NOL CARRYFORWARD SCHEDULE

Beginning NOL Balance (Year 1 / Formation = 0)
+ NOL Generated (if EBT < 0, then ABS(EBT), else 0)
- NOL Utilized (limited by taxable income and utilization cap)
= Ending NOL Balance

STARTING BALANCE RULE

For a new business or first modeled period:
  Beginning NOL Balance = 0
  NOL can only increase through realized losses (EBT < 0)
  NOL cannot be created from thin air or assumed

NOL UTILIZATION CALCULATION

Pre-Tax Income (EBT)
  If EBT > 0:
    NOL Available = Beginning NOL Balance
    Utilization Limit = EBT × 80%  (post-2017 federal limit)
    NOL Utilized = MIN(NOL Available, Utilization Limit)
    Taxable Income = EBT - NOL Utilized
  If EBT ≤ 0:
    NOL Utilized = 0
    Taxable Income = 0
    NOL Generated = ABS(EBT)

TAX CALCULATION WITH NOL

Taxes Payable = MAX(0, Taxable Income × Tax Rate)
  (Taxes cannot be negative; losses create NOL asset instead)

DEFERRED TAX ASSET (DTA) FOR NOL

DTA - NOL Carryforward = Ending NOL Balance × Tax Rate
ΔDTA = Current DTA - Prior DTA
  (Increase in DTA = non-cash benefit on CF)
  (Decrease in DTA = non-cash expense on CF)
```

## 资产负债表结构

```
ASSETS
  Cash (from CF ending cash)
  Accounts Receivable (from WC)
  Inventory (from WC)
  Total Current Assets
  
  PP&E, Net (from DA)
  Deferred Tax Asset - NOL (from NOL schedule)
  Total Non-Current Assets
  Total Assets

LIABILITIES
  Accounts Payable (from WC)
  Current Portion of Debt (from Debt)
  Total Current Liabilities
  
  Long-Term Debt (from Debt)
  Total Liabilities

EQUITY
  Common Stock
  Retained Earnings (from RE schedule)
  Total Equity

CHECK: Assets - Liabilities - Equity = 0
```

## 现金流量表结构

```
CASH FROM OPERATIONS (CFO)
  Net Income (LINK: IS)
  + D&A (LINK: DA schedule)
  + Stock-Based Compensation (SBC) (LINK: IS or Assumptions)
  - ΔDTA (Deferred Tax Asset) (LINK: NOL schedule; increase in DTA = use of cash)
  - ΔAR (LINK: WC)
  - ΔInventory (LINK: WC)
  + ΔAP (LINK: WC)
  = CFO

CASH FROM INVESTING (CFI)
  - CapEx (LINK: DA schedule)
  = CFI

CASH FROM FINANCING (CFF)
  + Debt Issuance (LINK: Debt)
  - Debt Repayment (LINK: Debt)
  + Equity Issuance (LINK: BS Common Stock/APIC)
  - Dividends (LINK: RE schedule)
  = CFF

Net Change in Cash = CFO + CFI + CFF
Beginning Cash
+ Net Change in Cash
= Ending Cash (LINK TO: BS Cash)
```

## 利润表结构

```
Net Revenue
  Growth %
(-) Cost of Revenue
  % of Net Revenue
────────────────
Gross Profit (= Net Revenue - Cost of Revenue)
  Gross Margin %

(-) S&M
  % of Net Revenue
(-) G&A
  % of Net Revenue
(-) R&D
  % of Net Revenue
(-) D&A
(-) SBC
  % of Net Revenue
────────────────
EBIT
  EBIT Margin %

EBITDA
  EBITDA Margin %

(-) Interest Expense
────────────────
EBT (Pre-Tax Income)
(-) NOL Utilization (from NOL schedule, reduces taxable income)
────────────────
Taxable Income
(-) Taxes (Taxable Income × Tax Rate)
────────────────
Net Income
  Net Income Margin %
```

## 检查公式

```
BS Balance Check:       = Assets - Liabilities - Equity  (must = 0)
Cash Tie-Out:           = BS Cash - CF Ending Cash       (must = 0)
RE Roll-Forward:        = Prior RE + NI + SBC - Div - BS RE  (must = 0)
DTA Tie-Out:            = NOL Schedule DTA - BS DTA      (must = 0)
Equity Raise Tie-Out:   = ΔCommon Stock/APIC (BS) - Equity Issuance (CFF)  (must = 0)
Year 0 Equity Tie-Out:  = Equity Raised (Year 0) - Beginning Equity (Year 1)  (must = 0)
Cash Monthly vs Annual: = Closing Cash (Monthly) - Closing Cash (Annual)  (must = 0)
NOL Utilization Cap:    = NOL Utilized ≤ EBT × 80%       (must be TRUE for post-2017)
NOL Non-Negative:       = Ending NOL Balance ≥ 0         (must be TRUE)
NOL Starting Balance:   = Beginning NOL (Year 1) = 0     (must be TRUE for new business)
NOL Accumulation:       = NOL increases only when EBT < 0 (losses generate NOL)
```
