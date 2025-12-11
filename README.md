# Introduction to open_fda_drug_label

*open_fda_drug_label* is a python Package leveraging the openFDA API to access label subcategory infromation of the drug dataset. It enables users to gather raw API output returns about drugs, store them in *Drug* objects for ease of data access, and store multiple *Drug* objects together in a *Shelf* for pharmaceutical work. High level functions like *make_drugs* ease the initialization process of *Drug* objects and documentation for all functions is contained in respective files and *help()* functions.

The FDA provides data through an Elasticsearch-based API that provides public FDA data about 3 high level categories: drugs, devices, and foods. Under the drugs category, there are 5 API endpoints: Adverse Events, Product Labeling, NDC Directory, Recall Enforcement Reports, Drugs@FDA, and Drug Shortages. For the purposes of collecting information about drugs documented in public FDA databases, the Product Labeling subcategory is the sole focus of this python package.

The label subset of the openFDA API Drug call allows users to search for drugs according to any of their labeled parameters, with common fields including brand name, ingredients, and risks. However, return format is a raw set of nested dictionaries and lists with large amounts of data available, so this package also works to create data-beneficial objects that make accessing information about complex drugs more accessible for non-technical users.

## Installation

```bash
$ pip install open_fda_drug_label
```

## Usage

- TODO

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`open_fda_drug_label` was created by Leo Jergovic. It is licensed under the terms of the MIT license.

## Credits

`open_fda_drug_label` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
