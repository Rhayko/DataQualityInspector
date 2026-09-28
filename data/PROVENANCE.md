# Sample Data Provenance

`sample_manufacturing_quality.csv` is entirely synthetic. It was generated for this portfolio project with `scripts/generate_sample_data.py` using NumPy's random generator with seed `42`; it contains no real company, employee, customer, or operational data.

The fictional dataset represents daily manufacturing inspections across three plants, shifts, and product lines. Most values follow plausible generated distributions. The generator deliberately inserts:

- seven missing cells;
- four invalid typed values (one date and three numeric fields);
- two copied records, creating four rows in duplicate groups;
- several large numeric values for outlier review.

Because the generator is committed, the dataset is reproducible and its limitations are transparent.

