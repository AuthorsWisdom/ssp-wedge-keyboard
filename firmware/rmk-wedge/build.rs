//! Puts memory.x on the linker path and packs vial.json for RMK's Vial support.
use std::{env, fs, io::Read, path::PathBuf};

use const_gen::*;
use xz2::read::XzEncoder;

fn main() {
    println!("cargo:rerun-if-changed=vial.json");
    println!("cargo:rerun-if-changed=memory.x");
    println!("cargo:rerun-if-changed=keyboard.toml");
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());

    let vial = fs::read_to_string("vial.json").expect("vial.json missing");
    let vial = json::stringify(json::parse(&vial).expect("vial.json is not valid JSON"));
    let mut packed = Vec::new();
    XzEncoder::new(vial.as_bytes(), 6).read_to_end(&mut packed).unwrap();
    // 8 random bytes identifying this keyboard to Vial
    let id: Vec<u8> = vec![0x53, 0x53, 0x50, 0x57, 0x45, 0x44, 0x47, 0x31];
    let decls = [
        const_declaration!(pub VIAL_KEYBOARD_DEF = packed),
        const_declaration!(pub VIAL_KEYBOARD_ID = id),
    ]
    .map(|s| "#[allow(clippy::redundant_static_lifetimes)]\n".to_owned() + s.as_str())
    .join("\n");
    fs::write(out.join("config_generated.rs"), decls).unwrap();

    fs::copy("memory.x", out.join("memory.x")).unwrap();
    println!("cargo:rustc-link-search={}", out.display());
    println!("cargo:rustc-link-arg=--nmagic");
    println!("cargo:rustc-link-arg=-Tlink.x");
    println!("cargo:rustc-link-arg=-Tdefmt.x");
}
