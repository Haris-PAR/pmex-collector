"""
PMEX Symbol Parsing Dictionaries
=================================
Every possible variation in a PMEX futures symbol, fully mapped.

SYMBOL ANATOMY
--------------
A PMEX symbol is made of up to 3 parts:

    {COMMODITY_CODE} - {EXPIRY_CODE} [{VARIANT_SUFFIX}]

    e.g.  GO10OZ  -  AU26  ID
          ICOTTON -  JY26
          PKWHEATSD - MON
          TOLAGOLD  - WED

    COMMODITY_CODE  = what is being traded (may embed size/type info)
    EXPIRY_CODE     = when it expires  → either MMYY (month+year) or DD (day-of-week)
    VARIANT_SUFFIX  = optional modifier appended after expiry  (e.g. "ID")
"""

# Map specific tickers back to their schedule categories
symbol_to_category = {
    "ICOTTON50K": "ICotton",
    "ICOTTON": "ICotton",
    "ISOYBEAN": "Grains_Group_(ISoybean_ICorn_IWheat)",
    "ICORN": "Grains_Group_(ISoybean_ICorn_IWheat)",
    "IWHEAT": "Grains_Group_(ISoybean_ICorn_IWheat)",
    "BRENT": "Brent",
    "ALUMINUM": "Aluminum",
    "IGOLD": "All_International_Except_Specified",
    "ISILVER": "All_International_Except_Specified"
}
trading_schedule = {
    "All_International_Except_Specified": {
        "Monday": {
            "existing": {"open": "04:00 AM", "close": "03:00 AM"},
            "revised": {"open": "03:00 AM", "close": "02:00 AM"}
        },
        "Tuesday": {
            "existing": {"open": "04:30 AM", "close": "03:00 AM"},
            "revised": {"open": "03:30 AM", "close": "02:00 AM"}
        },
        "Wednesday": {
            "existing": {"open": "04:30 AM", "close": "03:00 AM"},
            "revised": {"open": "03:30 AM", "close": "02:00 AM"}
        },
        "Thursday": {
            "existing": {"open": "04:30 AM", "close": "03:00 AM"},
            "revised": {"open": "03:30 AM", "close": "02:00 AM"}
        },
        "Friday": {
            "existing": {"open": "04:30 AM", "close": "03:00 AM"},
            "revised": {"open": "03:30 AM", "close": "02:00 AM"}
        }
    },
    "Aluminum": {
        "Monday": {"existing": {"open": "06:00 AM", "close": "12:00 AM"}, "revised": {"open": "05:00 AM", "close": "11:00 PM"}},
        "Tuesday": {"existing": {"open": "06:00 AM", "close": "12:00 AM"}, "revised": {"open": "05:00 AM", "close": "11:00 PM"}},
        "Wednesday": {"existing": {"open": "06:00 AM", "close": "12:00 AM"}, "revised": {"open": "05:00 AM", "close": "11:00 PM"}},
        "Thursday": {"existing": {"open": "06:00 AM", "close": "12:00 AM"}, "revised": {"open": "05:00 AM", "close": "11:00 PM"}},
        "Friday": {"existing": {"open": "06:00 AM", "close": "12:00 AM"}, "revised": {"open": "05:00 AM", "close": "11:00 PM"}}
    },
    "Brent": {
        "Monday": {
            "existing": {"open": "04:00 AM", "close": "03:00 AM"},
            "revised": {"open": "03:00 AM", "close": "02:00 AM"}
        },
        "Tuesday": {
            "existing": {"open": "06:00 AM", "close": "03:00 AM"},
            "revised": {"open": "05:00 AM", "close": "02:00 AM"}
        },
        "Wednesday": {
            "existing": {"open": "06:00 AM", "close": "03:00 AM"},
            "revised": {"open": "05:00 AM", "close": "02:00 AM"}
        },
        "Thursday": {
            "existing": {"open": "06:00 AM", "close": "03:00 AM"},
            "revised": {"open": "05:00 AM", "close": "02:00 AM"}
        },
        "Friday": {
            "existing": {"open": "06:00 AM", "close": "03:00 AM"},
            "revised": {"open": "05:00 AM", "close": "02:00 AM"}
        }
    },
    "Grains_Group_(ISoybean_ICorn_IWheat)": {
        "Monday": {
            "existing": {"open": "04:00 AM", "close": "12:00 AM"},
            "revised": {"open": "03:00 AM", "close": "11:00 PM"}
        },
        "Tuesday": {
            "existing": {"open": "04:30 AM", "close": "12:00 AM"},
            "revised": {"open": "03:30 AM", "close": "11:00 PM"}
        },
        "Wednesday": {
            "existing": {"open": "04:30 AM", "close": "12:00 AM"},
            "revised": {"open": "03:30 AM", "close": "11:00 PM"}
        },
        "Thursday": {
            "existing": {"open": "04:30 AM", "close": "12:00 AM"},
            "revised": {"open": "03:30 AM", "close": "11:00 PM"}
        },
        "Friday": {
            "existing": {"open": "04:30 AM", "close": "12:00 AM"},
            "revised": {"open": "03:30 AM", "close": "11:00 PM"}
        }
    },
    "ICotton": {
        "Monday": {"existing": {"open": "07:00 AM", "close": "12:00 AM"}, "revised": {"open": "06:00 AM", "close": "11:00 PM"}},
        "Tuesday": {"existing": {"open": "07:00 AM", "close": "12:00 AM"}, "revised": {"open": "06:00 AM", "close": "11:00 PM"}},
        "Wednesday": {"existing": {"open": "07:00 AM", "close": "12:00 AM"}, "revised": {"open": "06:00 AM", "close": "11:00 PM"}},
        "Thursday": {"existing": {"open": "07:00 AM", "close": "12:00 AM"}, "revised": {"open": "06:00 AM", "close": "11:00 PM"}},
        "Friday": {"existing": {"open": "07:00 AM", "close": "12:00 AM"}, "revised": {"open": "06:00 AM", "close": "11:00 PM"}}
    }
}
# Example: Get revised open time for Cotton on a Tuesday

