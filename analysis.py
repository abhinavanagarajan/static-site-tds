# 23f2000898@ds.study.iitm.ac.in
# Marimo interactive notebook demonstrating variable relationships

import marimo

app = marimo.App(width="medium")


@app.cell
def __():
    """
    Cell 1: Imports and base dataset
    This cell defines the raw data used by other cells.
    Data flow: `data` is consumed by downstream cells.
    """
    import numpy as np
    return np,


@app.cell
def __(np):
    """
    Cell 2: Dataset creation
    Data flow: Creates a dataset that depends on numpy from Cell 1.
    """
    x = np.linspace(0, 10, 50)  # independent variable
    y = 2 * x + 1              # dependent variable
    return x, y


@app.cell
def __(marimo):
    """
    Cell 3: Interactive widget
    Data flow: Slider value is used to modify the relationship in later cells.
    """
    slider = marimo.ui.slider(
        start=0,
        stop=5,
        step=0.1,
        value=2,
        label="Slope (multiplier)"
    )
    slider


@app.cell
def __(x, y, slider, marimo):
    """
    Cell 4: Dynamic computation
    Data flow: Uses `x` from Cell 2 and `slider.value` from Cell 3.
    """
    adjusted_y = slider.value * x + 1
    return adjusted_y,


@app.cell
def __(slider, marimo):
    """
    Cell 5: Dynamic markdown output
    Data flow: Markdown depends on the slider's current value.
    """
    marimo.md(
        f"""
        ### Interactive Relationship

        The current **slope value** selected is: **{slider.value}**

        Changing the slider updates the dependent variable dynamically.
        """
    )
