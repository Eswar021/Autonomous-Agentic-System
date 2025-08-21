You are the **Agent Planner** for NovaMobile Retail.

Return ONLY valid JSON (no fences) that matches this schema:
```json
{
  "goals": ["..."],
  "tools_to_create": [
    {
      "name": "...",
      "description": "Business purpose + exact logic (filters, windows, joins, dedupe), data-quality checks, validations, failure modes, performance notes.",
      "inputs": [],
      "outputs": [{"name":"...","type":"pd.DataFrame","description":"...","schema":"optional"}],
      "datasets": ["..."],
      "assumptions": ["List all hard assumptions explicitly"]
    }
  ],
  "agents_to_create": [
    {
      "name":"...",
      "goal":"Business role & how it moves KPIs using tools",
      "uses_tools":["..."],
      "inputs": [],
      "outputs":[{"name":"summary","type":"markdown"},{"name":"table","type":"pd.DataFrame"}],
      "implementation_notes":"Decision logic, ordering, empty-data handling, minimal facts, thresholds"
    }
  ],
  "runbook": [
    {"agent":"ExistingOrProposedAgentName", "inputs": {} }
  ]
}
```
Authoring rules (MANDATORY)
- Design agents first (roles & handoffs), not tasks.
- Reuse existing zero‑arg tools if they suffice; propose new tools only for real gaps.
- Use ONLY columns present in Dataset Metadata.
- New tools: must read via `tools._paths.find_data_dir(Path(__file__))`, be zero‑arg, compute internal filters (e.g., latest year), return DataFrame.
- Agents must return: summary (markdown), table (DataFrame), facts (dict) and call `agents.base.llm_analyze(context, fallback)`.
- Experiments preferred (A/B, geo-split) over blanket changes.
- Respect constraints: promotions ≤ 15%, transfers ≤ 20%/week, stockout_rate < 2%.

Dataset Selection Rules (MANDATORY)
- Objectives about sales/units/time → prefer sales.csv (via `sales_this_year`) for core performance.
- Use kpi_results.csv for drivers (marketing_spend, competitor_price, inventory_count, stockout_flag, temperature).
- Objectives about reviews/sentiment → prefer reviews.csv (via `reviews_this_year`).

Base Retail Context:
You are the planner for NovaMobile Retail (multi-region mobile-phone retailer).

Business primitives:
- Products: flagship, mid-range, entry-level phones; accessories (chargers, cases, wearables).
- Channels: Stores, Online, Partners.
- Regions: North, South, East, West.
- Constraints: promotions ≤ 15% (VP approval required if higher); inventory transfers ≤ 20%/week; target stockout_rate < 2%.
- Seasonality: Q4 demand spike; heat reduces South footfall in May–June.
- Prefer experiments (A/B, geo-split) over blanket changes.


Planning goal:
- Given an objective, propose the agents and any missing zero‑arg tools they need, then produce a runbook.

Dataset Metadata (AUTO‑DISCOVERED; use only these columns):
{
}

Existing Zero‑Arg Tools:
[
]

Existing Agents:
[
]

### Objective:
increse sales profit

==================== END PLANNER PROMPT ====================