# Output: ICOTTON50K opens at 06:00 AM on Tuesday.
# ══════════════════════════════════════════════════════════════════════════════
# 1.  MONTH CODES  (PMEX uses its own 2-letter system, NOT the CME 1-letter system)
# ══════════════════════════════════════════════════════════════════════════════
# Logic: first 2 distinctive letters of the English month name.
# January/June/July are disambiguated as JA / JU / JY.
# March uses MR (not MA) to avoid clash with May → MY.
# November uses NV (not NO) to pull a distinctive pair.

MONTH_CODES: dict[str, str] = {
    "JA": "January",
    "FE": "February",
    "MR": "March",
    "AP": "April",
    "MY": "May",
    "JU": "June",
    "JY": "July",
    "AU": "August",
    "SE": "September",
    "OC": "October",
    "NV": "November",
    "DE": "December",
}

# Reverse: month number → PMEX code  (useful when building queries)
MONTH_NUM_TO_CODE: dict[int, str] = {
    1: "JA", 2: "FE", 3: "MR",  4: "AP",
    5: "MY", 6: "JU", 7: "JY",  8: "AU",
    9: "SE", 10: "OC", 11: "NV", 12: "DE",
}

# ══════════════════════════════════════════════════════════════════════════════
# 2.  DAY-OF-WEEK CODES  (used only in daily / 1-day spot contracts)
# ══════════════════════════════════════════════════════════════════════════════
# Contracts: MAIZESD-MON, PKWheatSD-TUE, TOLAGOLD-WED, MTOLAGOLD-WED

DAY_CODES: dict[str, str] = {
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
}

# ══════════════════════════════════════════════════════════════════════════════
# 3.  EXPIRY CODE TYPE — how to tell if a suffix is a month-year or a day
# ══════════════════════════════════════════════════════════════════════════════
# Rule: after the dash, if the first 2 chars are in MONTH_CODES → it's MMYY.
#       if all 3 chars are in DAY_CODES → it's a weekday.

def parse_expiry(code: str) -> dict:
    """
    Input:  'JY26'  →  {'type': 'monthly', 'month': 'July',  'year': 2026}
    Input:  'MON'   →  {'type': 'daily',   'day':   'Monday', 'year': None}
    Input:  'AU26ID'→  {'type': 'monthly', 'month': 'August', 'year': 2026,
                         'variant': 'ID', 'variant_long': 'Import Duty Paid'}
    """
    code = code.strip()
    # Strip known trailing variant suffixes before parsing
    variant = None
    for sfx, meaning in VARIANT_SUFFIXES.items():
        if code.upper().endswith(sfx):
            variant = sfx
            code = code[: -len(sfx)]
            break

    if code[:2].upper() in MONTH_CODES and len(code) >= 4:
        result = {
            "type":       "monthly",
            "month_code": code[:2].upper(),
            "month":      MONTH_CODES[code[:2].upper()],
            "year":       2000 + int(code[2:4]),
        }
    elif code.upper() in DAY_CODES:
        result = {
            "type": "daily",
            "day":  DAY_CODES[code.upper()],
            "year": None,
        }
    else:
        result = {"type": "unknown", "raw": code}

    if variant:
        result["variant"]      = variant
        result["variant_long"] = VARIANT_SUFFIXES[variant]
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 4.  VARIANT SUFFIXES (appended AFTER the expiry code, e.g. AU26ID)
# ══════════════════════════════════════════════════════════════════════════════
# "ID" is the only confirmed variant suffix seen in live PMEX data.
# It appears on gold contracts (GO1OZ, GO10OZ, GO100OZ, SL10, SL100OZ)
# and on some forex/financial gold pairs (GOLDAUDUSD, GOLDEURUSD, etc.)

