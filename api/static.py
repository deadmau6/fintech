# class IEX_SECTOR_MAP:
#         other="Other Services (except Public Administration)"
#         commercial="Commercial Services"
#         retail="Retail Trade"
#         distribution="Distribution Services"
#         process="Process Industries"
#         professional="Professional, Scientific, and Technical Services"
#         wholesale="Wholesale Trade"
#         admin="Administrative and Support and Waste Management and Remediation Services"
#         tech="Technology Services"
#         education="Educational Services"
#         durables="Consumer Durables"
#         misc="Miscellaneous"
#         gov="Government"
#         real_estate="Real Estate and Rental and Leasing"
#         non_durables="Consumer Non-Durables"
#         communications="Communications"
#         health="Health Services"
#         finance="Finance"
#         producer="Producer Manufacturing"
#         manufacturing="Manufacturing"
#         info="Information"
#         health_care="Health Care and Social Assistance"
#         transportation="Transportation"
#         ag="Agriculture, Forestry, Fishing and Hunting"
#         "Accommodation and Food Services"
#         "Energy Minerals"
#         "Health Technology"
#         "Construction"
#         "Public Administration"
#         "Arts, Entertainment, and Recreation"
#         "Mining, Quarrying, and Oil and Gas Extraction"
#         "Consumer Services"
#         "Finance and Insurance"
#         "Utilities"
#         "Management of Companies and Enterprises"
#         "Non-Energy Minerals"
#         "Electronic Technology"
#         "Transportation and Warehousing"
#         "Industrial Services"

IEX_SECTORS = set([
    "Other Services (except Public Administration)",
    "Commercial Services",
    "Retail Trade",
    "Distribution Services",
    "Process Industries",
    "Professional, Scientific, and Technical Services",
    "Wholesale Trade",
    "Administrative and Support and Waste Management and Remediation Services",
    "Technology Services",
    "Educational Services",
    "Consumer Durables",
    "Miscellaneous",
    "Government",
    "Real Estate and Rental and Leasing",
    "Consumer Non-Durables",
    "Communications",
    "Health Services",
    "Finance",
    "Producer Manufacturing",
    "Manufacturing",
    "Information",
    "Health Care and Social Assistance",
    "Transportation",
    "Agriculture, Forestry, Fishing and Hunting",
    "Accommodation and Food Services",
    "Energy Minerals",
    "Health Technology",
    "Construction",
    "Public Administration",
    "Arts, Entertainment, and Recreation",
    "Mining, Quarrying, and Oil and Gas Extraction",
    "Consumer Services",
    "Finance and Insurance",
    "Utilities",
    "Management of Companies and Enterprises",
    "Non-Energy Minerals",
    "Electronic Technology",
    "Transportation and Warehousing",
    "Industrial Services"
])
IEX_ISSUE_TYPES = set(['ad', 'cs', 'cef', 'et', 'oef',
                      'ps', 'rt', 'struct', 'ut', 'wi', 'wt', 'empty'])

ANUAL_TO_DAILY_DRIFT = {
    0.01: 0.000040,
    0.0126: 0.000050,
    0.02: 0.000079,
    0.0252: 0.000100,
    0.03: 0.000119,
    0.0378: 0.000150,
    0.04: 0.000159,
    0.05: 0.000198,
    0.0504: 0.000200,
    0.06: 0.000238,
    0.0630: 0.000250,
    0.07: 0.000278,
    0.0756: 0.000300,
    0.08: 0.000317,
    0.0882: 0.000350,
    0.09: 0.000357,
    0.10: 0.000397,
    0.1008: 0.000400,
    0.11: 0.000437,
    0.1134: 0.000450,
    0.12: 0.000476,
    0.1260: 0.000500,
    0.13: 0.000516,
    0.1386: 0.000550,
    0.14: 0.000556,
    0.15: 0.000595,
    0.1512: 0.000600,
    0.16: 0.000635,
    0.1638: 0.000650,
    0.17: 0.000675,
    0.1764: 0.000700,
    0.18: 0.000714,
    0.1890: 0.000750,
    0.19: 0.000754,
    0.20: 0.000794,
    0.2016: 0.000800,
    0.2142: 0.000850,
    0.2268: 0.000900,
    0.2394: 0.000950,
}