=== PLAN ===
```json
 {
  "goals": [
    "Increase sales profit."
  ],
  "tools_to_create": [
    {
      "name": "kpi_results_this_year",
      "description": "Return kpi_results rows for the most recent year.",
      "inputs": [],
      "outputs": [
        {
          "name": "kpi_results",
          "type": "pd.DataFrame",
          "description": "KPI results for the current year."
        }
      ],
      "datasets": [
        "kpi_results"
      ],
      "assumptions": [
        "kpi_results has date column that can be parsed to datetime object."
      ]
    },
    {
      "name": "product_category_mapping",
      "description": "Creates a mapping between product_id and a product category (flagship, mid-range, entry-level, accessory). The mapping is based on product_id ranges.  The function reads a CSV file containing the mapping from product_id to product category. The file is located in the same directory as the script. Data quality checks: Ensures that product_id is an integer and product_category is a string. Validations: Checks if the product_id is within the defined ranges and the product_category is one of the allowed values. Failure modes: If the CSV file is missing or corrupted, the function returns an empty dictionary. If a product_id is not found in the mapping, it is assigned to 'Unknown'. Performance notes: The function reads the CSV file into a pandas DataFrame and creates a dictionary for fast lookup. The mapping is stored in memory for subsequent calls. The function is optimized for speed and memory usage.",
      "inputs": [],
      "outputs": [
        {
          "name": "product_category_mapping",
          "type": "dict",
          "description": "A dictionary mapping product_id to product category."
        }
      ],
      "datasets": [],
      "assumptions": [
        "A CSV file named 'product_category_mapping.csv' exists in the same directory as the script, containing the mapping between product_id and product category.",
        "The CSV file has two columns: 'product_id' and 'product_category'.",
        "The 'product_id' column contains integer values.",
        "The 'product_category' column contains string values representing the product category (e.g., 'flagship', 'mid-range', 'entry-level', 'accessory')."
      ]
    }
  ],
  "agents_to_create": [
    {
      "name": "ProfitDriverAnalyst",
      "goal": "Identify key drivers of profit (revenue - cost) by analyzing KPIs, including marketing spend, competitor price, inventory, and stockouts. The agent will use the kpi_results data to understand the relationship between these factors and profit, and make recommendations on how to optimize these factors to increase profit. It will also consider product categories.",
      "uses_tools": [
        "kpi_results_this_year",
        "product_category_mapping"
      ],
      "inputs": [],
      "outputs": [
        {
          "name": "summary",
          "type": "markdown"
        },
        {
          "name": "table",
          "type": "pd.DataFrame"
        }
      ],
      "implementation_notes": "The agent will calculate profit as revenue - cost. Cost will be estimated based on inventory count and a fixed cost per unit. The agent will analyze the correlation between marketing spend, competitor price, inventory, stockout_flag, temperature, and profit. It will identify the factors that have the strongest positive and negative correlation with profit. The agent will also analyze the impact of product category on profit. Decision logic: Prioritize factors with the strongest positive correlation with profit. Recommend increasing marketing spend for products with high profit margins. Recommend reducing inventory for products with low profit margins. Recommend adjusting prices to be competitive with competitors. Ordering: Analyze correlation, then analyze product category impact, then generate recommendations. Empty-data handling: If any of the required data is missing, the agent will return an error message. Minimal facts: The agent will return the correlation coefficients between the factors and profit, the average profit by product category, and the recommendations. Thresholds: The agent will use a threshold of 0.5 for the correlation coefficient to identify strong correlations."
    }
  ],
  "runbook": [
    {
      "agent": "ProfitDriverAnalyst",
      "inputs": {}
    }
  ]
}
```

==================== DEBUG: TOOL CODEGEN PROMPT ====================

You will return a **single Python module** for a **ZERO‑ARG tool** in this NovaMobile Retail codebase.

Output ONLY valid JSON:
{
  "filename": "snake_case_filename.py",
  "code": "<FULL PYTHON MODULE CODE>"
}

Constraints:
- The function must be zero‑arg and named exactly kpi_results_this_year().
- Return type: pandas.DataFrame.
- MUST import: `from tools._paths import find_data_dir` and do: `data_dir = find_data_dir(Path(__file__))`.
- Read CSVs ONLY from `data_dir` (sales.csv, reviews.csv, customers.csv, kpi_results.csv).
- Never hard‑code absolute paths.
- Parse dates after read: `df['date'] = pd.to_datetime(df['date'], errors='coerce')` (and for `review_date` if used).
- Join only if key columns exist and make business sense (e.g., sales.customer_id ↔ customers.customer_id).
- Compute internal filters (e.g., most recent year) — ZERO ARGS.
- No prints; clean, lint‑safe Python.
- Do **NOT** pass unexpected parameters to pandas APIs (no `errors=` on `read_csv`); do **NOT** use deprecated `date_parser`.
- Prefer canonical aggregation field names where sensible: `revenue`, `sales_units`, `average_price`, `stockout_rate`.
- If a needed column is missing, compute a safe fallback (e.g., `stockout_rate` from `stockout_flag`).

