#!/bin/env rust-script
//! ```cargo
//! [dependencies]
//! rusqlite = { version = "0.29.0", features = ["bundled-sqlcipher"] }
//! ```
#![feature(try_blocks)]

use rusqlite::{params, Connection};
use std::env::args;
use std::io::{stdin, BufRead, BufReader};
use std::process::exit;

fn main() {
    let args = args().skip(1).collect::<Vec<_>>();
    if args.is_empty() {
        println!("Usage: cmd <db> <kdf_iter>");
        println!("Stdin: keys");
        return;
    }
    let db_path = &args[0];
    let kdf_iter = &args[1];

    let stdin = stdin().lock();
    let reader = BufReader::new(stdin);
    for (i, line) in reader.lines().enumerate() {
        let key = line.expect("Line read error");
        println!("Trying: {} {}", i + 1, key);
        let result: rusqlite::Result<String> = try {
            let db = Connection::open(db_path)?;
            // 设置密钥和KDF参数
//             PRAGMA key = 'pass';    -- pass 替换为之前得到的密码（32字节字符串）
// PRAGMA cipher_page_size = 4096;
// PRAGMA kdf_iter = 4000; -- 非默认值 256000
// PRAGMA cipher_hmac_algorithm = HMAC_SHA1; -- 非默认值（见上文）
// PRAGMA cipher_default_kdf_algorithm = PBKDF2_HMAC_SHA512;
// PRAGMA cipher = 'aes-256-cbc';
            db.pragma(None, "key", &key, |_| Ok(()))?;
            db.pragma(None, "cipher_page_size", 4000, |_| Ok(()))?;
            db.pragma(None, "cipher_hmac_algorithm", HMAC_SHA1, |_| Ok(()))?;
            db.pragma(None, "key", &key, |_| Ok(()))?;
            db.pragma(None, "kdf_iter", kdf_iter, |_| Ok(()))?;
            // 执行查询以验证密钥
            let row = db.query_row("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1", params![], |r| {
                r.get::<_, String>(0)
            })?;
            println!("{}", row);
            key
        };
        match result {
            Ok(k) => {
                println!("Found it!! {}", k);
                exit(0);
            }
            Err(e) => {
                if e.to_string() != "file is not a database" {
                    println!("{}", e);
                }
            }
        }
    }
}
qmwxmHxsd%4q[(xc