<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Input data (`ui_in`) is passed through a delta modulator, which outputs on/off spikes (`uo_out[0]` and `uo_out[1]`) based on the input data. The threshold can be dynamically changed (`uio_in`).

## How to test

Run `make` in test/ to run the testbench.

## External hardware

N/A.