Context:
- Tool spec (freeform): Return kpi_results rows for the most recent year.
- Datasets & columns (JSON): {
  "customers": {
    "name": "customers",
    "path": "D:\\Zenith AI\\DB\\data\\customers.csv",
    "columns": [
      "customer_id",
      "region",
      "customer_type",
      "loyalty_years",
      "income_bracket"
    ],
    "dtypes": {
      "customer_id": "int64",
      "region": "object",
      "customer_type": "object",
      "loyalty_years": "int64",
      "income_bracket": "object"
    },
    "examples": {
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "region": [
        "North",
        "South",
        "East"
      ],
      "customer_type": [
        "Premium",
        "Standard",
        "New"
      ],
      "loyalty_years": [
        3,
        1,
        5
      ],
      "income_bracket": [
        "50K-100K",
        "<50K",
        ">100K"
      ]
    },
    "descriptions": {
      "customer_id": "Unique customer identifier.",
      "region": "Sales/Customer geographic region.",
      "customer_type": "'customer_type' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "loyalty_years": "'loyalty_years' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "income_bracket": "'income_bracket' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "customer_id": 1001,
        "region": "North",
        "customer_type": "Premium",
        "loyalty_years": 3,
        "income_bracket": "50K-100K"
      },
      {
        "customer_id": 1002,
        "region": "South",
        "customer_type": "Standard",
        "loyalty_years": 1,
        "income_bracket": "<50K"
      },
      {
        "customer_id": 1003,
        "region": "East",
        "customer_type": "Premium",
        "loyalty_years": 5,
        "income_bracket": ">100K"
      }
    ],
    "row_count_estimate": null
  },
  "kpi_results": {
    "name": "kpi_results",
    "path": "D:\\Zenith AI\\DB\\data\\kpi_results.csv",
    "columns": [
      "date",
      "product_id",
      "region",
      "sales_units",
      "revenue",
      "marketing_spend",
      "competitor_price",
      "inventory_count",
      "stockout_flag",
      "temperature"
    ],
    "dtypes": {
      "date": "object",
      "product_id": "object",
      "region": "object",
      "sales_units": "int64",
      "revenue": "float64",
      "marketing_spend": "int64",
      "competitor_price": "float64",
      "inventory_count": "int64",
      "stockout_flag": "int64",
      "temperature": "float64"
    },
    "examples": {
      "date": [
        "2023-01-01",
        "2023-01-08",
        "2023-01-15"
      ],
      "product_id": [
        "P1001",
        "P1002"
      ],
      "region": [
        "North",
        "South"
      ],
      "sales_units": [
        342,
        198,
        415
      ],
      "revenue": [
        5130.0,
        2970.0,
        6225.0
      ],
      "marketing_spend": [
        1200,
        800,
        1500
      ],
      "competitor_price": [
        24.99,
        19.99,
        23.5
      ],
      "inventory_count": [
        550,
        320,
        210
      ],
      "stockout_flag": [
        0,
        1
      ],
      "temperature": [
        12.4,
        -3.2,
        18.7
      ]
    },
    "descriptions": {
      "date": "Calendar date for the record (parseable to datetime).",
      "product_id": "Unique product identifier.",
      "region": "Sales/Customer geographic region.",
      "sales_units": "Units sold during the period (aggregated).",
      "revenue": "Sales revenue for the row/period (local currency).",
      "marketing_spend": "Marketing spend for the row/period (local currency).",
      "competitor_price": "Observed competitor price level.",
      "inventory_count": "Available inventory units at row time.",
      "stockout_flag": "1 if stockout occurred on the row date, else 0.",
      "temperature": "Ambient temperature for the row location/date."
    },
    "sample_rows": [
      {
        "date": "2023-01-01",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 342,
        "revenue": 5130.0,
        "marketing_spend": 1200,
        "competitor_price": 24.99,
        "inventory_count": 550,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-01",
        "product_id": "P1002",
        "region": "North",
        "sales_units": 198,
        "revenue": 2970.0,
        "marketing_spend": 800,
        "competitor_price": 19.99,
        "inventory_count": 320,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-08",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 415,
        "revenue": 6225.0,
        "marketing_spend": 1500,
        "competitor_price": 23.5,
        "inventory_count": 210,
        "stockout_flag": 1,
        "temperature": -3.2
      }
    ],
    "row_count_estimate": null
  },
  "reviews": {
    "name": "reviews",
    "path": "D:\\Zenith AI\\DB\\data\\reviews.csv",
    "columns": [
      "review_id",
      "product_id",
      "customer_id",
      "review_text",
      "rating",
      "review_date"
    ],
    "dtypes": {
      "review_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "review_text": "object",
      "rating": "int64",
      "review_date": "object"
    },
    "examples": {
      "review_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "review_text": [
        "Great value for money",
        "Premium quality but expensive",
        "Works as expected"
      ],
      "rating": [
        4,
        3,
        5
      ],
      "review_date": [
        "2023-01-10",
        "2023-01-20",
        "2023-01-25"
      ]
    },
    "descriptions": {
      "review_id": "'review_id' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "review_text": "Free\u2011text customer review content.",
      "rating": "Customer review rating (e.g., 1\u20135).",
      "review_date": "'review_date' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "review_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "review_text": "Great value for money",
        "rating": 4,
        "review_date": "2023-01-10"
      },
      {
        "review_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "review_text": "Premium quality but expensive",
        "rating": 3,
        "review_date": "2023-01-20"
      },
      {
        "review_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "review_text": "Works as expected",
        "rating": 3,
        "review_date": "2023-01-25"
      }
    ],
    "row_count_estimate": null
  },
  "sales": {
    "name": "sales",
    "path": "D:\\Zenith AI\\DB\\data\\sales.csv",
    "columns": [
      "order_id",
      "product_id",
      "customer_id",
      "date",
      "quantity",
      "price"
    ],
    "dtypes": {
      "order_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "date": "object",
      "quantity": "int64",
      "price": "float64"
    },
    "examples": {
      "order_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "date": [
        "2023-01-05",
        "2023-01-12",
        "2023-01-18"
      ],
      "quantity": [
        2,
        1,
        3
      ],
      "price": [
        15.99,
        29.99,
        45.0
      ]
    },
    "descriptions": {
      "order_id": "Unique sales order identifier.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "date": "Calendar date for the record (parseable to datetime).",
      "quantity": "Units sold in the transaction.",
      "price": "Unit price at time of sale (local currency)."
    },
    "sample_rows": [
      {
        "order_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "date": "2023-01-05",
        "quantity": 2,
        "price": 15.99
      },
      {
        "order_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "date": "2023-01-12",
        "quantity": 1,
        "price": 29.99
      },
      {
        "order_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "date": "2023-01-18",
        "quantity": 3,
        "price": 15.99
      }
    ],
    "row_count_estimate": null
  }
}
- Existing tools (names): reviews_this_year, sales_this_year

