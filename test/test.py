# SPDX-FileCopyrightText: © 2026 Raphael Huang
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

@cocotb.test()
async def test_delta_modulator(dut):
    dut._log.info("Start test_delta_modulator")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0      # data_in
    dut.uio_in.value = 10    # threshold 
    dut.rst_n.value = 0

    # Reset
    dut._log.info("Resetting design")
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Wait for initialization
    await ClockCycles(dut.clk, 2)
    await FallingEdge(dut.clk)

    # 1. Stay silent if within threshold
    dut._log.info("Test case 1: Input stays within threshold")
    dut.ui_in.value = 5 # Error = 5 - 0 = +5. Less than threshold (10).
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    
    # Output spike mapping: uo_out[0] = spike_on, uo_out[1] = spike_off
    assert dut.uo_out[0].value == 0, "Expected spike_on=0"
    assert dut.uo_out[1].value == 0, "Expected spike_off=0"

    # 2. Positive threshold crossed
    dut._log.info("Test case 2: Positive threshold crossed")
    dut.ui_in.value = 15 # Error = 15 - 0 = +15. >= threshold (10).
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    
    # Check outputs: ON spike should be 1
    assert dut.uo_out[0].value == 1, "Expected spike_on=1"
    assert dut.uo_out[1].value == 0, "Expected spike_off=0"

    # Wait another cycle, spikes should deassert since ref_val updated
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.uo_out[0].value == 0, "Expected spike_on=0 after one cycle"
    
    # 3. Negative threshold crossed
    dut._log.info("Test case 3: Negative threshold crossed")
    # Ref val is currently 15
    dut.ui_in.value = 0  # Error = 0 - 15 = -15. <= -threshold (-10).
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.uo_out[0].value == 0, "Expected spike_on=0"
    assert dut.uo_out[1].value == 1, "Expected spike_off=1"

    # 4. Jump drastically
    dut._log.info("Test case 4: Jump drastically to test ref_val update")
    # Flush outputs
    await RisingEdge(dut.clk)
    
    # Ref val is now 0.
    dut.ui_in.value = 200 # Error = 200 - 0 = +200.
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.uo_out[0].value == 1, "Expected spike_on=1"

    # 5. Verify ref_val caught up immediately
    dut._log.info("Test case 5: Verify ref_val caught up")
    # Flush outputs
    await RisingEdge(dut.clk) 
    # Ref val should now be 200. 
    dut.ui_in.value = 195 # Error = 195 - 200 = -5. No spike expected.
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.uo_out[0].value == 0, "Expected spike_on=0, ref_val didn't catch up"
    assert dut.uo_out[1].value == 0, "Expected spike_off=0"

    # 6. Change threshold dynamically
    dut._log.info("Test case 6: Change threshold dynamically")
    # Ref val is still 200, since step 5 didn't cause a spike.
    dut.uio_in.value = 20 # Threshold becomes 20
    dut.ui_in.value = 175 # Error = 175 - 200 = -25. <= -20.
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.uo_out[1].value == 1, "Expected spike_off=1 after dynamically changing threshold"

    dut._log.info("All tests passed!")
