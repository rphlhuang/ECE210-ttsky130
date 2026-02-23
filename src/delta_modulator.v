/*
 * Copyright (c) 2026 Raphael Huang
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_delta_modulator (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  reg [7:0] current_value;
  reg signed [8:0] threshold;
  reg signed [8:0] signed_current_value, signed_ui_in, error;
  reg [0:0] on_spike_n, on_spike_r, off_spike_n, off_spike_r;

  always @(posedge clk) begin
    if (~rst_n) begin
      current_value <= 8'b0;
    end else if (on_spike_n || off_spike_n) begin
      current_value <= ui_in;
    end else begin
      current_value <= current_value;
    end
    on_spike_r  <= on_spike_n;
    off_spike_r <= off_spike_n;
  end

  always @(*) begin
    threshold = {1'b0, uio_in};
    signed_current_value = {1'b0, current_value};
    signed_ui_in = {1'b0, ui_in};
    error = signed_ui_in - signed_current_value;

    on_spike_n = 1'b0;
    off_spike_n = 1'b0;

    if (error >= threshold) begin
      on_spike_n = 1'b1;
    end else if (error <= -threshold) begin
      off_spike_n = 1'b1;
    end
  end


  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out[0] = on_spike_r;
  assign uo_out[1] = off_spike_r;
  assign uo_out[2] = on_spike_r | off_spike_r;
  assign uo_out[7:3] = 5'b0;

  // Enable input on uio_in
  assign uio_oe = 0;


  // List all unused inputs to prevent warnings
  assign uio_out = '0;
  wire _unused = &{ena};

endmodule