==================== END TOOL CODEGEN PROMPT ====================


Wrote: d:\Zenith AI\MAS_UseCase_V3\created_tools\kpi_results_this_year.py


==================== DEBUG: TOOL CODEGEN PROMPT ====================

You will return a **single Python module** for a **ZERO‑ARG tool** in this NovaMobile Retail codebase.

Output ONLY valid JSON:
{
  "filename": "snake_case_filename.py",
  "code": "<FULL PYTHON MODULE CODE>"
}

Constraints:
- The function must be zero‑arg and named exactly product_category_mapping().
- Return type: pandas.DataFrame.
- MUST import: `from tools._paths import find_data_dir` and do: `data_dir = find_data_dir(Path(__file__))`.
- Read CSVs ONLY from `data_dir` (sales.csv, reviews.csv, customers.csv, kpi_results.csv).
- Never hard‑code absolute paths.
- Parse dates after read: `df['date'] = pd.to_datetime(df['date'], errors='coerce')` (and for `review_date` if used).
- Join only if key columns exist and make business sense (e.g., sales.customer_id ↔ customers.customer_id).
- Compute internal filters (e.g., most recent year) — ZERO ARGS.
- No prints; clean, lint‑safe Python.
- Do **NOT** pass unexpected parameters to pandas APIs (no `errors=` on `read_csv`); do **NOT** use deprecated `date_parser`.
- Prefer canonical aggregation field names where sensible: `revenue`, `sales_units`, `average_price`, `stockout_rate`.
- If a needed column is missing, compute a safe fallback (e.g., `stockout_rate` from `stockout_flag`).

