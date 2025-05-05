"""
Transforms eBay TSV rows into Gardner‑friendly CSV.
"""
import csv, pathlib, logging
from logger import get_logger

log = get_logger("transform")

COLUMNS = [
    "orderid", "buyerusername", "transactionprice",
    "shiptoaddressline1", "shiptoaddressline2",
    "shiptocity", "shiptoregion",
    "shiptopostalcode", "shiptocountry"
]

def transform(input_tsv: str) -> str | None:
    out_csv = pathlib.Path(input_tsv).with_suffix(".gardner.csv")
    rows_written = 0

    with open(input_tsv, newline='', encoding='utf-8') as fin:
        reader = csv.DictReader(fin, delimiter='\t')
        if reader.fieldnames is None:
            logging.warning("Input file %s has no header", input_tsv)
            return None
        with open(out_csv, "w", newline='', encoding='utf-8') as fout:
            writer = csv.DictWriter(fout, fieldnames=COLUMNS)
            writer.writeheader()
            for row in reader:
                out = {k: row.get(k, "") for k in COLUMNS}
                out["orderid"] = f"GARDNER-{out['orderid']}"
                writer.writerow(out)
                rows_written += 1

    if rows_written == 0:
        log.info("No orders to transform")
        out_csv.unlink(missing_ok=True)
        return None

    log.info("Transformed %s rows → %s", rows_written, out_csv)
    return str(out_csv)
