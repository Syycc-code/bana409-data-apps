# BANA409 Data Apps

Two Streamlit apps for the BANA409 Data App lesson, using the course-provided datasets.

## Run locally

Install Python 3.14 and uv, then run one app at a time:

```sh
uv sync
uv run streamlit run app-cities.py
uv run streamlit run app-housing.py
```

The cities app provides a population slider, capital multi-select, country form, map, table, and country population bar chart. Cities without a capital designation remain selectable as “Not a capital”.

The housing app provides the required price slider (0–500001; default 200000), location multi-select, income radio buttons, map, and 30-bin histogram. Income groups are Low ≤ 2.5, Medium > 2.5 and < 4.5, and High ≥ 4.5. Both apps handle empty selections without a chart error.

## Deploy

Publish these project files to a public GitHub repository, excluding `.venv`. In Streamlit Community Cloud, create two apps from the same repository with entrypoints `app-cities.py` and `app-housing.py`. Set Python to **3.14** in Advanced settings. Cloud installs dependencies from `uv.lock`.

## Learn the flow

1. Pandas reads a CSV into a dataframe.
2. Widgets return the values selected by the user.
3. Boolean conditions select matching rows.
4. Streamlit displays the filtered rows on a map and Matplotlib draws the chart.
5. Ordinary widget changes rerun the entire script. The country form applies changes only when Apply is clicked.

Course sources:
- https://bana409.harrywang.me/docs/lectures/data-app/data-app-tutorial
- https://bana409.harrywang.me/docs/lectures/data-app/data-app-lab

The housing lab is an in-class activity with nothing to submit. The housing data describes California districts in 1990; it is not current real-estate data.


## Assignment 4 — IndieScope

The individual Steam competitor discovery dashboard is in [`indiescope/`](indiescope/). Its [design README](indiescope/README.md) explains the decision-maker, display choices, exclusions and refresh proposal. Deploy `indiescope/app.py` with Python 3.14. Original city and housing apps remain available.


IndieScope live app: https://bana409-indiescope-syycc.streamlit.app/