Context:
- Tool spec (freeform): Creates a mapping between product_id and a product category (flagship, mid-range, entry-level, accessory). The mapping is based on product_id ranges.  The function reads a CSV file containing the mapping from product_id to product category. The file is located in the same directory as the script. Data quality checks: Ensures that product_id is an integer and product_category is a string. Validations: Checks if the product_id is within the defined ranges and the product_category is one of the allowed values. Failure modes: If the CSV file is missing or corrupted, the function returns an empty dictionary. If a product_id is not found in the mapping, it is assigned to 'Unknown'. Performance notes: The function reads the CSV file into a pandas DataFrame and creates a dictionary for fast lookup. The mapping is stored in memory for subsequent calls. The function is optimized for speed and memory usage.
- Datasets & columns (JSON): {
  "customers": {
    "name": "customers",
    "path": "D:\\Zenith AI\\DB\\data\\customers.csv",
    "columns": [
      "customer_id",
      "region",
      "customer_type",
      "loyalty_years",
      "income_bracket"
    ],
    "dtypes": {
      "customer_id": "int64",
      "region": "object",
      "customer_type": "object",
      "loyalty_years": "int64",
      "income_bracket": "object"
    },
    "examples": {
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "region": [
        "North",
        "South",
        "East"
      ],
      "customer_type": [
        "Premium",
        "Standard",
        "New"
      ],
      "loyalty_years": [
        3,
        1,
        5
      ],
      "income_bracket": [
        "50K-100K",
        "<50K",
        ">100K"
      ]
    },
    "descriptions": {
      "customer_id": "Unique customer identifier.",
      "region": "Sales/Customer geographic region.",
      "customer_type": "'customer_type' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "loyalty_years": "'loyalty_years' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "income_bracket": "'income_bracket' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "customer_id": 1001,
        "region": "North",
        "customer_type": "Premium",
        "loyalty_years": 3,
        "income_bracket": "50K-100K"
      },
      {
        "customer_id": 1002,
        "region": "South",
        "customer_type": "Standard",
        "loyalty_years": 1,
        "income_bracket": "<50K"
      },
      {
        "customer_id": 1003,
        "region": "East",
        "customer_type": "Premium",
        "loyalty_years": 5,
        "income_bracket": ">100K"
      }
    ],
    "row_count_estimate": null
  },
  "kpi_results": {
    "name": "kpi_results",
    "path": "D:\\Zenith AI\\DB\\data\\kpi_results.csv",
    "columns": [
      "date",
      "product_id",
      "region",
      "sales_units",
      "revenue",
      "marketing_spend",
      "competitor_price",
      "inventory_count",
      "stockout_flag",
      "temperature"
    ],
    "dtypes": {
      "date": "object",
      "product_id": "object",
      "region": "object",
      "sales_units": "int64",
      "revenue": "float64",
      "marketing_spend": "int64",
      "competitor_price": "float64",
      "inventory_count": "int64",
      "stockout_flag": "int64",
      "temperature": "float64"
    },
    "examples": {
      "date": [
        "2023-01-01",
        "2023-01-08",
        "2023-01-15"
      ],
      "product_id": [
        "P1001",
        "P1002"
      ],
      "region": [
        "North",
        "South"
      ],
      "sales_units": [
        342,
        198,
        415
      ],
      "revenue": [
        5130.0,
        2970.0,
        6225.0
      ],
      "marketing_spend": [
        1200,
        800,
        1500
      ],
      "competitor_price": [
        24.99,
        19.99,
        23.5
      ],
      "inventory_count": [
        550,
        320,
        210
      ],
      "stockout_flag": [
        0,
        1
      ],
      "temperature": [
        12.4,
        -3.2,
        18.7
      ]
    },
    "descriptions": {
      "date": "Calendar date for the record (parseable to datetime).",
      "product_id": "Unique product identifier.",
      "region": "Sales/Customer geographic region.",
      "sales_units": "Units sold during the period (aggregated).",
      "revenue": "Sales revenue for the row/period (local currency).",
      "marketing_spend": "Marketing spend for the row/period (local currency).",
      "competitor_price": "Observed competitor price level.",
      "inventory_count": "Available inventory units at row time.",
      "stockout_flag": "1 if stockout occurred on the row date, else 0.",
      "temperature": "Ambient temperature for the row location/date."
    },
    "sample_rows": [
      {
        "date": "2023-01-01",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 342,
        "revenue": 5130.0,
        "marketing_spend": 1200,
        "competitor_price": 24.99,
        "inventory_count": 550,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-01",
        "product_id": "P1002",
        "region": "North",
        "sales_units": 198,
        "revenue": 2970.0,
        "marketing_spend": 800,
        "competitor_price": 19.99,
        "inventory_count": 320,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-08",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 415,
        "revenue": 6225.0,
        "marketing_spend": 1500,
        "competitor_price": 23.5,
        "inventory_count": 210,
        "stockout_flag": 1,
        "temperature": -3.2
      }
    ],
    "row_count_estimate": null
  },
  "reviews": {
    "name": "reviews",
    "path": "D:\\Zenith AI\\DB\\data\\reviews.csv",
    "columns": [
      "review_id",
      "product_id",
      "customer_id",
      "review_text",
      "rating",
      "review_date"
    ],
    "dtypes": {
      "review_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "review_text": "object",
      "rating": "int64",
      "review_date": "object"
    },
    "examples": {
      "review_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "review_text": [
        "Great value for money",
        "Premium quality but expensive",
        "Works as expected"
      ],
      "rating": [
        4,
        3,
        5
      ],
      "review_date": [
        "2023-01-10",
        "2023-01-20",
        "2023-01-25"
      ]
    },
    "descriptions": {
      "review_id": "'review_id' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "review_text": "Free\u2011text customer review content.",
      "rating": "Customer review rating (e.g., 1\u20135).",
      "review_date": "'review_date' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "review_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "review_text": "Great value for money",
        "rating": 4,
        "review_date": "2023-01-10"
      },
      {
        "review_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "review_text": "Premium quality but expensive",
        "rating": 3,
        "review_date": "2023-01-20"
      },
      {
        "review_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "review_text": "Works as expected",
        "rating": 3,
        "review_date": "2023-01-25"
      }
    ],
    "row_count_estimate": null
  },
  "sales": {
    "name": "sales",
    "path": "D:\\Zenith AI\\DB\\data\\sales.csv",
    "columns": [
      "order_id",
      "product_id",
      "customer_id",
      "date",
      "quantity",
      "price"
    ],
    "dtypes": {
      "order_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "date": "object",
      "quantity": "int64",
      "price": "float64"
    },
    "examples": {
      "order_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "date": [
        "2023-01-05",
        "2023-01-12",
        "2023-01-18"
      ],
      "quantity": [
        2,
        1,
        3
      ],
      "price": [
        15.99,
        29.99,
        45.0
      ]
    },
    "descriptions": {
      "order_id": "Unique sales order identifier.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "date": "Calendar date for the record (parseable to datetime).",
      "quantity": "Units sold in the transaction.",
      "price": "Unit price at time of sale (local currency)."
    },
    "sample_rows": [
      {
        "order_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "date": "2023-01-05",
        "quantity": 2,
        "price": 15.99
      },
      {
        "order_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "date": "2023-01-12",
        "quantity": 1,
        "price": 29.99
      },
      {
        "order_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "date": "2023-01-18",
        "quantity": 3,
        "price": 15.99
      }
    ],
    "row_count_estimate": null
  }
}
- Existing tools (names): reviews_this_year, sales_this_year

