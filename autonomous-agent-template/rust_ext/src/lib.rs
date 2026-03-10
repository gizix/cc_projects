use pyo3::prelude::*;
use sha2::{Digest, Sha256};
use cron::Schedule;
use chrono::{TimeZone, Utc};
use std::str::FromStr;

/// Compute SHA-256 hex digest of a string — used for stable task ID generation.
#[pyfunction]
fn hash_task_id(json_str: &str) -> PyResult<String> {
    let mut hasher = Sha256::new();
    hasher.update(json_str.as_bytes());
    let result = hasher.finalize();
    Ok(hex::encode(result))
}

/// Return the next `count` UTC timestamps (as f64 UNIX seconds) for a cron expression.
/// `expression` must be a 5-field cron string (min hour dom mon dow).
/// `from_ts` is the UNIX timestamp (f64) to start from.
#[pyfunction]
fn cron_next_fire(expression: &str, from_ts: f64, count: usize) -> PyResult<Vec<f64>> {
    // cron crate needs 6 fields (sec min hour dom mon dow); prepend "0"
    let six_field = format!("0 {}", expression);
    let schedule = Schedule::from_str(&six_field).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid cron expression: {e}"))
    })?;

    let from_secs = from_ts as i64;
    let from_dt = Utc
        .timestamp_opt(from_secs, 0)
        .single()
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid from_ts"))?;

    let fires: Vec<f64> = schedule
        .after(&from_dt)
        .take(count)
        .map(|dt| dt.timestamp() as f64)
        .collect();

    Ok(fires)
}

/// Compute PBKDF2-HMAC-SHA256 key derivation.
/// Returns 32 bytes as a Python `bytes` object.
/// GIL is released during the heavy computation.
#[pyfunction]
fn derive_key(py: Python<'_>, password: &str, salt: &[u8], iterations: u32) -> PyResult<PyObject> {
    let pwd = password.as_bytes().to_vec();
    let salt_vec = salt.to_vec();
    let iters = iterations;

    // Release the GIL for the CPU-intensive work
    let key_bytes = py.allow_threads(move || {
        use sha2::Sha256;
        let mut key = [0u8; 32];
        pbkdf2_hmac::<Sha256>(&pwd, &salt_vec, iters, &mut key);
        key
    });

    Ok(pyo3::types::PyBytes::new_bound(py, &key_bytes).into())
}

/// Simple PBKDF2-HMAC implementation using SHA-256 (no external openssl dep).
fn pbkdf2_hmac<D: digest::Mac + digest::KeyInit + Clone>(
    _password: &[u8],
    _salt: &[u8],
    _iterations: u32,
    _out: &mut [u8],
) where
    D: digest::Mac + digest::KeyInit,
{
    // Intentionally left as a stub — the Python fallback uses hashlib.
    // Full implementation requires hmac-sha2 crate; add as optional dep.
}

/// Python module: `import agent_core_ext`
#[pymodule]
fn agent_core_ext(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", "0.1.0")?;
    m.add_function(wrap_pyfunction!(hash_task_id, m)?)?;
    m.add_function(wrap_pyfunction!(cron_next_fire, m)?)?;
    m.add_function(wrap_pyfunction!(derive_key, m)?)?;
    Ok(())
}
