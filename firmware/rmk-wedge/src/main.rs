//! Seven Swords Wedge keyboard firmware. Everything comes from keyboard.toml via RMK's macro.
#![no_main]
#![no_std]

use rmk::macros::rmk_keyboard;

#[rmk_keyboard]
mod keyboard {}