==================== END TOOL CODEGEN PROMPT ====================


Wrote: d:\Zenith AI\MAS_UseCase_V3\created_tools\product_category_mapping.py


==================== DEBUG: AGENT CODEGEN PROMPT (ProfitDriverAnalyst) ====================

You will return a **single Python module** defining a ZERO‑ARG Agent class that calls one or more ZERO‑ARG tools
and then asks an LLM to analyze via `agents.base.llm_analyze(context, fallback)`.

Output ONLY valid JSON:
{
  "filename": "ClassName.py",
  "code": "<FULL PYTHON MODULE CODE>"
}

Constraints:
- Class name must be exactly ProfitDriverAnalyst.
- __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None)
- run(self) -> Dict[str, Any] MUST return: summary (markdown str), table (pd.DataFrame), facts (dict).
- Import helper: `from agents.base import llm_analyze`.
- Import zero‑arg tools by name:
  - Tools listed under **new_tool_names** MUST be imported from `created_tools.<snake_file>`.
  - All other tools MUST be imported from `tools.<snake_file>`.
- Facts must include minimal numeric aggregates (e.g., totals/means).
- Only pandas + stdlib; no scipy/stats.
- Never call non‑existent DataFrame methods like `.use()`.
- After loading a DataFrame, ensure expected columns exist; if not, create them and coerce numerics:
  for col in ["revenue","sales_units","average_price","stockout_rate"]:
      if col not in df.columns: df[col] = pd.NA
      df[col] = pd.to_numeric(df[col], errors="coerce")
- Call pattern (MANDATORY):
    context = {"objective": self.objective, "memory": self.memory, "facts": facts}
    summary_md = llm_analyze(context, fallback)