VARIANT_SUFFIXES: dict[str, str] = {
    "ID": (
        "Import Duty Paid — gold (or silver) on which Pakistani customs/import "
        "duty has already been settled. These contracts are eligible for physical "
        "delivery within Pakistan under the local duty-paid regime. "
        "Trades at a slight premium to the non-ID variant."
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# 5.  CONTRACT TYPE MODIFIERS embedded inside the COMMODITY CODE
#     (these are NOT separate suffixes — they are part of the root code)
# ══════════════════════════════════════════════════════════════════════════════
# Examples: PKWheat[SD], PKWheat[LD], MAIZE[SD], MAIZE[LD], ICOTTON[50K]
# These describe the contract *design*, not the expiry.

CONTRACT_TYPE_MODIFIERS: dict[str, str] = {
    "SD":  (
        "Same Day — a 1-business-day spot contract. Opens and expires within "
        "a single trading session. Uses a weekday code (MON/TUE/WED/THU/FRI) "
        "instead of a month-year expiry. "
        "Examples: PKWheatSD-MON, MAIZESD-TUE"
    ),
    "LD":  (
        "Long Dated — a multi-month forward futures contract with monthly expiry "
        "dates published in advance. Uses MMYY expiry code. "
        "Examples: PKWheatLD-JY26, MAIZELD-AU26"
    ),
    "50K": (
        "50,000 Pound contract size (cotton only). "
        "10× larger than the standard ICOTTON (5,000 lb) contract. "
        "Symbol: ICOTTON50K"
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# 6.  SIZE CODES embedded inside commodity root symbols
#     (the number/unit tag in the root tells you contract size)
# ══════════════════════════════════════════════════════════════════════════════

SIZE_CODES_IN_ROOT: dict[str, str] = {
    # Gold ounce sizes
    "1OZ":   "1 Troy Ounce of Gold",
    "10OZ":  "10 Troy Ounces of Gold",
    "100OZ": "100 Troy Ounces of Gold",
    "MOZ":   "Milli Ounce of Gold = 1/1000 Troy Oz ≈ 0.031 grams",
    # Silver ounce sizes
    "SL1":     "Silver 1 Troy Ounce",
    "SL10":    "Silver 10 Troy Ounces",
    "SL100OZ": "Silver 100 Troy Ounces",
    # Crude Oil barrel sizes
    "CRUDE1":    "WTI Crude Oil — 1 Barrel",
    "CRUDE10":   "WTI Crude Oil — 10 Barrels",
    "CRUDE100":  "WTI Crude Oil — 100 Barrels",
    "CRUDE1000": "WTI Crude Oil — 1,000 Barrels",
    # Brent Oil barrel sizes
    "BRENT10":   "Brent Crude Oil — 10 Barrels",
    "BRENT100":  "Brent Crude Oil — 100 Barrels",
    "BRENT1000": "Brent Crude Oil — 1,000 Barrels",
    # Natural Gas
    "NGAS1K":  "Natural Gas — 1,000 MMBtu",
    "NGAS10K": "Natural Gas — 10,000 MMBtu",
    # Aluminium lot sizes
    "ALUMINUM1": "Aluminium — 1 Metric Ton",
    "ALUMINUM5": "Aluminium — 5 Metric Tons",
    # Copper lot sizes
    "COPPER":    "Copper — 1 lb (standard)",
    "COPPER100": "Copper — 100 lbs",
    "COPPER25K": "Copper — 25,000 lbs",
    # Platinum
    "PLATINUM1":  "Platinum — 1 Troy Ounce",
    "PLATINUM5":  "Platinum — 5 Troy Ounces",
    "PLATINUM50": "Platinum — 50 Troy Ounces",
    # Palladium
    "PALDIUM100": "Palladium — 100 Troy Ounces",
    # Indices (prefix explains size)
    "MICRO":  "Micro contract (smallest, ~1/10 of Mini)",
    "MINI":   "Mini contract (smaller than standard)",
    "2":      "2× standard contract size (prefix on 2NSDQ100)",
}

# ══════════════════════════════════════════════════════════════════════════════
# 7.  ALL COMMODITY CODES → FULL NAME + METADATA
#     Complete flat mapping of every commodity root seen on PMEX
# ══════════════════════════════════════════════════════════════════════════════

COMMODITY_CODES: dict[str, dict] = {

    # ── AGRICULTURE (International / Cash Settled) ────────────────────────
    "ICORN": {
        "full_name":       "International Corn (CBOT)",
        "asset_class":     "Agriculture — International",
        "contract_size":   "5,000 bushels",
        "price_unit":      "US cents per bushel",
        "settlement":      "Cash — PKR (via SBP USD/PKR rate)",
        "reference_mkt":   "CME Group / CBOT Corn Futures",
        "expiry_months":   ["MR", "MY", "JY", "SE", "DE"],
        "expiry_type":     "monthly",
    },
    "ICOTTON": {
        "full_name":       "International Cotton — 5,000 lbs (ICE)",
        "asset_class":     "Agriculture — International",
        "contract_size":   "5,000 pounds",
        "price_unit":      "US cents per pound",
        "settlement":      "Cash — PKR (via SBP USD/PKR rate)",
        "reference_mkt":   "ICE Cotton No.2 Futures",
        "expiry_months":   ["MR", "MY", "JY", "OC", "DE"],
        "expiry_type":     "monthly",
    },
    "ICOTTON50K": {
        "full_name":       "International Cotton — 50,000 lbs (ICE)",
        "asset_class":     "Agriculture — International",
        "contract_size":   "50,000 pounds",
        "price_unit":      "US cents per pound",
        "settlement":      "Cash — PKR (via SBP USD/PKR rate)",
        "reference_mkt":   "ICE Cotton No.2 Futures",
        "expiry_months":   ["MR", "MY", "JY", "OC", "DE"],
        "expiry_type":     "monthly",
        "note":            "10× the size of ICOTTON; for institutional hedgers",
    },
    "ISOYBEAN": {
        "full_name":       "International Soybean (CBOT)",
        "asset_class":     "Agriculture — International",
        "contract_size":   "5,000 bushels",
        "price_unit":      "US cents per bushel",
        "settlement":      "Cash — PKR (via SBP USD/PKR rate)",
        "reference_mkt":   "CME Group / CBOT Soybean Futures",
        "expiry_months":   ["JA", "MR", "MY", "JY", "AU", "SE", "NV"],
        "expiry_type":     "monthly",
    },
    "IWHEAT": {
        "full_name":       "International Wheat (CBOT)",
        "asset_class":     "Agriculture — International",
        "contract_size":   "5,000 bushels",
        "price_unit":      "US cents per bushel",
        "settlement":      "Cash — PKR (via SBP USD/PKR rate)",
        "reference_mkt":   "CME Group / CBOT Wheat Futures",
        "expiry_months":   ["MR", "MY", "JY", "SE", "DE"],
        "expiry_type":     "monthly",
        "note":            "Tracks GLOBAL wheat price. Different from WHEAT / PKWheatLD.",
    },
    "WHEAT": {
        "full_name":       "Wheat Futures (PMEX domestic / simplified symbol)",
        "asset_class":     "Agriculture — Domestic",
        "contract_size":   "10 Metric Tons",
        "price_unit":      "Rs. per 40 kg",
        "settlement":      "Physical / EWR",
        "reference_mkt":   "Local Pakistani spot market",
        "expiry_months":   ["JY", "AU", "SE"],
        "expiry_type":     "monthly",
        "note":            (
            "Appears to be an alias or simplified form for Pakistan Milling Wheat "
            "Long Dated contract. May represent PKWheatLD under a shorter symbol. "
            "Tracks LOCAL Pakistani wheat prices."
        ),
    },

    # ── AGRICULTURE (Domestic / Physical Delivery) ────────────────────────
    "LGMRRICE": {
        "full_name":       "Long Grain Milled Raw Rice Futures",
        "asset_class":     "Agriculture — Domestic (Physical)",
        "contract_size":   "10 Metric Tons",
        "delivery_unit":   "30 MT ± 2 MT",
        "price_unit":      "Rs. per 100 kg (delivered Karachi)",
        "settlement":      "Physical delivery at PMEX-approved warehouse OR cash",
        "delivery_center": "Meskay & Femtee Trading Co., Port Qasim, Karachi",
        "expiry_months":   ["FE","MR","AP","MY","JU","JY","AU","SE","OC","NV","DE","JA"],
        "expiry_type":     "monthly",
        "trading_hours":   "10:00 AM – 6:00 PM PST (Mon–Fri) [as of May 18, 2026]",
        "variety":         "IRRI-6 and similar long grain varieties",
    },
    "SUGAR": {
        "full_name":       "Refined White Sugar Futures",
        "asset_class":     "Agriculture — Domestic (Physical)",
        "contract_size":   "12 Metric Tons",
        "delivery_unit":   "12 MT ± 5%",
        "price_unit":      "Rs. per 100 kg (exclusive of taxes)",
        "settlement":      "Physical delivery at approved mills OR Ex-Mill DO OR cash",
        "delivery_center": (
            "Hunza Sugar Mills Unit-I (Faisalabad) | "
            "Hunza Sugar Mills Unit-II (Jhang)"
        ),
        "premium":         "PKR 3 per kg at both delivery centers",
        "expiry_months":   ["DE","JA","FE","MR","AP","MY","JU","JY","AU","SE","OC","NV"],
        "expiry_type":     "monthly",
        "quality":         "Polarization ≥99.8%, Moisture ≤0.08%, ICUMSA ≤100",
    },
    "PKWHEATSD": {
        "full_name":       "Pakistan Milling Wheat — Same Day Contract",
        "asset_class":     "Agriculture — Domestic (Physical EWR)",
        "contract_size":   "10 Metric Tons",
        "price_unit":      "Rs. per 40 kg",
        "settlement":      "Physical via Electronic Warehouse Receipt (EWR) on E+1",
        "expiry_type":     "daily",
        "expiry_codes":    ["MON", "TUE", "WED", "THU", "FRI"],
        "note":            (
            "New symbol each trading day. Buyer pays 100% cash upfront. "
            "No short selling — sellers need a valid EWR first. "
            "Symbol format: PKWheatSD-MON, PKWheatSD-TUE, etc."
        ),
    },
    "PKWHEATLD": {
        "full_name":       "Pakistan Milling Wheat — Long Dated Futures",
        "asset_class":     "Agriculture — Domestic (Physical EWR)",
        "contract_size":   "10 Metric Tons",
        "price_unit":      "Rs. per 40 kg",
        "settlement":      "Physical via EWR. E-1: seller deposits wheat. E+2: EWR transfer.",
        "expiry_months":   ["MR","AP","MY","JY","SE","DE"],
        "expiry_type":     "monthly",
        "note":            (
            "Symbol may include a location code: PKWheatLD-LC-MMYY. "
            "LC = 2-letter delivery center location code (e.g. LHR for Lahore). "
            "21 accredited CMC warehouses across Punjab."
        ),
    },
    "MAIZESD": {
        "full_name":       "Yellow Maize — Same Day Contract",
        "asset_class":     "Agriculture — Domestic (Physical EWR)",
        "contract_size":   "10 Metric Tons",
        "price_unit":      "Rs. per 40 kg",
        "settlement":      "Physical via EWR on E+1",
        "expiry_type":     "daily",
        "expiry_codes":    ["MON", "TUE", "WED", "THU", "FRI"],
        "daily_limit":     "±2.5% (tighter than other contracts)",
    },
    "MAIZELD": {
        "full_name":       "Yellow Maize — Long Dated Futures",
        "asset_class":     "Agriculture — Domestic (Physical)",
        "contract_size":   "10 Metric Tons",
        "delivery_unit":   "30 MT ± 2 MT",
        "price_unit":      "Rs. per 40 kg",
        "settlement":      "Physical at designated warehouse OR cash at final settlement",
        "expiry_months":   ["MY","JU","JY","AU","SE","OC","NV","DE"],
        "expiry_type":     "monthly",
    },
    "PALMOLEIN": {
        "full_name":       "RBD Palm Olein Futures",
        "asset_class":     "Agriculture — Domestic (Physical)",
        "contract_size":   "25 Metric Tons",
        "delivery_unit":   "25 MT",
        "price_unit":      "PKR per Maund",
        "settlement":      "Physical delivery at Karachi Port / Port Qasim",
        "reference_mkt":   (
            "Bursa Malaysia Derivatives (BMD) Crude Palm Oil Futures — "
            "palmolein is the liquid fraction of palm oil after fractionation"
        ),
        "expiry_months":   ["JY", "AU", "SE"],
        "expiry_type":     "monthly",
        "quality":         (
            "Moisture & Insol. Impurities ≤0.10%, Color R3 max (Lovibond 5¼\"), "
            "Iodine Value 50-55 (Wijs), FFA ≤0.25% (as palmitic), "
            "Slip Melting Point 37-39°C"
        ),
        "note":            (
            "Confirmed on PMEX. Pakistan is a major importer of palm/palmolein oil "
            "from Malaysia & Indonesia. Contract expires on the 15th of the contract "
            "month (or next business day)."
        ),
    },

    # ── GOLD (PKR-denominated, local) ─────────────────────────────────────
    "TOLAGOLD": {
        "full_name":       "Tola Gold Futures",
        "asset_class":     "Metals — Gold (Local PKR)",
        "contract_size":   "1 Tola = 11.664 grams",
        "price_unit":      "PKR per Tola",
        "settlement":      "Cash or Physical delivery",
        "expiry_type":     "daily (weekly on Wednesday)",
        "expiry_codes":    ["WED"],
        "note":            "Priced in PKR. 1 Tola = 11.664 grams. Local gold standard unit in Pakistan.",
    },
    "MTOLAGOLD": {
        "full_name":       "Milli Tola Gold Futures",
        "asset_class":     "Metals — Gold (Local PKR)",
        "contract_size":   "1 Milli-Tola = 1/1000 Tola = 0.011664 grams",
        "price_unit":      "PKR per Tola (tick PKR 1 = PKR 0.001 per milli-tola)",
        "settlement":      "Cash or Physical delivery",
        "expiry_type":     "daily (weekly on Wednesday)",
        "expiry_codes":    ["WED"],
        "note":            "Tiny contract designed for micro-retail investors.",
    },

    # ── GOLD (USD-denominated, international oz) ──────────────────────────
    "GO1OZ": {
        "full_name":       "Gold — 1 Troy Ounce",
        "asset_class":     "Metals — Gold (International)",
        "contract_size":   "1 Troy Ounce (31.1035 grams)",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "variants":        ["GO1OZ-MMYY", "GO1OZ-MMYYID"],
    },
    "GO10OZ": {
        "full_name":       "Gold — 10 Troy Ounces",
        "asset_class":     "Metals — Gold (International)",
        "contract_size":   "10 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "variants":        ["GO10OZ-MMYY", "GO10OZ-MMYYID"],
    },
    "GO100OZ": {
        "full_name":       "Gold — 100 Troy Ounces",
        "asset_class":     "Metals — Gold (International)",
        "contract_size":   "100 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "variants":        ["GO100OZ-MMYY", "GO100OZ-MMYYID"],
    },
    "GOMOZ": {
        "full_name":       "Gold — Milli Ounce (1/1000 Troy Oz)",
        "asset_class":     "Metals — Gold (International)",
        "contract_size":   "0.001 Troy Ounce ≈ 0.031 grams",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "note":            (
            "Highest-volume gold contract on PMEX (e.g. 27,844 in a single session). "
            "Entry-level micro gold contract accessible to retail investors."
        ),
    },

    # ── SILVER ────────────────────────────────────────────────────────────
    "SL1": {
        "full_name":       "Silver — 1 Troy Ounce",
        "asset_class":     "Metals — Silver",
        "contract_size":   "1 Troy Ounce",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "SL10": {
        "full_name":       "Silver — 10 Troy Ounces",
        "asset_class":     "Metals — Silver",
        "contract_size":   "10 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "variants":        ["SL10-MMYY", "SL10-MMYYID"],
    },
    "SL100OZ": {
        "full_name":       "Silver — 100 Troy Ounces",
        "asset_class":     "Metals — Silver",
        "contract_size":   "100 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
        "variants":        ["SL100OZ-MMYY", "SL100OZ-MMYYID"],
    },

    # ── PLATINUM ─────────────────────────────────────────────────────────
    "PLATINUM1": {
        "full_name":       "Platinum — 1 Troy Ounce",
        "asset_class":     "Metals — Platinum",
        "contract_size":   "1 Troy Ounce",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "PLATINUM5": {
        "full_name":       "Platinum — 5 Troy Ounces",
        "asset_class":     "Metals — Platinum",
        "contract_size":   "5 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "PLATINUM50": {
        "full_name":       "Platinum — 50 Troy Ounces",
        "asset_class":     "Metals — Platinum",
        "contract_size":   "50 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },

    # ── PALLADIUM ────────────────────────────────────────────────────────
    "PALDIUM100": {
        "full_name":       "Palladium — 100 Troy Ounces",
        "asset_class":     "Metals — Palladium",
        "contract_size":   "100 Troy Ounces",
        "price_unit":      "USD per troy ounce",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },

    # ── COPPER ───────────────────────────────────────────────────────────
    "COPPER": {
        "full_name":       "Copper Futures (standard)",
        "asset_class":     "Metals — Copper",
        "contract_size":   "Approx 1 lb (reference CME COMEX)",
        "price_unit":      "USD per pound",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "COPPER100": {
        "full_name":       "Copper Futures — 100 lbs",
        "asset_class":     "Metals — Copper",
        "contract_size":   "100 lbs",
        "price_unit":      "USD per pound",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "COPPER25K": {
        "full_name":       "Copper Futures — 25,000 lbs",
        "asset_class":     "Metals — Copper",
        "contract_size":   "25,000 lbs",
        "price_unit":      "USD per pound",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },

    # ── ALUMINIUM ────────────────────────────────────────────────────────
    "ALUMINUM1": {
        "full_name":       "Aluminium Futures — 1 Metric Ton",
        "asset_class":     "Metals — Aluminium",
        "contract_size":   "1 Metric Ton",
        "price_unit":      "USD per metric ton",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "ALUMINUM5": {
        "full_name":       "Aluminium Futures — 5 Metric Tons",
        "asset_class":     "Metals — Aluminium",
        "contract_size":   "5 Metric Tons",
        "price_unit":      "USD per metric ton",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },

    # ── CRUDE OIL (WTI) ───────────────────────────────────────────────────
    "CRUDE1": {
        "full_name":       "WTI Crude Oil — 1 Barrel",
        "asset_class":     "Energy — Crude Oil",
        "contract_size":   "1 Barrel",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX WTI Crude Oil",
        "expiry_type":     "monthly",
    },
    "CRUDE10": {
        "full_name":       "WTI Crude Oil — 10 Barrels",
        "asset_class":     "Energy — Crude Oil",
        "contract_size":   "10 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX WTI Crude Oil",
        "expiry_type":     "monthly",
        "variants":        ["CRUDE10-MMYY", "CRUDE10-MMYYID"],
    },
    "CRUDE100": {
        "full_name":       "WTI Crude Oil — 100 Barrels",
        "asset_class":     "Energy — Crude Oil",
        "contract_size":   "100 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX WTI Crude Oil",
        "expiry_type":     "monthly",
        "variants":        ["CRUDE100-MMYY", "CRUDE100-MMYYID"],
    },
    "CRUDE1000": {
        "full_name":       "WTI Crude Oil — 1,000 Barrels",
        "asset_class":     "Energy — Crude Oil",
        "contract_size":   "1,000 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX WTI Crude Oil",
        "expiry_type":     "monthly",
        "variants":        ["CRUDE1000-MMYY", "CRUDE1000-MMYYID"],
    },

    # ── BRENT CRUDE OIL ───────────────────────────────────────────────────
    "BRENT10": {
        "full_name":       "Brent Crude Oil — 10 Barrels",
        "asset_class":     "Energy — Brent Oil",
        "contract_size":   "10 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "ICE Brent Crude Futures",
        "expiry_type":     "monthly",
    },
    "BRENT100": {
        "full_name":       "Brent Crude Oil — 100 Barrels",
        "asset_class":     "Energy — Brent Oil",
        "contract_size":   "100 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "ICE Brent Crude Futures",
        "expiry_type":     "monthly",
    },
    "BRENT1000": {
        "full_name":       "Brent Crude Oil — 1,000 Barrels",
        "asset_class":     "Energy — Brent Oil",
        "contract_size":   "1,000 Barrels",
        "price_unit":      "USD per barrel",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "ICE Brent Crude Futures",
        "expiry_type":     "monthly",
    },

    # ── NATURAL GAS ───────────────────────────────────────────────────────
    "NGAS1K": {
        "full_name":       "Natural Gas — 1,000 MMBtu",
        "asset_class":     "Energy — Natural Gas",
        "contract_size":   "1,000 MMBtu (million British thermal units)",
        "price_unit":      "USD per MMBtu",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX Henry Hub Natural Gas",
        "expiry_type":     "monthly",
    },
    "NGAS10K": {
        "full_name":       "Natural Gas — 10,000 MMBtu",
        "asset_class":     "Energy — Natural Gas",
        "contract_size":   "10,000 MMBtu",
        "price_unit":      "USD per MMBtu",
        "settlement":      "Cash — PKR",
        "reference_mkt":   "NYMEX Henry Hub Natural Gas",
        "expiry_type":     "monthly",
    },

    # ── EQUITY INDICES ────────────────────────────────────────────────────
    "NSDQ100": {
        "full_name":       "NASDAQ-100 Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "MININSDQ100": {
        "full_name":       "NASDAQ-100 Mini Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "MICRONSDQ100": {
        "full_name":       "NASDAQ-100 Micro Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "2NSDQ100": {
        "full_name":       "NASDAQ-100 2× (Double) Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "SP500": {
        "full_name":       "S&P 500 Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "MINISP500": {
        "full_name":       "S&P 500 Mini Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "MICROSP500": {
        "full_name":       "S&P 500 Micro Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "DJ": {
        "full_name":       "Dow Jones Industrial Average (DJIA) Index Futures",
        "asset_class":     "Indices",
        "price_unit":      "Index points (USD)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "JPYEQTY1": {
        "full_name":       "JPY Equity Index Futures — 1× (Nikkei / Japanese Equity)",
        "asset_class":     "Indices",
        "price_unit":      "Index points (JPY)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },
    "JPYEQTY5": {
        "full_name":       "JPY Equity Index Futures — 5× (Nikkei / Japanese Equity)",
        "asset_class":     "Indices",
        "price_unit":      "Index points (JPY)",
        "settlement":      "Cash — PKR",
        "expiry_type":     "monthly",
    },

    # ── FINANCIAL (Gold Currency Pairs) ──────────────────────────────────
    # These are NOT regular forex — they are GOLD valued in currency pairs.
    # "GOLDEURUSD" = value of Gold expressed in EUR/USD terms (gold FX rate)
    "GOLDAUDUSD":  {"full_name": "Gold — AUD/USD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDAUDCAD":  {"full_name": "Gold — AUD/CAD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDAUDJPY":  {"full_name": "Gold — AUD/JPY FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURUSD":  {"full_name": "Gold — EUR/USD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURAUD":  {"full_name": "Gold — EUR/AUD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURCAD":  {"full_name": "Gold — EUR/CAD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURCHF":  {"full_name": "Gold — EUR/CHF FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURGBP":  {"full_name": "Gold — EUR/GBP FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDEURJPY":  {"full_name": "Gold — EUR/JPY FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDGBPUSD":  {"full_name": "Gold — GBP/USD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDGBPJPY":  {"full_name": "Gold — GBP/JPY FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDGBPCHF":  {"full_name": "Gold — GBP/CHF FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDUSDCAD":  {"full_name": "Gold — USD/CAD FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDUSDCHF":  {"full_name": "Gold — USD/CHF FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDUSDJPY":  {"full_name": "Gold — USD/JPY FX Rate Futures",  "asset_class": "Financials — Gold FX"},
    "GOLDCHFJPY":  {"full_name": "Gold — CHF/JPY FX Rate Futures",  "asset_class": "Financials — Gold FX"},
}


# ══════════════════════════════════════════════════════════════════════════════
# 8.  ASSET CLASS GROUPING  (group commodity codes by category)
# ══════════════════════════════════════════════════════════════════════════════

ASSET_CLASS_MAP: dict[str, list[str]] = {
    "Agriculture — International": [
        "ICORN", "ICOTTON", "ICOTTON50K", "ISOYBEAN", "IWHEAT", "PALMOLEIN",
    ],
    "Agriculture — Domestic (Physical)": [
        "LGMRRICE", "SUGAR", "MAIZELD", "WHEAT",
    ],
    "Agriculture — Domestic (Physical EWR)": [
        "PKWHEATSD", "PKWHEATLD", "MAIZESD",
    ],
    "Metals — Gold (Local PKR)": [
        "TOLAGOLD", "MTOLAGOLD",
    ],
    "Metals — Gold (International)": [
        "GO1OZ", "GO10OZ", "GO100OZ", "GOMOZ",
    ],
    "Metals — Silver": [
        "SL1", "SL10", "SL100OZ",
    ],
    "Metals — Platinum": [
        "PLATINUM1", "PLATINUM5", "PLATINUM50",
    ],
    "Metals — Palladium": [
        "PALDIUM100",
    ],
    "Metals — Copper": [
        "COPPER", "COPPER100", "COPPER25K",
    ],
    "Metals — Aluminium": [
        "ALUMINUM1", "ALUMINUM5",
    ],
    "Energy — Crude Oil": [
        "CRUDE1", "CRUDE10", "CRUDE100", "CRUDE1000",
    ],
    "Energy — Brent Oil": [
        "BRENT10", "BRENT100", "BRENT1000",
    ],
    "Energy — Natural Gas": [
        "NGAS1K", "NGAS10K",
    ],
    "Indices": [
        "NSDQ100", "MININSDQ100", "MICRONSDQ100", "2NSDQ100",
        "SP500", "MINISP500", "MICROSP500", "DJ", "JPYEQTY1", "JPYEQTY5",
    ],
    "Financials — Gold FX": [
        "GOLDAUDUSD", "GOLDAUDCAD", "GOLDAUDJPY",
        "GOLDEURUSD", "GOLDEURAUD", "GOLDEURCAD", "GOLDEURCHF",
        "GOLDEURGBP", "GOLDEURJPY",
        "GOLDGBPUSD", "GOLDGBPJPY", "GOLDGBPCHF",
        "GOLDUSDCAD", "GOLDUSDCHF", "GOLDUSDJPY", "GOLDCHFJPY",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# 9.  COMPLETE SYMBOL PARSER
# ══════════════════════════════════════════════════════════════════════════════

def parse_pmex_symbol(symbol: str) -> dict:
    """
    Parse any PMEX symbol into its component parts.

    Examples
    --------
    >>> parse_pmex_symbol("ICOTTON-JY26")
    {
      'raw': 'ICOTTON-JY26',
      'commodity_code': 'ICOTTON',
      'commodity_name': 'International Cotton — 5,000 lbs (ICE)',
      'asset_class': 'Agriculture — International',
      'expiry_type': 'monthly',
      'month_code': 'JY',
      'month': 'July',
      'year': 2026,
      'variant': None,
    }

    >>> parse_pmex_symbol("GO10OZ-AU26ID")
    {
      'raw': 'GO10OZ-AU26ID',
      'commodity_code': 'GO10OZ',
      'commodity_name': 'Gold — 10 Troy Ounces',
      'asset_class': 'Metals — Gold (International)',
      'expiry_type': 'monthly',
      'month_code': 'AU',
      'month': 'August',
      'year': 2026,
      'variant': 'ID',
      'variant_long': 'Import Duty Paid ...',
    }

    >>> parse_pmex_symbol("PKWHEATSD-MON")
    {
      'raw': 'PKWHEATSD-MON',
      'commodity_code': 'PKWHEATSD',
      'commodity_name': 'Pakistan Milling Wheat — Same Day Contract',
      'asset_class': 'Agriculture — Domestic (Physical EWR)',
      'expiry_type': 'daily',
      'day': 'Monday',
      'year': None,
      'variant': None,
    }
    """
    parts = symbol.upper().split("-", 1)
    if len(parts) != 2:
        return {"raw": symbol, "error": "No dash separator found"}

    commodity_code, expiry_raw = parts[0], parts[1]

    # Look up commodity
    commodity_info = COMMODITY_CODES.get(commodity_code, {})

    # Parse expiry (handles variant suffix stripping too)
    expiry = parse_expiry(expiry_raw)

    return {
        "raw":             symbol,
        "commodity_code":  commodity_code,
        "commodity_name":  commodity_info.get("full_name", "Unknown"),
        "asset_class":     commodity_info.get("asset_class", "Unknown"),
        "contract_size":   commodity_info.get("contract_size", "Unknown"),
        "price_unit":      commodity_info.get("price_unit", "Unknown"),
        "settlement":      commodity_info.get("settlement", "Unknown"),
        **expiry,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 10.  QUICK-REFERENCE: ALL SYMBOLS SEEN IN LIVE DATA
#      (from both data snapshots you shared)
# ══════════════════════════════════════════════════════════════════════════════

ALL_OBSERVED_SYMBOLS: list[str] = [
    # Agriculture - International
    "ICORN-JY26",
    "ICOTTON-DE26", "ICOTTON-JY26",
    "ICOTTON50K-DE26", "ICOTTON50K-JY26",
    "ISOYBEAN-JY26",
    "IWHEAT-JY26",
    "PALMOLEIN-AU26", "PALMOLEIN-JY26", "PALMOLEIN-SE26",
    # Agriculture - Domestic
    "SUGAR-JU26", "SUGAR-JY26",
    "LGMRRICE-JU26", "LGMRRICE-JY26", "LGMRRICE-AU26",
    "MAIZELD-JU26", "MAIZELD-JY26", "MAIZELD-AU26",
    "WHEAT-JY26", "WHEAT-AU26", "WHEAT-SE26",
    "PKWHEATLD-JY26", "PKWHEATLD-SE26",
    # Local Gold
    "TOLAGOLD-WED", "MTOLAGOLD-WED",
    # Gold oz
    "GO1OZ-AU26", "GO1OZ-AU26ID",
    "GO10OZ-AU26", "GO10OZ-AU26ID",
    "GO100OZ-AU26", "GO100OZ-AU26ID",
    "GOMOZ-AU26",
    # Silver
    "SL1-JY26",
    "SL10-JY26", "SL10-JY26ID",
    "SL100OZ-JY26", "SL100OZ-JY26ID",
    # Platinum / Palladium
    "PLATINUM1-JY26", "PLATINUM5-JY26", "PLATINUM50-JY26",
    "PALDIUM100-SE26",
    # Copper / Aluminium
    "COPPER-JY26", "COPPER100-JY26", "COPPER25K-JY26",
    "ALUMINUM1-SE26", "ALUMINUM5-SE26",
    # Energy
    "CRUDE1-AU26", "CRUDE1-JY26",
    "CRUDE10-AU26", "CRUDE10-JY26", "CRUDE10-JY26ID",
    "CRUDE100-AU26", "CRUDE100-JY26", "CRUDE100-JY26ID",
    "CRUDE1000-AU26", "CRUDE1000-JY26", "CRUDE1000-JY26ID",
    "BRENT10-AU26", "BRENT100-AU26", "BRENT1000-AU26",
    "NGAS1K-JY26", "NGAS10K-JY26",
    # Indices
    "NSDQ100-SE26", "MININSDQ100-SE26", "MICRONSDQ100-SE26", "2NSDQ100-SE26",
    "SP500-SE26", "MINISP500-SE26", "MICROSP500-SE26",
    "DJ-SE26",
    "JPYEQTY1-SE26", "JPYEQTY5-SE26",
    # Gold FX
    "GOLDAUDUSD-JY26", "GOLDAUDUSD-JY26ID",
    "GOLDAUDCAD-JY26", "GOLDAUDJPY-JY26",
    "GOLDEURUSD-JY26", "GOLDEURUSD-JY26ID",
    "GOLDEURAUD-JY26", "GOLDEURCAD-JY26", "GOLDEURCHF-JY26",
    "GOLDEURGBP-JY26", "GOLDEURJPY-JY26",
    "GOLDGBPUSD-JY26", "GOLDGBPUSD-JY26ID",
    "GOLDGBPJPY-JY26", "GOLDGBPCHF-JY26",
    "GOLDUSDCAD-JY26", "GOLDUSDCAD-JY26ID",
    "GOLDUSDCHF-JY26", "GOLDUSDCHF-JY26ID",
    "GOLDUSDJPY-JY26", "GOLDUSDJPY-JY26ID",
    "GOLDCHFJPY-JY26",
]