NovaMobile Retail context applies (datasets: sales, reviews, customers, kpi_results; constraints: promo ≤15%, transfer ≤20%/wk, stockout <2%).

Inputs to the generator:
- Agent goal: Identify key drivers of profit (revenue - cost) by analyzing KPIs, including marketing spend, competitor price, inventory, and stockouts. The agent will use the kpi_results data to understand the relationship between these factors and profit, and make recommendations on how to optimize these factors to increase profit. It will also consider product categories.
- Tools to use (comma delimited names): kpi_results_this_year, product_category_mapping
- Datasets metadata (JSON): {
  "customers": {
    "name": "customers",
    "path": "D:\\Zenith AI\\DB\\data\\customers.csv",
    "columns": [
      "customer_id",
      "region",
      "customer_type",
      "loyalty_years",
      "income_bracket"
    ],
    "dtypes": {
      "customer_id": "int64",
      "region": "object",
      "customer_type": "object",
      "loyalty_years": "int64",
      "income_bracket": "object"
    },
    "examples": {
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "region": [
        "North",
        "South",
        "East"
      ],
      "customer_type": [
        "Premium",
        "Standard",
        "New"
      ],
      "loyalty_years": [
        3,
        1,
        5
      ],
      "income_bracket": [
        "50K-100K",
        "<50K",
        ">100K"
      ]
    },
    "descriptions": {
      "customer_id": "Unique customer identifier.",
      "region": "Sales/Customer geographic region.",
      "customer_type": "'customer_type' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "loyalty_years": "'loyalty_years' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "income_bracket": "'income_bracket' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "customer_id": 1001,
        "region": "North",
        "customer_type": "Premium",
        "loyalty_years": 3,
        "income_bracket": "50K-100K"
      },
      {
        "customer_id": 1002,
        "region": "South",
        "customer_type": "Standard",
        "loyalty_years": 1,
        "income_bracket": "<50K"
      },
      {
        "customer_id": 1003,
        "region": "East",
        "customer_type": "Premium",
        "loyalty_years": 5,
        "income_bracket": ">100K"
      }
    ],
    "row_count_estimate": null
  },
  "kpi_results": {
    "name": "kpi_results",
    "path": "D:\\Zenith AI\\DB\\data\\kpi_results.csv",
    "columns": [
      "date",
      "product_id",
      "region",
      "sales_units",
      "revenue",
      "marketing_spend",
      "competitor_price",
      "inventory_count",
      "stockout_flag",
      "temperature"
    ],
    "dtypes": {
      "date": "object",
      "product_id": "object",
      "region": "object",
      "sales_units": "int64",
      "revenue": "float64",
      "marketing_spend": "int64",
      "competitor_price": "float64",
      "inventory_count": "int64",
      "stockout_flag": "int64",
      "temperature": "float64"
    },
    "examples": {
      "date": [
        "2023-01-01",
        "2023-01-08",
        "2023-01-15"
      ],
      "product_id": [
        "P1001",
        "P1002"
      ],
      "region": [
        "North",
        "South"
      ],
      "sales_units": [
        342,
        198,
        415
      ],
      "revenue": [
        5130.0,
        2970.0,
        6225.0
      ],
      "marketing_spend": [
        1200,
        800,
        1500
      ],
      "competitor_price": [
        24.99,
        19.99,
        23.5
      ],
      "inventory_count": [
        550,
        320,
        210
      ],
      "stockout_flag": [
        0,
        1
      ],
      "temperature": [
        12.4,
        -3.2,
        18.7
      ]
    },
    "descriptions": {
      "date": "Calendar date for the record (parseable to datetime).",
      "product_id": "Unique product identifier.",
      "region": "Sales/Customer geographic region.",
      "sales_units": "Units sold during the period (aggregated).",
      "revenue": "Sales revenue for the row/period (local currency).",
      "marketing_spend": "Marketing spend for the row/period (local currency).",
      "competitor_price": "Observed competitor price level.",
      "inventory_count": "Available inventory units at row time.",
      "stockout_flag": "1 if stockout occurred on the row date, else 0.",
      "temperature": "Ambient temperature for the row location/date."
    },
    "sample_rows": [
      {
        "date": "2023-01-01",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 342,
        "revenue": 5130.0,
        "marketing_spend": 1200,
        "competitor_price": 24.99,
        "inventory_count": 550,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-01",
        "product_id": "P1002",
        "region": "North",
        "sales_units": 198,
        "revenue": 2970.0,
        "marketing_spend": 800,
        "competitor_price": 19.99,
        "inventory_count": 320,
        "stockout_flag": 0,
        "temperature": 12.4
      },
      {
        "date": "2023-01-08",
        "product_id": "P1001",
        "region": "North",
        "sales_units": 415,
        "revenue": 6225.0,
        "marketing_spend": 1500,
        "competitor_price": 23.5,
        "inventory_count": 210,
        "stockout_flag": 1,
        "temperature": -3.2
      }
    ],
    "row_count_estimate": null
  },
  "reviews": {
    "name": "reviews",
    "path": "D:\\Zenith AI\\DB\\data\\reviews.csv",
    "columns": [
      "review_id",
      "product_id",
      "customer_id",
      "review_text",
      "rating",
      "review_date"
    ],
    "dtypes": {
      "review_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "review_text": "object",
      "rating": "int64",
      "review_date": "object"
    },
    "examples": {
      "review_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "review_text": [
        "Great value for money",
        "Premium quality but expensive",
        "Works as expected"
      ],
      "rating": [
        4,
        3,
        5
      ],
      "review_date": [
        "2023-01-10",
        "2023-01-20",
        "2023-01-25"
      ]
    },
    "descriptions": {
      "review_id": "'review_id' column; auto\u2011discovered. Provide semantics in docs if critical.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "review_text": "Free\u2011text customer review content.",
      "rating": "Customer review rating (e.g., 1\u20135).",
      "review_date": "'review_date' column; auto\u2011discovered. Provide semantics in docs if critical."
    },
    "sample_rows": [
      {
        "review_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "review_text": "Great value for money",
        "rating": 4,
        "review_date": "2023-01-10"
      },
      {
        "review_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "review_text": "Premium quality but expensive",
        "rating": 3,
        "review_date": "2023-01-20"
      },
      {
        "review_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "review_text": "Works as expected",
        "rating": 3,
        "review_date": "2023-01-25"
      }
    ],
    "row_count_estimate": null
  },
  "sales": {
    "name": "sales",
    "path": "D:\\Zenith AI\\DB\\data\\sales.csv",
    "columns": [
      "order_id",
      "product_id",
      "customer_id",
      "date",
      "quantity",
      "price"
    ],
    "dtypes": {
      "order_id": "int64",
      "product_id": "int64",
      "customer_id": "int64",
      "date": "object",
      "quantity": "int64",
      "price": "float64"
    },
    "examples": {
      "order_id": [
        1,
        2,
        3
      ],
      "product_id": [
        101,
        102,
        103
      ],
      "customer_id": [
        1001,
        1002,
        1003
      ],
      "date": [
        "2023-01-05",
        "2023-01-12",
        "2023-01-18"
      ],
      "quantity": [
        2,
        1,
        3
      ],
      "price": [
        15.99,
        29.99,
        45.0
      ]
    },
    "descriptions": {
      "order_id": "Unique sales order identifier.",
      "product_id": "Unique product identifier.",
      "customer_id": "Unique customer identifier.",
      "date": "Calendar date for the record (parseable to datetime).",
      "quantity": "Units sold in the transaction.",
      "price": "Unit price at time of sale (local currency)."
    },
    "sample_rows": [
      {
        "order_id": 1,
        "product_id": 101,
        "customer_id": 1001,
        "date": "2023-01-05",
        "quantity": 2,
        "price": 15.99
      },
      {
        "order_id": 2,
        "product_id": 102,
        "customer_id": 1002,
        "date": "2023-01-12",
        "quantity": 1,
        "price": 29.99
      },
      {
        "order_id": 3,
        "product_id": 101,
        "customer_id": 1003,
        "date": "2023-01-18",
        "quantity": 3,
        "price": 15.99
      }
    ],
    "row_count_estimate": null
  }
}
- ALL available zero‑arg tools (names): kpi_results_this_year, product_category_mapping, reviews_this_year, sales_this_year, west_kpi_this_year
- Newly created tool names (names): kpi_results_this_year, product_category_mapping, west_kpi_this_year

==================== END AGENT CODEGEN PROMPT (ProfitDriverAnalyst) ====================


Wrote: d:\Zenith AI\MAS_UseCase_V3\created_agents\ProfitDriverAnalyst.py